from liveness import *


class UInterferenceGraphNode:

    def __init__(self, value, avail_colors, color=0):
        self.color = color
        self.value = value
        self.adj_nodes = []
        self.avail_colors = []
        self.init_avail_colors(avail_colors)
        self.unspillable = False
    
    def init_avail_colors(self, avail_colors):
        for color in avail_colors:
            self.avail_colors.append(color)

    def remove_color_from_avail_colors(self, color):
        if color in self.avail_colors:
            self.avail_colors.remove(color)

    def set_color(self, color):
        self.color = color
        for adj_node in self.adj_nodes:
            adj_node.remove_color_from_avail_colors(color)

    def is_adjacent_to_color(self, color):
        for node in self.adj_nodes:
            if node.color == color:
                return True
        return False



class UInterferenceGraph:

    def __init__(self, prog_variables, unspillable_vars, liveness_map):

        self.int_size = 4
        self.caller_saved_regs = ['eax', 'ecx', 'edx']
        self.map_color_register = {1 : "eax",
                                   2 : "ecx",
                                   3 : "edx",
                                   4 : "ebx",
                                   5 : "edi",
                                   6 : "esi"}

        self.nodes = [] 
        self.prog_variables = prog_variables
        self.unspillable_vars = unspillable_vars
        self.liveness_map = liveness_map
        self.max_color = 0
        self.stack_spill_offset = 0

        self.append_prog_vars()
        self.append_registers()

        self.solve_edges()
        self.solve_color()
        self.assert_pairwise_unique_coloring()

    def print_vars_avail_colors(self):
        for var in self.prog_variables:
            node = self.get_node(var)
            res = f"Avail_Colors({var} (\033[1m {node.color}\033[0m)) = ["
            for color in node.avail_colors:
                res += f"\033[1m {color},\033[0m"
            print(res + "]")

    def append_prog_vars(self) : 
        for var in self.prog_variables:
            avail_colors = list(self.map_color_register)
            node = UInterferenceGraphNode(var, avail_colors)
            if var in self.unspillable_vars:
                node.unspillable = True
            self.nodes.append(node)
    
    def append_registers(self):
        for color in self.map_color_register:
            reg = self.map_color_register[color]
            avail_colors = []
            self.nodes.append(UInterferenceGraphNode(reg, avail_colors, color))
            self.max_color += 1
    
    def solve_edges(self):

        i = 0

        for instr_liveness_pair in self.liveness_map.lst:

            x86_instr = instr_liveness_pair.instruction
            liveness_set_after = self.liveness_map.get_instr_after(i).liveness

            if isinstance(x86_instr, IR_movl):

                s = x86_instr.src
                t = x86_instr.dest

                for v in liveness_set_after:
                    if v == t or v == s:
                        continue
                    self.add_edge(t, v)


            elif isinstance(x86_instr, IR_addl):

                s = x86_instr.src
                t = x86_instr.dest

                for v in liveness_set_after:
                    if v == t:
                        continue
                    self.add_edge(t, v)


            elif isinstance(x86_instr, IR_negl):

                t = x86_instr.src

                for v in liveness_set_after:
                    if v == t:
                        continue
                    self.add_edge(t, v)

            elif isinstance(x86_instr, IR_call):

                for v in liveness_set_after:
                    for r in self.caller_saved_regs:
                        self.add_edge(r, v)

                if x86_instr.id == "eval_input":
                    t = x86_instr.args

                    for v in liveness_set_after:
                        if v == t:
                            continue
                        self.add_edge(t, v)
                
            else:
                print(f"ERR : unrecognized instruction")
            
            i += 1

    def set_color(self, node_value, color):
        for node in self.nodes:
            if node.value == node_value:
                node.color = color
                return
        print(f"Err : in set_color() could not find node \'{node_value}\' to color")
        
            
    def order(self, node):
        return len(node.adj_nodes)

    def saturation(self, node):
        return len(set(node.color for node in node.adj_nodes))

    def get_most_saturated_uncolored_node(self):

        print(f"[+++++] START get_most_satureated_node")

        uncolored_node_saturs = []

        for node in self.nodes:
            if node.color == 0:
                satur = self.saturation(node)
                uncolored_node_saturs.append((node, satur))

        if len(uncolored_node_saturs) == 0:
            return None
        
        uncolored_node_saturs = sorted(uncolored_node_saturs, key=lambda x: x[1], reverse=True)

        highest_satur_unspillable = None
        highest_satur_unspillable_satur = -1

        for node_satur_pair in uncolored_node_saturs:
            if node_satur_pair[0].unspillable:
                highest_satur_unspillable = node_satur_pair[0]
                highest_satur_unspillable_satur = node_satur_pair[1]
        
        if highest_satur_unspillable == None:
            node_ret = uncolored_node_saturs[0][0]
            node_satur = uncolored_node_saturs[0][1]
            print(f"returning highest_satur {node_ret.value} with satur {node_satur}")
            return node_ret
        
        node_ret = highest_satur_unspillable
        print(f"returning highest_satur_UNSPILLABLE {node_ret.value} of satur {highest_satur_unspillable_satur}")
        print(f"[+++++] END get_most_satureated_node")
        return highest_satur_unspillable
        


    def get_highest_order_uncolored_node(self):

        max_order = 0
        max_order_node = None
        
        for node in self.nodes:
            if node.color > 0:
                continue

            c = self.order(node)

            if (c > max_order):
                max_order = c
                max_order_node = node

        return max_order_node    


    def solve_color(self):
        
        while True:

            node = self.get_most_saturated_uncolored_node()

            if not node:
                break

            if len(node.avail_colors) == 0:

                print(f"[+] SPILL required")

                self.stack_spill_offset += self.int_size
                self.max_color += 1
                self.map_color_register[self.max_color] = f"-{self.stack_spill_offset}(%ebp)"
                node.set_color(self.max_color)

                continue
            
            color = node.avail_colors[0]
            node.set_color(color)


    def get_node(self, value):
        for node in self.nodes:
            if node.value == value:
                return node
        print(f"UInterferenceGraph Error : node \'{value}\' not found in nodes")


    def add_edge(self, v1, v2):

        node_1 = self.get_node(v1)
        node_2 = self.get_node(v2)

        if node_1 == None or node_2 == None:
            return

        if node_1.color > 0 and node_2.color == 0:
            node_2.remove_color_from_avail_colors(node_1.color)

        if node_1.color == 0 and node_2.color > 0:
            node_1.remove_color_from_avail_colors(node_2.color)

        if node_1 not in node_2.adj_nodes:
            node_2.adj_nodes.append(node_1)

        if node_2 not in node_1.adj_nodes:
            node_1.adj_nodes.append(node_2)
        
    def assert_pairwise_unique_coloring(self):
        for node in self.nodes:
            n_color = node.color
            if n_color == 0:
                print(f"***ERROR*** : Node {node.value} is Un-colored")
                return False
            for adj_node in node.adj_nodes:
                if adj_node.color == n_color:
                    print(f"***ERROR*** :  Graph coloring failed")
                    print(f"*** NODE {node.value} ({node.color}) has same color as {adj_node.value} ({adj_node.color})")
                    return False
        print("[+] Graph colored successfully")
        return True

    def __repr__(self):
        s = ""
        if len(self.nodes) == 0:
            return "<Empty Graph>"
        for node in self.nodes:
            s += f"\033[1m{node.value}\033[0m (\033[1m{node.color}\033[0m) : "
            adj_s = ""
            if len(node.adj_nodes) == 0:
                adj_s = "[]"
            else:
                adj_s = "["
                i = 0
                for adj_node in node.adj_nodes:
                    comma = ""  if i == len(node.adj_nodes) -1 else ", "
                    adj_s += f"\033[1m{adj_node.value}{comma}\033[0m"
                    i += 1
                adj_s = adj_s + "]"
            s += adj_s + "\n"
        return s



class RegisterAllocation:

    def __init__(self, interference_graph):
        self.IG = interference_graph
        self.homes = {}
        self.assign_homes()

    def assign_homes(self):
        for var in self.IG.prog_variables:
            var_node = self.IG.get_node(var)
            self.homes[var] = self.IG.map_color_register[var_node.color]

    def get_home(self, var):
        home = self.homes[var]
        if not home:
            print(f"Err : in get_home() var \'{var}\' doesn't have a home")
            return None
        return self.homes[var]
    
    def get_spillage(self):
        lst = []
        for var in self.homes:
            home = self.get_home(var)
            if self.is_stack_ref(home):
                lst.append((var, home))
        return lst

    def is_stack_ref(self, loc):
        return "(" in loc

    def __repr__(self):
        res = ""
        for key in self.homes:
            res += f"{key} : {self.homes[key]}" + "\n"
        return res
