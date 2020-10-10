'''
dp solution for traveling salesman problem, O(n^2 * 2^n), n is the number of nodes
'''

if __name__ == '__main__':
    d = [[float('inf') for _ in range(5)] for _ in range(5)]
    edges = [[0, 1, 3], [1, 2, 5], [2, 3, 5], [3, 4, 3], [4, 0, 7], [4, 1, 6], [0, 3, 4], [2, 0, 4]]
    for u, v, l in edges:
        d[u][v] = l
    dp = [[float('inf') for _ in range(5)] for _ in range((1 << 5))]
    dp[0][0] = 0

    for s in range(1, (1 << 5)):       # the current (binary) state that needs to update. the previous states are done.
        for u in range(5):             # previous node u
            for v in range(5):         # current node v
                if (s >> v) & 1 == 0:  # current node v needs be in the current state
                    continue
                if dp[s - (1 << v)][u] + d[u][v] < dp[s][v]:
                    dp[s][v] = dp[s - (1 << v)][u] + d[u][v]
    print(dp[(1 << 5) - 1][0])
