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

#####################
# Utility functions #
#####################

# rounds num up to size
def round_up(num, size):
    return (num + size - 1) // size * size

# converts hex string to int, or returns default on invalid value
def hex_to_int(string, default):
    try:
        return int(string, 16)
    except ValueError:
        return default


##############
# Type class #
##############

class Type(object):
    # size is the overall size of the type in bytes
    # alignment_size is the size needed for alignment
    def __init__(self, name, size, alignment_size):
        self.name = name
        self.size = size
        self.alignment_size = alignment_size
        self.is_compound_type = False
        self.is_array_type = False

    def align_to_size(self, num):
        return round_up(num, self.alignment_size)


###############
# Basic types #
###############

char_type = Type('char', 1, 1)
short_type = Type('short', 2, 2)
int_type = Type('int', 4, 4)
double_type = Type('double', 8, 8)
basic_types = [char_type, short_type, int_type, double_type]


##################
# Compound types #
##################

class Array(Type):
    # generates an array declaration
    # generator is an RNG to use for array type and dimensions
    # name is a name for the array
    # num_dimensions is the number of dimensions
    # start_address is the starting address
    # types is an array of valid types for the array
    def __init__(self, generator, name, num_dimensions, start_address, types):
        from operator import mul

        self.name = name
        self.num_dimensions = num_dimensions
        self.element_type = generator.choice(types)
        self.element_size = self.element_type.size 
        self.alignment_size = self.element_type.alignment_size
        self.is_compound_type = False
        self.is_array_type = True
        self.code = '{} {}'.format(self.element_type.name, name)
        self.dimension_sizes = []
        self.start_address = start_address

        for i in xrange(num_dimensions):
            dimension_size = generator.randrange(4, 10) * 16
            self.code += '[{}]'.format(dimension_size)
            self.dimension_sizes.append(dimension_size)

        self.code += '; // starts at address 0x{:x}\n'.format(start_address)

        # only correct for 1D arrays, but only used for those too
        self.ptr_code = '{0} *{1} = ({0} *) 0x{2:x};\n'.format(
                self.element_type.name, name, start_address)

        self.size = reduce(mul, self.dimension_sizes, self.element_size)
        # this is used for calculating offsets
        self._dimension_multipliers = [1] * num_dimensions
        for i in xrange(num_dimensions - 2, -1, -1):
            self._dimension_multipliers[i] = \
                    self._dimension_multipliers[i + 1] * \
                    self.dimension_sizes[i + 1]

    # returns the offset of an index into the array, passed as a tuple
    def offset(self, index):
        offsets = [self._dimension_multipliers[i] * index[i]
                for i in xrange(self.num_dimensions)]
        return sum(offsets) * self.element_size

    # returns the address of an index into the array, passed as a tuple
    def address(self, index):
        return self.start_address + self.offset(index)


class Struct(Type):
    # generates code for a C struct
    # generator is an RNG to use for element types
    # name is a name for the struct
    # num_elements is the number of elements to put
    # types is an array of valid types for elements
    # elements are named a, b, c, etc.
    def __init__(self, generator, name, num_elements, types):
        self.generator = generator
        self.name = name
        self.num_elements = num_elements
        self.is_compound_type = True
        self.is_array_type = False
        self.code = 'typedef struct {\n'
        self.offsets = {}
        self.alignment_size = 0 # needed for struct padding
        cur_offset = 0

        for i in xrange(num_elements):
            element_name = chr(ord('a') + i)
            # TODO: support arrays as struct elements
            element_type = generator.choice(types)
            if element_type.alignment_size > self.alignment_size:
                self.alignment_size = element_type.alignment_size
            # make sure elements are properly aligned
            cur_offset = element_type.align_to_size(cur_offset)
            self.code += '    {} {};\n'.format(element_type.name, element_name)
            self.offsets[element_name] = cur_offset
            cur_offset += element_type.size

        # insert padding at end if needed
        self.size = round_up(cur_offset, self.alignment_size)
        self.code += '}} {};\n'.format(name)

    # returns a random field name from the struct
    def random_field(self):
        return self.generator.choice(self.offsets.keys())


###########################
# Code generation classes #
###########################

# generates a loop template
# num_loops is the number of nested loops
# the returned template has placeholders for each loop's initialization,
# termination condition and increment, as well as the innermost loop body
# the client code is responsible for properly indenting the body
# returns the generated template
def generate_loops(num_loops):
    loop_str = ''
    for i in xrange(num_loops):
        indent_str = '    ' * i
        loop_var = chr(ord('i') + i)
        loop_str += '{0}for (int {1} = {{}}; {1} {{}}; {1}{{}}) {{{{\n'.format(
                indent_str, loop_var)
    loop_str += '{}'
    for i in xrange(num_loops - 1, -1, -1):
        indent_str = '    ' * i
        loop_str += indent_str + '}}\n'
    return loop_str


# used in code
operators = ['+', '-', '*', '/']


class ArrayLoop(object):
    # generates code for a loop or loops over an array of arbitrary dimension
    # generator is an RNG to use in generation
    # arrays are the arrays to use:
    # - the maximum dimensions of any array is the number of nested loops
    # - first array is used as destination
    # - others arrays used as sources in given order
    # use_complex_loops enables random starting positions and non-unit strides
    # use_compound_operators enables +=, etc.
    # this does NOT generate the code for any array or type definitions
    def __init__(self, generator, arrays,
            use_compound_operators, use_complex_loops):
        max_array = max(arrays, key = lambda array: array.num_dimensions)
        self._num_dimensions = max_array.num_dimensions

        # this is a list of (start, end, step) triples
        self._loop_data = []
        for i in xrange(self._num_dimensions):
            if use_complex_loops:
                start = generator.randrange(8)
                step = generator.randrange(1, 5)
            else:
                start = 0
                step = 1
            end = start + 48
            # reverse loops 50% of the time
            if use_complex_loops and generator.randrange(2):
                start, end = end, start
                step *= -1
            self._loop_data.append((start, end, step))

        loop_template = generate_loops(self._num_dimensions)
        indent_str = '    ' * self._num_dimensions
        dest_access = self._generate_access(generator, arrays[0])
        loop_body = indent_str + dest_access[0] + ' '
        if use_compound_operators:
            loop_body += generator.choice(operators)
        loop_body += '= '

        # this is a list of (array, field) tuples
        self._accesses = []
        if use_compound_operators:
            self._accesses.append(dest_access[1])
        loop_body += str(generator.randrange(2, 9))
        for i in xrange(1, len(arrays)):
            access = self._generate_access(generator, arrays[i])
            operator = generator.choice(operators)
            loop_body += ' {} {}'.format(operator, access[0])
            self._accesses.append(access[1])

        # ensure the write appears at the end
        loop_body += ';\n'
        self._accesses.append(dest_access[1])

        params = []
        for i in xrange(self._num_dimensions):
            loop_data = self._loop_data[i]
            params.append(loop_data[0])
            if loop_data[2] > 0:
                params.append('< ' + str(loop_data[1]))
                if loop_data[2] == 1:
                    params.append('++')
                else:
                    params.append(' += ' + str(loop_data[2]))
            else:
                params.append('> ' + str(loop_data[1]))
                if loop_data[2] == -1:
                    params.append('--')
                else:
                    params.append(' -= ' + str(-loop_data[2]))
        params.append(loop_body)
        self.code = loop_template.format(*params)

    # gets the access pattern for the loop
    # the arrays used should have been given start addresses beforehand
    # num_accesses is the number of accesses to get
    def get_accesses(self, num_accesses):
        accesses = []
        indices = [x[0] for x in self._loop_data]
        for i in xrange(0, num_accesses, len(self._accesses)):
            # FIXME: can go over the bounds of the outer loop
            for access in self._accesses:
                order = [indices[x] for x in access[1]]
                address = access[0].address(order)
                element_type = access[0].element_type
                if element_type.is_compound_type:
                    address += element_type.offsets[access[2]]
                accesses.append(address)
            # FIXME: does not do bounds checking of loop
            for j in xrange(len(indices) - 1, -1, -1):
                indices[j] += self._loop_data[j][2]
                if self._loop_data[j][2] > 0:
                    out_of_bounds = indices[j] >= self._loop_data[j][1]
                else:
                    out_of_bounds = indices[j] <= self._loop_data[j][1]
                if out_of_bounds:
                    indices[j] = self._loop_data[j][0]
                    # continue onto next iteration to increment outer index
                else:
                    break # no further increments needed

        return accesses

    # generates an access to an array
    # returns an access string, access info pair
    # access info is triple of array, index order and field (if applicable)
    def _generate_access(self, generator, array):
        access_str = array.name
        index_order = range(array.num_dimensions)
        generator.shuffle(index_order)
        for i in index_order:
            access_str += '[{}]'.format(chr(ord('i') + i))
        element_type = array.element_type
        if element_type.is_compound_type:
            field = element_type.random_field()
            access_str += '.' + field
        else:
            field = None
        access_info = (array, index_order, field)
        return (access_str, access_info)


##########################
# web homework functions #
##########################

# generates data for a question
# generator is an RNG to use in generation
# level is a bitmask determining question characteristics:
# - bit 0 is 1 if non-unit strides and non-zero starts are allowed
# - bits 1-2 are 00 for one array
#                01 for one array with compound operators
#                10 for two arrays
#                11 for three arrays
# - bits 3-4 are 00 for 1D array of normal type
#                01 for pointer to normal type
#                10 for 2D array of normal type
#                11 for 1D array of structs
def data_for_question(generator, level):
    num_bits = level >> 1 & 3
    num_arrays = num_bits + int(num_bits == 0)
    use_compound_operators = num_bits == 1
    use_complex_loops = bool(level & 1)
    loop_type = level >> 3
    num_dimensions = int(loop_type == 2) + 1

    name_prefixes = ['foo', 'bar', 'baz']

    if loop_type != 3:
        types = [basic_types] * num_arrays
    else:
        types = []
        for i in xrange(num_arrays):
            struct = Struct(generator, name_prefixes[i] + '_t',
                    generator.randrange(3, 5), basic_types)
            types.append([struct])

    suffix = '_ptr' if loop_type == 1 else '_arr'
    arrays = []
    start_address = 0x10010000
    for i in xrange(num_arrays):
        name = name_prefixes[i] + suffix
        array = Array(generator, name, num_dimensions, start_address, types[i])
        arrays.append(array)
        start_address += 0x10000
    loop = ArrayLoop(generator, arrays,
            use_compound_operators, use_complex_loops)

    code = ''
    if loop_type == 3:
        for i in xrange(num_arrays):
            code += types[i][0].code + '\n'
    for i in xrange(num_arrays):
        if loop_type != 1:
            code += arrays[i].code
        else:
            code += arrays[i].ptr_code
    code += '\n' + loop.code.rstrip() # remove trailing newline

    num_accesses = 9 if num_arrays == 3 else 8
    return { 'code': code, 'loop': loop, 'num_accesses': num_accesses }


# scores a student answer
# question_data is the data for the question
# student_answer is a list of answers input by the student
def score_student_answer(question_data, student_answer):
    import json

    num_accesses = question_data['num_accesses']
    # 0 should never be a valid address
    student_sequence = [hex_to_int(x, 0) for x in json.loads(student_answer)]
    correct_sequence = question_data['loop'].get_accesses(num_accesses)
    score = round(sum([int(student_sequence[i] == correct_sequence[i])
                 for i in xrange(num_accesses)]) * 100.0 / num_accesses, 1)
    return (score, json.dumps(correct_sequence))
