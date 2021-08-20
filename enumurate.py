input_bits = 3
MAX = (1<<(1<<input_bits))-1
NUM_FN = 1 << ((1 << input_bits) - 1)
MAX_DAGS = 1<<20

import itertools

permutations = list(itertools.permutations([i for i in range(input_bits)]))

trivial_funcs = [0]
for i in range(input_bits):
    val = 0
    for j in range(1<<input_bits):
        if not (j >> i) & 1:
            val |= (1<<j)
    trivial_funcs.append(val)

empty_dag = trivial_funcs, []

'''
for x in empty_dag:
    print ("{0:b}".format(x))
'''

permute_function = [[0]*len(permutations) for i in range(NUM_FN)]

all_dag_set = set([tuple(sorted(trivial_funcs))])
all_dag_list = [empty_dag]
func_dag_map = {}
for func in trivial_funcs:
    func_dag_map[func] = 0

for i in range(MAX_DAGS):
    if len(func_dag_map) >= NUM_FN:
        break
    funcs, ops = all_dag_list[i]
    set_funcs = set(funcs)
    n = len(funcs)
    def check_new_op(func, op):
        if func in set_funcs:
            return
        new_funcs = funcs[:]
        new_funcs.append(func)
        new_funcs_tuple = tuple(sorted(new_funcs))
        if new_funcs_tuple in all_dag_set:
            return
        all_dag_set.add(new_funcs_tuple)
        new_ops = ops[:]
        new_ops.append(op)
        all_dag_list.append((new_funcs, new_ops))
        if func not in func_dag_map:
            func_dag_map[func] = len(all_dag_list)-1
            print ("{0:b}".format(func), ["{0:b}".format(x) for x in new_funcs], new_ops)
        print(len(all_dag_list), len(func_dag_map))
        print(sorted(new_funcs), new_ops)

    for i in range(1, n):
        for j in range(1, i):
            check_new_op(funcs[i] ^ funcs[j], (i, j, '^'))
            check_new_op(funcs[i] | funcs[j], (i, j, '|'))
            check_new_op(funcs[i] & funcs[j], (i, j, '&'))
            check_new_op(funcs[i] & (MAX-funcs[j]), (i, j, '>'))
            check_new_op((MAX-funcs[i]) & funcs[j], (i, j, '<'))