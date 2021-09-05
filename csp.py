from ortools.sat.python import cp_model
import random

model = cp_model.CpModel()

# 2mod3: 10, 15, 19

input_bits = 8
num_ins = 23
memory_len = num_ins+input_bits
output_bits = 1
function_table = []

MAX = (1 << (1 << input_bits)) - 1

for idx in range(1 << input_bits):
    in_bits = tuple([1 if idx & (1 << (input_bits-i-1)) else 0 for i in range(input_bits)])
    #out_bits = (random.getrandbits(1) if idx != 0 else 0,)
    #out_bits = (1 if sum(in_bits) == 1 else 0,)
    #out_bits = (1 if sum(in_bits) % 2 == 1 else 0,)
    out_bits = (1 if idx % 3 == 2 else 0,)
    #out_bits = (1 if sum(in_bits) > input_bits // 2 else 0,)
    function_table.append((in_bits, out_bits))

print (function_table)

instructions = []

for ins_id in range(num_ins):
    working_mem = min(memory_len - 1, input_bits + ins_id - 1)
    operand = model.NewIntVar(0, working_mem - 1, 'operand_' + str(ins_id))
    operator = model.NewIntVar(0, 4, 'operator_' + str(ins_id))
    instructions.append((operand, operator))

all_bits_list = []


for calc_id in range(len(function_table)):
    in_bits, out_bits = function_table[calc_id]
    all_bits = [model.NewBoolVar('result_' + str(calc_id) + '_' + str(i)) for i in range(input_bits + num_ins)]
    for i in range(len(in_bits)):
        model.Add(all_bits[i] == in_bits[i])
    for i in range(len(out_bits)):
        model.Add(all_bits[-i-1] == out_bits[-i-1])
    for ins_id in range(num_ins):
        operand, operator = instructions[ins_id]
        all_bit_id = input_bits + ins_id
        operand_bit = model.NewBoolVar('operand_' + str(calc_id) + '_' + str(ins_id))
        all_bits.append(operand_bit)
        for operand_id in range(0, memory_len-1):
            if all_bit_id-2-operand_id < 0:
                continue
            model.AddForbiddenAssignments([operand, operand_bit, all_bits[all_bit_id-2-operand_id]], [(operand_id, 0, 1), (operand_id, 1, 0)])
        model.AddAllowedAssignments([operator, all_bits[all_bit_id-1], operand_bit, all_bits[all_bit_id]],
                                    [(0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0),
                                     (1, 0, 0, 0), (1, 0, 1, 0), (1, 1, 0, 0), (1, 1, 1, 1),
                                     (2, 0, 0, 0), (2, 0, 1, 0), (2, 1, 0, 1), (2, 1, 1, 0),
                                     (3, 0, 0, 0), (3, 0, 1, 1), (3, 1, 0, 0), (3, 1, 1, 0),
                                     (4, 0, 0, 0), (4, 0, 1, 1), (4, 1, 0, 1), (4, 1, 1, 1)])
    all_bits_list.append(all_bits)

solver = cp_model.CpSolver()
status = solver.Solve(model)


def print_var(var):
    print (var.Name(), solver.Value(var))


operator_dict = {0: '^', 1: '&', 2: '>', 3: '<', 4: '|', 5: '*', 6: '!'}

if status == cp_model.OPTIMAL:
    exprs = []
    for i in range(input_bits):
        val = 0
        for j in range(1 << input_bits):
            if not (j >> (input_bits - i - 1)) & 1:
                val |= (1 << j)
        exprs.append(val)
        print('\t'.join([str(i), '', '', bin(exprs[-1])[2:].zfill(1 << input_bits)]))
    for ins_id in range(num_ins):
        operand, operator = instructions[ins_id]
        all_bit_id = input_bits + ins_id
        operand_id = all_bit_id - 2 - solver.Value(operand)
        operator_str = operator_dict[solver.Value(operator)]
        if operator_str == '*':
            exprs.append(exprs[operand_id])
        elif operator_str == '!':
            exprs.append(MAX - exprs[operand_id])
        elif operator_str == '^':
            exprs.append(exprs[-1] ^ exprs[operand_id])
        elif operator_str == '&':
            exprs.append(exprs[-1] & exprs[operand_id])
        elif operator_str == '>':
            exprs.append(exprs[-1] & (MAX - exprs[operand_id]))
        elif operator_str == '<':
            exprs.append((MAX - exprs[-1]) & exprs[operand_id])
        elif operator_str == '|':
            exprs.append(exprs[-1] | exprs[operand_id])
        prev_equal = ''
        for i in range(all_bit_id):
            if exprs[i] == exprs[-1]:
                prev_equal = str(i)
        print('\t'.join([str(all_bit_id), operator_str, str(operand_id), bin(exprs[-1])[2:].zfill(1 << input_bits), prev_equal]))

print(solver.WallTime())

'''
for all_bits in all_bits_list:
    for v in all_bits:
        print_var(v)
'''