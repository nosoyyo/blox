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
			self.__enter__()
			self.__exit__()

		elif arg in ['reset']:
			self.db = s.open(local_conf.BloxDBName, flag='n', writeback=True)

			# create 2 blocks, one closed and one active
			b1 = Block('0o100000')
			b1.state = 'closed'
			b2 = Block('0o100010')
			b2.state = 'active'
			self.storeInstance(b1, b2)

			# create sample tasks with different states
			t1 = Task('0o100001', 'A sample task in a closed block.')
			t1.notes = []
			t1.state = 'finished'

			t2 = Task('0o100002', 'Another sample task in a closed block but not finished.')
			t2.notes = [\
						'Only put off', 
						'until tomorrow what you are', 
						'willing to die having left undone.', 
						'Pablo', 
						'Picasso',
						]
			t2.state = 'stashed'
			# update t1 and t2 into their parent block b1
			b1.updateTask(t1, t2)

			# go on creating sample tasks
			t3 = Task('0o100011', 'Start to use blox. [currently active and focusing]')
			t3.state = 'active'
			t3.focus = True

			t4 = Task('0o100012', 'Waiting to be focused on. [currently active but not focusing]')
			t4.state = 'active'
			t4.focus = False
			# update t3 and t4 into their parent block b2
			b2.updateTask(t3, t4)
			
			self.storeInstance(t1, t2, t3, t4)

			self.index = s.open(local_conf.BloxIndexName, flag='n', writeback=True)
			self.updateIndex(b1, b2)
			self.updateIndex(t1, t2, t3, t4)

	def __enter__(self):
		self.db = s.open(local_conf.BloxDBName, flag='c', writeback=True)
		self.index = s.open(local_conf.BloxIndexName, flag='c', writeback=True)
		return self

	def __exit__(self):
		self.sync()
		self.db.close()
		self.index.close()

	def ls(self):
		'''
			just use it like 'ls'.
		'''
		ls = [value for value in self.index.values()]
		return ls

	def storeInstance(self, *objs):
		'''
			update block or task instance into db.
		'''
		for obj in objs:
			self.db[obj._id] = obj
			self.db.sync()
		return True

	def updateIndex(self, *objs):
		'''
			write the properties of a block or task into bloxDB.index
		'''
		for obj in objs:
			try:
				if obj._id.endswith('0'):
					try:
						self.index[obj._id] = obj.__dict__
						return True
					except Exception as e:
						print('exception from 7134')
						print(e)
			finally:
				self.sync()

	def sync(self):
		self.db.sync()
		self.index.sync()
		return True

	# selectors
	def getKeyList(self, arg):
		kl = [key for key in self.index.keys()]
		bl = [key for key in kl if key.endswith('0')]
		tl = list(set(kl).difference(bl))
		if arg in ['b', 'block']:
			return bl
		else:
			return tl

	def getInstance(self, arg=None):
		
		if arg in ['lb']:
			bl = self.getKeyList('b')
			bl.sort()
			_id = bl[-1]

		elif arg in ['lt']:
			tl = self.getKeyList('t')
			tl.sort()
			_id = tl[-1]

		else:
			_id = arg
		
		instance = self.db[_id]
		return instance

	def getBlock(self, arg=None):
		'''
			# get latest block by default, no matter the block is active or not
			# getBlock('active') returns 
			# getBlock by id returns the block itself
			# v0.3 update: getBlock() now returns block instance when possible
			# 0.0.4: shorten codes, following EYTP princple
		'''

		if arg in [None,'latest','last']:
			instance = self.getInstance('lb')
			return instance

		elif arg in ['active', 'Active']:
			instance = self.getInstance('lb')
			if instance.state == 'active':
				return instance
			else:
				print('no active block')

		elif arg in ['All','all']:
			bl = self.getKeyList('b')
			return bl

		# accepts decimal id here
		elif parse(arg)[0].endswith('0'):
			instance = self.getInstance(parse(arg)[0])
			return instance

	def getTask(self, arg=None):
		'''
		'''
		if arg in [None,'latest','last']:
			instance = self.getInstance('lt')
			return instance

		elif arg in ['All','all']:
			tl = self.getKeyList('t')
			return tl

		else:
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
		self.tasks = {}
		self.eoc = None
		self.notes = []

		# transitions
		self.states = ['empty', 'active', 'closed']
		self.machine = Machine(model=self, states=self.states, initial='empty')
		self.machine.add_transition(trigger='boc', source='empty', dest='active', after='sync')
		self.machine.add_transition(trigger='eoc', source=['empty', 'active'], dest='closed', before='stash', after='sync')
		self.machine.add_transition(trigger='addTask', source=['empty', 'active'], dest='active', after='sync')


	def genNewBlockId(self):
		s = bloxDB()
		last_block_id = s.getBlock('last')._id
		_id = '0o' + str(int(last_block_id[2:-1])*10 + 10)
		s.db.close()
		s.index.close()
		return _id

	def boc():
		
		if not getBlock('active'):
			_id = self.genNewBlockId()
			b = Block(_id)
			return b

		else:
			# utils.stats()
			return
	def eoc(self):
		self.eoc = int(time.time())
		return True

	def updateTask(self, *tasks):
		for task in tasks:
			self.tasks[task._id] = task.__dict__
		return True

	def stashTasks(self):
		'''
			only call block.instance.stash() when attempting to close a block
			for other conditions, just call stash()
		'''
		for task in self.tasks:
			self.stash(task)
		return True
	
	def stash(self, task):
		'''
		'''

		return

	def storeInstance(self):
		'''
			store this instance into
		'''
		s = bloxDB()
		with s:
			s.storeInstance(self)
		return True

	def updateIndex(self):
		'''
		write current block into 
		'''
		s = bloxDB()
		with s:
			s.updateIndex(self)
		return True

	def sync(self):
		'''
			call self.storeInstance() and self.updateIndex()
		'''
		self.storeInstance()
		self.updateIndex()
		return True

class Task(Block):

	'''
		task_id is also str(octal nums), it follows block_id in an octal pattern.
	    srsly starts from 0o447256
	'''
	def __init__(self, _id, title):
		self._id = parse(_id)[0]
		self.parent = parse(_id)[2]
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

	def close(self):
		'''
			change self state and call parent.updateTask()
		'''
		self.end = int(time.time())
		self.focus = False
		s = bloxDB()
		with s:
			b = s.getBlock(self.parent)
		b.updateTask(self)
		return True

	def regInParent(self):
		'''
			update self in parent block.tasks
		'''
		s = bloxDB()
		with s:
			b = s.getBlock(self.parent)
		b.updateTask(self)

		return True