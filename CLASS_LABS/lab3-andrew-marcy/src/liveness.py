from x86_IR import *


def copy_set(s):
    new_set = set() 
    for elem in s:
        new_set.add(elem)
    return new_set


class InstructionLivenessPair:
    def __init__(self, instruction, liveness):
        self.instruction = instruction
        self.liveness = liveness
    def __repr__(self):
        return f"{self.instruction} : L_BEFORE = \033[1m{self.liveness} \033[0m"


class LivenessMap:

    def __init__(self, IR):
        self.IR = IR
        self.lst = []
        self.init_intruction_liveness_map()
        self.cur_liveness_set = set()
        self.solve_liveness()

        if len(self.cur_liveness_set) != 0:
            print(f"\033[1mWARNING\033[0m : current liveness set NOT empty after solving: {self.cur_liveness_set}")

    def init_intruction_liveness_map(self):
        for i in range(len(self.IR)):
            self.lst.append(None)

    def get_instr_after(self, i):
        lst = self.lst
        if (i == len(lst) - 1):
            return InstructionLivenessPair(instruction = None, liveness = set())
        else:
            return lst[i + 1]
        
    def solve_liveness(self):

        i = len(self.IR) - 1

        while i >= 0:

            ir_op = self.IR[i]
            
            if isinstance(ir_op, IR_addl):

                if not is_numeric(ir_op.src):
                    self.cur_liveness_set |= {ir_op.src}
                
                self.cur_liveness_set |= {ir_op.dest}
            
            elif isinstance(ir_op, IR_movl):
                if not is_eval_input(ir_op.src):
                    if not is_numeric(ir_op.src):
                        self.cur_liveness_set |= {ir_op.src}

                self.cur_liveness_set -= {ir_op.dest}
            
            elif isinstance(ir_op, IR_negl):

                if not is_numeric(ir_op.src):
                    self.cur_liveness_set |= {ir_op.src}
            
            elif isinstance(ir_op, IR_call):

                if ir_op.id == "print":
                    if not is_numeric(ir_op.args):
                        self.cur_liveness_set |= {ir_op.args}
                
                elif ir_op.id == "eval_input":
                    self.cur_liveness_set -= {ir_op.args}
    

            liveness_snapshot = copy_set(self.cur_liveness_set)
            pair = (ir_op, liveness_snapshot)
            self.lst[i] = InstructionLivenessPair(instruction = ir_op, liveness = liveness_snapshot)

            i -= 1

    def __repr__(self):
        s = ""
        for instr_liveness_pair in self.lst:
            s += str(instr_liveness_pair) + "\n"
        return s
