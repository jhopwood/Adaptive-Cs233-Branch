# Craig Zilles  6/21/2012

import random
import string
import os
import copy
import logging

# code:
# 1 = remove the terminal
# 2 = remove both the terminal and its complement
# 3 = select a terminal whose complement is still in the pool
# 4 = select a terminal whose complement is still in the pool & remove term.
# 5 = select any terminal
# 6 = remove the complement of the terminal
# 7 = select a negated terminal

# family = [And, Or, Not]
# num_terminals = 2
equation_templates11 = [["5", "2+5", "25", "21+5"],      # level0
                       ["(1+4)(1+5)", "14+15"],          # level1
                       ["(25)'", "(2+5)'"]]              # level2
# num_terminals = 3
equation_templates12 = [["5", "2+5", "25", "1+25", "225"],         # level3
                       ["13+225", "2(1+45)", "2(2+5)", "2+2+5"]]   # level4

# family = 2, 3: [Nand], [Nand, Not]
# num_terminals = 2
equation_templates31 = [["5", "2^5", "(2^5)'"],          # level0
                       ["6^(2^5)", "(6^(2^5))'"],        # level1
                       ["6^(2^5)'", "(6^(2^5)')'"]]      # level2
# num_terminals = 3
equation_templates32 = [["2^(2^5)", "(2^(2^5))'"],       # level3
                       ["2^(2^5)'", "(2^(2^5)')'"]]      # level4

# family = 4, 5: [Nor], [Nor, Not]
# num_terminals = 2
equation_templates51 = [["7", "2/5", "(2/5)'"],          # level0
                       ["6/5", "(2/5)'"],                # level1
                       ["6/5", "(2/5)'"]]      # level2 theseneedhelp
                       # (6/(2/5)')' --> x + y' --> draws complicated solution
                       # x'/(y'/x')' --> xy --> VERY complicated solution especially family=4
# num_terminals = 3
equation_templates52 = [["2/(2/5)", "(2/(2/5))'"],       # level3
                       ["2/(2/5)'", "(2/(2/5)')'"]]      # level4

equation_templates = {0: [equation_templates11, equation_templates12], 
                      1: [equation_templates31, equation_templates32], 
                      2: [equation_templates51, equation_templates52]}

# this helper class keeps track of which terminals are still available
# complements of terminals are stored as capital letters.
# only supports terminal sets of up to 6 terminals

my_random = random.Random()
terminals1 = ["x", "X", "y", "Y", "z", "Z", "w", "W", "v", "V", "u", "U"]

class terminals:
    def __init__ (self, num_terminals):
        self.terminals = terminals1[:num_terminals*2]
        
    def get_random ( self ):
        return my_random.choice(self.terminals)

    def remove ( self, term ):
        if self.terminals.count(term) != 0:
            self.terminals.remove(term)

    def output ( self, term ):
        if term.isupper():
            return term.lower() + "'"
        return term

    def complement ( self, term ):
        if term.isupper():
            return term.lower()
        return term.upper()

    def get_random_has_complement ( self ):
        terms = copy.deepcopy(self.terminals)
        while terms:
            term = my_random.choice(terms)
            if terms.count(self.complement(term)) == 1:
                return term
            terms.remove(term)
        print "COULDN'T FIND A TERMINAL"
        return "g"

    def remove_complement ( self ):
        term = my_random.choice(self.terminals)
        if self.terminals.count(self.complement(term)) == 1:
            self.terminals.remove(self.complement(term))
        return term

    def select_complement ( self ):
    	terms = copy.deepcopy(self.terminals)
    	term =  my_random.choice(terms)
    	if term.isupper():
    		return term
    	return term.upper()
    

# populates an expression template with terminals

def get_expression(num_terminals, etemplates, random_seed):
    my_random.seed(random_seed)
    etemplate = my_random.choice(etemplates)
    output = ""
    terms = terminals(num_terminals)
    # print etemplate
    for c in etemplate:
        # print output
        if c == "1" or c == "2":
            term = terms.get_random()
            terms.remove(term)
            if c == "2":
                terms.remove(terms.complement(term))
            output += terms.output(term)
        elif c == "3" or c == "4":
            term = terms.get_random_has_complement()
            if c == "4":
                terms.remove(term)
            output += terms.output(term)
        elif c == '5':
            output += terms.output(terms.get_random())
        elif c == '6':
            term = terms.remove_complement()
            output += terms.output(term)
        elif c == '7':
        	output += terms.output(terms.select_complement())
        else:
            output += c

    return output