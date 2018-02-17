#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity v0.3 block.py

__author__ = 'nosoyyo'

import time
import pickle

import utils
from .control import *
from .command import stash

# debug
settings = {}
settings['debug'] = True

class Block():

	'''blox use str(octal nums) as block_id
	   srsly starts from 0o447250
	'''
	def __init__(self, _id):
		self._id = utils.parse(_id)[0]
		self.status = 'active'
		# for compatible to older versions. 'block_id' is deprecated since v0.3
		self.block_id = self._id
		self.boc = int(time.time())
		self.tasks = []
		self.eoc = None
		self.notes = []

	def updateInDB(self):
		'''
		write current block into bloxCol.blocks
		'''
		updateInDB(self)
		return True

	def close(self):
		'''
		change self status and call updateInDB()
		'''
		self.eoc = int(time.time())
		self.status = 'closed'
		return True

	def storeInstance(self):
		'''
			store this instance into bloxCol
		'''
		storeInstanceInDB(self)
		return True

	def sync(self):
		'''
			call self.updateInDB(), then call self.storeInstance()
		'''
		self.updateInDB()
		self.storeInstance()
		return True

	def addTask(self, task):
		self.tasks.append(pickle.dumps(task))
		self.sync()
		return True

	def stash(self, debug=settings['debug']):
		'''
			only call block.instance.stash() when attempting to close a block
			for other conditions, just call stash()
		'''
		if debug:
			print('some debug msg from classmethod Block.stash')
			pass

		if getTask('b'):
			for task in getTask('b'):
				stash(task)
			# no need to sync here because stash() will call sync()
	

# commands
def boc():

	if not getBlock('active'):
		
		thisId = genNewBlockId()
		b = Block(thisId)
		b.sync()

	else:
		utils.stats()

def eoc(arg=None, debug=settings['debug']):
	
	def operationBundle(instance):
		instance.stash()
		instance.close()
		instance.sync()
		return

	# close the active block by default
	if arg in [None,'active']:
		if getBlock('active'):
			b = getBlock('active')
		else:
			b = getBlock('last')
	else:
		b = getBlock(arg)

	# end it
	operationBundle(b)