import itertools

N = 4
MAX = (1 << (1 << N)) - 1
NUM_FN = 1 << ((1 << N) - 1)
MAX_DAGS = 1 << 30
MAX_OPS = 12

operand_pairs = []
for i in range(2, MAX_OPS):
    for j in range(1, i):
        operand_pairs.append((i, j))

v = [0]
for i in range(N):
    val = 0
    for j in range(1 << N):
        if not (j >> i) & 1:
            val |= (1 << j)
    v.append(val)

empty_dag = v, []

'''
for x in empty_dag:
    print ("{0:b}".format(x))
'''

def bin(x, d):
    return ('{0:0' + str(d) +'b}').format(x)

permutations = list(itertools.permutations([i for i in range(N)]))
pos_perm = [] # for each pid, return a permutation of 1 << N
for pid in range(len(permutations)):
    perm = permutations[pid]
    perm_idx = []
    for input in range(1 << N):
        inputs = [int(i) for i in bin(input, N)]
        pinputs = [inputs[perm[i]] for i in range(N)]
        pinput = int("".join(str(i) for i in pinputs), 2)
        perm_idx.append(pinput)
    pos_perm.append(perm_idx)
permute_function = [[0]*len(permutations) for i in range(NUM_FN)]

for func in range(NUM_FN):
    for pid in range(len(permutations)):
        perm = permutations[pid]
        val = 0
        for input in range(1 << N):
            if (func >> input) & 1:
                val |= (1 << pos_perm[pid][input])
        permute_function[func][pid] = val

canonical_func = []
set_canonical_funcs = set()
for func in range(NUM_FN):
    best = func, 0
    for pid in range(1, len(permutations)):
        new_func = permute_function[func][pid]
        if new_func < best[0]:
            best = new_func, pid
    canonical_func.append(best)
    set_canonical_funcs.add(best[0])

print (len(set_canonical_funcs))

def canonical_funcs(funcs):
    best = tuple(sorted(funcs)), 0
    for pid in range(1, len(permutations)):
        new_funcs = tuple(sorted([permute_function[func][pid] for func in funcs]))
        if new_funcs < best[0]:
            best = new_funcs, pid
    return best


all_dag_set = set()
all_dag_set.add(canonical_funcs(v)[0])
all_dag_list = [empty_dag]
func_dag_map = {}
for func in v:
    func_dag_map[canonical_func[func][0]] = []

for i in range(MAX_DAGS):
    if len(func_dag_map) >= len(set_canonical_funcs) or i >= len(all_dag_list):
        break
    funcs, ops = all_dag_list[i]
    set_funcs = set(funcs)
    n = len(funcs)
    def check_new_op(func, op):
        if func in set_funcs:
            return
        if len(ops) < 6:
            new_funcs = funcs[:]
            new_funcs.append(func)
            new_canonical_funcs = canonical_funcs(new_funcs)[0]
            if new_canonical_funcs in all_dag_set:
                return
            all_dag_set.add(new_canonical_funcs)
            new_ops = ops[:]
            new_ops.append(op)
            all_dag_list.append((new_funcs, new_ops))
        can_func = canonical_func[func][0]
        if can_func not in func_dag_map:
            new_funcs = funcs[:]
            new_funcs.append(func)
            new_ops = ops[:]
            new_ops.append(op)
            func_dag_map[can_func] = new_ops
            print (bin(func, (1<<N)-1), new_ops)
            print(i, len(all_dag_list), len(func_dag_map))

    for (j, k) in operand_pairs:
        if j >= len(funcs):
            break
        if len(ops) > 0 and (j, k) <= ops[-1]:
            continue
        check_new_op(funcs[j] ^ funcs[k], (j, k, '^'))
        check_new_op(funcs[j] | funcs[k], (j, k, '|'))
        check_new_op(funcs[j] & funcs[k], (j, k, '&'))
        check_new_op(funcs[j] & (MAX-funcs[k]), (j, k, '>'))
        check_new_op((MAX-funcs[j]) & funcs[k], (j, k, '<'))

complexity_counts = {}
for func in func_dag_map:
    dag = func_dag_map[func]
    if len(dag) not in complexity_counts:
        complexity_counts[len(dag)] = 0
    complexity_counts[len(dag)] += 1

print (complexity_counts)

import pickle

with open('func_dict_4.pickle', 'wb') as handle:
    pickle.dump(func_dag_map, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('func_dict_4.pickle', 'rb') as handle:
    func_dict = pickle.load(handle)
    tests = [
        #v[1] ^ v[2] ^ v[3],
        #(v[1] ^ v[2]) & v[3],
        (v[2] ^ v[4]) & (v[1] ^ v[3]),
        v[1] ^ v[2] ^ v[3] ^ v[4],
        (v[2] ^ v[3]) & (v[1] ^ v[4]),
    ]
    for test in tests:
        canonical_test = canonical_func[test][0]
        print (bin(canonical_test, (1<<N)-1), func_dict[canonical_test])
