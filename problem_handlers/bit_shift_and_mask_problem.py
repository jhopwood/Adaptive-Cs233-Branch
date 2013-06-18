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
from pprint import pprint

from helpers import shift_expression

from base_handler import BaseHandler

class BitShiftAndMaskProblem(BaseHandler):
  # Types are code-to-number and 
  valid_types = ["c2n","r2c"]
  total_shift_amount = 0

  def generate_mask(self):
    return self.generator.choice(["0xffffff00",
                                  "0x000000ff",
                                  "0xff000000",
                                  "0x00ffffff",
                                  "0x0000ffff"])

  def generate_shift_amount(self):
    """
    Generates the amount to shift a number by. This method trys to avoid
    generating nothing but 0s (aka shifting by more than 31 to one side).
    """
    adjusted = math.fabs(self.total_shift_amount)
    return self.generator.randint(0,31-adjusted)

  def generate_expression(self,level):
    """
    Generates a shifting/masking expression by text. Level is the level of
    nesting of the expression. Each 'level' is one operation (aka a shift or a
    mask). An expression of level n is a single operation where the left hand
    side is an expression of level n-1 (base case of level = 0, where the left
    hand side is x) and the right hand side is either a shift amount or a mask
    """
    ops = [">>","<<","&","|"]
    op = self.generator.choice(ops)
    if level == 0:
      lhs = shift_expression.SEValue("x")
    else:
      lhs = self.generate_expression(level-1)
    if op == "<<" or op == ">>":
      rhs = self.generate_shift_amount()
      if op == "<<":
        self.total_shift_amount = self.total_shift_amount - rhs
      else:
        self.total_shift_amount = self.total_shift_amount + rhs
    else:
      rhs = self.generate_mask()
    rhs = shift_expression.SEValue(str(rhs))
    return shift_expression.SEExpression(lhs,op,rhs)

  def maximum_level(self, question_type):
    if question_type == "c2n":
      return 1
    else:
      return 0

  def data_for_c2n(self):
    # 32-bit operands - this will pick a random 32-bit unsigned integer
    operand = self.generator.randint(0, 4294967295)
    # Shift by anywhere from 1 - 16 bytes to the right/left
    shamt = self.generate_shift_amount()
    mask = self.generate_mask()
    operation = self.generator.choice(["lshift", "rshift"])
    ops = ("<<", "|") if operation == "lshift" else (">>", "&")
    if operation == "lshift":
      # Keep generating masks until we find one that works
      while (int(mask, 16) << shamt) & 0xffffffff == 0:
        mask = self.generate_mask()
    rdict = {"operand": hex(operand), "mask": mask, "shamt": shamt, "ops": ops, "operation": operation}
    if self.level >= 1:
      # Pick another 32-bit operand and throw it in. 
      rdict["operand2"] = hex(self.generator.randint(0, 4294967295))
      # Throw in another and/or for good measure
      rdict["op2"] = self.generator.choice(["&", "|"])
    return rdict

  def score_c2n(self, question_data, student_answer):
    if student_answer is not None:
      student_answer = int(student_answer, 16)
    op = int(question_data["operand"], 16)
    mask = int(question_data["mask"], 16)
    op2 = int(question_data["operand2"], 16) if self.level == 1 else 0xffffffff
    op = op | op2 if (self.level == 1 and question_data["op2"] == "|") else op & op2
    if question_data["operation"] == "rshift":
      correct_answer = ((op & op2) >> question_data['shamt']) & mask
    else:
      # For some reason numbers occasionally get larger than 32 bits, fixed here
      msk = (mask << question_data["shamt"]) & 0xffffffff
      correct_answer = op | msk
    score = 100.0 if student_answer is not None and student_answer == correct_answer else 0.0
    return (score, hex(correct_answer))  

  def data_for_question(self, question_type):
    if question_type == "c2n":
      return self.data_for_c2n()
    elif question_type == "r2c":
      nesting_level = self.generator.randint(0,4)
      expression = self.generate_expression(nesting_level)
      result = expression.evaluate({"x":shift_expression.SEBits(32)})
      return {"expression":str(expression),"expression_result":str(result)}
      
  def score_student_answer(self,question_type,question_data,student_answer):
    if question_type == "r2c":
      # Send the student answer through our parser and see if it comes out with
      # the same result
      student_result = shift_expression.parse_and_evaluate(student_answer,{"x":shift_expression.SEBits(32)})
      if isinstance(student_result,int):
          # If the student result is an integer, we need to turn it into the
          # same form as the expression_result.
          student_result = "|".join(list(bin(student_result)[2:].zfill(32)))
      logging.warn(student_result)
      if student_result is not None and str(student_result) == question_data["expression_result"]:
        return (100.0,question_data["expression"])
      else:
        return (0.0,question_data["expression"])
    elif question_type == "c2n":
      return self.score_c2n(question_data, student_answer)
