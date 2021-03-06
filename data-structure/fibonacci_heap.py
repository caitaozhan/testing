'''
after figuring out that fibonacci heap is complex, decide to import package instead
'''

import fibheap as fibh

item_list = [3, 1, 2, 1, 6]
heap = fibh.makefheap()
nodes = [fibh.Node(i) for i in item_list]
for node in nodes:
    heap.insert(node)

min_node = heap.extract_min()
print(min_node.key)
heap.decrease_key(nodes[4], -1)   # 4 here is the node index

for node in nodes:
    print(node.key, end=' ')
print()

sorted_list = []
while heap.num_nodes:
    sorted_list.append(heap.extract_min().key)
print(sorted_list)
