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

from base_handler import BaseHandler

class RegisterFile(BaseHandler):
    # should this be moved up to BaseHandler?
    # also IDK if this is intentional or not, but these are "static" variables
    # see http://stackoverflow.com/a/69067
    __my_random__ = None

    valid_types = ['d2o']

    half_period = 5;
    period = 10; # can't figure out how to reference half_period here :(
    max_time = 80 # should be kept synced with timing_diagram.js


    def get(self, question_type):
        self.get_basics(2)
        # If the user wants a random question, replace question_type with
        # a random valid question type
        if question_type == 'random':
            question_type = random.choice(self.valid_types)
            if self.request.get('l', None) == None:
                self.level = random.randrange(3)

        # If the question type is valid, check to see if it is a grade request
        # (aka type=json), otherwise generate a new problem     
        if self.is_valid_type(question_type):
            if self.request.get('type') == 'json':
                return self.get_grades(question_type)
            question_data = json.dumps(self.data_for_question(question_type))
            submit_data = {'question_type': question_type, 'magic': self.magic,
                    'level': self.level, 'problem_id': self.problem_id}
            data = {'submit': submit_data, 'question': question_data}
            self.add_best_score(data, question_type)
            self.render('register_file.html', **data)
        else:
            self.response.out.write('Invalid URL')


    def post(self, question_type):
        if not self.is_valid_type(question_type):
            return self.response.out.write('Invalid URL')
        self.get_basics(2)
        student_answer = self.request.get('answer')
        question_data = self.data_for_question(question_type)

        register_values = self.get_register_values(question_data['signals'])
        time = question_data['labeled_markers'][0]
        readnum_signal = 5 + question_data['readdata_num'] # FIXME: hardcoding 5 is ugly
        register_number = self.get_value_at_time(question_data['signals'][readnum_signal]['values'], time)
        correct_answer = self.get_register_value(register_values, register_number, time)

        score = 100.0 if str(correct_answer) == student_answer.strip() else 0.0
        # store the result in the database
        self.put_submission(question_type, int(self.level), score, student_answer)

        blob = json.dumps({'score': score, 'wanted': correct_answer})
        self.response.out.write(blob)


    def data_for_question(self, question_type):
        # only handling d2o for now
        if self.__my_random__ == None:
            self.__my_random__ = random.Random()
        self.__my_random__.seed(self.generate_index(self.magic, self.level, self.problem_id, question_type))

        writenum_signal, writenum_times = self.generate_writenum()
        clock_signal, unlabeled_markers = self.generate_clock()

        signals = [
                   clock_signal,
                   self.generate_reset(),
                   self.generate_writeenable(),
                   writenum_signal,
                   self.generate_writedata(),
                   self.generate_readnum('readnum1', writenum_times),
                   self.generate_readnum('readnum2', writenum_times),
                  ]
        labeled_markers = self.generate_markers()
        unlabeled_markers = [t for t in unlabeled_markers if t not in labeled_markers]
        readdata_num = self.__my_random__.randrange(2);
        return {
                'signals': signals,
                'labeled_markers': labeled_markers,
                'unlabeled_markers': unlabeled_markers,
                'readdata_num': readdata_num
               }


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


    def generate_reset(self):
        # pretty boring right now but could be spiced up
        values = [{'time': 0, 'value': 1}, {'time': 3, 'value': 0}]
        return {'name': 'reset', 'binary': True, 'values': values}


    def generate_writeenable(self):
        # there should be some randomization here
        values = [{'time': 0, 'value': 0}, {'time': 3, 'value': 1}]
        return {'name': 'writeenable', 'binary': True, 'values': values}


    def generate_writenum(self):
        value_function = lambda _: xrange(31)
        writenum_values = self.generate_signal_values(value_function, True)
        writenum_regs = []
        writenum_times = []

        for i in xrange(len(writenum_values)):
            writenum_regs.append(writenum_values[i]['value'])
            time = {'time': writenum_values[i]['time'], 'value': writenum_regs[:]}
            writenum_times.append(time)

        writenum_signal = {'name': 'writenum', 'binary': False, 'values': writenum_values}
        return (writenum_signal, writenum_times)


    def generate_readnum(self, name, writenum_times):
        value_function = lambda time: self.get_value_at_time(writenum_times, time)
        values = self.generate_signal_values(value_function, False)
        return {'name': name, 'binary': False, 'values': values}


    def generate_writedata(self):
        value_function = lambda _: xrange(100, 1000)
        values = self.generate_signal_values(value_function, True)
        return {'name': 'writedata', 'binary': False, 'values': values}


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


    # should also be hoisted up
    def is_valid_type(self, question_type):
      return question_type in self.valid_types
