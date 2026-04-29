import math
from x86_IR import *


# Local variable liveness calculations
# ===============================================


def copy_set(s):
    new_set = set() 
    for elem in s:
        new_set.add(elem)
    return new_set



class IRInstruction:
    def __init__(self, instruction):
        self.instruction = instruction
        self.liveness_before = set()
        self.LOG_offset = 30
    def __repr__(self):
        s1 = str(self.instruction)
        s2 = str(self.liveness_before)
        space = max(self.LOG_offset - len(s1), 0)
        space_s = "-" * space
        return f"{s1}{space_s}LBefore = \033[1m{s2}\033[0m"



class BasicBlock:

    def __init__(self, id):
        self.id = id
        self.name = f"BLOCK_{id}"
        self.IR_instr_list = []
        self.successors = []
        self.predecessors = []
        self.live_in = set()
        self.live_out = set()
        self.liveness_converged = False
        self.visited = False
        self.successor_liveness_contributors = []

        # purpose - we need to know when this basic block
        # has had it's liveness set contributed
        # to by ALL it's successors in the
        # in the liveness analysis algorithm
        # hence we keep a list of the liveness
        # contributors
        

    def contains_label(self, label):
        for IR_instr in self.IR_instr_list:
            if isinstance(IR_instr.instruction, IR_label):
                if IR_instr.instruction.label == label:
                    return True
        return False

    def add_successor(self, s):
        if s not in self.successors:
            self.successors.append(s)

    def add_predecessor(self, p):
        if p not in self.predecessors:
            self.predecessors.append(p)
    
    def add_liveness_contributor(self, block):
        if block == None:
            return
        if block not in self.successor_liveness_contributors:
            self.successor_liveness_contributors.append(block)

    def all_successors_contributed_to_liveness(self):
        return len(self.successor_liveness_contributors) == len(self.successors)

    def add_instr(self, instr):
        self.IR_instr_list.append(IRInstruction(instr))

    def last_instr(self):
        return self.IR_instr_list[len(self.IR_instr_list) - 1].instruction

    def __repr__(self):
        res = ""
        for IR_instr in self.IR_instr_list:
            res += str(IR_instr) + "\n"
        return res


class BasicBlockList:

    def __init__(self, IR):
        self.IR = IR
        self.counter = 1
        self.basic_blocks = []
        self.get_basic_blocks()
        self.solve_successors()
        self.solve_predecessors()
        
    
    def get_dest_block(self, label):
        for block in self.basic_blocks:
            if block.contains_label(label):
                return block
        print(f"BB find label ERR: \"{label}\"")
        exit(0)

    def is_basic_block_end(self, instr):
        if isinstance(instr, IR_je):
            return 0
        if isinstance(instr, IR_jmp):
            return 0
        if isinstance(instr, IR_label):
            if "while" in instr.label:
                return 1
            elif "end" in instr.label:
                return 1
        return -1
    
    def new_basic_block(self, IR, start_idx, end_idx):
        bb = BasicBlock(self.counter)
        self.counter += 1
        for i in range(start_idx, end_idx):
            bb.add_instr(IR[i])
        return bb

    def get_basic_blocks(self):

        IR = self.IR.get_instruction_list()
        IR_len = len(IR)
        idx = 0
        
        while idx < IR_len:

            scan_idx = idx + 1

            while (scan_idx < IR_len):

                is_while_start = self.is_basic_block_end(IR[scan_idx])

                if is_while_start == 1:
                    break
                    
                if is_while_start == 0:
                    scan_idx += 1 # want to include while: in basic_block
                    break

                scan_idx += 1

            bb = self.new_basic_block(IR, idx, scan_idx)
            self.basic_blocks.append(bb)

            idx = scan_idx  

    def solve_successors(self):
        
        for i in range(len(self.basic_blocks)):

            blocks = self.basic_blocks

            block_end = blocks[i].last_instr()

            if isinstance(block_end, IR_je):        
                blocks[i].add_successor(blocks[i + 1])
                blocks[i].add_successor(self.get_dest_block(block_end.label))
        
            elif isinstance(block_end, IR_jmp):
                blocks[i].add_successor(self.get_dest_block(block_end.label))

            elif i < len(self.basic_blocks) - 1:
                blocks[i].add_successor(blocks[i + 1])

    def solve_predecessors(self):
        for block in self.basic_blocks:
            for successor_block in block.successors:
                successor_block.add_predecessor(block)


    def __repr__(self):
        res = ""
        for block in self.basic_blocks:
            res += f"===={block.name}====\n{block}\n"
        return res



class CFGraph:

    def __init__(self, bb_list):
        self.basic_blocks = bb_list.basic_blocks
        self.solve_liveness()
    
    def solve_liveness(self):
        if len(self.basic_blocks) == 0:
            return    
            
        last_block = self.basic_blocks[len(self.basic_blocks) - 1]
        cur_liveness_set = set()
        self.solve(last_block, None, cur_liveness_set)
        
    def solve(self, block, successor, live_in_successor):

        # block --> the block whose liveness is being solved here
        # successor --> the block that is calling solve() a.k.a. the successor
        # of "block"
        
        # print(f"\nsolve({block.name})")
        # print(f"Visiting {block.name}")
        # print(f"Block's current LiveOut = {block.live_out}")
        # print(f"Block's predecessor's live_in = {live_out}")


        if block.visited == True:
            if block.live_out == live_in_successor:
                if block.all_successors_contributed_to_liveness():
                    print(f"{block.name} converged...")
                    block.liveness_converged = True

        
        block.live_out |= live_in_successor
        this_liveness = copy_set(block.live_out)

        i = len(block.IR_instr_list) - 1
        while i >= 0:

            IR_instr = block.IR_instr_list[i]
            ir_op = IR_instr.instruction
            
            if isinstance(ir_op, IR_addl):
                if not is_numeric(ir_op.src):
                    this_liveness |= {ir_op.src}
                this_liveness |= {ir_op.dest}
            
            elif isinstance(ir_op, IR_movl):
                this_liveness -= {ir_op.dest}
                if not is_eval_input(ir_op.src):
                    if not is_numeric(ir_op.src):
                        this_liveness |= {ir_op.src}
            
            elif isinstance(ir_op, IR_movzbl):
                this_liveness -= {ir_op.dest}
            
            elif isinstance(ir_op, IR_negl):
                if not is_numeric(ir_op.src):
                    this_liveness |= {ir_op.src}
            
            elif isinstance(ir_op, IR_cmpl):
                if not is_numeric(ir_op.left):
                    this_liveness |= {ir_op.left}
                if not is_numeric(ir_op.right):
                    this_liveness |= {ir_op.right}
            
            elif isinstance(ir_op, IR_call):
                if ir_op.id == "print":
                    if not is_numeric(ir_op.args):
                        this_liveness |= {ir_op.args}
                elif ir_op.id == "eval_input":
                    this_liveness -= {ir_op.args}

            # if i == len(block.IR_instr_list) - 1:
            #     print(f"Setting IR_instr({IR_instr.instruction}).liveness_before = {this_liveness}")
            IR_instr.liveness_before |= this_liveness
            i -= 1
        
        block.visited = True
        block.live_in = this_liveness
        block.add_liveness_contributor(successor)
        
        for predecessor in block.predecessors:

            if not predecessor.liveness_converged:

                live_out_pred = copy_set(block.live_in)
                self.solve(predecessor, block, live_out_pred)


    def __repr__(self):
        res = "\n-----successor-relations-----\n"
        for block in self.basic_blocks:
            res += block.name + " : ["
            if len(block.successors) == 0:
                res += "]\n"
            else:
                for successor_block in block.successors:
                    res += successor_block.name + ", "
                res = res[:-2] 
                res += "]\n"
        res += "\n-----predecessor-relations-----\n"
        for block in self.basic_blocks:
            res += block.name + " : ["
            if len(block.predecessors) == 0:
                res += "]\n"
            else:
                for predecessor_block in block.predecessors:
                    res += predecessor_block.name + ", "
                res = res[:-2] 
                res += "]\n"
        return res
    


class LivenessMap:

    def __init__(self, cfgraph):
        self.cfgraph = cfgraph
        self.IR_instr_list = []
        self.init_intruction_liveness_map()

    def init_intruction_liveness_map(self):
        for block in self.cfgraph.basic_blocks:
            for IR_instr in block.IR_instr_list:
                self.IR_instr_list.append(IR_instr)

    def get_instr_after(self, i):
        if i >= len(self.IR_instr_list) - 1:
            empty_instr = IRInstruction(None)
            empty_instr.liveness_before = set()
            return empty_instr
        return self.IR_instr_list[i + 1]
    
    def __repr__(self):
        s = ""
        for instr in self.IR_instr_list:
            s += str(instr) + "\n"
        return s
