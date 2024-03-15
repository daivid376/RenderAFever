import maya.cmds as mc
import os
from collections import OrderedDict

class Light(dict):
	def __init__(self):
		pass

class LightingLibrary(dict):

	"""docstring for LightingLibraryFunctions"""
	def __init__(self):
		super(LightingLibrary, self).__init__()

		self.lightData = []
		self.lightType = None
		self.lightName = None
		self.lightFilePath = None
		self.thumbnailFilePath = None
		self.noLightFile = True
		self.noThumbnail = True


	def readLightData(self,lightPath):
		thumbnailExts = ['jpg','png','JPG','PNG']
		lightFileExts = ['ma','mb']
		#print lightPath, '   lightPath in  LightingLibrary'
		if not os.path.isfile(lightPath):
			#print 'what'
			files = os.listdir(lightPath)
			if files != []:
				for file in files:
					ext = file.rpartition('.')[2]
					#print ext ,'  ext'
					if ext in lightFileExts:
						#print lightPath, '   lightPath'
						self.lightType = lightPath.rpartition('\\')[2]
						self.lightName = file.rpartition('.')[0]
						self.lightFilePath = os.path.join(lightPath,file) 
						self.noLightFile = False
					if self.noLightFile:
						self.lightType = None
						self.lightFilePath = None
						self.lightName = None
						self.thumbnailFilePath = None
				
				
				if not self.noLightFile:
		
					for file in files:
						ext = file.rpartition('.')[2]
						if ext in thumbnailExts:
							self.thumbnailFilePath = os.path.join(lightPath,file)
							self.noThumbnail = False
						if self.noThumbnail:
							self.thumbnailFilePath = None

		#else:
		#	mc.warning(lightPath + ' is not a folder!')


		self.lightData =  {'lightName' : self.lightName,
		'lightFilePath' : self.lightFilePath,
		'thumbnailFilePath': self.thumbnailFilePath}

		self[self.lightType] = self.lightData
		#print self.lightData

