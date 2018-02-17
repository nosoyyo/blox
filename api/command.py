#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity

__author__ = 'nosoyyo'
# __all__ = ['now', 'focus', 'context']

import time
import pickle
import datetime

from .control import *
import utils

def now(arg=None):
	
	''' run this after boc, or after tf, or just any time you feel lost
		when no task active, gives task list so that one can get to know what to do really quick.
		one can pick up a task to focus, or checkout something meaningful
		(important infos would be sent into now() by other functions but won't disturb you instantly)
		and this function should stay as extremely simple
	'''
	def nowsPlus1(instance):
		instance.nows += 1
		setStatusInDB(instance._id, 'nows', instance.nows)
		return

	if checkFocus():
		t = getTask()
		
		# utils.printc
		utils.printc('#' + t._id + ' - ' + t.title)

		# nows += 1
		nowsPlus1(t)

	elif getBlock().status == 'active':
		# if we have tasks registered in current active block
		if getBlock().tasks:
			b = getBlock()
			tasks =[pickle.loads(item) for item in b.tasks]
			finished, stashed = [],[]
			content = ['block #' + b._id + "[active]",'\n','finished:']
			
			# distinguish tasks by status
			for item in tasks:
				if item.status == 'finished':
					finished.append('#' + item._id + ' - ' + item.title)
				elif item.status == 'stashed':
					stashed.append('#' + item._id + ' - ' + item.title)
			
			for item in finished:
				content.append(item)

			# separator
			content.append('\n')
			content.append('stashed:')
			
			# then append stashed tasks
			for item in stashed:
				content.append(item)

			# finally
			content.append('\n')
			content.append("no active task right now. try 'add(a task)'")
			utils.printc(content)

		elif getTask('s'):
			stashed = getTask('s')
			content = ['stashed:']
			for item in stashed:
				content.append(item['task_id'] + ' - ' + item['title'])
			utils.printc(content)
		else:
			utils.printc("pure nothing", "try add('a task')")
	else:
		content = ['not at work.', "'boc()' when you feel like begin."]
		utils.printc(content)

def stash(arg=None, debug=conf.Debug):
	''' stash a specific task
		or display the currently stashed tasks list by default
	'''
	if arg in [None,'list']:
		content = ['tasks stashed:']
		tasks = mt.find({'status':'stashed'})
		for item in tasks:
			content.append('#' + item['task_id'] + ' - ' + item['title'])
		if content:
			return content
		else:
			utils.printc('we are clean.')
	# accepts bytes here to deal with task instances
	elif type(arg) == type(b''):
		print('really need to accept bytes obj?')
	else:
		# prepare task attrs to set
		t = getTask(arg)
		t.focus= False
		t.status = 'stashed'
		t.paused = int(time.time())
		t.context = input('persistize your mind as context:\n')
		t.acrossing = None

		# update in db and register in parent
		t.sync()
		
		if debug:
			print('task #' + t._id + ' stashed.')

def focus(arg=None):
	'''use focus() to switch active between tasks.
		display a prettfied task list by default like ' <1> TASK ID  -   TITLE  (context optional)'
		can only switch to stashed tasks:
		can be used to restore auto-stashed task from last block
		display context when restore
	'''
	if arg in [None]:
		'''
			default action
		'''
		if stash():

			content = []
			for item in stash():
				content.append(item)
			utils.printc(content)

			# choose from list above
			choice = input('\033[0;35m' + 'choose a task to focus[1~' + str(len(content)-1) + ']:')
			print('\033[0m')

			if choice:
				if checkFocus():
					cf = checkFocus()
					# unfocus current focusing one
					cfId = cf['task_id']
					setFocus(cfId, False)
					# unregister in its parent
					old_parent = cf['parent']
					setFocus(old_parent, False)

				# focus the destined one

				dest = content[int(choice)].split(' ')[0][1:]
				setFocus(dest, True)
				# register in its parent
				new_parent = getParent(dest)
				setFocus(new_parent, True)

			else:
				pass

		else:
			content = ["no stashed task. ", "try add('a task')"]
			utils.printc(content)
			





