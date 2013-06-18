#!/usr/bin/env python
# encoding: utf-8
"""
shift_expression.py

Created by Scott on 2013-04-20.
Copyright (c) 2013 Scott Rice. All rights reserved.
"""

import sys
import os
import re

from cStringIO import StringIO
from tokenize import generate_tokens

def lex(string):
    STRING = 1
    return list(token[STRING] for token in generate_tokens(StringIO(string).readline))
    
class SEBits(object):
    def __init__(self,length):
        self.bits = []
        for i in range(length):
            self.bits.append("a"+str(31-i))
        
    def __repr__(self):
        bitstrings = []
        for i in range(0,len(self.bits)):
            bit = self.bits[i]
            bitstrings.append(str(bit))
        return "|".join(bitstrings)
    
    def mask_to_list(self,mask):
        """
        Takes an integer, turns it into binary
        13 => 0b1101
        Removes the first 2 characters
        0b1101 => 1101
        Zero fills till it is length 32
        1101 => 00000000000000000000000000001101
        And turns it into a list
        """
        return list(bin(mask)[2:].zfill(32))
        
    def bitwise_and(self,mask):
        ml = self.mask_to_list(mask)
        for i in range(32):
            # For a bitwise and, if ml[i] is 1, then the bit stays the same. If 
            # it is 0, then the bit gets set to 0
            mb = ml[i]
            if mb == "0":
                self.bits[i] = 0
        return self
        
    def bitwise_or(self,mask):
        ml = self.mask_to_list(mask)
        for i in range(32):
            # For a bitwise or, if ml[i] is 0, then the bit stays the same. If 
            # it is 1, then the bit gets set to 1
            mb = ml[i]
            if mb == "1":
                self.bits[i] = 1
        return self
        
    def shift_right(self,amount):
        """
        Shifts the bits by a given amount to the right. If bits is
            a31|a30|...|a1|a0
        and amount is 3, then the result is
            0|0|0|a31|a30|...|a4|a3
        """
        # If amount is 0, then this method screws up everything. Since 0 = -0,
        # doing self.bits[:-amount] will evaluate to "give me everything before
        # the 0th element", which gives us the empty list. Avoid this situation
        # entirely by just returning if they shift by 0
        if amount == 0:
            return self
        new_bits = self.bits[:-amount]
        for i in range(amount):
            new_bits.insert(0,0)
        self.bits = new_bits
        return self
        
    def shift_left(self,amount):
        """
        Shifts the bits by a given amount to the right. If bits is
            a31|a30|...|a1|a0
        and amount is 3, then the result is
            a28|a27|...|a1|a0|0|0|0
        """
        new_bits = self.bits[amount:]
        for i in range(amount):
            new_bits.append(0)
        self.bits = new_bits
        return self
        
class SEExpression(object):
    ops = ["<<",">>","&","|"]
    
    def __init__(self,left,value,right):
        self.left = left
        self.value = value
        self.right = right
    
    def __repr__(self):
        return "(%s %s %s)" % (self.left,self.value,self.right)
        
    def shift_right(self,lhs,rhs):
        # Dont check for if rhs is SEBits, cause that cant work. 3 >> a31|a30...
        # makes no sense...
        if isinstance(lhs,SEBits):
            return lhs.shift_right(rhs)
        return lhs >> rhs
        
    def shift_left(self,lhs,rhs):
        # Dont check for if rhs is SEBits, cause that cant work. 3 << a31|a30...
        # makes no sense...
        if isinstance(lhs,SEBits):
            return lhs.shift_left(rhs)
        return lhs << rhs    
    
    def bitwise_and(self,lhs,rhs):
        if isinstance(lhs,SEBits):
            return lhs.bitwise_and(rhs)
        if isinstance(rhs,SEBits):
            return rhs.bitwise_and(lhs)
        return lhs & rhs
        
    def bitwise_or(self,lhs,rhs):
        if isinstance(lhs,SEBits):
            return lhs.bitwise_or(rhs)
        if isinstance(rhs,SEBits):
            return rhs.bitwise_or(lhs)
        return lhs | rhs
        
    def evaluate(self,variable_mappings):
        lhs = self.left.evaluate(variable_mappings)
        rhs = self.right.evaluate(variable_mappings)
        if self.value == ">>":
            return self.shift_right(lhs,rhs)
        if self.value == "<<":
            return self.shift_left(lhs,rhs)
        if self.value == "&":
            return self.bitwise_and(lhs,rhs)
        if self.value == "|":
            return self.bitwise_or(lhs,rhs)
            
# All values are also expressions (for the purposes of typechecking and rules)
class SEValue(SEExpression):
    def __init__(self,value):
        self.value = value

    def __repr__(self):
        return str(self.value)
        
    def is_variable(self):
        """
        Checks to see whether our value is that of a variable
        
        A variable is defined as anything that isnt a constant. A constant is
        a numeric value (as in, consists of only 0-9), or a numeric value that
        is prefixed with 0x or 0b (which tells us the base)
        """
        # If it starts with 0x or 0b, it is a hex or binary constant
        if self.value.startswith("0x") or self.value.startswith("0b"):
            return False
        # Otherwise, if it contains any non-numeric characters, it is a variable
        return re.match(r"[^0-9]+",self.value) is not None
    
    def to_integer(self):
        """
        Converts our value string to a base 10 integer. Our value can be either
        a regular integer string, a hex string, or a binary string
        """
        if self.value.startswith("0x"):
            return int(self.value[2:],16)
        if self.value.startswith("0b"):
            return int(self.value[2:],2)
        return int(self.value)
        
    def evaluate(self,variable_mappings):
        if self.is_variable():
            return variable_mappings[self.value]
        else:
            return self.to_integer()
        
class SEParser(object):
    def is_value(self,token):
        # It is easier to check that it ISNT one of our operators than to check
        # that it IS a value, so lets do that
        ops = ["<<",">>","&","|","(",")"]
        return token not in ops
        
    def reduce(self):
        if len(self.stack) >= 3:
            vs = self.stack[-3:]
            # Check for rules
            reduced = None
            if vs[0] == "(" and vs[2] == ")":
                reduced = vs[1]
            if isinstance(vs[0],SEExpression) and vs[1] in SEExpression.ops and isinstance(vs[2],SEExpression):
                reduced = SEExpression(vs[0],vs[1],vs[2])
            # If we reduced the stack at all, remove the last 3 elements (the
            # ones we reduced), push our new value, and try again
            if reduced is not None:
                self.stack = self.stack[:-3]
                self.stack.append(reduced)
                self.reduce()
    
    def parse(self,tokens):
        self.stack = []
        for token in tokens:
            if token == "":
                continue
            if self.is_value(token):
                self.stack.append(SEValue(token))
            else:
                self.stack.append(token)
            self.reduce()
        # If there is anything left in the stack other than the start rule, 
        # parsing failed and we should return None
        if len(self.stack) == 1:
            return self.stack[0]
        else:
            return None

# Variable Rule:
# <Val> = [A-Za-z]
# Constants Rule: 
# (any constants with length > 8 for hex or > 32 for bin will be truncated)
# <Val> = 0x[0-9a-fA-F]+
# <Val> = 0b[01]+
# Shift Rule:
# <Expr> = <Expr> >> <Expr>
# <Expr> = <Expr> << <Expr>
# Mask Rule:
# <Expr> = <Expr> & <Expr>
# <Expr> = <Expr> | <Expr>
# Paren Rule:
# <Expr> = (<Expr>)
# Value Rule:
# <Expr> = <Val>
def generate_tree(string):
    tokens = lex(string)
    return SEParser().parse(tokens)
      
def parse_and_evaluate(string,variables):
    """
    Parses and Evaluates the string with the variable mapping 'variables'.
    Returns None if there are any errors.
    """
    try:
      tree = generate_tree(string)
      return tree.evaluate(variables)
    # KeyError is a variable was parsed that wasn't passed in the list
    except KeyError:
        return None
    # AttributeError is when parsing failed
    except AttributeError:
        return None
    # TypeError is when they put SEBits on the right hand side of a shift
    except TypeError:
        return None