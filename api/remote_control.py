#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity
__author__ = 'nosoyyo'

import pickle
import datetime

import ezcf
import conf

import utils

# initDB
# m, bloxCol, mb, mt, mn = utils.initDB(settings)

class bloxDB(utils.Singleton):
	
	def __init__(self, dbname, usr, pwd):
		'''
			when operates the index, use
			self.index.blocks
			self.index.tasks
			self.index.notes
		'''
		self.index = utils.MongoDBPipeline(dbname, usr, pwd,).setCol(dbname,conf.Blindex).col


	def clearIndex(self):
		confirmation = input('this will do {}.drop, are you sure?'.format(self.index))
		if confirmation == 'Yes':
			self.index.drop()

	def initIndex(self):
		something


def genNewBlockId():
	last_block_id = getBlock('last')._id
	return '0o' + str(int(last_block_id[2:-1])*10 + 10)

def storeInstanceInDB(obj):
	'''
		field: block_id | task_id
	'''
	if obj._id.endswith('0'):
		field = 'block_id'
	else:
		field = 'task_id'
	bloxCol.update({field:obj._id},{'$set':{'object':pickle.dumps(obj)}},upsert=True)
	return True

def updateInDB(obj):
		'''
			write current block into bloxCol.blocks
		'''
		if obj._id.endswith('0'):
			try:
				mb.update({
							'block_id' : obj._id
							},
								{'$set':{
										'block_id' : obj._id, 
										'boc' : obj.boc, 
										'eoc' : obj.eoc,
										'status' : obj.status,
										'tasks' : [pickle.dumps(task) for task in obj.tasks],
										'notes' : obj.notes,
								}}, upsert=True)
				return True
			except Exception as e:
				print('exception from 9169')
				print(e)
		else:
			try:
				mt.update({
							'task_id' : obj._id
							},
								{'$set':{
										'task_id' : obj._id,
										'title' : obj.title,
										'started_at' : obj.started_at, 
										'end' : obj.end,
										'parent' : obj.parent,
										'status' : obj.status,
										'focus' : obj.focus,
										'notes' : obj.notes,
										'nows' : obj.nows,
										'context' : obj.context,
								}}, upsert=True)
				return True
			except Exception as e:
				print('exception from 7134')
				print(e)

def context(arg=None):
	'''
		save context for next block, 
		or get context from last block,
		or stash context for task switching,
		or for the acrossing task
	'''
	if arg in [None]:
		# default action
		return

	if arg in ['s','set']:
		context = input('\033[0;35m' + 'context://')
		print('\033[0m')
		return context

	else:
		parent, field = utils.parse(arg)
		context = getInstance(parent).context
		return context

def checkFocus(debug=False):
	''' 
		normally we would have only one focus task at one time
	'''
	try:
		f = [item for item in mt.find({'focus':True})]
		if f:
			if not debug:
				return getInstance(f[0]['task_id'])
			else:
				printTasks(f)
				return True
		else:
			pass
	except Exception as e:
		print(e)

def getInstance(_id, debug=conf.Debug):
	try:
		if utils.parse(_id)[0].endswith('0'):
			instance = pickle.loads(bloxCol.find({'block_id' : utils.parse(_id)[0]})[0]['object'])
			if debug:
				print('ready to return block obj #' + instance._id)
		else:
			instance = pickle.loads(bloxCol.find({'task_id':utils.parse(_id)[0]})[0]['object'])
			if debug:
				print('ready to return task obj #' + instance._id)
		return instance
	except Exception as e:
		print(e)

def getBlock(arg=None, debug=conf.Debug):
	'''
	# get latest block by default, no matter the block is active or not
	# getBlock('active') returns 
	# getBlock by id returns the block itself
	# v0.3 update: getBlock() now returns block instance when possible
	'''
	try:

		if arg in [None,'latest','last']:
			if debug == True:
				print('Fetching latest block...')
			_id = mb.find()[mb.count() - 1]['block_id']
			instance = getInstance(_id)
			return instance

		elif arg in ['active', 'Active']:
			tmp = []
			for item in mb.find({'status':'active'}):
				tmp.append(item)
			if len(tmp) == 1:
				block_id = mb.find({'status':'active'})[0]['block_id']
				instance = getInstance(block_id)
				return instance
			
			elif len(tmp) > 1:
				if debug == True:
					print("Panic attack, more than 1 active task! Human is not multitasking animal. ")
			else:
				if debug == True:
					print("Most likely there's no active block.")

		elif arg in ['All','all']:
			raw_blocks = []
			block_list = []
			for item in mb.find():
				raw_blocks.append(item)
			for item in raw_blocks:
				block_list.append(item['block_id'])
			return block_list

		# accepts decimal id here
		elif utils.parse(arg)[0].endswith('0'):
			block_id = utils.parse(arg)[0]
			if debug == True:
				print('get the block id, redirect to getInstance() now...')
			instance = getInstance(block_id)
			return instance
	
	except KeyError:
		print("Most likely there's no active block.")
	except AttributeError:
		print('Carefully check the input is strongly recommended.')
	except IndexError:
		print('No such item. You sure?')
	except Exception as e:
		print(e)

def getTask(arg=None, debug=conf.Debug):

	try:

		if arg in [None, 'current','focus']:
			if checkFocus():
				_id = checkFocus()._id
				task = getInstance(_id)
				return task
			else:
				if debug:
					print('no active task')
				tasks = [item for item in mt.find()]
				return tasks
		
		elif arg in ['s','acrossing','stash','stashed']:
			tasks = [item for item in mt.find({'status':'stashed'})]
			if tasks:
				return tasks
			else:
				if debug:
					print('no stashed task')
		
		elif arg in ['a','all','ALL','list']:
			for item in mt.find():
				tasks.append(item)
			return tasks
		
		elif arg in ['b','block']:
			b = getBlock()
			# all control funcs basically return instances
			tasks = [pickle.loads(task) for task in b.tasks]
			return tasks

		else:
			if not utils.parse(arg)[0].endswith('0'):
				task = getInstance(arg)
				return task
			else:
				tasks = getInstance(arg).tasks
				return tasks
	
	except Exception as e:
		print(e)

def getFinishedTask(arg='c'):
	try:
		tasks = getBlock().tasks
		tf = [tasks[i] for i in range(0,len(tasks))]
		if arg in ['c','count']:
			return len(tf)
		elif arg in ['t','tasks']:
			return tf
	except Exception as e:
		print(e)

def printTasks(tasks):
	'''
	# accept a list of mt items
	'''
	#print("<blox-bot> 'Current block #" + _id + " contains following tasks:'")
	
	print('n |  Task Id  | Title ')
	print('\n--------\n')

	for i in range(0, len(tasks)):
		print(str(i) + ' | ' + tasks[i]['task_id'] + ' | ' + tasks[i]['title'] + '[' + tasks[i]['status'].replace("'",' ') + ']')
	print('\n--------\n')
	return

def setFocus(_id, state):
	if utils.parse(_id)[0].endswith('0'):
		return print('dont try to mess with block')
	else:
		if state == True or False:
			t = getInstance(utils.parse(_id)[0])
			t.focus = state
			return True
		else:
			print("invalid state. should only be 'True' or 'False'.")

def setStatusInDB(dest, field, state, debug=conf.Debug):
	'''
		could be used both by blocks and tasks
	'''
	_id, db_field = utils.parse(dest)
	instance = getInstance(_id)
	instance.__setattr__(field, state)

	if debug:
		print('#' + instance._id + '.' + str(field) + ' set to "' + str(state) +'".')
	
	instance.sync()

	if debug:
		print('#' + instance._id + ' successfully updated in m' + db_field[0] + '.')
	return True

def getNote(arg=None, raw=True):
	notes = []

	if arg in [None,'latest']:
		for item in mn.find():
			notes.append(item)
		return notes[-1]

	elif arg in ['a','all','All']:
		for item in mn.find():
			notes.append(item)
		return notes

	elif type(arg) == type(1):
		note = mn.find({'note_id':arg})[0]
		return note

	elif arg.startswith('0o'):
		if arg.endswith('0'):
			parent = getBlock(arg)
		else:
			parent = getTask(arg)
		notes = parent['notes']
		return notes