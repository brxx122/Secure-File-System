#!/usr/bin/env python2.7

READ = 1
WRITE = 2
EXEC = 3

class Inode:
	def __init__(self, username, filename):
		self.username = username
		self.filename = filename
		self.perm = WRITE
		self.share = {}
	def setperm(self, perm):
		self.perm = perm
	def setshareperm(self, sharename, perm):
		self.share[sharename] = perm
	def checkperm(self, require):
		if self.perm > require:
			return True
		else:
			return False
	def checkshareperm(self, username, require):
		if not username in self.share.keys():
			return False
		else:
			if self.share[username] > require:
				return True
			else:
				return False