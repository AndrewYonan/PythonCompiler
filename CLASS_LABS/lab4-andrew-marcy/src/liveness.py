import math
from x86_IR import *
from queue import Queue


# Local variable liveness calculations
# ===============================================

def copy_set(s):
    new_set = set() 
    for elem in s:
        new_set.add(elem)
    return new_set


class BasicBlock:

    def __init__(self, id):
        self.id = id
        self.name = f"BLOCK_{id}"
        self.IR_instr_list = []
        self.successors = []
        self.predecessors = []
        self.live_in = set()
        self.live_out = set()
    
    def get_IR_instr_list(self):
        return self.IR_instr_list
    
    def get_instr_liveness_after(self, i):

        if i == len(self.IR_instr_list) - 1:

            live_after = set()

            for successor in self.successors:
                live_after |= successor.live_in
            
            return live_after
        
        elif i >= len(self.IR_instr_list):
            print(f"ERR : attempting to get liveness after instruction index > MAX")
            exit(1)
        
        return self.IR_instr_list[i + 1].liveness_before

    def contains_label(self, label):
        for IR_instr in self.IR_instr_list:
            if isinstance(IR_instr.instruction, IR_label):
                if IR_instr.instruction.label == label:
                    return True
        return False

    def get_union_live_in_successors(self):
        union = set()
        for successor in self.successors:
            union |= successor.live_in
        return union

    def add_successor(self, s):
        if s not in self.successors:
            self.successors.append(s)

    def add_predecessor(self, p):
        if p not in self.predecessors:
            self.predecessors.append(p)

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
        self.solve()
        
    def solve(self):
        self.solve_basic_blocks()
        self.solve_successors()
        self.solve_predecessors()
        
    def get_basic_blocks(self):
        return self.basic_blocks
    
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

    def solve_basic_blocks(self):

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
        self.iter_counter = 0
        self.bbl = bb_list
        self.basic_blocks = bb_list.basic_blocks
        self.fail_safe = 2000 # max recursive iterations
    
    def liveness_analysis(self):
        self.clear_liveness()
        self.solve_liveness()
    
    def get_basic_blocks(self):
        return self.basic_blocks
    
    def clear_liveness(self):
        for block in self.basic_blocks:
            block.live_in = set()
            block.live_out = set()
            for IR_instr in block.IR_instr_list:
                IR_instr.liveness_before = set()

    def solve_liveness(self):

        q = Queue()
        i = len(self.basic_blocks) - 1

        while i >= 0:
            q.put(self.basic_blocks[i])
            i -= 1

        while (not q.empty()):

            block = q.get()
            union_live_in_successors = block.get_union_live_in_successors()

            old_live_in = copy_set(block.live_in)
            new_live_in = self.propogate_liveness_up(block, union_live_in_successors)

            if (old_live_in != new_live_in):
                for predecessor in block.predecessors:
                    q.put(predecessor)


    def propogate_liveness_up(self, block, live_in_successor):

        block.live_out |= live_in_successor
        this_liveness = copy_set(block.live_out)

        i = len(block.IR_instr_list) - 1
        while i >= 0:

            IR_instr = block.IR_instr_list[i]
            ir_op = IR_instr.instruction
            
            if isinstance(ir_op, IR_addl):
                if is_var(ir_op.src):
                    this_liveness |= {ir_op.src}
                this_liveness |= {ir_op.dest}
            
            elif isinstance(ir_op, IR_movl):
                this_liveness -= {ir_op.dest}
                if not is_eval_input(ir_op.src):
                    if is_var(ir_op.src):
                        this_liveness |= {ir_op.src}
            
            elif isinstance(ir_op, IR_movzbl):
                this_liveness -= {ir_op.dest}
            
            elif isinstance(ir_op, IR_negl):
                if is_var(ir_op.src):
                    this_liveness |= {ir_op.src}
            
            elif isinstance(ir_op, IR_cmpl):
                if is_var(ir_op.src):
                    this_liveness |= {ir_op.src}
                if is_var(ir_op.dest):
                    this_liveness |= {ir_op.dest}
            
            elif isinstance(ir_op, IR_call):
                if ir_op.target != None:
                    if is_var(ir_op.target):
                        this_liveness -= {ir_op.target}
                for arg in ir_op.args:
                    if is_var(arg):
                        this_liveness |= {arg}
            
            IR_instr.liveness_before |= this_liveness
            i -= 1
        
        block.live_in = this_liveness
        return this_liveness


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