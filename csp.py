from ortools.sat.python import cp_model
import random

model = cp_model.CpModel()

input_bits = 6
num_gates = 13
output_bits = 1
function_table = []

for idx in range(1 << input_bits):
    in_bits = tuple([1 if idx & (1 << (input_bits-i-1)) else 0 for i in range(input_bits)])
    #out_bits = (random.getrandbits(1) if idx != 0 else 0,)
    out_bits = (1 if sum(in_bits) == input_bits//2 else 0,)
    function_table.append((in_bits, out_bits))

print (function_table)

gates = []

for gate_id in range(num_gates):
    left_wire = model.NewIntVar(0, input_bits - 2 + gate_id, 'gate_left_' + str(gate_id))
    right_wire = model.NewIntVar(1, input_bits - 1 + gate_id, 'gate_right_' + str(gate_id))
    model.Add(left_wire < right_wire)
    gate_op = model.NewIntVar(0, 4, 'gate_op_' + str(gate_id))
    gates.append((gate_op, left_wire, right_wire))

all_bits_list = []


for calc_id in range(len(function_table)):
    in_bits, out_bits = function_table[calc_id]
    all_bits = [model.NewBoolVar('calc_bit_' + str(calc_id) + '_' + str(i)) for i in range(input_bits + num_gates)]
    for i in range(len(in_bits)):
        model.Add(all_bits[i] == in_bits[i])
    for i in range(len(out_bits)):
        model.Add(all_bits[-i-1] == out_bits[-i-1])
    for gate_id in range(num_gates):
        gate_op, left_wire, right_wire = gates[gate_id]
        left_bit = model.NewBoolVar('calc_left_' + str(calc_id) + '_' + str(gate_id))
        right_bit = model.NewBoolVar('calc_right_' + str(calc_id) + '_' + str(gate_id))
        all_bits.append(left_bit)
        all_bits.append(right_bit)
        for wire_id in range(0, input_bits - 1 + gate_id):
            model.AddForbiddenAssignments([left_wire, left_bit, all_bits[wire_id]], [(wire_id, 0, 1), (wire_id, 1, 0)])
        for wire_id in range(1, input_bits + gate_id):
            model.AddForbiddenAssignments([right_wire, right_bit, all_bits[wire_id]], [(wire_id, 0, 1), (wire_id, 1, 0)])
        model.AddAllowedAssignments([gate_op, left_bit, right_bit, all_bits[input_bits + gate_id]],
                                    [(0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0),
                                     (1, 0, 0, 0), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 1),
                                     (2, 0, 0, 0), (2, 0, 1, 0), (2, 1, 0, 0), (2, 1, 1, 1),
                                     (3, 0, 0, 0), (3, 0, 1, 0), (3, 1, 0, 1), (3, 1, 1, 0),
                                     (4, 0, 0, 0), (4, 0, 1, 1), (4, 1, 0, 0), (4, 1, 1, 0)])
    all_bits_list.append(all_bits)

solver = cp_model.CpSolver()
status = solver.Solve(model)


def print_var(var):
    print (var.Name(), solver.Value(var))


if status == cp_model.OPTIMAL:
    for gate_id in range(num_gates):
        gate_op, left_wire, right_wire = gates[gate_id]
        print_var(gate_op)
        print_var(left_wire)
        print_var(right_wire)

print (solver.WallTime())

'''
for all_bits in all_bits_list:
    for v in all_bits:
        print_var(v)
'''