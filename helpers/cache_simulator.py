#!/usr/bin/env python
#
# Copyright 2013 University of Illinois
#

import math

class CacheStats(object):
  
  def __init__(self):
    self.accesses = 0
    self.hits = 0
    
  def access(self):
    self.accesses += 1

class CacheBlock(object):
  
  def __init__(self):
    self.valid = False
    self.last_access_time = 0
    # Initialize it to SOMETHING
    self.tag = 0

class CacheSimulator(object):
  
  def __init__(self, size, nways, block_size):
    """
    Initialize the cache by allocating space for all of the cache blocks and
    initializing them to be invalid and with 0 last access times.
    """
    num_blocks = size/block_size
    
    self.index_bits = int(math.log(num_blocks/nways,2))
    self.boff_bits = int(math.log(block_size,2))
    self.tag_bits = 32 - (self.index_bits + self.boff_bits)
    
    # Copy over parameters
    self.size = size
    self.num_blocks = num_blocks
    self.nways = nways
    self.block_size = block_size
    
    # Initialize counters and statistics
    self.LRU_counter = 1
    
    # Bitmasks for tag and index
    self.tag_mask = (1 << self.tag_bits) - 1
    self.index_mask = (1 << self.index_bits) - 1
    
    self.blocks = []
    
    # Initialize each cache block to be invalid
    for i in range(num_blocks):
      self.blocks.append(CacheBlock())
      
    # TODO: Possibly add stats?
      
  def get_block(self,index,way):
    """
    This function returns the cache block which is the "way"th entry in the 
    "index"th set
    """  
    # TODO: Assert way < self.nways
    num_sets = self.num_blocks / self.nways
    # TODO: Assert index < num_sets
    i = (index * self.nways) + way
    return self.blocks[i]
    
  def extract_tag(self,address):
    """
    Given an address, extract the tag field
    """
    return (address >> (self.boff_bits + self.index_bits)) & self.tag_mask
    
  def extract_index(self,address):
    """
    Given an address, extract the index field
    """
    return (address >> self.boff_bits) & self.index_mask
    
  def find_block_and_update_lru(self,address,stats=None):
    """
    Given an address, look up in cache to see if that address hits. If it does,
    update the last access time
    """
    tag = self.extract_tag(address)
    index = self.extract_index(address)
    
    # stats.access()
    
    for way in range(self.nways):
      block = self.get_block(index,way)
      if block.tag == tag and block.valid:
        # stats.hit()
        self.LRU_counter += 1
        block.last_access_time = self.LRU_counter
        return True
        
    return False
    
  def fill_cache_with_block(self,address):
    """
    This function should find the LRU block and replace it with one that
    contains "address"
    """
    index = self.extract_index(address)
    lru_block = self.get_block(index,0)
    
    # We technically don't need to check the validity of the blocks we look at,
    # because all invalid blocks will have a last_access_time of 0, but I've
    # added the code to do the check, just for completeness
    if lru_block.valid:
      for way in range(self.nways):
        block = self.get_block(index,way)
        if not block.valid:
          lru_block = block
          break
        if block.last_access_time < lru_block.last_access_time:
          lru_block = block
    
    self.LRU_counter += 1
    lru_block.last_access_time = self.LRU_counter
    lru_block.valid = True
    lru_block.tag = self.extract_tag(address)