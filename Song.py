"""
################
#   Overview   #
################
Program: Matteorr Song Class
Description: A song object
Author: Matthew E. Orr
Created: 2009.03.27
License: Creative Commons BY+NC+SA

####################
#   Requirements   #
####################
-eyeD3 python library

"""


import eyeD3 #for manipulating mp3 id3 tags

class Song:
	""" a song object """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,songFilename,songPath=""):
		#--set the song's path--
		if(Song.isValidSongFilename(songFilename)):
			if(songPath and len(songPath) > 0):
				#start with path
				self._songPath = songPath
				
				#add slash if needed
				if(self._songPath[-1] != '/'):
					self._songPath += '/'
					
				#end with filename
				self._songPath += songFilename
			else:
				#set filename (assumes full path is specified)
				self._songPath = songFilename
		else:
			raise ValueError("Error: File does not have a valid song filename")
		
		#--load the other ID3 tag info--
		self.loadID3Tags()
		
		return
	
	##################
	#   toString()   #
	##################
	
	def __str__(self):
		""" toString method """
		
		if(self.getTitle()):
			rv = ""
			if(self._genre):
				rv += self._genre
			if(self._artist):
				rv += self._artist
			rv += self._title
			return rv
		else:
			return self.getPath()
	
	######################
	#   static methods   #
	######################
	
	def isValidSongFilename(filename):
		""" checks if its a valid song filename """
		
		validFileExtentions = ('mp3',)
		if(filename[-3:] in validFileExtentions):
			return True
		else:
			return False
	isValidSongFilename = staticmethod(isValidSongFilename)
	
	#################
	#   accessors   #
	#################
	
	def getPath(self):
		""" returns the song path """
		
		return self._songPath
	
	def getTitle(self):
		""" returns the song title """
		
		if(self._title):
			return self._title
		else:
			return self._songPath
	
	def getArtist(self):
		""" returns the song's artist """
		
		if(self._artist):
			return self._artist
		else:
			return "Unknown Artist"
	
	def getGenre(self):
		""" returns the song's genre """
		
		if(self._genre):
			return self._genre
		else:
			return "Unknown Genre"
	
	###############
	#   methods   #
	###############
	
	def loadID3Tags(self):
		try:
			tag = eyeD3.Tag()
			tagSuccessful = tag.link(self._songPath)
			if(tagSuccessful):
				self._artist = tag.getArtist()
				self._title = tag.getTitle()
				genreObject = tag.getGenre()
				if(genreObject):
					self._genre = genreObject.name
				else:
					self._genre = None
			else:
				self._artist = None
				self._title = None
				self._genre = None
		except:
			self._artist = None
			self._title = None
			self._genre = None
			print("Error loading tag for: %s" % self._songPath)
#end of Song class