import random
import string

class number_set:
    def __init__ (self):
        self.used = set()
        self.range = 100

    def get(self):
        if 2*len(self.used) > self.range:
            self.range *= 2
        while True:
            num = random.randrange(0, self.range)
            if num not in self.used:
                self.used.add(num)
                return num



class generator:
    def __init__ (self, numset = number_set()):
        self.reset(numset)
        self.offsets = [[0], [-10, 10], [-15, 0, 15], [-15, -5, 5, 15]]
        self.or_offsets = [[0], [5, 5], [3, 7, 3], [3, 6, 6, 3]]
        self.lanes = {"x": 8, "y": 16, "z": 24, "wire": 30}
        self.rails = {"x": 20, "y": 40, "z": 60}

    def reset(self, numset = number_set()):
        self.numset = numset
        self.gates = []
        self.wires = []

    def generate_circuit(self, graph, output):
        graph.output = output
        graph.level = 0
        self.traverse(graph, self.generate, 0)
    
    def traverse(self, graph, fun, level):
        fun(graph, level)
        if hasattr(graph, 'term1'):
            self.traverse(graph.term1, fun, level+1)
        if hasattr(graph, 'term2'):
            self.traverse(graph.term2, fun, level+1)

    def get_wire(self):
        name = "w%s" % self.numset.get()
        if len(name) == 2:
            name = name[0] + "0" + name[1]
        self.wires.append(name)
        return name

    def add_child(self, gate, child):
        next_level = gate[5] + 1
        if hasattr(child, 'terminal'):
            # if child.instance_of(TokenTerminal):
            gate.append(child.terminal)
        elif gate[3] == child.type or child.type == 0:  # if this and its child are the same type, then merge
            if hasattr(child, 'term1'):
                self.add_child(gate, child.term1)
                child.term1.level = next_level
            if hasattr(child, 'term2'):
                self.add_child(gate, child.term2)
                child.term1.level = next_level
        else:
            wire = self.get_wire()
            child.output = wire
            child.level = next_level
            gate.append(wire)

    def generate(self, node, level):
        if not hasattr(node, "output"):
            return
        type_num = node.type
        node_type = ["buf", "not", "and", "or "][type_num]
        number = self.numset.get()
        name = "%s%s" % (node_type[0], number)

        gate = [number, name, node_type, type_num, node.output, node.level]

        if hasattr(node, 'term1'):
            self.add_child(gate, node.term1)
        if hasattr(node, 'term2'):
            self.add_child(gate, node.term2)

        self.gates.append(gate)

    def generate_verilog(self, name, output, inputs):
        verilog = []
        verilog.append("module %s(%s, %s);" % (name, output, inputs))
        verilog.append("   output %s;" % output)
        verilog.append("   input  %s;" % inputs)
        if len(self.wires) > 0: 
            self.wires.sort()
            verilog.append("   wire   " + reduce(lambda x, y: "%s, %s" % (x, y), self.wires) + ";")
        verilog.append("")
        for gate in self.gates:
            string = "   %s %s(%s" % (gate[2], gate[1], gate[4])
            for i in gate[6:]:
                string += ", %s" % i
            verilog.append(string + ");")
        verilog.append("")
        verilog.append("endmodule // %s" % name)
        return verilog

    def generate_schematic(self):
        terminal_wires = {"x":[-1, 0, 0], "y":[-1, 0, 0], "z":[-1, 0, 0]}  # (j, cheight_mod, offset) coordinates of previous attach
        wires = {}
        schematic = ""
        gates = {"buf":"", "not":"", "and":"", "or ":""}
        levels = [[], [], [], [], [], []]
        for gate in self.gates:  # assign gates to levels
            level = gate[5]
            levels[level].append(gate)

        cheight = 0
        cwidth = 0

        for i in range(6):
            level = levels[i]
            num = len(level)
            if num > 0:
                cwidth = i*100 + 150
                cheight = max(cheight, (num + 1) * 100)

            for j in range(num):
                gate = level[j]
                cheight_mod = (j+1.0)/(num+1)
                cwidth_mod = 100*(i+1)

                # draw the gate
                gates[gate[2]] += "context.drawImage(%s, cwidth - %s, %s*cheight - gate_height/2, gate_width, gate_height);\n" % (string.upper(gate[2]), cwidth_mod, cheight_mod)

                # draw the wire coming out of this gate, if it is not the final output.
                # since we're drawing the circuit from right to left, we already know
                # where the wire goes to (the 3rd segment has already been drawn).
                # also, we know (by construction of these circuits) it only has 1 sink.
                if gate[4][0] == "w":   
                    wire = wires[gate[4]]
                    # draw the horizontal segment
                    gates[gate[2]] += "draw_line(context, cwidth + gate_width - 2 - %s , %s*cheight, cwidth - %s , %s*cheight);\n" % (cwidth_mod, cheight_mod, cwidth_mod - 100 + wire[0] - 1, cheight_mod)
                    # draw the vertical segment
                    schematic += "draw_line(context, cwidth - %s , %s*cheight, cwidth - %s , %s*cheight + %s);\n" % (cwidth_mod - 100 + wire[0], cheight_mod, cwidth_mod - 100 + wire[0], wire[1], wire[2])
                else:
                    gates[gate[2]] += "draw_line(context, cwidth-100+gate_width-3, cheight/2, cwidth, cheight/2);\n"

                # draw wires for the gate's inputs
                nextlane = self.lanes["wire"]   # first non-terminal lane
                num_inputs = len(gate) - 6
                for ii in range(num_inputs):
                    inp = gate[6+ii]
                    offset = self.offsets[num_inputs-1][ii]
                    flush = 2 if gate[3] != 3 else (2 + self.or_offsets[num_inputs-1][ii])

                    if inp[0] != "w":  # is a terminal (e.g., x, y, or z)
                        # for these wires, we need to figure out if we need to draw rails
                        # (the horizontal lines from the left hand edge) or put in joints
                        lane = self.lanes[inp]
                        if terminal_wires[inp][0] == -1:  # first wire, draw rail and label
                            schematic += "draw_line(context, 0, %s, cwidth - %s, %s);\n" % (self.rails[inp], cwidth_mod+lane, self.rails[inp])
                            
                        elif terminal_wires[inp][0] != i: # need to put a joint on rail
                            schematic += "draw_circle(context, cwidth - %s, %s, 2);\n" % (cwidth_mod+lane, self.rails[inp])
                        else: # need to put a joint on line from rail at the previous gate
                            schematic += "draw_circle(context, cwidth - %s, %s*cheight + %s, 2);\n" % (cwidth_mod+lane, terminal_wires[inp][1], terminal_wires[inp][2])

                        terminal_wires[inp] = [i, cheight_mod, offset]
                            
                        # draw vertical wire (might be redundant if overlapped by later wire)
                        schematic += "draw_line(context, cwidth - %s, %s, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod+lane, self.rails[inp], cwidth_mod+lane, cheight_mod, offset+1)

                    else: # not a terminal
                        if wires.has_key(inp):
                            lane = wires[inp][0]  # this shouldn't happen...  wire has 2 sinks
                        else: # assign it a lane, and record it so that we can connect to it
                            lane = nextlane
                            wires[inp] = [lane, cheight_mod, offset]
                            nextlane += 6

                    # draw horizontal wire going into gate's input
                    gates[gate[2]] += "draw_line(context, cwidth - %s, %s*cheight + %s, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod+lane+1, cheight_mod, offset, cwidth_mod-flush, cheight_mod, offset)

        size = "var cwidth = %s;\n var cheight = %s;\n" % (cwidth, cheight)
	canvas = "canvas.width  = cwidth; canvas.height = cheight - 50;\n"
        t = 0
        for pair in [("x", 1), ("y", 2), ("z", 4)]:
            if terminal_wires[pair[0]][0] != -1:
                t += pair[1]
            terms = "var draw_terminals = %s;\n" % t

        for gate in gates.keys():
            schematic += "%s.onload = function() {\n" % string.upper(gate)
            schematic += gates[gate]
            schematic += "}\n"
            
        return size + canvas + terms + schematic
