'''https://developers.google.com/optimization/assignment/linear_assignment
'''

import time
import random
import numpy as np
from greedy_match import cost2edges, greedy
from ortools.graph import pywrapgraph



def create_data_array_toy():
    cost = [[90, 76, 75, 70],
          [35, 85, 55, 65],
          [125, 95, 90, 105],
          [45, 110, 95, 115]]
    return cost

def create_data_array(n: int):
    '''n is the number of nodes
    '''
    cost = [[0 for _ in range(n)] for _ in range(n)]
    for left in range(n):
        right_side = random.sample(range(n), int(n/10))
        for right in right_side:
            cost[left][right] = -random.randint(100, 10_000)
    return cost


def main(cost):
    # 1: create the solver
    rows = len(cost)
    cols = len(cost[0])
    assignment = pywrapgraph.LinearSumAssignment()

    start = time.time()
    # 2: add costs to the solver
    for worker in range(rows):
        for task in range(cols):
            if cost[worker][task]:
                assignment.AddArcWithCost(worker, task, int(cost[worker][task]))
    print('2. time for initializing the linear assignment solver = {:.6f}'.format(time.time()-start))

    # 3: invoke the solver
    opt = 0
    start = time.time()
    solve_status = assignment.Solve()
    print('3. time for the algorithm = {:.6f}'.format(time.time() - start))
    if solve_status == assignment.OPTIMAL:
        opt = assignment.OptimalCost()
        print('Total cost = ', opt, '\n')
        # for i in range(assignment.NumNodes()):
        #     print('worker {} assigned to task {}. cost = {}'.format(i, assignment.RightMate(i), assignment.AssignmentCost(i)))
    elif solve_status == assignment.INFEASIBLE:
        print('No assignment is possible')
    elif solve_status == assignment.POSSIBLE_OVERFLOW:
        print('Some inputs costs are too large and may cause an integer overflow')
    return opt


if __name__ == '__main__':
    for n in [100, 500, 1000, 5000]:
        print('n = {}'.format(n))
        start = time.time()
        cost = create_data_array(n)
        print('1. time for creating the cost matrix = {:.6f}'.format(time.time()-start))
        opt = main(cost) * -1

        edges = cost2edges(cost)
        weight_sum, _ = greedy(n, edges)
        print('weight sum', weight_sum)
        print('{} percent optimal'.format(weight_sum/opt*100))
        print('*'*10, '\n')

    cost = create_data_array_toy()
    cost = -np.array(cost).astype(np.int)
    main(cost)
