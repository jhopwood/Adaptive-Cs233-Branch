#!/usr/bin/env python
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

import urllib2
import logging
import random
import json
import itertools
import math

from base_handler import BaseHandler
from helpers.eparser import Parser, spec
from collections import OrderedDict

class FiniteStateProblem(BaseHandler):
  # The valid types are finite state machines 
  # and next state tables.
  valid_types = ["nst", "fsm"]
  # FSM problems will have two states or three states
  # The only input symbols are 0 and 1
  two_states = ["A", "B"]
  three_states = ["A", "B", "C"]
  machine_alphabet = [0, 1]
  problem_scores = {}
  symbols = []

  def maximum_level(self, question_type):
    return 1

  def is_valid_type(self, problem_name):
    return problem_name in self.valid_types

  def get_score_dict(self, student_answer, transitions):
    scores = {}
    for k, v in student_answer.iteritems():
      tt = self.get_truthtable(v)
      scores[k] = int(round(self.get_score(k, tt, transitions)))
    self.problem_scores = scores
    return scores

  def score_student_answer(self,question_type,question_data,student_answer):
    transitions = OrderedDict(question_data[0])
    return_obj = json.loads(student_answer)
    correct_expressions = self.get_correct_expressions(return_obj.iterkeys(), transitions)
    scores = self.get_score_dict(return_obj, transitions)
    # The score is just the average over the expressions
    overall = sum(scores.values()) / len(scores)  
    return (float(overall), json.dumps(correct_expressions))

  def get_return_data(self, score, wanted):
    base_dict = super(FiniteStateProblem, self).get_return_data(score, wanted)
    base_dict["scores"] = json.dumps(self.problem_scores)
    return base_dict

  def get_score(self, expname, tt, transitions):
    # This is an expression for nextX, we grab the X here
    next_state = expname[-1]
    num_correct = 0
    # Calculate a score for every expression given and return 
    for state_tup, output in tt.iteritems():
      val = transitions.get(state_tup, None)
      sym = next_state if output else val
      num_correct = num_correct + int(sym == val)
    return (float(num_correct) / len(tt)) * 100

  def get_correct_expressions(self, expression_names, transitions):
    exps = {}
    for exp in expression_names:
      st = exp[-1]
      nextSet = dict((k, v) for (k, v) in transitions.iteritems() if v == st)
      terms = []
      for k in nextSet.iterkeys():
        term = k[0] + "I" if k[1] == 1 else k[0] + "I'"
        terms.append(term)
      sum_of_minterms = " + ".join(terms)
      exps[exp] = sum_of_minterms.strip()
    return exps

  def get_truthtable(self, expression):
    tt = {}
    (p, s, g) = self.parse_expression(expression)
    terminals_map = p.terminals
    num_terminals = len(self.symbols)
    for i in range(num_terminals - 1):
      for j in range(num_terminals - 1):
        # Make it so that we are only ever in one state at a time.
        val = int (i == j)
        # Grab the current state! It's important to know.
        if val == 1:
          cur_state = self.symbols[j]
        terminals_map[self.symbols[j]].val = val
      # Set input = 0
      terminals_map[self.symbols[-1]].val = 0
      tt[(cur_state, 0)] = 1 if g.evaluate() else 0
      # Set input = 1
      terminals_map[self.symbols[-1]].val = 1
      value_tuple = tuple([terminals_map[s].val for s in self.symbols])
      tt[(cur_state, 1)] = 1 if g.evaluate() else 0
    return tt

  def parse_expression(self, answer):
    symstring = ''.join(self.symbols);
    parser = Parser(spec, symstring)
    parser.reset()
    parser.scan(answer)
    graph = parser.start[0].final
    return (parser, symstring, graph)

  # The 'data' for a question should basically be the states
  def data_for_question(self,problem_name):
    return self.data_for_nst_request()

  def data_for_nst_request(self):
    # Set the number of states based on the problem level.
    headers = ["Initial State", "Input", "Next State"]
    if self.level == 1:
      states = self.three_states
    else:
      states = self.two_states
    # The symbols we will encounter include "I" for input
    symbols = states + ["I"]
    symstring = ''.join(symbols)
    self.symbols = symbols
    # Generate the Cartesian product of states and inputs (inputs are 0 and 1)
    table = itertools.product(states, self.machine_alphabet)
    # Make this the key to a dictionary
    d = {k: self.generator.choice(states) for k in table}
    # Sort this by initial state
    sorted_list = sorted(d.iteritems(), key=lambda x: x[0])
    return (sorted_list, states, symbols, symstring, headers) 
