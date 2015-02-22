"""
################
#   Overview   #
################
Program: Matteorr Music Library class
Description: An object that loads mp3s from a folder
Author: Matthew E. Orr
Created: 2009.03.27
License: Creative Commons BY+NC+SA
"""

import os
from Song import Song

class MusicLibrary:
	""" a music library object """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,folderPath,doLoad=True):
		#--save the folder path--
		self.setPath(folderPath)
		
		#--initialize the list of song files--
		self._songs = []
		
		#--load the music from the path--
		if(doLoad):
			self.load()
		else:
			self._loaded = False
		return
	
	#################
	#   accessors   #
	#################
	
	def getPath(self):
		return self._folderPath
	
	def getSongs(self):
		return self._songs
	
	################
	#   mutators   #
	################
	
	def setPath(self,folderPath):
		self._folderPath = folderPath
		return
		
	def addSong(self,song):
		self._songs.append(song)
		return
	
	###############
	#   methods   #
	###############
	
	def load(self):
		""" loads the music in the folder recursively """
		
		print("loading music library: %s..." % (self.getPath()))
		
		#--actually load the library--
		directoryWalk = os.walk(self.getPath())
		for root, dirs, files in directoryWalk:
			for file in files:
				if(Song.isValidSongFilename(file)):
					song = Song(file,root)
					self.addSong(song)
					print("Added: %s" % (song.getPath()))
		
		#set loaded to true
		self._loaded = True
		print("done")
		return
	
	def isLoaded(self):
		""" returned true if the library has been loaded and false otherwise """
		
		return self._loaded
#end of MusicLibrary class