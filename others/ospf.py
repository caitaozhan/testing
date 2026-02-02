from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Iterable, Set
from collections import defaultdict
import heapq
import math

MAX_AGE = 3600.0  # seconds (toy value; change as you like)

# ---------------------------
# Minimal LSA (seq + age only)
# ---------------------------
@dataclass
class Link:
    neighbor: str
    cost: float  # must be additive along a path


@dataclass
class Hello:
    sender: str
    seen_neighbors: Set[str]


@dataclass
class LSAHeader:
    advertising_router: str
    sequence_number: int
    age: float


@dataclass
class DBD:
    sender: str
    summaries: List[LSAHeader]


@dataclass
class LSR:
    sender: str
    requested: List[str]


@dataclass
class LSU:
    sender: str
    lsas: List[LSA]

@dataclass
class LSAck:
    sender: str
    acks: List[Tuple[str, int]]  # (advertising_router, sequence_number)


@dataclass
class NeighborFSM:
    STATE_ORDER = ["Down", "Init", "TwoWay", "ExStart", "Exchange", "Loading", "Full"]
    state: str = "Down"           # Down, Init, TwoWay, Exchange, Loading, Full
    last_hello: float = -1e9
    pending_requested: Set[str] = field(default_factory=set)
    master: bool = False


@dataclass
class OSPFMessage:
    type: str  # "HELLO", "DBD", "LSR", "LSU", "LSAck"
    payload: object

@dataclass
class LSA:
    header: LSAHeader
    links: List[Link]

# --------------------------------
# LSDB with seq/age freshness rules
# --------------------------------
class LSDB:
    def __init__(self):
        self._lsas: Dict[str, LSA] = {}  # key = advertising_router

    def get(self, adv: str) -> Optional[LSA]:
        return self._lsas.get(adv)

    def __iter__(self) -> Iterable[LSA]:
        return iter(self._lsas.values())

    def install(self, lsa: LSA) -> bool:
        """
        Install if newer. Return True if DB changed.
        Freshness order within same adv_router:
            1) higher sequence_number wins
            2) if equal seq: smaller age (younger) wins
            3) if lsa.header.age >= MAX_AGE: treat as withdrawal (install briefly to flood, then remove)
        """
        cur = self._lsas.get(lsa.header.advertising_router)

        # Treat withdrawals specially: install (to enable flood) then remove
        if lsa.header.age >= MAX_AGE:
            # Install only if we still have something to withdraw
            if cur is not None:
                self._lsas[lsa.header.advertising_router] = lsa
                # Signal caller to immediately purge after flooding
                return True
            return False

        if cur is None:
            self._lsas[lsa.header.advertising_router] = lsa
            return True

        if lsa.header.sequence_number > cur.header.sequence_number:
            self._lsas[lsa.header.advertising_router] = lsa
            return True
        if lsa.header.sequence_number < cur.header.sequence_number:
            return False

        # Same seq: prefer the younger copy
        if lsa.header.age < cur.header.age - 1e-9:
            self._lsas[lsa.header.advertising_router] = lsa
            return True
        return False

    def purge_withdrawn(self) -> List[str]:
        """Remove any LSAs that are stored at MAX_AGE (after flooding)."""
        removed = []
        for adv, lsa in list(self._lsas.items()):
            if lsa.header.age >= MAX_AGE:
                removed.append(adv)
                del self._lsas[adv]
        return removed

# ---------------------------
# Router with p2p adjacencies
# ---------------------------
class OSPFRouter:
    HELLO_INTERVAL = 10.0
    DEAD_INTERVAL = 40.0

    def __init__(self, router_id: str):
        self.rid = router_id
        self.link_cost: Dict[str, float] = {}            # configured links (physical)
        self.adj_cost: Dict[str, float] = {}             # neighbors with 2-way hellos
        self.lsdb = LSDB()
        self.seq = 1                                      # local sequence number
        self.inbox: List[Tuple[str, OSPFMessage]] = []     # (from_id, message)
        self.outbox: List[Tuple[str, OSPFMessage]] = []    # (to_id, message)
        self.time = 0.0
        self._hello_timer = 0.0
        self._fsm: Dict[str, NeighborFSM] = {}            # neighbor -> fsm state/info

    def add_p2p(self, neighbor: str, cost: float):
        self.link_cost[neighbor] = float(cost)
        self._ensure_fsm(neighbor)

    def _ensure_fsm(self, neighbor: str) -> NeighborFSM:
        if neighbor not in self._fsm:
            self._fsm[neighbor] = NeighborFSM()
        return self._fsm[neighbor]

    def _set_state(self, neighbor: str, new_state: str):
        info = self._ensure_fsm(neighbor)
        if info.state == new_state:
            return
        info.state = new_state
        # Update adjacency table only when crossing the 2-way boundary
        if new_state == "TwoWay":
            if neighbor not in self.adj_cost:
                self.adj_cost[neighbor] = self.link_cost[neighbor]
                self.originate_and_flood()
        elif NeighborFSM.STATE_ORDER.index(new_state) < NeighborFSM.STATE_ORDER.index("TwoWay"):
            if neighbor in self.adj_cost:
                del self.adj_cost[neighbor]
                self.originate_and_flood()

    # ---- Origination ----
    def originate(self) -> LSA:
        links = [Link(n, c) for n, c in sorted(self.adj_cost.items())]
        header = LSAHeader(self.rid, self.seq, 0.0)
        lsa = LSA(header, links)
        self.seq += 1
        return lsa

    def withdraw_self(self) -> LSA:
        # Flood one MaxAge copy of self to withdraw (e.g., before shutdown)
        links = []  # body content is irrelevant for a flush
        return LSA(LSAHeader(self.rid, self.seq, MAX_AGE), links)

    # ---- Flooding core ----
    def _flood_to_all(self, lsa: LSA, exclude_neighbor: Optional[str] = None):
        for nbr in self.adj_cost:
            if nbr == exclude_neighbor:
                continue
            self.outbox.append((nbr, OSPFMessage("LSU", LSU(self.rid, [lsa]))))

    def receive(self, from_id: str, message: OSPFMessage):
        """Process a received OSPF message."""
        if message.type == "HELLO":
            self._receive_hello(from_id, message.payload)
        elif message.type == "DBD":
            self._receive_dbd(from_id, message.payload)
        elif message.type == "LSR":
            self._receive_lsr(from_id, message.payload)
        elif message.type == "LSU":
            self._receive_lsu(from_id, message.payload)
        elif message.type == "LSAck":
            self._receive_lsack(from_id, message.payload)
        else:
            raise ValueError(f"unknown message type {message.type}")

    def originate_and_flood(self):
        lsa = self.originate()
        # Install our own LSA (always newer for self) then flood
        self.lsdb.install(lsa)
        self._flood_to_all(lsa, exclude_neighbor=None)

    # ---- Hellos / adjacency management ----
    def send_hellos(self):
        """Send one Hello to every configured link neighbor."""
        seen = {n for n, info in self._fsm.items() if self.time - info.last_hello <= self.DEAD_INTERVAL}
        for nbr in self.link_cost:
            hello = Hello(self.rid, set(seen))
            self.outbox.append((nbr, OSPFMessage("HELLO", hello)))

    def _receive_hello(self, from_id: str, hello: Hello):
        info = self._ensure_fsm(from_id)
        info.last_hello = self.time
        if info.state == "Down":
            self._set_state(from_id, "Init")
        two_way = self.rid in hello.seen_neighbors
        if two_way and NeighborFSM.STATE_ORDER.index(info.state) < NeighborFSM.STATE_ORDER.index("TwoWay"):
            # Promote to TwoWay and start exchange
            self._set_state(from_id, "TwoWay")
            self._start_exstart(from_id)

    def _reap_dead_neighbors(self):
        """Demote adjacencies whose Hellos have expired."""
        dead: List[str] = []
        for nbr, info in list(self._fsm.items()):
            if info.state != "Down" and self.time - info.last_hello > self.DEAD_INTERVAL:
                dead.append(nbr)
        for nbr in dead:
            self._set_state(nbr, "Down")
            self._fsm[nbr].pending_requested.clear()

    def _start_exstart(self, neighbor: str):
        """Enter ExStart (choose master) and begin DB exchange."""
        info = self._ensure_fsm(neighbor)
        info.pending_requested.clear()
        info.master = self.rid > neighbor
        self._set_state(neighbor, "ExStart")
        # Master kicks off with first DBD
        if info.master:
            self._send_dbd(neighbor)

    def _send_dbd(self, to_id: str):
        """Send a Database Description (summary of our LSDB) to a neighbor."""
        summaries = [LSAHeader(lsa.header.advertising_router, lsa.header.sequence_number, lsa.header.age)
                     for lsa in self.lsdb
                     if lsa.header.age < MAX_AGE]
        self.outbox.append((to_id, OSPFMessage("DBD", DBD(self.rid, summaries))))

    def _receive_dbd(self, from_id: str, dbd: DBD):
        """On receiving DBD, request anything we lack or have older copy of."""
        info = self._ensure_fsm(from_id)
        if info.state == "Down":
            return
        if info.state == "TwoWay":
            # Ensure master/slave negotiation happens before Exchange
            self._start_exstart(from_id)
            info = self._ensure_fsm(from_id)
        if info.state == "ExStart":
            # If we are slave, receiving master's first DBD transitions us to Exchange
            if not info.master:
                self._set_state(from_id, "Exchange")
                self._send_dbd(from_id)
            else:
                # Master transitions once it sees the peer's first DBD
                self._set_state(from_id, "Exchange")
        want: List[str] = []
        for summ in dbd.summaries:
            cur = self.lsdb.get(summ.advertising_router)
            if cur is None:
                want.append(summ.advertising_router)
            else:
                newer_seq = summ.sequence_number > cur.header.sequence_number
                same_seq_younger = summ.sequence_number == cur.header.sequence_number and summ.age < cur.header.age - 1e-9
                if newer_seq or same_seq_younger:
                    want.append(summ.advertising_router)
        if want:
            info.pending_requested = set(want)
            self._set_state(from_id, "Loading")
            self.outbox.append((from_id, OSPFMessage("LSR", LSR(self.rid, want))))
        else:
            if info.pending_requested:
                info.pending_requested.clear()
            if NeighborFSM.STATE_ORDER.index(info.state) < NeighborFSM.STATE_ORDER.index("Full"):
                self._set_state(from_id, "Full")

    def _receive_lsr(self, from_id: str, lsr: LSR):
        """Respond with the requested LSAs."""
        info = self._ensure_fsm(from_id)
        if info.state == "Down":
            return
        lsas: List[LSA] = []
        for adv in lsr.requested:
            cur = self.lsdb.get(adv)
            if cur is not None:
                lsas.append(cur)
        if lsas:
            self.outbox.append((from_id, OSPFMessage("LSU", LSU(self.rid, lsas))))

    def _receive_lsu(self, from_id: str, lsu: LSU):
        info = self._ensure_fsm(from_id)
        if NeighborFSM.STATE_ORDER.index(info.state) < NeighborFSM.STATE_ORDER.index("Exchange"):
            return
        acks: List[Tuple[str, int]] = []
        for lsa in lsu.lsas:
            self._receive_lsa(from_id, lsa)
            acks.append((lsa.header.advertising_router, lsa.header.sequence_number))
            if lsa.header.advertising_router in info.pending_requested:
                info.pending_requested.discard(lsa.header.advertising_router)
        if acks:
            self.outbox.append((from_id, OSPFMessage("LSAck", LSAck(self.rid, acks))))
        if not info.pending_requested and NeighborFSM.STATE_ORDER.index(info.state) >= NeighborFSM.STATE_ORDER.index("Exchange"):
            self._set_state(from_id, "Full")

    def _receive_lsack(self, from_id: str, lsack: LSAck):
        """Toy handling: accept acknowledgements but do not track retransmission."""
        return

    # ---- LSA handling ----
    def _receive_lsa(self, from_id: str, lsa: LSA):
        """Process a received LSA; install-if-newer and flood onward."""
        changed = self.lsdb.install(lsa)
        if not changed:
            return
        # If it's a withdrawal we still flood once, then purge locally
        if lsa.header.age >= MAX_AGE:
            self._flood_to_all(lsa, exclude_neighbor=from_id)
            self.lsdb.purge_withdrawn()
        else:
            self._flood_to_all(lsa, exclude_neighbor=from_id)

    # ---- Aging ----
    def tick(self, dt: float, send_hellos: bool = True):
        """
        Advance local time and age LSAs. If any reach MAX_AGE, flood once & purge.
        Optionally send Hellos (disable for scenarios where control traffic stops).
        """
        self.time += dt
        if send_hellos:
            self._hello_timer += dt
            if self._hello_timer >= self.HELLO_INTERVAL - 1e-12:
                self._hello_timer = self._hello_timer % self.HELLO_INTERVAL
                self.send_hellos()

        self._reap_dead_neighbors()

        expired: List[LSA] = []
        # Age copies
        for lsa in list(self.lsdb):
            if lsa.header.age < MAX_AGE:
                lsa.header.age = min(MAX_AGE, lsa.header.age + dt)
                if math.isclose(lsa.header.age, MAX_AGE) or lsa.header.age >= MAX_AGE:
                    expired.append(lsa)
        # Flood withdrawals for those that hit MaxAge
        for lsa in expired:
            # Create a MaxAge copy to flood (same seq; age=MAX_AGE)
            maxage_lsa = LSA(LSAHeader(lsa.header.advertising_router, lsa.header.sequence_number, MAX_AGE), [])
            # Install to ensure we flood it even if body changed
            changed = self.lsdb.install(maxage_lsa)
            if changed:
                self._flood_to_all(maxage_lsa, exclude_neighbor=None)
        # Purge withdrawn after flooding
        self.lsdb.purge_withdrawn()

    # ---- SPF (Dijkstra) ----
    def spf(self) -> Tuple[Dict[str, float], Dict[str, str]]:
        """
        Return (dist, nexthop) where:
          dist[dst] = total cost from self.rid to dst
          nexthop[dst] = first router to send to (simple single-path; pick lowest RID on ties)
        """
        # Build adjacency from installed LSAs
        adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        for lsa in self.lsdb:
            if lsa.header.age >= MAX_AGE:
                continue
            u = lsa.header.advertising_router
            for link in lsa.links:
                adj[u].append((link.neighbor, link.cost))

        INF = 1e18
        dist = {n: INF for n in adj}
        prev: Dict[str, Set[str]] = {n: set() for n in adj}
        dist[self.rid] = 0.0
        pq: List[Tuple[float, str]] = [(0.0, self.rid)]
        visited: Set[str] = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            for v, w in adj.get(u, []):
                alt = d + w
                if alt < dist[v] - 1e-12:
                    dist[v] = alt
                    prev[v] = {u}
                    heapq.heappush(pq, (alt, v))
                elif abs(alt - dist[v]) <= 1e-12:
                    prev[v].add(u)

        # Simple next-hop selection (break ECMP ties by smallest neighbor RID)
        nexthop: Dict[str, str] = {}
        for dst in adj:
            if dst == self.rid or dist[dst] >= INF:
                continue
            # Walk back one step at a time until reaching a neighbor of self
            cur_front = {dst}
            first_hops: Set[str] = set()
            while cur_front and not first_hops:
                nxt = set()
                for node in cur_front:
                    for p in prev.get(node, set()):
                        if p == self.rid:
                            first_hops.add(node)
                        else:
                            nxt.add(p)
                cur_front = nxt
            if first_hops:
                nexthop[dst] = sorted(first_hops)[0]
        return dist, nexthop

# ---------------------------
# Perfect channel "Network"
# ---------------------------
class Network:
    def __init__(self):
        self.routers: Dict[str, OSPFRouter] = {}

    def add(self, r: OSPFRouter):
        self.routers[r.rid] = r

    def connect_p2p(self, a: str, b: str, cost_ab: float, cost_ba: Optional[float] = None):
        if cost_ba is None:
            cost_ba = cost_ab
        self.routers[a].add_p2p(b, cost_ab)
        self.routers[b].add_p2p(a, cost_ba)

    def deliver_all(self):
        # Drain every outbox into receivers' inboxes
        pending = False
        for r in self.routers.values():
            while r.outbox:
                to_id, message = r.outbox.pop(0)
                payload = message.payload
                if isinstance(payload, LSA):
                    payload = LSA(LSAHeader(payload.header.advertising_router, payload.header.sequence_number, payload.header.age), list(payload.links))
                elif isinstance(payload, Hello):
                    payload = Hello(payload.sender, set(payload.seen_neighbors))
                elif isinstance(payload, DBD):
                    payload = DBD(payload.sender, [LSAHeader(s.advertising_router, s.sequence_number, s.age) for s in payload.summaries])
                elif isinstance(payload, LSR):
                    payload = LSR(payload.sender, list(payload.requested))
                elif isinstance(payload, LSU):
                    payload = LSU(payload.sender, [LSA(LSAHeader(lsa.header.advertising_router, lsa.header.sequence_number, lsa.header.age), list(lsa.links)) for lsa in payload.lsas])
                elif isinstance(payload, LSAck):
                    payload = LSAck(payload.sender, list(payload.acks))
                self.routers[to_id].inbox.append((r.rid, OSPFMessage(message.type, payload)))
                pending = True
        # Process all inboxes (could interleave send/recv; here we do two passes)
        for r in self.routers.values():
            while r.inbox:
                from_id, message = r.inbox.pop(0)
                r.receive(from_id, message)
        return pending

    def flood_until_quiescent(self):
        while self.deliver_all():
            pass

# ---------------------------
# Demo
# ---------------------------
if __name__ == "__main__":
    net = Network()
    for rid in ["R1", "R2", "R3", "R4"]:
        net.add(OSPFRouter(rid))

    # Topology (p2p):
    # R1--10--R2--10--R3
    #  \               /
    #   \--12----------R4
    # R3--5--R4
    net.connect_p2p("R1", "R2", 10)
    net.connect_p2p("R2", "R3", 10)
    net.connect_p2p("R3", "R4", 5)
    net.connect_p2p("R1", "R4", 12)

    # Step 1: neighbor discovery via Hellos (two rounds to reach 2-way)
    for r in net.routers.values():
        r.send_hellos()
    net.flood_until_quiescent()
    for r in net.routers.values():
        r.tick(OSPFRouter.HELLO_INTERVAL)
    net.flood_until_quiescent()

    # Show initial routes from R1
    dist, nh = net.routers["R1"].spf()
    print("=== After initial flood ===")
    print("Distances from R1:")
    for k in sorted(dist):
        if dist[k] < 1e17:
            print(f"  {k}: {dist[k]:.1f}")
    print("Next-hops from R1:")
    for k in sorted(nh):
        print(f"  to {k} via {nh[k]}")

    # Step 2: let time pass (no refresh), LSAs age out and get withdrawn
    # (For demo, jump near MAX_AGE so we see withdrawal flooding)
    for r in net.routers.values():
        r.tick(MAX_AGE - 1, send_hellos=False)  # almost expired
    net.flood_until_quiescent()
    # one more second to hit MAX_AGE and trigger withdrawals
    for r in net.routers.values():
        r.tick(1, send_hellos=False)
    net.flood_until_quiescent()

    print("\n=== After expiry (no refresh) ===")
    for rid, r in sorted(net.routers.items()):
        print(f"{rid} LSDB size: {len(list(r.lsdb))}")

    # Step 3: restart Hellos to rediscover neighbors and rebuild LSDBs
    for r in net.routers.values():
        r.send_hellos()
    net.flood_until_quiescent()
    for r in net.routers.values():
        r.tick(OSPFRouter.HELLO_INTERVAL)
    net.flood_until_quiescent()

    dist, nh = net.routers["R1"].spf()
    print("\n=== After rediscovery ===")
    print("Distances from R1:")
    for k in sorted(dist):
        if dist[k] < 1e17:
            print(f"  {k}: {dist[k]:.1f}")
    print("Next-hops from R1:")
    for k in sorted(nh):
        print(f"  to {k} via {nh[k]}")
