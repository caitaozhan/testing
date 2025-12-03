from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Iterable, Set
import heapq
import math

MAX_AGE = 3600.0  # seconds (toy value; change as you like)

# ---------------------------
# Minimal LSA (seq + age only)
# ---------------------------
@dataclass
class RouterLink:
    neighbor: str
    cost: float  # must be additive along a path

@dataclass
class LSA:
    advertising_router: str              # unique router ID; doubles as key
    sequence_number: int                 # monotonic while router is alive
    age: float                           # seconds since origination
    links: List[RouterLink] = field(default_factory=list)

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
            3) if lsa.age >= MAX_AGE: treat as withdrawal (install briefly to flood, then remove)
        """
        cur = self._lsas.get(lsa.advertising_router)

        # Treat withdrawals specially: install (to enable flood) then remove
        if lsa.age >= MAX_AGE:
            # Install only if we still have something to withdraw
            if cur is not None:
                self._lsas[lsa.advertising_router] = lsa
                # Signal caller to immediately purge after flooding
                return True
            return False

        if cur is None:
            self._lsas[lsa.advertising_router] = lsa
            return True

        if lsa.sequence_number > cur.sequence_number:
            self._lsas[lsa.advertising_router] = lsa
            return True
        if lsa.sequence_number < cur.sequence_number:
            return False

        # Same seq: prefer the younger copy
        if lsa.age < cur.age - 1e-9:
            self._lsas[lsa.advertising_router] = lsa
            return True
        return False

    def purge_withdrawn(self) -> List[str]:
        """Remove any LSAs that are stored at MAX_AGE (after flooding)."""
        removed = []
        for adv, lsa in list(self._lsas.items()):
            if lsa.age >= MAX_AGE:
                removed.append(adv)
                del self._lsas[adv]
        return removed

# ---------------------------
# Router with p2p adjacencies
# ---------------------------
class OSPFRouter:
    def __init__(self, router_id: str):
        self.rid = router_id
        self.neigh_cost: Dict[str, float] = {}           # neighbor -> local cost
        self.lsdb = LSDB()
        self.seq = 1                                      # local sequence number
        self.inbox: List[Tuple[str, LSA]] = []            # (from_id, lsa)
        self.outbox: List[Tuple[str, LSA]] = []           # (to_id, lsa)
        self.time = 0.0

    def add_p2p(self, neighbor: str, cost: float):
        self.neigh_cost[neighbor] = float(cost)

    # ---- Origination ----
    def originate(self) -> LSA:
        links = [RouterLink(n, c) for n, c in sorted(self.neigh_cost.items())]
        lsa = LSA(self.rid, self.seq, 0.0, links)
        self.seq += 1
        return lsa

    def withdraw_self(self) -> LSA:
        # Flood one MaxAge copy of self to withdraw (e.g., before shutdown)
        links = []  # body content is irrelevant for a flush
        return LSA(self.rid, self.seq, MAX_AGE, links)

    # ---- Flooding core ----
    def _flood_to_all(self, lsa: LSA, except_from: Optional[str] = None):
        for nbr in self.neigh_cost:
            if nbr == except_from:
                continue
            self.outbox.append((nbr, lsa))

    def receive(self, from_id: str, lsa: LSA):
        """Process a received LSA; install-if-newer and flood onward."""
        changed = self.lsdb.install(lsa)
        if not changed:
            return
        # If it's a withdrawal we still flood once, then purge locally
        if lsa.age >= MAX_AGE:
            self._flood_to_all(lsa, except_from=from_id)
            self.lsdb.purge_withdrawn()
        else:
            self._flood_to_all(lsa, except_from=from_id)

    def originate_and_flood(self):
        lsa = self.originate()
        # Install our own LSA (always newer for self) then flood
        self.lsdb.install(lsa)
        self._flood_to_all(lsa, except_from=None)

    # ---- Aging ----
    def tick(self, dt: float):
        """Advance local time and age LSAs. If any reach MAX_AGE, flood once & purge."""
        self.time += dt
        expired: List[LSA] = []
        # Age copies
        for lsa in list(self.lsdb):
            if lsa.age < MAX_AGE:
                lsa.age = min(MAX_AGE, lsa.age + dt)
                if math.isclose(lsa.age, MAX_AGE) or lsa.age >= MAX_AGE:
                    expired.append(lsa)
        # Flood withdrawals for those that hit MaxAge
        for lsa in expired:
            # Create a MaxAge copy to flood (same seq; age=MAX_AGE)
            maxage_lsa = LSA(lsa.advertising_router, lsa.sequence_number, MAX_AGE, [])
            # Install to ensure we flood it even if body changed
            changed = self.lsdb.install(maxage_lsa)
            if changed:
                self._flood_to_all(maxage_lsa, except_from=None)
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
        adj: Dict[str, List[Tuple[str, float]]] = {}
        for lsa in self.lsdb:
            if lsa.age >= MAX_AGE:
                continue
            u = lsa.advertising_router
            adj.setdefault(u, [])
            for link in lsa.links:
                adj.setdefault(link.neighbor, [])
                adj[u].append((link.neighbor, link.cost))

        INF = 1e18
        dist = {n: INF for n in adj}
        prev: Dict[str, Set[str]] = {n: set() for n in adj}
        dist[self.rid] = 0.0
        pq: List[Tuple[float, str]] = [(0.0, self.rid)]
        seen: Set[str] = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in seen:
                continue
            seen.add(u)
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
                to_id, lsa = r.outbox.pop(0)
                self.routers[to_id].inbox.append((r.rid, LSA(lsa.advertising_router, lsa.sequence_number, lsa.age, list(lsa.links))))
                pending = True
        # Process all inboxes (could interleave send/recv; here we do two passes)
        for r in self.routers.values():
            while r.inbox:
                from_id, lsa = r.inbox.pop(0)
                r.receive(from_id, lsa)
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

    # Step 1: every router originates once and flood
    for r in net.routers.values():
        r.originate_and_flood()
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
        r.tick(MAX_AGE - 1)  # almost expired
    net.flood_until_quiescent()
    # one more second to hit MAX_AGE and trigger withdrawals
    for r in net.routers.values():
        r.tick(1)
    net.flood_until_quiescent()

    print("\n=== After expiry (no refresh) ===")
    for rid, r in sorted(net.routers.items()):
        print(f"{rid} LSDB size: {len(list(r.lsdb))}")

    # Step 3: R2 refreshes (re-originates), others still expired -> network rebuilds from partial info
    net.routers["R2"].originate_and_flood()
    net.flood_until_quiescent()
    print("\n=== After R2 refreshes ===")
    for rid, r in sorted(net.routers.items()):
        print(f"{rid} sees: {[lsa.advertising_router for lsa in r.lsdb]}")
