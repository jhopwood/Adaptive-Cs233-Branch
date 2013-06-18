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

import logging
import random
import json

from mips_assembler import mips

import base_handler

class MIPSRepresentation(base_handler.BaseHandler):
    __my_random__ = None
    valid_types = ["m2b","b2m"]

    valid_instructions = {
        # R type instructions
        "add":["r","r","r"],
        "and":["r","r","r"],
        "nor":["r","r","r"],
        "or":["r","r","r"],
        "sll":["r","r","s"],
        "srl":["r","r","s"],
        "sub":["r","r","r"],
        "slt":["r","r","r"],
        # I type instructions
        "addi":["r","r","i"],
        "andi":["r","r","i"],
        "lw":["r","r","i"],
        "lbu":["r","r","i"],
        "ori":["r","r","i"],
        "sw":["r","r","i"],
        "sb":["r","r","i"],
        "slti":["r","r","i"],
        # J type instructions (and jr of course)
        # "j":["a"],
        # "jal":["a"],
        "jr":["r"]
    }
    
    valid_registers = [
        # I'm not going to include $ra, as it is only really used for jr $ra,
        # and jr isn't one of the valid instructions
        "$v0",
        "$v1",
        "$a0",
        "$a1",
        "$a2",
        "$a3",
        "$t0",
        "$t1",
        "$t2",
        "$t3",
        "$t4",
        "$t5",
        "$t6",
        "$t7",
        "$s0",
        "$s1",
        "$s2",
        "$s3",
        "$s4",
        "$s5",
        "$s6",
        "$s7",
        "$t8",
        "$t9",
        # Since there is no reason to do most functions with $sp (like
        # 'sll $t0, $sp, 4'), I will just leave it out until I come up with
        # a better solution
        # "$sp"
    ]

    def is_valid_type(self, question_type):
      return question_type in self.valid_types
    
    def get(self, question_type):
        self.get_basics(2)
        # If the user wants a random question, replace question_type with
        # a random valid question type
        if question_type == "random":
            question_type = random.choice(self.valid_types)
            if self.request.get('l', None) == None:
                self.level = random.choice(range(2))
        # If the question type is valid, check to see if it is a grade request
        # (aka type=json), otherwise generate a new problem     
        if self.is_valid_type(question_type):
            if self.request.get('type') == 'json':
                return self.get_grades(question_type)
            question_data = self.data_for_question(question_type)
            logging.warn(question_data)
            submit_data = { "question_type":question_type, "magic":self.magic,
                            "level":self.level, "problem_id":self.problem_id}
            data = {"submit": submit_data, "question":question_data}
            self.add_best_score(data, question_type)
            self.render("mips_representation.html", **data)
        else:
            self.response.out.write("Invalid URL")
        
    def post(self, question_type):
        if not self.is_valid_type(question_type):
            return self.response.out.write("Invalid URL")
        self.get_basics(2)
        student_answer = self.request.get('answer')
        question_data = self.data_for_question(question_type)
        wanted_binary = question_data["binary"]
        student_answer_binary = student_answer
        # If the student is converting to MIPS, we convert their MIPS to binary
        # and compare against that instead
        if question_type == "b2m":
            wanted = question_data["mips"]
            student_answer_binary = self.binary_from_mips(student_answer)
        else:
            # We just want the binary answer
            wanted = wanted_binary
            student_answer_binary = student_answer_binary.replace(" ","")
        score = 100.0 if wanted_binary.strip() == student_answer_binary.strip() else 0.0
        # store the result in the database
        self.put_submission(question_type, int(self.level), score, self.request.get('answer'))

        blob = json.dumps({"score":score, "wanted":wanted})
        self.response.out.write(blob)
        
    # The 'data' for a question should basically be:
    # mips - The MIPS instruction string
    # binary - The binary version of the MIPS instruction
    def data_for_question(self,question_type):
        if self.__my_random__ == None:
            self.__my_random__ = random.Random()
        self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))
        instruction = self.random_mips_instruction()
        binary = self.binary_from_mips(instruction)
        return {    "mips": instruction, 
                    "binary": binary,
                    # If the opcode is 0, then the instruction is an R type
                    "r_type": binary.startswith("000000")
                }
        
    def random_mips_instruction(self):
        """
        Generates a random valid MIPS string. It will be something along the 
        lines of
        
        'srl $a0, $s7, 2'
        'addi $t0, $t1, 10'
        
        etc...
        """
        instr = self.__my_random__.choice(self.valid_instructions.keys())
        data = []
        for datatype in self.valid_instructions[instr]:
            if datatype == 'r':   # Register
                component = self.__my_random__.choice(self.valid_registers)
            elif datatype == 'i': # Immediate (16 bits)
                component = str(self.__my_random__.randint(0, 255))
            elif datatype == 's': # Shift Amount (5 bits)
                component = str(self.__my_random__.randint(0,31))
            elif datatype == 'a': # Address (26 bits)
                component = str(self.__my_random__.randint(0,33554431))
            data.append(component)
        data_string = ", ".join(data)
        return "%s %s" % (instr,data_string)
    
    def binary_from_mips(self,instruction):
        # From messing in the python interpreter
        parser = mips.MIPSProgram()
        parser.HandleLine(instruction)
        binary = ""
        for byte in parser.Bytes():
            # bin(byte) takes an int and returns a string of the form
            # 0bxxxxx where the x's represent the binary version of the int.
            # I remove the 0b with the split call ([2:]), and then do a zfill
            # to add in any zeroes that bin might have left out
            binary += bin(byte)[2:].zfill(8)
        return binary