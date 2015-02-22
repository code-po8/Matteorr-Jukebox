"""
################
#   Overview   #
################
Program: Matteorr Music Database class
Description: An object that holds a collection of songs
Author: Matthew E. Orr
Created: 2009.03.27
License: Creative Commons BY+NC+SA
"""


import random

class MusicDatabase:
	""" a database of songs from multiple libraries """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,parent):
		#setup attributes
		self.parent = parent
		self._songs = []
		random.seed()
		
		return
	
	#################
	#   accessors   #
	#################
	
	def getSongs(self):
		""" returns the list of songs """
		
		return self._songs
	
	def getRandomSong(self):
		""" returns a random song """
		
		if(len(self._songs) > 0):
			return random.choice(self._songs)
		else:
			return None
	
	################
	#   mutators   #
	################
	
	def addSong(self,songObject):
		""" adds a Song object to the list of songs """
		
		if(not songObject in self._songs):
			self._songs.append(songObject)
			print("Added song: %s" % (songObject.getPath()))
		return
	
	def removeSong(self,songObject):
		""" removes a Song object from the list of songs """
		
		if(songObject in self._songs):
			self._songs.remove(songObject)
		else:
			print("Song (%s) not in music database" % str(songObject))
#end of MusicDatabase class