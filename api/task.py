#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity

__author__ = 'nosoyyo'
#__all__ = [add,tf,ft]

import time

import utils
from .block import Block
from .control import *

class Task(Block):

	'''
		task_id is also str(octal nums), it follows block_id in an octal pattern.
	    srsly starts from 0o447256
	'''
	def __init__(self, _id, title):
		self._id = utils.parse(_id)[0]
		self.parent = ''
		self.title = title

		# for compatible to older versions. 'task_id' is deprecated since v0.3
		self.task_id = self._id
		self.started_at = int(time.time())
		self.context = None
		self.status = 'active'
		self.focus = None
		self.notes = []
		self.nows = 0
		self.end = None

	def close(self, status):
		'''
			change self status and call updateInDB()
		'''
		self.end = int(time.time())
		self.focus = False
		self.status = status
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

def add(title):

	try:

		# check if within an active block
		if getBlock('active'):
			b = getBlock('active')
			parent = b._id
				
			# 1st task of a block
			abId = int(b._id[2:])
			taskSpace = range(abId, abId + 8)
			if not b.tasks:
				task_id = '0o' + str(taskSpace[0] + 1)
			else:
				task_id = '0o' + str(taskSpace[len(b.tasks)] + 1)

			# verbosity
			print('trying to add task #' + task_id + '...')

			t = Task(task_id, title)
			t.parent = parent
			t.status = 'active'
			# verbosity
			now = time.ctime().split(' ')[-2]
			print('<nosoyyo> start to ' + t.title + ' at ' + now)

			# we already get a Task() object, now deal with following stuff
			if not checkFocus():
				t.focus = True
				print("...and is focusing on it!")
			
			else:
				if len(b.tasks) in range(1,8):
					t.focus = False	
					# print current task
					printTask(b.tasks)
					# force to set context
					cf = checkFocus()
					print('currently focusing on #' + cf['task_id'] + ' - ' + cf['title'])
					t.context = context('set')

				else:
					t.status = 'invalid'
					print('at most 8 tasks stashed. exceeded task will vanish.\nLike us in death...')
			
			# update self
			t.sync()

			# register in parent
			t.regInParent()

		else:
			print('adding task when not working')
			print('as blox bot, i assume that you are going to do this as soon as next boc.')
			print('for this devel slice, we do nothing here')
	
	except Exception as e:
		print(e)


def finish(arg=None): 
	'''
		finish() is all about get the task_id and finish it.
		like close() and other similiar functions.
	'''
	def operationBundle(instance):
		instance.close('finished')
		instance.regInParent()
		instance.sync()
		return

	if arg in [None]:
		if checkFocus():
			t = checkFocus()
			operationBundle(t)

	elif arg in ['all']:
		print('in what case do you need to finish all tasks? super curious.')

	# accepts specific task id here
	else:
		_id = utils.parse(arg)[0]
		t = getInstance(_id)
		operationBundle(t)
