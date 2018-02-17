#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity

__author__ = 'nosoyyo'
__all__ = ['terminalSize', 'printc', 'getParent', 'parse']

from wxpy import *
from .pipelines import MongoDBPipeline

def terminalSize():
	'''
		get current terminal window size
	'''
	import fcntl, termios, struct
	th, tw, hp, wp = struct.unpack('HHHH',
		fcntl.ioctl(0, termios.TIOCGWINSZ,
		struct.pack('HHHH', 0, 0, 0, 0)))
	return tw, th

def printc(content,align='c'):
	'''
		print content right in the middle of the screen
	'''
	tw,th = terminalSize()
	if type(content) == type(str()):
		print('\n'*round((th-1)/2))
		if align == 'c':
			print(' '*round(round(tw - len(content))/2)+ content)
		elif align == 'l':
			print(content)
		else:
			print('no code here')
		print('\n'*round((th-1)/2))
	elif type(content) == type([]):
		print('\n'*round((th-len(content))/2))
		for item in content:
			if align == 'c':
				print(' '*round(round(tw - len(item))/2)+ item)
			elif align == 'l':
				print(item)
			else:
				print('no code here')
		print('\n'*round((th-len(content))/2))

def getParent(arg):
	'''
		simply get the parent block id of arg
	'''
	parent = str(arg).replace(arg[-1],'0')
	return parent

def parse(input):

	'''
		parse the input and return a list of [_id, field]
		field is used when modifying database kv pairs as the key
	'''

	result = []

	# transform decimal input into octal
	if type(input) == type(1):
		_id = '0o' + str(input)
	else:
		if input.startswith('0o'):
			_id = input
		else:
			_id = '0o' + str(input)
	result.append(_id)

	# block or task
	if str(input).endswith('0'):
		field = 'block_id'
	else:
		field = 'task_id'
	result.append(field)

	return result
