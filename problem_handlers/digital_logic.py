#!/usr/bin/env python
# TODO: Should this license be here? I mean, is the code we write copywright Google?
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import math
import logging
import sys
import os
import re
import random
import string
import json

from helpers import circuit
from helpers import eparser
from helpers import expression

import base_handler

terminals2 = "xy"
# parser2 = eparser.Parser(eparser.spec, terminals2)
terminals3 = "xyz"
# parser3 = eparser.Parser(eparser.spec, terminals3)
cg = circuit.generator()

two_rows = [["0", "0"], ["0", "1"], ["1", "0"], ["1", "1"]]
three_rows = [["0", "0", "0"], ["0", "0", "1"], ["0", "1", "0"], ["0", "1", "1"], ["1", "0", "0"], ["1", "0", "1"], ["1", "1", "0"], ["1", "1", "1"]]

truthtable_defaults = {
 3 : {"cols":["x", "y", "z", "f(x,y,z)"], "rows":three_rows, "numrows":8, "terminals":"xyz"}, 
 2 : {"cols":["x", "y", "f(x,y)"], "rows":two_rows, "numrows":4, "terminals":"xy"}}

class DigitalLogic(base_handler.BaseHandler):
    valid_names = {"e2c": "29IJIFhvuzE", "c2t": "oDMmsa8WxJU",
    		   "t2c": "8sja1RXR_Iw", "e2t": "i2HZ_ZZKg1M",
		   "t2e": "fvPjmPx7g5k", "v2c": "G6rybJ7X6HU",
		   "c2e": "_0KaTciimNM", "v2e": None, "v2t": None}

    def get_expression(self, level, index):
        if level < 3:
           num_terminals = 2
           etemplate = expression.equation_templates2[level]
        else:
           num_terminals = 3
           etemplate = expression.equation_templates3[level-3]
        exp = expression.get_expression(num_terminals, etemplate, index)
        return exp

    def parse_expression(self, level, exp):
        # parser = parser2 if level < 3 else parser3
        if level < 3:
            parser = eparser.Parser(eparser.spec, terminals2)
        else:
            parser = eparser.Parser(eparser.spec, terminals3)
        terminals = terminals2 if level < 3 else terminals3
        parser.reset()
        parser.scan(exp)
        graph = parser.start[0].final
        return (parser, terminals, graph)

    def get_truthtable(self, level, exp):
        tt = []
        (parser, terminals, graph) = self.parse_expression(level, exp)
        terminals_map = parser.terminals
        num_combinations = int(math.pow(2,len(terminals)))
        num_terminals = len(terminals)
        for i in range(num_combinations):
           for j in range(num_terminals):
                # setting the value of terminal j
               val = (i>>(num_terminals-1-j)) & 1
               terminals_map[terminals[j]].val = val
           tt.append(1 if graph.evaluate() else 0)
        return tt

    def get_verilog(self, level, exp, name, output):
        cg.reset()
        (parser, terminals, graph) = self.parse_expression(level, exp)
        cg.generate_circuit(graph, output)
        inputs = "x, y%s" % ('' if level < 3 else ', z')
        return cg.generate_verilog(name, output, inputs)

    def get_circuit(self, level, exp, name, output):
        cg.reset()
        (parser, terminals, graph) = self.parse_expression(level, exp)
        cg.generate_circuit(graph, output)
        inputs = "x, y%s" % ('' if level < 3 else ', z')
        return cg.generate_schematic()

    def get(self, problem_name):   
        self.get_basics(4)
        if self.request.get('type') == "json":    # gradebook request
            self.get_grades(problem_name)     
        else:                                     # student request
            if problem_name == "random":          # give a random problem/level
                problem_name = random.choice(self.valid_names.keys())
                self.problem_id = int(random.random()*100000)
                if self.request.get('l', None) == None:
                    self.level = random.choice(range(5))
            self.serve_problem(problem_name)      

    # the root of every question is generating an expression using all the parameters
    # also we populate "data" with a bunch of junk about the problem.
    def get_base_expression(self, problem_name):
        num_terminals = 2 if self.level < 3 else 3
        exp = self.get_expression(self.level, self.generate_index(self.magic, self.level,
                                                   self.problem_id, problem_name))
	submit_data = {"magic": self.magic, "level": self.level, "problem_id": self.problem_id}
        data = {"submit": submit_data, "magic": self.magic, "problem_id":self.problem_id,
                "qtype": problem_name, "level": self.level, "youtube": self.valid_names[problem_name]}
        data.update(truthtable_defaults[num_terminals])
        return (exp, data, self.level, num_terminals)

    def serve_problem(self, problem_name): # a student requested a problem.
        # generate an expression
        (exp, data, level, num_terminals) = self.get_base_expression(problem_name)

	self.add_best_score(data, problem_name)

        # convert that into the right type of "given"
        given_type = problem_name[0]         
        if given_type == "e": 
            data["expression"] = ("f(x,y) = " if level==2 else "f(x,y,z) = ") + exp
        elif given_type == "t":
            data["truthtable"] = self.get_truthtable(level, exp)
        elif given_type == "v":
            ver = self.get_verilog(level, exp, "circuit", "out")
            data["verilog"] = string.join(ver, "\n")
        elif given_type == "c":
            data["circuit"] = self.get_circuit(level, exp, "circuit", "out")
        else:
            return

        # serve it using the correct template.
        self.render("%s.html" % problem_name, **data)

    
    def post(self, name):   # this is a request for grading a problem.  
        # validate that is a useful thing to grade
        problem_name = self.request.get('q')
        if name != "submit" or not problem_name in self.valid_names:
            logging.info("unrecognized type: %s" % problem_name)

        # generate the expression for the problem that we're trying to grade
        self.get_basics(4)
        (exp, data, level, num_terminals) = self.get_base_expression(problem_name)
        result_tt = self.get_truthtable(level, exp)
        answer = self.request.get('answer')       # grab student answer
        response = {"exp":exp, "result_tt":result_tt}

        # evaluate student answer based on the type of "ask"
        ask_type = problem_name[2]         
        if ask_type == "e" or ask_type == "c":
            user_tt = self.get_truthtable(level, answer)
            score = 100.0 * reduce(lambda x, y: x * y, 
                                   map(lambda x: 1 if x[0] == x[1] else 0, 
                                       zip(map(lambda x: "%s"%x, result_tt), 
                                           map(lambda x: "%s"%x, user_tt))), 1)
            if ask_type == "c":
                response["circuit"] = self.get_circuit(level, exp, "circuit", "out")
        elif ask_type == "t":
            score = 100.0 * reduce(lambda x, y: x + y, 
                                   map(lambda x: 1 if x[0] == x[1] else 0, 
                                       zip(map(lambda x: "%s"%x, result_tt), 
                                           map(lambda x: x[-1], answer.split()))))
            score /= len(result_tt)

        # store the result in the database
	self.put_submission(problem_name, self.level, score, answer)

        # send back a response to the user
        response["score"] = score
        blob = json.dumps(response)
        self.response.out.write(blob)
