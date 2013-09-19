import random
import string
import logging
import math

terminals = ["a", "b", "c", "d", "e", "f", "g", "h", "x", "y", "z"]

gates_4_from_2 = [[64, 'm64', 'mux2', 1, 'w14', 1, ['a', 'b'], ['e']], 
  			  [20, 'm20', 'mux2', 1, 'w87', 1, ['c', 'd'], ['e']], 
				  [75, 'm75', 'mux2', 1, 'out', 0, ['w14', 'w87'], ['f']]]

gates_8_from_4 = [[64, 'm64', 'mux4', 2, 'w14', 1, ['a', 'b', 'c', 'd'], ['e', 'f']], 
				  [20, 'm20', 'mux4', 2, 'w87', 1, ['e', 'f', 'g', 'h'], ['e', 'f']], 
				  [75, 'm75', 'mux2', 1, 'out', 0, ['w14', 'w87'], ['g']]]

gates_4 = [[64, 'm64', 'mux4', 2, 'out', 0, ['a', 'b', 'c', 'd'], ['e', 'f']]]
gates_8 = [[64, 'm64', 'mux8', 3, 'out', 0, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'], ['x', 'y', 'z']]]

num_inp_sel = {3: [2, 1], 6: [4, 2], 11: [8, 3]}

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
		logging.info("__init__()")
		self.reset(numset)
		self.lanes = {"a": 8, "b": 16, "c": 24, "d": 32, "e": 40, "f": 48, "g": 56, "h": 64, "x":72, "y": 80, "z": 88, "wire": 56}
		self.rails = {"a": 20, "b": 40, "c": 60, "d": 80, "e": 100, "f": 120, "g": 140, "h": 160, "x": 180, "y": 200, "z": 220}
		self.widths = {"mux2": 35, "mux4": 37, "mux8": 50}
		self.heights = {"mux2": 75, "mux4": 87, "mux8": 130}

	def reset(self, numset = number_set()):
		logging.info("reset()")
		self.numset = numset
		self.gates = []
		self.wires = []

	def hardcode_circuit(self, num_terminals, level, solution):
		logging.info("hardcode_circuit(%d,%d)" % (num_terminals, level))
		self.num_inputs = num_inp_sel[num_terminals][0]
		self.num_select = num_inp_sel[num_terminals][1]
		self.rails["wire"] = 8*(num_terminals+1)
		self.gen_circuit(self.num_inputs, level, solution)

	def generate_mux(self, type_num, inputs, select, output, level):
		node_type = ["buf", "mux2", "mux4", "mux8"][type_num]
		number = self.numset.get()
		name = "%s%s" % (node_type[0], number)

		gate = [number, name, node_type, type_num, output, level, inputs, select]
		return gate

	def gen_circuit(self, num_inputs, level, solution):
		if solution == False:
			self.gates = []
			self.gates = gates_4 if level == 0 else gates_8
			return
		inputs = terminals[:self.num_inputs]
		selects = terminals[self.num_inputs:self.num_inputs+self.num_select]
		root_inputs = []
		root_select = selects[len(selects)-1:len(selects)]

		for i in range(0,2):
			input_wire = self.get_wire()
			root_inputs.append(input_wire)
			child_inputs = inputs[i*(self.num_inputs/2):(i+1)*(self.num_inputs/2)]
			child_selects = selects[:len(selects)-1]
			gate = self.generate_mux(len(child_selects), child_inputs, child_selects, input_wire, 1)
			self.gates.append(gate)

		root = self.generate_mux(1, root_inputs, root_select, 'out', 0)
		self.gates.append(root)

	def get_wire(self):
		logging.info("get_wire()")
		name = "w%s" % self.numset.get()
		if len(name) == 2:
			name = name[0] + "0" + name[1]
		self.wires.append(name)
		return name

	def generate_schematic(self):
		logging.info("generate_schematic()")
		logging.info(self.gates)
		terminal_wires = {"a":[-1, 0, 0], "b":[-1, 0, 0], "c":[-1, 0, 0], "d":[-1, 0, 0], "e":[-1, 0, 0], "f":[-1, 0, 0], "g":[-1, 0, 0], "h":[-1, 0, 0], "x":[-1, 0, 0], "y":[-1, 0, 0], "z":[-1, 0, 0]}
		wires = {}
		schematic = ""
		gates = {"buf":"", "mux2":"", "mux4":"", "mux8":""}
		levels = [[], [], [], [], [], []]

		for gate in self.gates:  # assign gates to levels
			level = gate[5]
			levels[level].append(gate)

		cheight = 0
		cwidth = 0
		cheight_mod = 0.5
		cwidth_mod = 0
		max_num = 0
		max_cheight_mod = cheight_mod
		lowest_wire = 0
		max_level = 0

		for i in range(6):
			level = levels[i]
			num = len(level)
			if num > 0:
				final_cwidth = i*100 + 200
				final_cheight = max(cheight, (num + 1) * 120)
				max_level = i

		for i in range(6):
			level = levels[i]
			num = len(levels[i])
			if num > 0:
				for j in range(num):
					gate = level[j]
					gate_width = self.widths[gate[2]]
					gate_height = self.heights[gate[2]]
					num_select = len(gate[7])
					if ((j+1.0)/(num+1) >= max_cheight_mod):
						max_cheight_mod = (j+1.0)/(num+1)
						lowest_wire = max_cheight_mod*final_cheight + gate_height/2 + self.num_select*10

		lowest_wire -= 30

		for i in range(6):
			level = levels[i]
			num = len(level)
			if num > 0:
				cwidth = i*100 + 200
				cheight = lowest_wire + 10

			for j in range(num):
				gate = level[j]
				cheight_mod = (j+1.0)/(num+1)
				cwidth_mod = 100*(i+1)
				gate_width = self.widths[gate[2]]
				gate_height = self.heights[gate[2]]
				num_inputs = len(gate[6])
				num_select = len(gate[7])

				# draw the gate
				# context.drawImage(string.upper(gate[2]), cwidth-cwidth_mod, cheight_mod*cheight-gate_height/2, gate_width, gate_height)
				gates[gate[2]] += "context.drawImage(%s, cwidth - %s, %s*cheight - %s/2, %s, %s);\n" % (string.upper(gate[2]), cwidth_mod, cheight_mod, gate_height, gate_width, gate_height)

				# draw the wire coming out of this gate, if it is not the final output.
				# since we're drawing the circuit from right to left, we already know
				# where the wire goes to (the 3rd segment has already been drawn).
				# also, we know (by construction of these circuits) it only has 1 sink.
				if gate[4][0] == "w":
					wire = wires[gate[4]]
					# draw the horizontal segment
					# draw_line(context, cwidth+gate_width-2-cwidth_mod, cheight_mod*cheight, cwidth-(cwidth_mod-100+wire[0]-1), cheight_mod*cheight)
					draw_wire_horiz = "draw_line(context, cwidth + %s - 2 - %s, %s*cheight, cwidth - %s, %s*cheight);\n" % (gate_width, cwidth_mod, cheight_mod, cwidth_mod - 100 + wire[0] - 1, cheight_mod)
					gates[gate[2]] += draw_wire_horiz
					# draw the vertical segment
					# draw_line(context, cwidth-(cwidth_mod-100+wire[0]), cheight_mod*cheight, cwidth-(cwidth_mod-100+wire[0]), wire[1]*cheigth+wire[2])
					draw_wire_vert = "draw_line(context, cwidth - %s, %s*cheight, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod - 100 + wire[0], cheight_mod, cwidth_mod - 100 + wire[0], wire[1], wire[2])
					schematic += draw_wire_vert
				else:
					# draw_line(context, cwidth-100+gate_width-3, cheight/2, cwidth, cheight/2)
					draw_output = "draw_line(context, cwidth-100+%s-2, cheight/2+0.5, cwidth, cheight/2+0.5);\n" % gate_width
					gates[gate[2]] += draw_output
				
				# draw wires for the gate's inputs
				nextlane = 8*(num_inputs+num_select)
				for k in range(num_inputs):
					inp = gate[6][k]
					# offset is the y-value offset (relative to the center of the gate)
					# where this input wire will go into the gate
					offset = -1*gate_height/2 + (k+1)*(gate_height/(num_inputs+1))
					flush = 2

					if inp[0] != "w":  # is a terminal (e.g., x, y, or z)
						# for these wires, we need to figure out if we need to draw rails
						# (the horizontal lines from the left hand edge) or put in joints
						lane = self.lanes[inp]
						if terminal_wires[inp][0] == -1:  # first wire, draw rail and label
							# draw_line(context, 0, self.rails[inp], cwidth-(cwidth_mod+lane), self.rails[inp])
							draw_first_wire = "draw_line(context, 0, %s, cwidth - %s, %s);\n" % (self.rails[inp], cwidth_mod+lane, self.rails[inp])
							schematic += draw_first_wire
						elif terminal_wires[inp][0] != i: # need to put a joint on rail
							# draw_circle(context, cwidth-(cwidth_mod+lane), self.rails[inp], 2)
							draw_joint = "draw_circle(context, cwidth - %s, %s, 2);\n" % (cwidth_mod+lane, self.rails[inp])
							schematic += draw_joint
						else: # need to put a joint on line from rail at the previous gate
							# draw_circle(context, cwidth-(cwidth_mod+lane), terminal_wires[inp][1]*cheight+terminal_wires[inp][2])
							draw_joint_prv = "draw_circle(context, cwidth - %s, %s*cheight + %s, 2);\n" % (cwidth_mod+lane, terminal_wires[inp][1], terminal_wires[inp][2])
							schematic += draw_joint_prv
						terminal_wires[inp] = [i, cheight_mod, offset]
							
						# draw vertical wire (might be redundant if overlapped by later wire)
						# draw_line(context, cwidth-(cwidth_mod+lane), self.rails[inp], cwidth-(cwidth_mod+lane), cheight_mod*cheight+offset+1)
						draw_vertical_wire = "draw_line(context, cwidth - %s, %s, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod+lane, self.rails[inp], cwidth_mod+lane, cheight_mod, offset+1)
						schematic += draw_vertical_wire
					else: # not a terminal
						if wires.has_key(inp):
							lane = wires[inp][0]  # this shouldn't happen...  wire has 2 sinks
						else: # assign it a lane, and record it so that we can connect to it
							lane = nextlane
							wires[inp] = [lane, cheight_mod, offset]
							nextlane += 8

					# draw horizontal wire going into gate's input
					# draw_line(context, cwidth-(cwidth_mod+lane+1), cheight_mod*cheight+offset, cwidth-(cwidth_mod-2), cheight_mod*cheight+offset)
					draw_input = "draw_line(context, cwidth - %s, %s*cheight + %s, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod+lane+1, cheight_mod, offset+0.5, cwidth_mod-flush, cheight_mod, offset+0.5)
					gates[gate[2]] += draw_input

				for ii in range(num_select):
					inp = gate[7][ii]
					# offset is the y-coordinate of the select wire before
					# it reaches the input (relative to the center of the gate)
					offset = gate_height/2 + 2 + ii*10
					# select_height is the height of the select wire into the gate
					# relative to the center of the gate
					select_height = gate_height/2 - ((ii+1)*gate_height/4)/(num_select+1)
					select_width = cwidth_mod-(ii+1)*gate_width/(num_select+1)
					lowest = False

					if inp[0] != "w":  # is a terminal (e.g., x, y, or z)
						# for these wires, we need to figure out if we need to draw rails
						# (the horizontal lines from the left hand edge) or put in joints

						# lane is a horizontal offset for wires (separated by 8px)
						lane = self.lanes[inp]
						if terminal_wires[inp][0] == -1:  # first wire, draw rail and label
							draw_first_wire = "draw_line(context, 0, %s, cwidth - %s, %s);\n" % (self.rails[inp], cwidth_mod+lane, self.rails[inp])
							draw_first = "draw_line(context, 0, %s, cwidth - %s, %s);\n" % (self.rails[inp], cwidth_mod+lane+100, self.rails[inp])
							if i > 0 or max_level == 0:
								# draw_line(context, 0, self.rails[inp], cwidth - (cwidth_mod+lane), self.rails[inp])
								schematic += draw_first_wire
							else:
								# draw_line(context, 0, self.rails[inp], cwidth - (cwidth_mod+lane+100), self.rails[inp])
								schematic += draw_first
								lowest = True
						elif terminal_wires[inp][0] != i: # need to put a joint on rail
							# draw_circle(context, cwidth-(cwidth_mod+lane), self.rails[inp], 2)
							draw_joint = "draw_circle(context, cwidth - %s, %s, 2);\n" % (cwidth_mod+lane, self.rails[inp])
							schematic += draw_joint
						else: # need to put a joint on line from rail at the previous gate
							# draw_circle(context, cwidth-(cwidth_mod+lane), terminal_wires[inp][1]*cheight+terminal_wires[inp][2])
							draw_joint_prv = "draw_circle(context, cwidth - %s, %s*cheight + %s, 2);\n" % (cwidth_mod+lane, terminal_wires[inp][1], terminal_wires[inp][2])
							schematic += draw_joint_prv
							
						# this is to ensure the joint is drawn where it should be
						if self.rails[inp] < cheight_mod*final_cheight+offset:
							terminal_wires[inp] = [i, cheight_mod, offset]
						else:
							terminal_wires[inp] = [i, 0, self.rails[inp]]
							
						# draw vertical wire (might be redundant if overlapped by later wire)
						draw_vertical_wire = "draw_line(context, cwidth - %s, %s, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod+lane, self.rails[inp], cwidth_mod+lane, cheight_mod, offset)
						draw_vertical = "draw_line(context, cwidth - %s, %s, cwidth - %s, %s);\n" % (cwidth_mod+lane+100, self.rails[inp], cwidth_mod+lane+100, lowest_wire)
						if i > 0 or max_level == 0:
							# draw_line(context, cwidth-(cwidth_mod+lane), self.rails[inp], cwidth-(cwidth_mod+lane), cheight_mod*cheight+offset)
							schematic += draw_vertical_wire
						else:
							# draw_line(context, cwidth-(cwidth_mod+lane+100), self.rails[inp], cwidth-(cwidth_mod+lane+100), lowest_wire)
							schematic += draw_vertical
							#lowest = True
					else: # not a terminal
						if wires.has_key(inp):
							lane = wires[inp][0]  # this shouldn't happen...  wire has 2 sinks
						else: # assign it a lane, and record it so that we can connect to it
							lane = nextlane
							wires[inp] = [lane, cheight_mod, offset]
							nextlane += 8
					if lowest == False:
						# draw horizontal wire going towards gate's select input
						# draw_line(context, cwidth-(cwidth_mod+lane+1), cheight_mod*cheight+offset, cwidth-select_width, cheight_mod*cheight+offset)
						draw_wire_inputh = "draw_line(context, cwidth - %s, %s*cheight + %s, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod+lane, cheight_mod, offset+0.5, select_width, cheight_mod, offset+0.5)
						# draw vertical wire up to gate's select input
						# draw_line(context, cwidth-select_width, cheight_mod*cheight+offset, cwidth-select_width, cheight_mod*cheight+select_height)
						draw_wire_inputv = "draw_line(context, cwidth - %s, %s*cheight + %s, cwidth - %s, %s*cheight + %s);\n" % (select_width, cheight_mod, offset, select_width, cheight_mod, select_height)
					else:
						#draw_wire_inputh = "draw_line(context, cwidth - %s, %s*cheight + %s, cwidth - %s, %s*cheight + %s);\n" % (cwidth_mod+lane+1, cheight_mod, offset, select_width, cheight_mod, offset)
						#draw_wire_inputv = "draw_line(context, cwidth - %s, %s*cheight + %s, cwidth - %s, %s*cheight + %s);\n" % (select_width, cheight_mod, offset, select_width, cheight_mod, select_height)

						# draw_line(context, cwidth-(cwidth_mod+lane+101), lowest_wire, cwidth-select_width), lowest_wire)
						draw_wire_inputh = "draw_line(context, cwidth - %s, %s, cwidth - %s, %s);\n" % (cwidth_mod+lane+101, lowest_wire, select_width, lowest_wire)
						# draw_line(context, cwidth-select_width, lowest_wire, cwidth-select_width, cheight_mod*cheight+select_height)
						draw_wire_inputv = "draw_line(context, cwidth - %s, %s, cwidth - %s, %s*cheight + %s);\n" % (select_width, lowest_wire, select_width, cheight_mod, select_height)
						lowest_wire += 10
					gates[gate[2]] += draw_wire_inputh + draw_wire_inputv

		cheight = lowest_wire + 10
		size = "var cwidth = %s;\nvar cheight = %s;\n" % (cwidth, cheight)
		canvas = "canvas.width  = cwidth;\ncanvas.height = cheight;\n"

		t = 0
		pairs = [("a", 1), ("b", 2), ("c", 4), ("d", 8), ("e", 16), ("f", 32), ("g", 64), ("h", 128), ("x", 256), ("y", 512), ("z", 1024)]
		for pair in pairs:
			if terminal_wires[pair[0]][0] != -1:
				t += pair[1]
			terms = "var draw_terminals = %s;\n" % t

		num_inputs = "var num_inputs = %i;\n" % self.num_inputs
		num_select = "var num_select = %i;\n" % self.num_select

		for gate in gates.keys():
			schematic += "%s.onload = function() {\n" % string.upper(gate)
			schematic += gates[gate]
			schematic += "}\n"

		logging.info(size + canvas + terms + num_inputs + num_select + schematic)

		return size + canvas + terms + num_inputs + num_select + schematic
