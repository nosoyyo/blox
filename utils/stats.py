#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @absurdity

__author__ = 'nosoyyo'

import time
import datetime

import api.control
from .tools import printc

def stats(arg=None):

	stats = {}
	stats['abId'] = api.control.getBlock('latest')._id
	stats['boc'] = api.control.getBlock('latest').boc
	stats['ago'] = int((time.time() - stats['boc'])/60)
	stats['tf'] = api.control.getFinishedTask('count')
	
	# simply showcase
	if arg in [None,'general','g']:
		content = []	
		content.append('Woking within block #' + stats['abId'])
		content.append('boc - ' + datetime.datetime.fromtimestamp(stats['boc']).ctime().split(' ')[-2])
		content.append('That was ' + str(stats['ago']) + ' mins ago.')
		content.append(str(stats['tf']) + ' tasks finished.')
		printc(content)
	if arg in ['d','density']:
		return

	if arg in ['v','verbose']:
		return
	
	# return the list
	elif arg == 'dict':
		return stats