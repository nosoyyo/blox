#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity
# 0.0.4

__author__ = 'nosoyyo'

import time
import datetime
import shelve as s
from transitions import Machine

import ezcf
from . import local_conf
from .. utils import parse

class bloxDB():
	
	def __init__(self, arg=None):
		'''
			the main interface for db and indexing operations.

						       WARNING:
						     ONLY DO THIS 
				WHEN YOU ARE 100% SURE WHAT YOU ARE DOING
				  AND ARE 100% SURE WHAT'S GONNA HAPPEN
						    ---------------
						    bloxDB('reset')
						    ---------------
				DANGEROUS! NO CONFIRMATION WILL BE PROMPTED.
						ALL YOUR DATA WILL BE LOST
						  EVEN THOSE WERE SAVED

		'''
		if arg in [None]:
			self.db = s.open(local_conf.BloxDBName, flag='c', writeback=True)
			self.index = s.open(local_conf.BloxIndexName, flag='c', writeback=True)
		
		elif arg in ['reset']:
			self.db = s.open(local_conf.BloxDBName, flag='n', writeback=True)

			b = Block('0o100000')
			b.tasks, b.state = ['0o100001'], 'empty'
			self.storeInstance(b)

			t = Task('0o100001', 'A sample task.')
			t.notes = ['A sample note.']
			self.storeInstance(t)

			self.index = s.open(local_conf.BloxIndexName, flag='n', writeback=True)
			self.updateIndex(b)
			self.updateIndex(t)

	def ls(self):
		'''
			just use it like 'ls'.
		'''
		ls = [value for value in self.index.values()]
		return ls

	def storeInstance(self, obj):
		'''
			update block or task instance into db.
		'''
		self.db[obj._id] = obj
		self.db.sync()
		return True

	def updateIndex(self, obj):
		'''
			write the properties of a block or task into bloxDB.index
			'upsert=True' by default.
		'''
		try:
			if obj._id.endswith('0'):
				try:
					self.index[obj._id] = {
											'_id' : obj._id,
											'block_id' : obj._id, 
											'boc' : obj.boc, 
											'eoc' : obj.eoc,
											'state' : obj.state,
											'tasks' : obj.tasks,
											'notes' : obj.notes,
											}
					return True
				except Exception as e:
					print('exception from 9169')
					print(e)
			else:
				try:
					self.index[obj._id] = {
											'_id' : obj._id,
											'task_id' : obj._id,
											'title' : obj.title,
											'started_at' : obj.started_at, 
											'end' : obj.end,
											'parent' : obj.parent,
											'state' : obj.state,
											'focus' : obj.focus,
											'notes' : obj.notes,
											'nows' : obj.nows,
											'context' : obj.context,
											}
					return True
				except Exception as e:
					print('exception from 7134')
					print(e)
		finally:
			self.index.sync()

	# selectors
	def getInstance(self, _id):
		instance = self.db[_id]
		return instance

	def getBlock(self, arg=None):
		'''
			# get latest block by default, no matter the block is active or not
			# getBlock('active') returns 
			# getBlock by id returns the block itself
			# v0.3 update: getBlock() now returns block instance when possible
			# 0.0.4: shorten codes
		'''
		def getKeyList(self):
			kl = [key for key in self.index.keys() if key.endswith('0')]
			return kl

		def getLatestBlock(self):
			kl = getKeyList()
			kl.sort()
			_id = kl[-1]
			instance = self.getInstance(_id)
			return instance

		if arg in [None,'latest','last']:
			instance = self.getLatestBlock()
			return instance

		elif arg in ['active', 'Active']:
			instance = self.getLatestBlock()
			if instance.state == 'active':
				return instance
			else:
				print('no active block')

		elif arg in ['All','all']:
			kl = self.getBlockIdList()
			return kl

		# accepts decimal id here
		elif parse(arg)[0].endswith('0'):
			instance = self.getInstance(parse(arg)[0])
			return instance

class Block():

	'''blox use str(octal nums) as block_id
	   srsly starts from 0o447250
	'''
	def __init__(self, _id):
		self._id = parse(_id)[0]
		# for compatible to older versions. 'block_id' is deprecated since v0.3
		self.block_id = self._id
		self.boc = int(time.time())
		self.tasks = []
		self.eoc = None
		self.notes = []

		self.states = ['empty', 'active', 'closed']
		self.machine = Machine(model=self, states=self.states, initial='empty')

	def updateIndex(self):
		'''
		write current block into bloxCol.blocks
		'''
		updateIndex(self)
		return True

	def close(self):
		'''
		change self state and call updateInDB()
		'''
		self.eoc = int(time.time())
		self.state = 'closed'
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

	def stash(self):
		'''
			only call block.instance.stash() when attempting to close a block
			for other conditions, just call stash()
		'''
		pass

class Task(Block):

	'''
		task_id is also str(octal nums), it follows block_id in an octal pattern.
	    srsly starts from 0o447256
	'''
	def __init__(self, _id, title):
		self._id = parse(_id)[0]
		self.parent = ''
		self.title = title

		# for compatible to older versions. 'task_id' is deprecated since v0.3
		self.task_id = self._id
		self.started_at = int(time.time())
		self.context = None
		self.state = 'active'
		self.focus = None
		self.notes = []
		self.nows = 0
		self.end = None

	def close(self, state):
		'''
			change self state and call updateInDB()
		'''
		self.end = int(time.time())
		self.focus = False
		self.state = state
		return True

	def regInParent(self):
		'''
			update self in parent block.tasks
		'''
		b = getBlock(self.parent)
		if self not in b.tasks:
			b.addTask(self)
		elif self._id in [task._id for task in getTask(b).tasks]:
			# pseudocode here
			#b.removeTask(self)
			#b.addTask(self)
			return
		else:
			print('some error msg from regInParent()')

		return True