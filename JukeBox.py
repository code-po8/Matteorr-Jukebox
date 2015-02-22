#!/usr/bin/env python
"""

################
#   Overview   #
################
Program: Matteorr JukeBox
Description: An application that behaves like a jukebox
Created: 2009.03.27
License: Creative Commons BY+NC+SA


####################
#   REQUIREMENTS   #
####################
-gstreamer version 0.10
-python-gstreamer python library
-python-gobject python bindings
-wxPython python library
-eyeD3 python library


#######################
#   Future Features   #
#######################
-add saving of music library directories so that they persist when app is restarted
-scale the "currently playing" fonts with window size
-remember last folder selected when starting up the application
-capture mouse scroll wheel to change system volume
"""

###############
#   imports   #
###############

import sys, os
import getopt #for commandline arg processing
import wx #wxPython
import pygst #python gstreamer
pygst.require("0.10")
import gst #gstreamer

import gobject #not sure what this is but it's required for gstreamer
gobject.threads_init()

from Song import Song #matteorr song class
from MusicLibrary import MusicLibrary #matteorr music library class
from MusicDatabase import MusicDatabase #matteorr music database class


###############
#   globals   #
###############

#progress bar steps
progressSteps = 10000
timerMS = 100

#fonts
boldFont12 = None
boldFont18 = None
regularFont = None
titleFont = None

#image files
albumCoverFilename = "albumCover.png"
btn_musicFolderFilename = "btn_musicFolders.png"
btn_playlistFilename = "btn_playlist.png"
btn_nowPlayingFilename = "btn_nowPlaying.png"
btn_playFilename = "btn_play.png"
btn_stopFilename = "btn_stop.png"
btn_addFilename = "btn_add.png"
btn_removeFilename = "btn_remove.png"
btn_rightArrowFilename = "btn_rightArrow.png"


######################
#   custom classes   #
######################

class JukeBoxMenuPanel(wx.Panel):
	""" the main menu panel """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,*args,**kwargs):
		#--call the super-class constructor--
		wx.Panel.__init__(self,*args,**kwargs)
		
		#--setup parent--
		self.parent = args[0]
		
		#globals
		global btn_musicFolderFilename
		global btn_playlistFilename
		global btn_nowPlayingFilename
		
		#--set background color--
		self.SetBackgroundColour("BLACK")
		
		#--buttons--
		#music folders button
		self.panel_musicFolders = wx.Panel(self,id=wx.ID_ANY) #add panel for button
		self.panel_musicFolders.SetBackgroundColour("BLACK")
		self.btn_musicFolders = wx.BitmapButton(self.panel_musicFolders,id=wx.ID_ANY,bitmap=wx.Bitmap(btn_musicFolderFilename),size=(80,80)) #add button
		self.btn_musicFolders.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_musicFolders.Bind(wx.EVT_BUTTON,self.onClick_musicFolders) #bind button to onclick method
		self.btn_musicFolders.SetToolTip(wx.ToolTip("Manage Music Folders")) #set tooltip
		self.sizer_musicFolders = wx.BoxSizer(wx.VERTICAL) #add sizer for button
		self.sizer_musicFolders.Add(self.btn_musicFolders,0,wx.ALIGN_CENTER) #add button to sizer
		self.panel_musicFolders.SetSizer(self.sizer_musicFolders) #set panel's sizer
		
		
		#playlist button
		self.panel_playlist = wx.Panel(self,id=wx.ID_ANY) #add panel for button
		self.panel_playlist.SetBackgroundColour("BLACK")
		self.btn_playlist = wx.BitmapButton(self.panel_playlist,id=wx.ID_ANY,bitmap=wx.Bitmap(btn_playlistFilename),size=(80,80)) #add button
		self.btn_playlist.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_playlist.Bind(wx.EVT_BUTTON,self.onClick_playlist) #bind button to onclick method
		self.btn_playlist.SetToolTip(wx.ToolTip("Add Songs To The Playlist")) #set tooltip
		self.sizer_playlist = wx.BoxSizer(wx.VERTICAL) #add sizer for button
		self.sizer_playlist.Add(self.btn_playlist,0,wx.ALIGN_CENTER) #add button to sizer
		self.panel_playlist.SetSizer(self.sizer_playlist) #set panel's sizer
		
		#now playing button
		self.panel_nowPlaying = wx.Panel(self,id=wx.ID_ANY) #add panel for button
		self.panel_nowPlaying.SetBackgroundColour("BLACK")
		self.btn_nowPlaying = wx.BitmapButton(self.panel_nowPlaying,id=wx.ID_ANY,bitmap=wx.Bitmap(btn_nowPlayingFilename),size=(80,80)) #add button
		self.btn_nowPlaying.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_nowPlaying.Bind(wx.EVT_BUTTON,self.onClick_nowPlaying) #bind button to onclick method
		self.btn_nowPlaying.SetToolTip(wx.ToolTip("Now Playing")) #set tooltip
		self.sizer_nowPlaying = wx.BoxSizer(wx.VERTICAL) #add sizer for button
		self.sizer_nowPlaying.Add(self.btn_nowPlaying,0,wx.ALIGN_CENTER) #add button to sizer
		self.panel_nowPlaying.SetSizer(self.sizer_nowPlaying) #set panel's sizer
		
		#--add a sizer--
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.panel_musicFolders, 1, wx.ALIGN_CENTER|wx.ALL,10)
		sizer.Add(self.panel_playlist, 1, wx.ALIGN_CENTER|wx.ALL,10)
		sizer.Add(self.panel_nowPlaying, 1, wx.ALIGN_CENTER|wx.ALL,10)
		self.SetSizer(sizer)
	
	######################
	#   event handlers   #
	######################
	
	def onClick_musicFolders(self,event):
		""" music folders button event handler """
		self.parent.showMusicFolders()
		return
	
	def onClick_playlist(self,event):
		""" playlist button event handler """
		self.parent.showPlaylist()
		return
	
	def onClick_nowPlaying(self,event):
		""" now playing button event handler """
		self.parent.showNowPlaying()
		return

class MusicFoldersPanel(wx.Panel):
	""" a panel for the music folders """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,*args,**kwargs):
		#--call the super-class constructor--
		wx.Panel.__init__(self,*args,**kwargs)
		
		#--globals--
		global titleFont
		global btn_addFilename
		global btn_removeFilename
		
		#--setup parent--
		self.parent = args[0].GetParent()
		
		#--set the background color--
		self.SetBackgroundColour(wx.Color(0,0,128))
		
		#--add a panel title label--
		self.labelTitle = wx.StaticText(self,id=wx.ID_ANY,label="Music Folders")
		self.labelTitle.SetForegroundColour(wx.Color(255,255,255))
		self.labelTitle.SetFont(titleFont)
		
		#--add a listbox for all of the music folders--
		self.musicFoldersList = wx.ListBox(parent=self,id=wx.ID_ANY)
		self.musicFoldersList.SetBackgroundColour(wx.Color(102,102,255))
		
		self.btn_add = wx.BitmapButton(self,id=wx.ID_ANY,bitmap=wx.Bitmap(btn_addFilename),size=(80,80)) #add button to add folders
		self.btn_add.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_add.Bind(wx.EVT_BUTTON,self.onClick_add) #bind button to onclick method
		self.btn_add.SetToolTip(wx.ToolTip("Add Music Folder")) #set tooltip
		
		self.btn_remove = wx.BitmapButton(self,id=wx.ID_ANY,bitmap=wx.Bitmap(btn_removeFilename),size=(80,80)) #add button to remove folder
		self.btn_remove.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_remove.Bind(wx.EVT_BUTTON,self.onClick_remove) #bind button to onclick method
		self.btn_remove.SetToolTip(wx.ToolTip("Remove the select music folder")) #set tooltip
		
		self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL) #add sizer for buttons
		self.buttonSizer.Add(self.btn_add,0,wx.ALIGN_CENTER,10) #add button to sizer
		self.buttonSizer.Add(self.btn_remove,0,wx.ALIGN_CENTER,10) #add button to sizer
		
		#--add sizer--
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.labelTitle,0,wx.ALL,10)
		sizer.Add(self.musicFoldersList,1,wx.ALL|wx.EXPAND,10)
		sizer.Add(self.buttonSizer,0,wx.ALL|wx.ALIGN_RIGHT,10)
		self.SetSizer(sizer)
		self.Fit()
		
		#--load music library folders--
		self.refresh()
	
	######################
	#   event handlers   #
	######################
	
	def onClick_add(self,event):
		""" add button event handler """
		
		self.newMusicLibraryFolder()
		
		return
	
	def onClick_remove(self,event):
		""" remove button event handler """
		
		self.removeSelectedMusicFolder()
		
		return
	
	###############
	#   methods   #
	###############
	
	def refresh(self):
		""" method to reload the list of music folders """
		
		#clear the music folder list
		self.musicFoldersList.Clear()
		
		#add music folders to list
		musicLibraries = self.parent.getMusicLibraries()
		for library in musicLibraries:
			self.musicFoldersList.Append(library.getPath())
	
	def newMusicLibraryFolder(self):
		""" method to select and add a new music library folder """
		
		#get default path
		musicLibraries = self.parent.getMusicLibraries()
		if(len(musicLibraries) > 0):
			defaultPath = musicLibraries[-1].getPath()
		else:
			defaultPath = ".."
		#open dir dialog box
		print("Opening folder browser with default path set as %s" % defaultPath)
		dirDialog = wx.DirDialog(self,"Choose a folder...",defaultPath)
		selected = dirDialog.ShowModal()
		#get choosen directory
		if(selected == wx.ID_OK):
			#get the choosen directory path
			selectedPath = dirDialog.GetPath()
			#add directory to list of music libraries
			self.addMusicLibraryFolder(selectedPath)
		else:
			print("canceled")
		dirDialog.Destroy()
	
	def addMusicLibraryFolder(self,folderPath):
		""" method to add the path to the collection of music library folders """
		
		self.parent.addMusicLibraryFolder(folderPath)
		return
	
	def removeSelectedMusicFolder(self):
		""" method to remove the selected folder from the collection """
		
		#get the selected music folder path
		folderPath = self.musicFoldersList.GetStringSelection()
		
		#remove the selected music folder path
		self.parent.removeMusicLibraryFolder(folderPath)
		return

class MusicDatabasePanel(wx.Panel):
	""" a panel for the playlist """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,*args,**kwargs):		
		#--call the super-class constructor--
		wx.Panel.__init__(self,*args,**kwargs)
		
		#--globals--
		global regularFont
		global boldFont12
		global btn_rightArrowFilename
		
		#--setup parent--
		self.parent = args[0]
		
		#--set the background color--
		self.SetBackgroundColour(wx.Color(0,0,128))
		
		#--attributes--
		self.songsDict = {}
		
		#--add static text labels--
		labelMusicDB = wx.StaticText(self,id=wx.ID_ANY,label="Music Collection:")
		labelMusicDB.SetForegroundColour(wx.Color(255,255,255))
		labelMusicDB.SetFont(boldFont12)
		labelGenre = wx.StaticText(self, id=wx.ID_ANY,label="Genre")
		labelGenre.SetForegroundColour(wx.Color(102,102,255))
		labelGenre.SetFont(regularFont)
		labelArtist = wx.StaticText(self, id=wx.ID_ANY,label="Artist")
		labelArtist.SetForegroundColour(wx.Color(102,102,255))
		labelArtist.SetFont(regularFont)
		labelSong = wx.StaticText(self, id=wx.ID_ANY,label="Song")
		labelSong.SetForegroundColour(wx.Color(102,102,255))
		labelSong.SetFont(regularFont)
		
		#--display to show all the songs in the music database--
		#genre chooser
		self.genreList = wx.ListBox(parent=self,id=wx.ID_ANY)
		self.genreList.SetBackgroundColour(wx.Color(102,102,255))
		self.genreList.Bind(wx.EVT_LISTBOX, self.onSelect_genre)
		self.genreList.Disable()
		#artist chooser
		self.artistList = wx.ListBox(parent=self,id=wx.ID_ANY)
		self.artistList.SetBackgroundColour(wx.Color(102,102,255))
		self.artistList.Bind(wx.EVT_LISTBOX, self.onSelect_artist)
		self.artistList.Disable()
		#song chooser
		self.songList = wx.ListBox(parent=self,id=wx.ID_ANY)
		self.songList.SetBackgroundColour(wx.Color(102,102,255))
		self.songList.Bind(wx.EVT_LISTBOX, self.onSelect_song)
		self.songList.Disable()
		
		#--button to add to music queue--
		self.btn_add = wx.BitmapButton(self, id=wx.ID_ANY,bitmap=wx.Bitmap(btn_rightArrowFilename),size=(80,80))
		self.btn_add.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_add.Bind(wx.EVT_BUTTON,self.onClick_add)
		self.btn_add.SetToolTip(wx.ToolTip("Click here to add the song to the playlist"))
		self.btn_add.Disable() #disabled until a song is selected
		
		#--add sizer--
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(labelMusicDB,0,wx.ALL,10)
		sizer.Add(labelGenre,0,wx.ALL,10)
		sizer.Add(self.genreList,1,wx.ALL|wx.EXPAND,10)
		sizer.Add(labelArtist,0,wx.ALL,10)
		sizer.Add(self.artistList,1,wx.ALL|wx.EXPAND,10)
		sizer.Add(labelSong,0,wx.ALL,10)
		sizer.Add(self.songList,1,wx.ALL|wx.EXPAND,10)
		sizer.Add(self.btn_add, 0,wx.ALL|wx.ALIGN_RIGHT,10)
		self.SetSizer(sizer)
		self.Fit()
		
		#--load the music database display--
		self.refresh()
		return
	
	######################
	#   event handlers   #
	######################
	
	def onClick_add(self,event):
		""" add song button event handler """
		
		#get the currently selected genre
		selectedGenre = self.genreList.GetStringSelection()
		
		#get the currently selected artist
		selectedArtist = self.artistList.GetStringSelection()
		
		#get the currently selected song title
		selectedSongTitle = self.songList.GetStringSelection()
		
		#get the first song with this genre/artist/songTitle combo
		for song in self.songsDict[selectedGenre][selectedArtist]:
			if(song.getTitle() == selectedSongTitle):
				selectedSong = song
				break
		if(selectedSong):
			self.parent.queueSong(song)
			self.parent.parent.controlPanel.onClick_play(None)
			self.parent.parent.showNowPlaying()
		else:
			print("Did not find combination of genre/artist/songTitle in songsDict: %s/%s/%s" % (selectedGenre,selectedArtist,selectedSongTitle))
		return
	
	def onSelect_genre(self,event):
		""" select genre event handler """
		
		#clear the artist and song lists
		self.artistList.Clear()
		self.songList.Clear()
		self.songList.Append("Empty")
		self.songList.Disable()
		self.btn_add.Disable()
		
		#get the currently selected genre
		selectedGenre = self.genreList.GetStringSelection()
		
		#load artist list if genre is chosen
		if(selectedGenre != None and selectedGenre != ""):
			#get the list of artists in the selected genre
			artistsDict = self.songsDict[selectedGenre]
			artists = artistsDict.keys()
			#sort artists
			if(artists):
				artists.sort()
			
			#populate the artists listbox
			for artist in artists:
				self.artistList.Append(artist)
			
			#enable the artist listbox
			if(artists and (len(artists) > 0)):
				self.artistList.Enable()
			else:
				self.artistList.Append("Empty")
				self.artistList.Disable()
		else:
			self.artistList.Append("Empty")
			self.artistList.Disable()
		return
	
	def onSelect_artist(self,event):
		""" select artist event handler """
		
		#clear song list
		self.songList.Clear()
		self.btn_add.Disable()
		
		
		#get the currently selected artist
		selectedArtist = self.artistList.GetStringSelection()
		
		#load song list if artist is chosen
		if(selectedArtist != None and selectedArtist != ""):
			#get the currently selected genre
			selectedGenre = self.genreList.GetStringSelection()
			
			#get the list of songs for the selected genre:artist
			songs = self.songsDict[selectedGenre][selectedArtist]
			
			#populate the songs listbox
			songTitles = [song.getTitle() for song in songs]
			#sort song titles
			if(songTitles):
				songTitles.sort()
			for songTitle in songTitles:
				self.songList.Append(songTitle)
			
			#enable the song listbox
			if(songs and (len(songs) > 0)):
				self.songList.Enable()
			else:
				self.songList.Append("Empty")
				self.songList.Disable()
		else:
			self.songList.Append("Empty")
			self.songList.Disable()
		return
	
	def onSelect_song(self,event):
		""" select song event handler """
		
		#get the currently selected song title
		selectedSongTitle = self.songList.GetStringSelection()
		
		#enable/disable the add button depending on if a song is selected
		if(selectedSongTitle != None and selectedSongTitle != ""):
			self.btn_add.Enable()
		else:
			self.btn_add.Disable()
		return
	
	###############
	#   methods   #
	###############
	
	def refresh(self):
		""" refreshes the display of the music database """
		
		#populate the songsDict
		self.songsDict = {}
		for song in self.parent.parent.musicDatabase.getSongs():
			genre = song.getGenre()
			artist = song.getArtist()
			if(not genre in self.songsDict.keys()):
				self.songsDict[genre] = {}
			if(not artist in self.songsDict[genre].keys()):
				self.songsDict[genre][artist] = []
			if(not song in self.songsDict[genre][artist]):
				self.songsDict[genre][artist].append(song)
		
		#populate the genre list
		self.genreList.Clear()
		genres = self.songsDict.keys()
		#sort genres
		if(genres):
			genres.sort()
		for genre in genres:
			self.genreList.Append(genre)
		
		#enable the list
		if(genres and len(genres) > 0):
			self.genreList.Enable()
		else:
			self.genreList.Append("Empty")
			self.genreList.Disable()
		
		#clear the artist and song lists
		self.artistList.Clear()
		self.artistList.Append("Empty")
		self.artistList.Disable()
		self.songList.Clear()
		self.songList.Append("Empty")
		self.songList.Disable()
		return

class MusicQueuePanel(wx.Panel):
	""" a panel to hold all of the music play queue stuff """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,*args,**kwargs):
		#--call the super-class constructor--
		wx.Panel.__init__(self,*args,**kwargs)
		
		#--globals--
		global boldFont12
		
		#--setup parent--
		self.parent = args[0]
		
		#--set the background color--
		self.SetBackgroundColour(wx.Color(0,0,128))
		
		#--attributes--
		self.playQueue = []
		
		#--add static text label--
		label = wx.StaticText(self, id=wx.ID_ANY,label="Playlist:")
		label.SetForegroundColour(wx.Color(255,255,255))
		label.SetFont(boldFont12)
		
		#--play queue--
		self.playQueueDisplay = wx.ListBox(parent=self,id=wx.ID_ANY)
		self.playQueueDisplay.SetBackgroundColour(wx.Color(102,102,255))
		self.playQueueDisplay.Bind(wx.EVT_LISTBOX, self.onSelect_song)
		#self.playQueueDisplay.Disable() #disable since it is read-only
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(label,0,wx.ALL,10)
		sizer.Add(self.playQueueDisplay,1,wx.ALL|wx.EXPAND,10)
		self.SetSizer(sizer)
		self.Fit()
		return
	
	######################
	#   event hanlders   #
	######################
	
	def onSelect_song(self,event):
		self.playQueueDisplay.DeselectAll()
	
	###############
	#   methods   #
	###############
	
	def pop(self):
		""" gets the next song out of the queue """
		
		#get next song
		if(len(self.playQueue) > 0):
			#get next song
			nextSong = self.playQueue.pop(0)
		
			#refresh display
			self.refreshDisplay()
		else:
			nextSong = None
		return nextSong
	
	def push(self,song):
		""" adds a new song to the queue """
		
		#append song to play queue
		self.playQueue.append(song)
		
		#refresh display
		self.refreshDisplay()
		return
	
	def refreshDisplay(self):
		""" refreshes the display """
		
		self.playQueueDisplay.Clear()
		for song in self.playQueue:
			songDisplayStr = "%s - %s - %s" % (song.getGenre(),song.getArtist(),song.getTitle())
			self.playQueueDisplay.Append(songDisplayStr)
		return
#end of MusicQueuePanel class

class PlaylistPanel(wx.Panel):
	""" panel to hold the music library and play queue """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,*args,**kwargs):
		#--call the super-class constructor--
		wx.Panel.__init__(self,*args,**kwargs)
		
		#--setup parent--
		self.parent = args[0].GetParent()
		
		#--set the background color--
		self.SetBackgroundColour(wx.Color(0,0,128))
		
		#--add a music database panel--
		self.musicDatabasePanel = MusicDatabasePanel(self,wx.ID_ANY,style=wx.SIMPLE_BORDER)
		
		#--add a play queue panel--
		self.playQueuePanel = MusicQueuePanel(self,wx.ID_ANY,style=wx.SIMPLE_BORDER)
		
		#--add a sizer--
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.musicDatabasePanel,1,wx.EXPAND,10)
		sizer.Add(self.playQueuePanel,1,wx.EXPAND,10)
		self.SetSizer(sizer)
		self.Fit()
		
		return
	
	###############
	#   methods   #
	###############
	
	def queueSong(self,song):
		""" method to add a song to the play queue """
		
		#push song on to the play queue
		self.playQueuePanel.push(song)
		return
	
	def getNextSong(self):
		""" gets the next song to play """
		
		#get the next song in the play queue
		nextSong = self.playQueuePanel.pop()
		
		#if play queue is empty, get a random song from the music db
		if(not nextSong):
			nextSong = self.parent.musicDatabase.getRandomSong()
		
		#return the next song to play
		return nextSong
	
	def refresh(self):
		""" refreshes the panel """
		
		self.musicDatabasePanel.refresh()
#end of PlaylistPanel class

class NowPlayingPanel(wx.Panel):
	""" panel to show the now playing details """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,*args,**kwargs):
		#--call the super-class constructor--
		wx.Panel.__init__(self,*args,**kwargs)
		
		#--globals--
		global titleFont
		global regularFont
		global boldFont18
		global albumCoverFilename
		global progressSteps
		
		#--setup parent--
		self.parent = args[0].GetParent()
		
		#--set the background color--
		self.SetBackgroundColour(wx.Color(0,0,128))
		
		#--add a panel title label--
		self.labelTitle = wx.StaticText(self,id=wx.ID_ANY,label="Now Playing")
		self.labelTitle.SetForegroundColour(wx.Color(255,255,255))
		self.labelTitle.SetFont(titleFont)
		
		#--album cover placeholder--
		self.albumCoverImage = wx.Image(albumCoverFilename, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.albumCover = wx.StaticBitmap(self, -1, self.albumCoverImage, size=(250, 250))
		self.albumCoverSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.albumCoverSizer.Add(self.albumCover,1,wx.ALIGN_CENTER)
		self.albumCoverSizer2 = wx.BoxSizer(wx.VERTICAL)
		self.albumCoverSizer2.Add(self.albumCoverSizer,1,wx.ALIGN_CENTER)
		
		#--info section labels--
		self.labelGenre = wx.StaticText(self, id=wx.ID_ANY,label="Genre")
		self.labelGenre.SetForegroundColour(wx.Color(102,102,255))
		self.labelGenre.SetFont(regularFont)
		self.labelArtist = wx.StaticText(self, id=wx.ID_ANY,label="Artist")
		self.labelArtist.SetForegroundColour(wx.Color(102,102,255))
		self.labelArtist.SetFont(regularFont)
		self.labelSong = wx.StaticText(self, id=wx.ID_ANY,label="Song")
		self.labelSong.SetForegroundColour(wx.Color(102,102,255))
		self.labelSong.SetFont(regularFont)
		
		#--info section text--
		self.textGenre = wx.StaticText(self, id=wx.ID_ANY,label="")
		self.textGenre.SetForegroundColour(wx.Color(255,255,255))
		self.textGenre.SetFont(boldFont18)
		self.textArtist = wx.StaticText(self, id=wx.ID_ANY,label="")
		self.textArtist.SetForegroundColour(wx.Color(255,255,255))
		self.textArtist.SetFont(boldFont18)
		self.textSong = wx.StaticText(self, id=wx.ID_ANY,label="")
		self.textSong.SetForegroundColour(wx.Color(255,255,255))
		self.textSong.SetFont(boldFont18)
		
		#--add info section sizer--
		self.infoSizer = wx.BoxSizer(wx.VERTICAL)
		self.infoSizer.Add(self.labelGenre,0,wx.ALL,10)
		self.infoSizer.Add(self.textGenre,0,wx.ALL,10)
		self.infoSizer.Add(self.labelArtist,0,wx.ALL,10)
		self.infoSizer.Add(self.textArtist,0,wx.ALL,10)
		self.infoSizer.Add(self.labelSong,0,wx.ALL,10)
		self.infoSizer.Add(self.textSong,0,wx.ALL,10)
		
		#--add horizontal sizer--
		self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.hsizer.Add(self.albumCoverSizer2,1,wx.ALL|wx.ALIGN_CENTER,30)
		self.hsizer.Add(self.infoSizer,1,wx.ALL|wx.ALIGN_CENTER,30)
		
		#--add progress bar placeholder--
		self.progressBar = wx.Gauge(self, range=progressSteps, size=(50,50))
		self.progressBar.SetBackgroundColour(wx.Color(0,0,0))
		self.progressBarSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.progressBarSizer.Add(self.progressBar,1,wx.ALL|wx.EXPAND,10)
		
		#--add panel sizer--
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.labelTitle,0,wx.ALL,10)
		sizer.Add(self.hsizer,1,wx.ALL|wx.EXPAND|wx.ALIGN_CENTER,10)
		sizer.Add(self.progressBarSizer,0,wx.ALL|wx.EXPAND,10)
		self.SetSizer(sizer)
		self.Fit()
	
	###############
	#   methods   #
	###############
	
	def refresh(self):
		""" refreshes the panel """
		
		currentSong = self.parent.getCurrentlyPlayingSong()
		if(currentSong):
			genre = currentSong.getGenre().replace('&', ' and ')
			artist = currentSong.getArtist().replace('&', ' and ')
			title = currentSong.getTitle().replace('&', ' and ')
		else:
			genre = ""
			artist = ""
			title = ""
		self.textGenre.SetLabel(genre)
		self.textArtist.SetLabel(artist)
		self.textSong.SetLabel(title)
	
	def setProgressBar(self,percentage):
		self.progressBar.SetValue(percentage)

class JukeBoxControlPanel(wx.Panel):
	""" a panel for all of the jukebox controls """
	
	###################
	#   constructor   #
	###################
	
	def __init__(self,*args,**kwargs):
		#--call the super-class constructor--
		wx.Panel.__init__(self,*args,**kwargs)
		
		#--setup parent--
		self.parent = args[0]
		
		#--globals--
		global btn_playFilename
		global btn_stopFilename
		
		#--set background color--
		self.SetBackgroundColour("BLACK")
		
		#--buttons--
		#play button
		self.btn_play = wx.BitmapButton(self, id=wx.ID_ANY,bitmap=wx.Bitmap(btn_playFilename),size=(80,80))
		self.btn_play.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_play.Bind(wx.EVT_BUTTON,self.onClick_play)
		self.btn_play.SetToolTip(wx.ToolTip("Play"))
		
		#stop button
		self.btn_stop = wx.BitmapButton(self, id=wx.ID_ANY,bitmap=wx.Bitmap(btn_stopFilename),size=(80,80))
		self.btn_stop.SetBackgroundColour(wx.Color(0,0,128))
		self.btn_stop.Bind(wx.EVT_BUTTON,self.onClick_stop)
		self.btn_stop.SetToolTip(wx.ToolTip("Stop"))
		self.btn_stop.Disable() #disable to start with
		
		#--now playing label--
		self.nowPlayingDisplay = wx.StaticText(self, id=wx.ID_ANY,style=wx.SIMPLE_BORDER|wx.EXPAND,label="")
		self.nowPlayingDisplay.SetForegroundColour(wx.Color(0,0,255))
		
		#--add sizer--
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.btn_play, 0,wx.ALL,10)
		sizer.Add(self.btn_stop, 0,wx.ALL,10)
		sizer.Add(self.nowPlayingDisplay,1,wx.ALL,10)
		self.SetSizer(sizer)
		self.Fit()
		
		return
	
	######################
	#   event handlers   #
	######################
	
	def onClick_play(self,event):
		""" play button event handler """
		
		#check if currently playing
		currentlyPlaying = self.parent.parent.started
		if(not currentlyPlaying):
			#start playing next song
			self.playNextSong()
			
			#toggle the buttons' clickability
			self.btn_play.Disable()
			self.btn_stop.Enable()
			
			#reset focus
			self.btn_stop.SetFocus()
		
		return
	
	def onClick_stop(self,event):
		""" stop button event handler """
		
		#stop playing the song
		self.parent.stopPlaying()
		
		#clear the now playing display
		self.clearNowPlaying()
		
		#toggle the buttons' clickability
		self.btn_play.Enable()
		self.btn_stop.Disable()
		
		#reset focus
		self.btn_play.SetFocus()
		
		return
	
	###############
	#   methods   #
	###############
	
	def setNowPlaying(self,song=None):
		""" updates the now playing display """
		
		if(song == None):
			self.nowPlayingDisplay.SetLabel("")
		else:
			self.nowPlayingDisplay.SetLabel("Currently Playing: %s - %s - %s" % (song.getGenre().replace("&"," and "),song.getArtist().replace("&"," and "),song.getTitle().replace("&"," and ")))
		return
	
	def clearNowPlaying(self):
		""" clears the now playing display """
		
		self.setNowPlaying()
		return
	
	def newMusicLibraryFolder(self):
		""" passes this call from the music library panel up to the main window frame """
		
		self.parent.newMusicLibraryFolder()
		return
	
	def playNextSong(self):
		#get the next song to play
		song = self.parent.getNextSong()
		
		#set the now playing display
		self.setNowPlaying(song)
		
		#start playing the song
		self.parent.playSong(song)
#end of JukeBoxControlPanel class

class MainWindowFrame(wx.Frame):
	def __init__(self, *args,**kwargs):
		#--call the super-class constructor--
		wx.Frame.__init__(self, *args,**kwargs)
		
		
		#--initialize attributes--
		self._fullScreen = False
		
		#--set min size--
		self.SetMinSize((800,600))
		
		
		#--currently playing song--
		self._currentlyPlaying = None
		
		
		#--add accelerator table for capturing ctrl-* keys--
		acceleratorEntries = []
		
		#bind ctrl f event to handler
		fullscreenID = wx.NewId() #create new id
		self.Bind(wx.EVT_MENU,self.onCtrlF,id=fullscreenID) #bind id to event handler
		accelEntryCtrlF = wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('F'), fullscreenID) #create entry for binding ctrl-f to id
		acceleratorEntries.append(accelEntryCtrlF)
		
		#bind ctrl q event to handler
		exitID = wx.NewId() #create new id
		self.Bind(wx.EVT_MENU,self.onCtrlQ,id=exitID) #bind id to event handler
		accelEntryCtrlQ = wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('Q'), exitID) #create entry for binding ctrl-q to id
		acceleratorEntries.append(accelEntryCtrlQ)
		
		#add entries to table
		aTable = wx.AcceleratorTable(acceleratorEntries)
		self.SetAcceleratorTable(aTable)
		
		#--add music database--
		self.musicDatabase = MusicDatabase(self)
		self.musicLibraries = []
		
		#--add main menu panel--
		self.menuPanel = JukeBoxMenuPanel(self,wx.ID_ANY,style=wx.SIMPLE_BORDER)
		
		#--add main panel--
		self.mainPanel = wx.Panel(self,id=wx.ID_ANY)
		
		#--add music folders (music library) panel--
		self.musicFoldersPanel = MusicFoldersPanel(self.mainPanel,id=wx.ID_ANY)
		self.musicFoldersPanel.Show(True)
		
		#--add playlist (music database) panel--
		self.playlistPanel = PlaylistPanel(self.mainPanel,id=wx.ID_ANY)
		self.playlistPanel.Show(False)
		
		#--add now playing panel--
		self.nowPlayingPanel = NowPlayingPanel(self.mainPanel,id=wx.ID_ANY)
		#self.nowPlayingPanel.SetBackgroundColour('GREEN')
		self.nowPlayingPanel.Show(False)
		
		#--add main panel sizer--
		self.mainPanelSizer = wx.BoxSizer(wx.VERTICAL)
		self.mainPanelSizer.Add(self.musicFoldersPanel,1,wx.EXPAND)
		self.mainPanelSizer.Add(self.playlistPanel,1,wx.EXPAND)
		self.mainPanelSizer.Add(self.nowPlayingPanel,1,wx.EXPAND)
		self.mainPanel.SetSizer(self.mainPanelSizer)
		
		#--add control panel--
		self.controlPanel = JukeBoxControlPanel(self,wx.ID_ANY,style=wx.SIMPLE_BORDER)
		
		#--add a sizer--
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.menuPanel,0,wx.EXPAND)
		sizer.Add(self.mainPanel,1,wx.EXPAND)
		sizer.Add(self.controlPanel,0,wx.EXPAND)
		self.SetSizer(sizer)
		self.Fit()
		
		#--start frame in fullscreen--
		self.toggleFullscreen()
		self.menuPanel.SetFocus()
		
	def setParent(self,parent):
		self.parent = parent
	
	######################
	#   event handlers   #
	######################
	
	def onCtrlF(self,event):
		""" ctrl-f event handler """
		
		#toggle fullscreen view
		self.toggleFullscreen()
	
	def onCtrlQ(self,event):
		""" ctrl-q event handler """
		
		#close application
		self.closeApplication()
	
	###############
	#   methods   #
	###############
	
	def toggleFullscreen(self):
		""" toggles the main frame to and from fullscreen """
		
		self._fullScreen = not self._fullScreen
		self.ShowFullScreen(self._fullScreen)
	
	def closeApplication(self):
		""" closes the application """
		
		self.Close()
	
	def showMusicFolders(self):
		""" shows the music folders panel """
		
		#hide other main panels
		self.playlistPanel.Show(False)
		self.nowPlayingPanel.Show(False)
		
		#show music folders panel
		self.musicFoldersPanel.SetSize(self.mainPanel.GetSize())
		self.musicFoldersPanel.Show(True)
		return
	
	def showPlaylist(self):
		""" shows the playlist panel """
		
		#hide other main panels
		self.musicFoldersPanel.Show(False)
		self.nowPlayingPanel.Show(False)
		
		#show playlist panel
		self.playlistPanel.SetSize(self.mainPanel.GetSize())
		self.playlistPanel.Show(True)
		return
	
	def showNowPlaying(self):
		""" shows the now playing panel """
		
		#hide other main panels
		self.musicFoldersPanel.Show(False)
		self.playlistPanel.Show(False)
		
		#show now playing panel
		self.nowPlayingPanel.SetSize(self.mainPanel.GetSize())
		self.nowPlayingPanel.Show(True)
		return
	
	def loadMusicLibraries(self):
		""" loads the saved music libraries """
		
		#--load the music library folder paths--
		self.musicLibraries = []
		#load from saved file
		#todo
		
		#--load the music in those library directories--
		for library in self.musicLibraries:
			library.load()
		
		#--refresh the music db panel--
		self.playlistPanel.refresh()
		return
	
	def getMusicLibraries(self):
		""" returns the list of music library folders """
		
		return self.musicLibraries
	
	def addMusicLibraryFolder(self,folderPath):
		""" method to add the path to the collection of music library folders """
		
		#add path to list
		if(not folderPath in [library.getPath() for library in self.musicLibraries]):
			#--add to music library collection--
			print("Adding music library: %s..." % (folderPath))
			musicLibrary = MusicLibrary(folderPath)
			self.musicLibraries.append(musicLibrary)
			print("done")
			
			#--add music to full music collection--
			print("Adding songs from music library to music database...")
			for song in musicLibrary.getSongs():
				self.musicDatabase.addSong(song)
			print("done")
			
			#refresh the music db panel
			self.playlistPanel.refresh()
			self.musicFoldersPanel.refresh()
		else:
			print("Music library already added: %s" % (folderPath))
	
	def removeMusicLibraryFolder(self,folderPath):
		""" method to remove the path from the collection of music library folders """
		
		for library in self.musicLibraries:
			if(folderPath == library.getPath()):
				#loop through library and remove the songs from music collection
				for song in library.getSongs():
					self.musicDatabase.removeSong(song)
				
				#remove the library
				self.musicLibraries.remove(library)
				
				#refresh panels
				self.playlistPanel.refresh()
				self.musicFoldersPanel.refresh()
				
				#break out of for loop
				break
	
	def getNextSong(self):
		""" gets the next song from the jukebox music panel """
		
		#get the next song
		nextSong = self.playlistPanel.getNextSong()
		
		#return the next song
		return nextSong
	
	def stopPlaying(self):
		""" stops the player from playing """
		
		#stop player
		self.parent.stopPlaying()
		self._currentlyPlaying = None
		self.nowPlayingPanel.refresh()
	
	def playSong(self,song):
		self._currentlyPlaying = song
		self.parent.playSong(song)
		self.nowPlayingPanel.refresh()
	
	def getCurrentlyPlayingSong(self):
		return self._currentlyPlaying
	
	def updateProgressBar(self,percentage):
		self.nowPlayingPanel.setProgressBar(percentage)
		return
	
	def songFinished(self):
		self.controlPanel.playNextSong()
#end of MainWindowFrame class

class JukeBoxApp(wx.PySimpleApp):
	def OnInit(self):
		global boldFont12
		global boldFont18
		global regularFont
		global titleFont
		
		#setup fonts
		boldFont12 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		boldFont18 = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		regularFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		titleFont = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		
		
		self.window = MainWindowFrame(None)
		self.window.SetTitle("Matteorr JukeBox")
		self.window.Bind(wx.EVT_CLOSE,self.destroy)
		self.window.setParent(self)
		
		self.player = gst.element_factory_make("playbin", "player")
		fakesink = gst.element_factory_make("fakesink", "fakesink")
		self.player.set_property("video-sink", fakesink)
		bus = self.player.get_bus()
		bus.add_signal_watch()
		#bus.enable_sync_message_emission()
		bus.connect('message', self.on_message)
		#bus.connect('sync-message::element', self.on_sync_message)
		
		self.started = False
		self._timerAttempts = 0
		self._maxTimerAttempts = 10
		self.time_format = gst.Format(gst.FORMAT_TIME)
		#self.TIMER_ID = 100
		self.timer = wx.Timer(self)
		#self.timer.Bind(wx.EVT_TIMER, self.on_timer)
		self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
		
		return True
	
	######################
	#   event handlers   #
	######################
	
	def on_timer(self,event):
		""" timer event handler """
		
		global progressSteps
		global timerMS
		
		try:
			position = self.player.query_position(self.time_format, None)[0]
			duration = self.player.query_duration(self.time_format, None)[0]
			if(duration and duration != 0):
				percentage = float(position) / float(duration) * progressSteps
				self.window.updateProgressBar(percentage)
		except:
			self._timerAttempts += 1
			if(self._timerAttempts < self._maxTimerAttempts):
				print "Warning: Unable to determine progress bar.  Attempt %d" % (self._timerAttempts)
			else:
				print "Warning: Unable to determine progress bar.  Attempt %d.  Giving up." % (self._timerAttempts)
				self.stopProgressBarTimer()
	
	###############
	#   methods   #
	###############
	
	def stopProgressBarTimer(self):
		""" stops the progress bar timer """
		
		self.timer.Stop()
		self._timerAttempts = 0

	def playSong(self,song):
		""" starts the player playing the specified song """
		
		global timerMS
		
		if((not self.started) and (song)):
			filepath = song.getPath()
			if os.path.exists(filepath):
				self.started = True
				self.player.set_property('uri',"file://" + filepath)
				self.player.set_state(gst.STATE_PLAYING)
				self.timer.Start(timerMS)
					
	def stopPlaying(self):
		self.player.set_state(gst.STATE_NULL)
		self.started = False
		self.stopProgressBarTimer()
	
	def songFinished(self):
		self.window.songFinished()
	
	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			self.started = False
			self.stopProgressBarTimer()
			self.songFinished()
		elif t == gst.MESSAGE_ERROR:
			self.player.set_state(gst.STATE_NULL)
			self.started = False
			self.stopProgressBarTimer()
	
	def destroy(self,event):
		#Stop the player pipeline to prevent a X Window System error
		self.player.set_state(gst.STATE_NULL)
		event.Skip()
#end of JukeBoxApp class

############
#   MAIN   #
############
def main(argv):
	""" main method """
	
	#local variables
	defaultDirectory = None
	
	#get commandline args
	helpText = "JukeBox.py -d <path to music dir>"
	try:
		opts,args = getopt.getopt(argv,"d:")
	except getopt.GetoptError:
		print helpText
		sys.exit(2)
	for opt,arg in opts:
		if opt == '-d':
			defaultDirectory = arg
		
	
	#start jukebox
	app = JukeBoxApp()
	if(defaultDirectory):
		print "Setting music directory to %s..." % (defaultDirectory)
		
		#add directory
		app.window.addMusicLibraryFolder(defaultDirectory)
		
		#disable music folder button
		app.window.menuPanel.btn_musicFolders.Disable()
		
		#show the now playing screen
		app.window.showNowPlaying()
		
		#start playing a random song
		app.window.controlPanel.onClick_play(None)
	app.MainLoop()
if __name__ == "__main__":
	main(sys.argv[1:])
