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
import ast

from base_handler import BaseHandler

class FlipFlop(BaseHandler):
    __my_random__ = None
    valid_types = ['d2o']
    half_period = 5
    period = 10
    max_time = 80

    def maximum_level(self, question_type):
        return 0

    def data_for_question(self, question_type):
        # only handling d2o for now
        if self.__my_random__ == None:
            self.__my_random__ = random.Random()
        self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))

        clock_signal, unlabeled_markers = self.generate_clock()
        D = self.generate_D()

        signals = [
                   clock_signal,
                   D,
                   self.generate_Q(),
                   self.generate_Q_sol(D['values'])
                  ]
        answer = self.generate_Q_sol(D['values'])
        labeled_markers = [] # self.generate_markers()
        unlabeled_markers = [t for t in unlabeled_markers if t not in labeled_markers]
        readdata_num = self.__my_random__.randrange(2);
        return json.dumps({
                'signals': signals,
                'labeled_markers': labeled_markers,
                'unlabeled_markers': unlabeled_markers,
                'readdata_num': readdata_num
               })

    def generate_clock(self):
        unlabeled_markers = []
        values = []
        value = 0
        for time in xrange(0, self.max_time, self.half_period):
            if value == 1:
                unlabeled_markers.append(time)
            values.append({'time': time, 'value': value})
            value ^= 1
        signal = {'name': 'clock', 'binary': True, 'values': values}
        return (signal, unlabeled_markers)

    def generate_D(self):
        values = []
        value = 0
        values.append({'time': 0, 'value': 0})
        for i in range(4):
            time = self.generator.randint(i*(self.max_time/4),(i+1)*(self.max_time/4))
            values.append({'time': time, 'value': value})
            value ^= 1
        signal = {'name': 'D', 'binary': True, 'values': values}
        return signal

    def generate_Q(self):
        values = []
        value = 0
        values.append({'time': 0, 'value': 0})
        for time in xrange(5, self.max_time, self.period):
            values.append({'time': time, 'value': 0})
        return {'name': 'Q', 'binary': True, 'values': values}

    def generate_Q_sol(self, d_values):
        values = []
        value = 0
        values.append({'time': 0, 'value': 0})
        for time in xrange(5, self.max_time, self.period):
            d_value = self.get_value_at_time(d_values, time)
            values.append({'time': time, 'value': d_value})
        return {'name': 'Q_sol', 'binary': True, 'values': values}

    # values_function(t) returns all valid values at t
    # synchronized being True means value will not change on +ve clock edge
    def generate_signal_values(self, values_function, synchronized):
        min_separation = 10 # between signal changes
        max_separation = 25 # as above

        time = 0
        values = []
        last_value = -1; # FIXME: what if -1 is actual first value?

        while time < self.max_time - min_separation:
            if (synchronized and self.is_positive_edge(time)):
                time -= 1 # shift before +ve edge
            value_choices = values_function(time)
            while True:
                value = self.__my_random__.choice(value_choices)
                if value != last_value:
                    values.append({'time': time, 'value': value})
                    last_value = value
                    break
                elif len(value_choices) == 1:
                    break   # prevent infinite loops
            time += self.__my_random__.randrange(min_separation, max_separation)

        return values

    def generate_markers(self):
        time = self.__my_random__.randrange(40, self.max_time)
        return [time]

    def get_value_at_time(self, values, time):
        for i in xrange(len(values) - 1, -1, -1):
            if time >= values[i]['time']:
                return values[i]['value']

    def get_register_values(self, signals):
        num_registers = 31; # ignoring 0 register
        register_values = [[] for i in xrange(num_registers)]

        # TODO: major ugliness - these should not be hardcoded
        reset_values = signals[1]['values']
        writeenable_values = signals[2]['values']
        writenum_values = signals[3]['values']
        writedata_values = signals[4]['values']

        for time in xrange(self.half_period, self.max_time, self.period):
            if self.get_value_at_time(reset_values, time) == 0 and \
                    self.get_value_at_time(writeenable_values, time) == 1:
                regnum = self.get_value_at_time(writenum_values, time)
                if regnum != 0:
                    regdata = self.get_value_at_time(writedata_values, time)
                    time_value = {"time": time, "value": regdata}
                    register_values[regnum - 1].append(time_value)

        for i in xrange(len(reset_values)):
            if reset_values[i]['value'] == 1:
                for regnum in xrange(num_registers):
                    time_value = {"time": reset_values[i]['time'], "value": 0}
                    register_values[regnum].append(time_value)

        for regnum in xrange(num_registers):
            register_values[regnum].sort(key = lambda time_value: time_value['time'])

        return register_values

    def get_register_value(self, register_values, register_number, time):
        if register_number == 0:
            return 0
        else:
            return self.get_value_at_time(register_values[register_number - 1], time)

    def is_positive_edge(self, time):
        return time % self.period == self.half_period

    def score_student_answer(self,question_type,question_data,student_answer):
        student_answer = ast.literal_eval(student_answer)
        question_data = json.loads(question_data)
        answer = question_data['signals'][3]['values']
        score = 0
        for i in range(len(answer)):
            if (answer[i]['value'] == student_answer[i]['value']):
                score += 100.0 / len(answer)
        score = round(score,2) 
        return (score, "placeholder")
