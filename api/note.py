#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity

__author__ = 'nosoyyo'

import time

import utils
from .control import *

class Note():

	''' note is very simple, it has less attrs, less status
		a note always has a parent, either block or task
		the content of note might be inputed separatedly, so they're stored in a list
		so are the urls
	'''
	def __init__(self, note_id, parent):
		self.parent = parent
		self.content = ''
		self.note_id = note_id
		self.created_at = int(time.time())
		self.urls = []

def note(arg=None):

	# find parent
	if checkFocus():
		parent = checkFocus()['task_id']
		flag = mt
		field = 'task_id'
	else:
		parent = getBlock('last')['block_id']
		flag = mb
		field = 'block_id'
	
	note_id = getNote()['note_id'] + 1
	n = Note(note_id, parent)
	
	# get content
	if arg in [None]:
		content = input('note://')
	else:
		content = arg
	n.content = content

	# register in parent
	flag.update({field:parent},{'$push':{'note_id':n.note_id,'notes':n.content}},upsert=True)
	print('note updated in #' + n.parent + '.')

	# store whole in m.notes
	mn.insert({'note_id':n.note_id, 'contents':n.content, 'parent':n.parent, 'created_at':n.created_at})

def noteRemove(parent, content):
	''' basically blox don't support remove any note. 
		or later there'll be ctrl+z, ctrl+z of ctrl + z, recycle bin, and so on.
		what's input is input.
	'''
	if parent.endswith('0'):
		flag = mb
		field = 'block_id'
	else:
		flag = mt
		field = 'task_id'
	flag.update({field:parent},{'$pull':{'notes':content}})
	# feedback
	print('note removed')
