from ortools.sat.python import cp_model
import random

model = cp_model.CpModel()

# majority function: (5,3), (7,6), ()

input_bits = 5
num_ins = 10
memory_len = 10
output_bits = 1
function_table = []

for idx in range(1 << input_bits):
    in_bits = tuple([1 if idx & (1 << (input_bits-i-1)) else 0 for i in range(input_bits)])
    #out_bits = (random.getrandbits(1) if idx != 0 else 0,)
    #out_bits = (1 if sum(in_bits) == input_bits//2 else 0,)
    #out_bits = (1 if sum(in_bits) % 2 == 1 else 0,)
    #out_bits = (0 if idx % 3 == 0 else 1,)
    out_bits = (1 if sum(in_bits) > input_bits // 2 else 0,)
    function_table.append((in_bits, out_bits))

print (function_table)

instructions = []

for ins_id in range(num_ins):
    working_mem = min(memory_len - 1, input_bits + ins_id - 1)
    operand = model.NewIntVar(0, working_mem - 1, 'operand_' + str(ins_id))
    operator = model.NewIntVar(0, 5, 'operator_' + str(ins_id))
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
                                     (1, 0, 0, 0), (1, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1),
                                     (2, 0, 0, 0), (2, 0, 1, 1), (2, 1, 0, 1), (2, 1, 1, 1),
                                     (3, 0, 0, 0), (3, 0, 1, 0), (3, 1, 0, 0), (3, 1, 1, 1),
                                     (4, 0, 0, 0), (4, 0, 1, 0), (4, 1, 0, 1), (4, 1, 1, 0),
                                     (5, 0, 0, 0), (5, 0, 1, 1), (5, 1, 0, 0), (5, 1, 1, 0)])
    all_bits_list.append(all_bits)

solver = cp_model.CpSolver()
status = solver.Solve(model)


def print_var(var):
    print (var.Name(), solver.Value(var))


operator_dict = {0: '^', 1: '|', 2: '&', 3: '>', 4: '<', 5: '*'}

if status == cp_model.OPTIMAL:
    exprs = []
    for inp in range(input_bits):
        exprs.append(str(inp))
        print('\t'.join([str(inp), '', '', exprs[-1]]))
    for ins_id in range(num_ins):
        operand, operator = instructions[ins_id]
        all_bit_id = input_bits + ins_id
        operand_id = all_bit_id - 2 - solver.Value(operand)
        operator_str = operator_dict[solver.Value(operator)]
        if operator_str == '*':
            exprs.append(exprs[operand_id])
        else:
            left = exprs[-1] if len(exprs[-1]) == 1 else '(' + exprs[-1] + ')'
            right = exprs[operand_id] if len(exprs[operand_id]) == 1 else '(' + exprs[operand_id] + ')'
            exprs.append(left + operator_str + right)
        print('\t'.join([str(all_bit_id), operator_str, str(operand_id), exprs[-1]]))

print(solver.WallTime())

'''
for all_bits in all_bits_list:
    for v in all_bits:
        print_var(v)
'''