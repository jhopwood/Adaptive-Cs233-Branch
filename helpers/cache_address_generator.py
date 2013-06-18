#!/usr/bin/env python
#
# Copyright 2013 University of Illinois
#

import logging

ADDRESS_SIZE_32 = 0xffffffff

class AddressGenerator(object):
  def __init__(self,generator,description):
    self.generator = generator
    self.description = description
    
  def _to_int(self,address):
    """
    Converts a hex string into an integer
    """
    length = len(address) - 1
    return int(address[:length],16)
    
  def _to_str(self,iaddress):
    """
    Converts an integer into a hex string
    """
    return hex(iaddress)[2:]
  
  def _same_block_mask(self):
    """
    Returns a mask which, when anded with an address, will remove the block 
    offset portion of the address
    """
    return (ADDRESS_SIZE_32 << self.description["offset"]["bits"]) & ADDRESS_SIZE_32
    
  def _same_set_mask(self):
    """
    Returns a mask which, when anded with an address, will remove the index 
    portion of the address
    """
    shift_bits = self.description["index"]["bits"] + self.description["offset"]["bits"]
    tag_as_1s = (ADDRESS_SIZE_32 << shift_bits) & ADDRESS_SIZE_32
    offset_mask = (1 << self.description["offset"]["bits"]) - 1
    opposite_mask = tag_as_1s | offset_mask
    # This is what I needed to do to get Python to do a 32bit bitwise not.
    # I guess I understand that they don't use a constant number of bits to store
    # their integers, but it would be nice if they had a function where I could
    # input the size to not...
    return ~(opposite_mask) & ADDRESS_SIZE_32
    
  def _merge_addresses(self,large,small,mask):
    """
    Replaces the portion of 'large' defined by 'mask' by the equivalent section
    of 'small'
    """
    ilarge = self._to_int(large)
    ismall = self._to_int(small)
    opposite_mask = ~(mask) & ADDRESS_SIZE_32
    # Remove the masked section from 'large'
    priscilla = ilarge & opposite_mask
    # Takes only the masked section from 'small'
    beatrice = ismall & mask
    # Combines the two
    iresult = priscilla | beatrice # A hard choice!
    return self._to_str(iresult)
  
  def generate_same_block(self,address):
    """
    Generates an address which is in the same block as 'address'
    """
    r = self.generate_random_address()
    return self._merge_addresses(r,address,self._same_block_mask())
    
  def generate_adjacent_block(self,address):
    """
    Generates an address which is in an adjacent block to 'address'
    """
    iaddress = self._to_int(address)
    bo_bits = self.description["offset"]["bits"]
    index = iaddress & self._same_set_mask() >> bo_bits
    indexpp = index + 1
    indexpp_mask = indexpp << bo_bits
    return self._merge_addresses(address,self._to_str(indexpp_mask),self._same_set_mask())
  
  def generate_same_set(self,address):
    """
    Generates an address which is in the same set as 'address'
    """
    r = self.generate_random_address()
    return self._merge_addresses(r,address,self._same_set_mask())
    
  def generate_random_address(self):
    """
    Generates a random address
    """
    return self._to_str(self.generator.randint(0,(2**32)-1))
