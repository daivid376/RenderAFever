# -*- coding: utf-8 -*- 
from Qt import QtCore,QtWidgets
import Qt
import maya.cmds as mc
import os,json,inspect,gc,pprint
import UI
import UI.materialImporter
import UI.materialConverter
import UI.lightManager as lightManager
from functools import partial
from maya import OpenMayaUI as omui
import material.materialImporter
#import material.materialConverter


if Qt.__binding__ == 'PySide':
	#logger.debug('using PySide with shiboken')
	from shiboken import wrapInstance
	from Qt.QtCore import Signal
elif Qt.__binding__.startswith('PyQt'):
	from sip import wrapInstance as wrapInstance
	from Qt.QtCore import pyqtSignal as Signal
else:
	from shiboken2 import wrapInstance
	from Qt.QtCore import Signal

reload(UI.materialImporter)
reload(material.materialImporter)
reload(lightManager)
reload(UI.materialConverter)

version = 'v3.00_beta    '
mainUI_smallSize = [500,500]
mainUI_largeSize = [1200,800]
size01 = [500,400]
size02 = [500,200]
size03 = [1200,800]

def saveDataToJsonFile(content,jsonFile):

	with open(jsonFile, "w") as fp:
		json.dump(content, fp,indent = 4) 

def readDataFromJsonFile(jsonFile):
	with open(jsonFile) as jsFile:
		jsonData = json.load(jsFile)
	return jsonData

		
class RegisterUIManager():
	def __init__(self,affectedUI):
		self.scriptPath = mc.internalVar(usd = 1)
		self.UILanguagePath = os.path.join(self.scriptPath,'RenderAFever','UI','languages')
		self.presetFilePath = os.path.join(self.scriptPath,'RenderAFever_presets','RenderAFever_lastUI_preset.json')
		self.lastPresetFilePath = os.path.join(self.scriptPath,'RenderAFever_presets','RenderAFever_lastUI_preset.json')
		self.defaultPresetFilePath = os.path.join(self.scriptPath,'RenderAFever_presets','RenderAFever_defaultUI_preset.json')
		self.registar = {}
		self.language = 'English'
		self.UIName_UIInstance_dict = {}
		self.UIClass_functions_dict = {'QComboBox':['currentIndex','currentIndexChanged','setCurrentIndex'],
		'QCheckBox':['isChecked','stateChanged','setChecked'],
		'QRadioButton':['isChecked','toggled','setChecked'],
		'QLineEdit':['text','textChanged','setText'],
		'QTabWidget':['currentIndex','currentChanged','setCurrentIndex']}

		self.affectedUI = affectedUI

		#self.execute()

	#functions will be executed for this class
	def start(self):
		if hasattr(self.affectedUI,'storableUIs'):
			self.storableUIs = self.affectedUI.storableUIs
		else:
			self.storableUIs = []
		for storableUI in self.storableUIs:
			UIName = storableUI[0]
			UIInstance = storableUI[1]
			self.UIName_UIInstance_dict[UIName] = UIInstance
		
		self.restoreUIToJsonFile(self.lastPresetFilePath)
		self.UIChangeConnectToRefresh()
		self.register()
		

	#register ui uiInstances and uiFunctions
	def register(self):

		for UIName,thisInstance in self.UIName_UIInstance_dict.items():
			if type(thisInstance).__name__ in self.UIClass_functions_dict:
				UIClass = type(thisInstance).__name__
				thisDict = {}
				getFunc = getattr(thisInstance,self.UIClass_functions_dict[UIClass][0])
				value = getFunc()

				self.registar[UIName] = value
				self.registar['language'] = self.language
				self.UIName_UIInstance_dict[UIName] =thisInstance


		
	def UIChangeConnectToRefresh(self):
		for UIName,UIInstance in self.UIName_UIInstance_dict.items():
			UIClass = type(UIInstance).__name__
			changeFunc = getattr(UIInstance,self.UIClass_functions_dict[UIClass][1])
			changeFunc.connect(self.refresh)


	#resize the ui to default set
	def refresh(self):
		#the ui animation effect between different tabwidget
		
		def __animeForMainUI(UIName,UIInstance):
			if UIName == 'tabWidget01':
				index = UIInstance.currentIndex()
				if index ==  0:
					#self.affectedUI.resize(mainUI_largeSize[0],mainUI_largeSize[1])
					self.animation01 = QtCore.QPropertyAnimation(self.affectedUI, "size")
					self.animation01.setDuration(200)
					#self.animation01.setKeyValueAt(0.1,QtCore.QSize(mainUI_smallSize[0]-30, mainUI_smallSize[1]-10) )
					#self.animation01.setKeyValueAt(0.3,QtCore.QSize(mainUI_largeSize[0] + 20, mainUI_largeSize[1] + 10))
					self.animation01.setEndValue(QtCore.QSize(size01[0], size01[1]))
					self.animation01.setEasingCurve(QtCore.QEasingCurve.OutBack)
					self.animation01.start()
				if index == 1:
					#self.affectedUI.resize(mainUI_smallSize[0],mainUI_smallSize[1])

					self.animation02 = QtCore.QPropertyAnimation(self.affectedUI, "size")
					self.animation02.setDuration(240)
					#self.animation.setStartValue(QtCore.QSize(100, 100))
					#self.animation02.setKeyValueAt(0.1,QtCore.QSize(mainUI_smallSize[0]-20, mainUI_smallSize[1]-10) )
					#self.animation02.setKeyValueAt(0.3,QtCore.QSize(mainUI_smallSize[0], mainUI_smallSize[1]) )
					self.animation02.setEndValue(QtCore.QSize(size02[0], size02[1]))
					self.animation02.setEasingCurve(QtCore.QEasingCurve.InBack)
					self.animation02.start()
				if index == 2:
					#self.affectedUI.resize(mainUI_smallSize[0],mainUI_smallSize[1])

					self.animation02 = QtCore.QPropertyAnimation(self.affectedUI, "size")
					self.animation02.setDuration(240)
					#self.animation.setStartValue(QtCore.QSize(100, 100))
					#self.animation02.setKeyValueAt(0.1,QtCore.QSize(mainUI_smallSize[0]-20, mainUI_smallSize[1]-10) )
					#self.animation02.setKeyValueAt(0.3,QtCore.QSize(mainUI_smallSize[0], mainUI_smallSize[1]) )
					self.animation02.setEndValue(QtCore.QSize(size03[0], size03[1]))
					self.animation02.setEasingCurve(QtCore.QEasingCurve.InBack)
					self.animation02.start()
			if UIName == 'tabWidget02':
				index = UIInstance.currentIndex()
				if index == 2:
					#self.affectedUI.resize(mainUI_largeSize[0],mainUI_largeSize[1])
					self.animation01 = QtCore.QPropertyAnimation(self.affectedUI, "size")
					self.animation01.setDuration(200)
					#self.animation01.setKeyValueAt(0.1,QtCore.QSize(mainUI_smallSize[0]-30, mainUI_smallSize[1]-10) )
					#self.animation01.setKeyValueAt(0.3,QtCore.QSize(mainUI_largeSize[0] + 20, mainUI_largeSize[1] + 10))
					self.animation01.setEndValue(QtCore.QSize(mainUI_largeSize[0], mainUI_largeSize[1]))
					self.animation01.setEasingCurve(QtCore.QEasingCurve.OutBack)
					self.animation01.start()
				else:
					#self.affectedUI.resize(mainUI_smallSize[0],mainUI_smallSize[1])

					self.animation02 = QtCore.QPropertyAnimation(self.affectedUI, "size")
					self.animation02.setDuration(240)
					#self.animation.setStartValue(QtCore.QSize(100, 100))
					#self.animation02.setKeyValueAt(0.1,QtCore.QSize(mainUI_smallSize[0]-20, mainUI_smallSize[1]-10) )
					#self.animation02.setKeyValueAt(0.3,QtCore.QSize(mainUI_smallSize[0], mainUI_smallSize[1]) )
					self.animation02.setEndValue(QtCore.QSize(mainUI_smallSize[0], mainUI_smallSize[1]))
					self.animation02.setEasingCurve(QtCore.QEasingCurve.InBack)
					self.animation02.start()



		for UIName,UIInstance in self.UIName_UIInstance_dict.items():
			self.register()
			__animeForMainUI(UIName,UIInstance)
		self.storeUIData()



		
	def storeUIData(self):
		allRegistar = {}
		allUIManagers = [obj for obj in gc.get_objects() if isinstance(obj,RegisterUIManager)]
		for UIManager in allUIManagers:

			allRegistar.update(UIManager.registar)

		saveDataToJsonFile(allRegistar,self.lastPresetFilePath)

	#set UI to the input json UI data file
	def restoreUIToJsonFile(self,jsonFile):
		print '__________________restoreUI________________'
		try:
			UI_name_value_dict = readDataFromJsonFile(jsonFile)
		except:
			UI_name_value_dict = readDataFromJsonFile(self.defaultPresetFilePath)
			print 'error , read default ui file'
		

		__languageName = ''
		for UIName in self.UIName_UIInstance_dict:
			#print UIName
			#make sure it will not be wrong ,when UI is changed
			if hasattr(self.affectedUI,UIName):
				UIInstance = getattr(self.affectedUI,UIName)
				UIClass = type(UIInstance).__name__
				if UIName in UI_name_value_dict.keys():
					value = UI_name_value_dict[UIName]
					setFunc = getattr(UIInstance,self.UIClass_functions_dict[UIClass][2])
					setFunc(value)
			
		#load the language user set
		if 'language' in UI_name_value_dict:
			__languageName = UI_name_value_dict['language']
		else:
			__languageName = 'English'

		self.language = __languageName
		#self.refresh() # why use this refresh? no use and create bug every time


	def setLanguage(self,languageName):
		languageConfigFiles = os.listdir( self.UILanguagePath)
		for file in languageConfigFiles:
			if languageName in file:
				#set the language of the ui
				self.language = languageName
				filePath = os.path.join(self.UILanguagePath,file)
				languageContent = readDataFromJsonFile(filePath)
				for varName,displayName in languageContent.items():
					if hasattr(self.affectedUI,varName):
						thisVar = getattr(self.affectedUI,varName)
						try:
							thisVar.setText(displayName)
						except:
							print displayName
							for list in displayName:
								position = list[0]
								name = list[1]
								thisVar.setTabText(position,name)
		self.refresh()
	def rebuildUI(self):
		self.affectedUI.buildUI()

class RenderAFeverMainUI(QtWidgets.QMainWindow):
	def __init__(self):
		self.parent = self.getMayaMainWindow()
		super(RenderAFeverMainUI,self).__init__(parent = self.parent)
		self.scriptPath = mc.internalVar(usd = 1 )
		self.UILanguagePath = os.path.join(self.scriptPath,r'RenderAFever\\UI\\languages')
		self.setWindowTitle('RenderAFever')
		#self.resize(mainUI_smallSize[0],mainUI_smallSize[1])
		self.storableUIs = []
		self.UIGroups = []

		self.buildUI()

		self.UIManager = RegisterUIManager(self)
		self.UIManager.start()
		self.setLanguageTotal(self.UIManager.language)

	
	def getMayaMainWindow(self):
		win = omui.MQtUtil_mainWindow()
		prt = wrapInstance(long(win),QtWidgets.QMainWindow)
		return prt
	
	def resetUI(self):
		#reset UI for all UIGroup
		for UIGroup in self.UIGroups:
			if  hasattr(UIGroup,'UIManager'):

				UIGroup.UIManager.restoreUIToJsonFile(self.UIManager.defaultPresetFilePath)

	def setLanguageTotal(self,languageName):
		self.UIManager.setLanguage(languageName)
		self.materialImporter.UIManager.setLanguage(languageName)
	def setModel(self):
		if self.chooseModelLabelCB.currentIndex() == 0:
			self.tabWidget01.setVisible(1)
			self.tabWidget02.setVisible(0)
			print 'material'
		elif self.chooseModelLabelCB.currentIndex() == 1:
			self.tabWidget01.setVisible(0)
			self.tabWidget02.setVisible(1)
			print 'render'

	def tabWidget01Changed(self):
		index = self.tabWidget01.currentIndex()
		name = self.tabWidget01.tabText(index)
		print name
		print 'this is current name'
		print ''
		if name == 'Material Converter':
			print 1
			firstTabName = self.tabWidget01.tabText(0)
			if firstTabName == 'Material Importer':
				self.blankWidget = QtWidgets.QWidget()
				self.tabWidget01.insertTab(0,self.blankWidget,'MI') 
				self.tabWidget01.removeTab(1)
			
					
			
		if name == 'MI':
			print '0'
			self.tabWidget01.insertTab(1,self.materialImporter,'Material Importer') 
			#self.tabWidget01.insertTab(0,self.materialImporter,'Material Importer') 
			#self.tabWidget01.removeTab(0)
			self.tabWidget01.setCurrentIndex(1)
			self.tabWidget01.removeTab(0)

			

	def buildUI(self):
		self.centralWidget = QtWidgets.QWidget(self)
		self.setCentralWidget(self.centralWidget)
		self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)
		#self.mainLayout.setSpacing(1)
		self.mainLayout.setContentsMargins(0,0,0,0)
		
		self.mainMenu = QtWidgets.QMenuBar()
		self.mainMenu_right = QtWidgets.QMenuBar()

		self.mainMenu.setStyleSheet(" QMenuBar{background-color : dark grey  ; border : 1px }");
		UIMenu = self.mainMenu.addMenu('UI')
		UIMenu.setMinimumWidth(90)
		resetAction = QtWidgets.QAction('reset',self)
		resetAction.triggered.connect(self.resetUI)
		UIMenu.addAction(resetAction)
		
		#resetAction.triggered.connect(partial(self.mainUIManager.restoreUIToJsonFile,defaultPresetFilePath))


		self.languageMenu = self.mainMenu.addMenu('Language')
		self.languageMenu.setMinimumWidth(180)
		self.languageConfigFiles = os.listdir(self.UILanguagePath)

		for file in self.languageConfigFiles:
			filePath = os.path.join(self.UILanguagePath,file)
			fileName = os.path.splitext(file)[0]
			thisAction = QtWidgets.QAction(fileName,self)
			thisAction.triggered.connect(partial(self.setLanguageTotal,fileName))
			self.languageMenu.addAction(thisAction)

		
		self.mainMenu.setCornerWidget(self.mainMenu_right, QtCore.Qt.TopRightCorner)
		self.mainMenu_right.addMenu('Help')
		

		self.mainLayout.addWidget(self.mainMenu)
				

		self.tabWidget01 = QtWidgets.QTabWidget()
		self.tabWidget02 = QtWidgets.QTabWidget()
		#self.tabWidget.setStyleSheet(" QTabWidget{background-color :  black  ; border : 10px };QTabBar{qproperty-drawBase: 0;}");

		#all ui goups here
		self.materialImporter = UI.materialImporter.MaterialImporterMainUI(self)#the material importer need to get the mainUI,to refresh the mainUI when some UI changed
		self.materialConverter = UI.materialConverter.MaterialConverterMainUI(self)
		self.materialPresets = QtWidgets.QWidget()
		self.lightManager = lightManager.LightManagerMainUI()
		self.miscTools = QtWidgets.QWidget()
		self.UIGroups = [self,self.materialImporter,self.materialConverter,self.materialPresets,self.lightManager,self.miscTools]


		self.chooseModelWidget = QtWidgets.QWidget()
		self.chooseModelGridLayout = QtWidgets.QGridLayout(self.chooseModelWidget)
		
		
		self.mainLayout.addWidget(self.chooseModelWidget)

		self.chooseModelLabel = QtWidgets.QLabel(' ChooseModel:    ')
		self.chooseModelGridLayout.addWidget(self.chooseModelLabel,0,0)
		#self.mainLayout.setAlignment(self.chooseModelLabel,QtCore.Qt.AlignLeft)
		self.chooseModelLabelCB = QtWidgets.QComboBox()
		self.chooseModelLabelCB.setMaximumWidth(200)

		self.chooseModelLabelCB.addItems(['Material','Render'])
		self.chooseModelLabelCB.currentIndexChanged.connect(self.setModel)
		self.storableUIs.append(['chooseModelLabelCB',self.chooseModelLabelCB])
		self.chooseModelGridLayout.addWidget(self.chooseModelLabelCB,0,1,1,5)


		self.tabWidget01.addTab(self.materialImporter,'Material Importer')
		self.tabWidget01.addTab(self.materialConverter,'Material Converter')
		self.tabWidget01.addTab(self.materialPresets,'Material Preset')
		self.tabWidget02.addTab(self.lightManager,'Light Manager')
		self.tabWidget02.addTab(self.miscTools,'MiscTools')

		self.tabWidget01.currentChanged.connect(self.tabWidget01Changed)

		self.storableUIs.append(['tabWidget01',self.tabWidget01])
		self.storableUIs.append(['tabWidget02',self.tabWidget02])
		self.mainLayout.addWidget(self.tabWidget01)
		self.mainLayout.addWidget(self.tabWidget02)
		self.setModel()


		

		self.versionInfo = QtWidgets.QLabel(version)
		self.mainLayout.addWidget(self.versionInfo)
		self.mainLayout.setAlignment(self.versionInfo,QtCore.Qt.AlignRight)



		self.mainLayout.addSpacing(10)


		

		





if __name__ == '__main__':
	ui = UI()

	ui.show()
