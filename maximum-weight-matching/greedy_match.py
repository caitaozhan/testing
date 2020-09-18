import time
import random
from typing import List

def create_data_array_toy():
    n = 4
    edges = [(0, 4, 90),  (0, 5, 76),  (0, 6, 75), (0, 7, 70),
             (1, 4, 35),  (1, 5, 85),  (1, 6, 55), (1, 7, 65),
             (2, 4, 125), (2, 5, 95),  (2, 6, 90), (2, 7, 105),
             (3, 4, 45),  (3, 5, 110), (3, 6, 95), (3, 7, 115)]
    return n, edges

def cost2edges(cost, negative=True):
    start = time.time()
    n = len(cost)
    edges = []
    for i in range(n):
        for j in range(n):
            c = -cost[i][j] if negative else cost[i][j]
            if c != 0:
                edges.append((i, j+n, c))
    print('1. time for building the edges = {}'.format(time.time() - start))
    return edges


def create_data_array(n: int):
    '''n is the number of nodes
    '''
    cost = [[0 for _ in range(n)] for _ in range(n)]
    for left in range(n):
        right_side = random.sample(range(n), int(n/10))
        for right in right_side:
            cost[left][right] = -random.randint(100, 10_000)
    return cost


def greedy(n: int, edges: List):
    '''
    Args:
        n -- number of nodes
        edges -- represent a bitar
    '''
    start = time.time()
    edges = sorted(edges, key=lambda x:x[2], reverse=True)
    left_node = set()
    right_node = set()
    match = {}
    i = 0
    weight_sum = 0
    while len(left_node) < n and len(right_node) < n and i < len(edges):
        left, right, weight = edges[i]
        if (left not in left_node) and (right not in right_node):
            weight_sum += weight
            left_node.add(left)
            right_node.add(right)
            match[left] = right
        i += 1
    print('2. time for greedy = {:.6f}'.format(time.time() - start))
    return weight_sum, match


if __name__ == '__main__':
    # n, edges = create_data_array_toy()
    # print(greedy(n, edges))

    cost = create_data_array(1000)
    edges = cost2edges(cost)
    weight_sum, match = greedy(len(cost), edges)
    print(weight_sum, len(match))

