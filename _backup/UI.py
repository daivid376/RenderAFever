from Qt import QtCore,QtGui,QtWidgets
from dataClass import Data
import maya.cmds as mc
import os,json,inspect,gc
from functools import partial
#import qApp


storableUIs = {}

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
		self.UILanguagePath = os.path.join(self.scriptPath,r'DW_MaterialManager\\UI\\languages')
		self.presetFilePath = os.path.join(self.scriptPath,r'DW_RenderExtra_presets\\RenderExtra_lastUI_preset.json')
		self.defaultPresetFilePath = os.path.join(self.scriptPath,r'DW_RenderExtra_presets\\RenderExtra_lastUI_preset.json')
		self.registar = {}
		self.UIName_UIInstance_dict = {}
		self.UIClass_functions_dict = {'QComboBox':['currentIndex','currentIndexChanged','setCurrentIndex'],
		'QCheckBox':['isChecked','stateChanged','setChecked'],
		'QRadioButton':['isChecked','toggled','setChecked'],
		'QLineEdit':['text','textChanged','setText'],
		'QTabWidget':['currentIndex','currentChanged','setCurrentIndex']}

		self.affectedUI = affectedUI

		self.execute()

	def execute(self):
		if hasattr(self.affectedUI,'storableUIs'):
			self.storableUIs = self.affectedUI.storableUIs
		else:
			self.storableUIs = []
		for storableUI in self.storableUIs:
			UIName = storableUI[0]
			UIInstance = storableUI[1]
			self.UIName_UIInstance_dict[UIName] = UIInstance
		self.restoreUI()
		self.UIChangeConnectToRefresh()
		self.register()

	def register(self):
		for UIName,thisInstance in self.UIName_UIInstance_dict.items():
			if type(thisInstance).__name__ in self.UIClass_functions_dict:
				UIClass = type(thisInstance).__name__
				thisDict = {}
				getFunc = getattr(thisInstance,self.UIClass_functions_dict[UIClass][0])
				value = getFunc()

				self.registar[UIName] = value
				self.UIName_UIInstance_dict[UIName] =thisInstance

	def getValue(self,UIInstance):
		getFunc = getattr(UIInstance,self.UIClass_functions_dict[UIClass][0])
		value = getFunc()
		return value
		
	def UIChangeConnectToRefresh(self):
		for UIName,UIInstance in self.UIName_UIInstance_dict.items():
			UIClass = type(UIInstance).__name__
			changeFunc = getattr(UIInstance,self.UIClass_functions_dict[UIClass][1])
			changeFunc.connect(self.refresh)

	def refresh(self):
		print 'refresh'

		for UIName,UIInstance in self.UIName_UIInstance_dict.items():
			self.register()
		self.storeUIData()
	def storeUIData(self):
		allRegistar = {}
		allUIManagers = [obj for obj in gc.get_objects() if isinstance(obj,RegisterUIManager)]
		for UIManager in allUIManagers:

			allRegistar.update(UIManager.registar)
		saveDataToJsonFile(allRegistar,self.presetFilePath)
	def restoreUI(self):
		UI_name_value_dict = readDataFromJsonFile(self.presetFilePath)
		for UIName in self.UIName_UIInstance_dict:
			UIInstance = getattr(self.affectedUI,UIName)
			UIClass = type(UIInstance).__name__
			if UIName in UI_name_value_dict.keys():
				value = UI_name_value_dict[UIName]
				setFunc = getattr(UIInstance,self.UIClass_functions_dict[UIClass][2])
				setFunc(value)

	def readUIData(self):
		UI_name_value_dict = readDataFromJsonFile(self.presetFilePath)
		return UI_name_value_dict

	def setLanguage(self,languageName):
		print languageName
		languageConfigFiles = os.listdir( self.UILanguagePath)
		for file in languageConfigFiles:
			if languageName in file:
				filePath = os.path.join(self.UILanguagePath,file)
				languageContent = readDataFromJsonFile(filePath)
				for varName,displayName in languageContent.items():
					if hasattr(self.affectedUI,varName):
						thisVar = getattr(self.affectedUI,varName)
						try:
							thisVar.setText(displayName)
						except:
							print displayName
							thisVar.setTabText(eval(displayName))
		#self.rebuildUI()
	def rebuildUI(self):
		self.affectedUI.buildUI()



class MaterialImporterUI(QtWidgets.QWidget):
	def __init__(self):
		super(MaterialImporterUI,self).__init__()
		self.scriptPath = mc.internalVar(usd = 1 )
		self.heightMapUIVisible = False
		self.path = r'\\DW_MaterialManager\\data\\materialAttrs'
		self.materialAttrsConfigFilesPath = os.path.join(self.scriptPath,r'DW_MaterialManager\\data\\materialAttrs')
		self.textureTemplatesConfigFilesPath = os.path.join(self.scriptPath,r'DW_MaterialManager\\data\\textureTemplates')
		self.UILanguagePath = os.path.join(self.scriptPath,r'DW_MaterialManager\\UI\\languages')
		self.supportedMaterials = [os.path.splitext( file)[0] for file in os.listdir(self.materialAttrsConfigFilesPath) if 'Default' not in file]
		self.supportedTemplates = [os.path.splitext( file)[0] for file in os.listdir(self.textureTemplatesConfigFilesPath) if 'Default' not in file]
		
		self.storableUIs = []
		self.buildUI()
		self.UIManager = RegisterUIManager(self)

		
	def buildUI(self):
		self.mainLayout = QtWidgets.QGridLayout(self)
		self.mainLayout.setVerticalSpacing(10)
		self.mainLayout.setHorizontalSpacing(10)
		self.mainLayout.setColumnStretch(5, 1)
		#button = QtWidgets.QPushButton()
		#self.mainLayout.addWidget(button)

		self.createMaterialLabel = QtWidgets.QLabel('CreateMaterial:   ')
		self.mainLayout.addWidget(self.createMaterialLabel,0,0)
		self.mainLayout.setAlignment(self.createMaterialLabel,QtCore.Qt.AlignRight)

		self.createMaterialLabelCB = QtWidgets.QComboBox()
		self.createMaterialLabelCB.setMaximumWidth(250)
		
		self.createMaterialLabelCB.addItems(self.supportedMaterials)


		self.mainLayout.addWidget(self.createMaterialLabelCB,0,1,1,4)
		self.storableUIs.append(['createMaterialLabelCB',self.createMaterialLabelCB])
		
		#separator = QtWidgets.QFrame()
		#separator.setFrameShape(QtWidgets.QFrame.HLine)
		#self.mainLayout.addWidget(separator,0,2,1,1)

		self.useTemplateLabel = QtWidgets.QLabel('UseTemplate:   ')
		self.mainLayout.addWidget(self.useTemplateLabel,1,0,1,1)
		self.mainLayout.setAlignment(self.useTemplateLabel,QtCore.Qt.AlignRight)

		self.useTemplateCB = QtWidgets.QComboBox()
		self.useTemplateCB.setMaximumWidth(290)
		for supportedTemplate in self.supportedTemplates:
			self.useTemplateCB.addItem(supportedTemplate)

		self.mainLayout.addWidget(self.useTemplateCB,1,1,1,2)
		self.storableUIs.append(['useTemplateCB',self.useTemplateCB])


		
		space01 = QtWidgets.QSpacerItem(10,50,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
		self.mainLayout.addItem(space01,2,0,1,4,QtCore.Qt.AlignTop)


		self.udimCheckBox = QtWidgets.QCheckBox('udim textures')
		#self.udimCheckBox.stateChanged.connect(self.test)
		self.mainLayout.addWidget(self.udimCheckBox,3,1)
		self.storableUIs.append(['udimCheckBox',self.udimCheckBox])

		self.usingMayaColorManagermentCheckBox = QtWidgets.QCheckBox('usingMayaColorManagerment')
		self.mainLayout.addWidget(self.usingMayaColorManagermentCheckBox,4,1)
		self.storableUIs.append(['usingMayaColorManagermentCheckBox',self.usingMayaColorManagermentCheckBox])


		buttonGrp = QtWidgets.QWidget()

		self.openglRadioButton = QtWidgets.QRadioButton('opengl normal')
		self.openglRadioButton.setChecked(1)
		self.mainLayout.addWidget(self.openglRadioButton,5,1)
		self.storableUIs.append(['openglRadioButton',self.openglRadioButton])
		#buttonGrp.addButton(openglRadioButton)

		self.directXRadioButton = QtWidgets.QRadioButton('directX')
		self.mainLayout.addWidget(self.directXRadioButton,5,1,QtCore.Qt.AlignCenter)
		self.storableUIs.append(['directXRadioButton',self.directXRadioButton])
		#buttonGrp.addButton(directXRadioButton)

		separator01 = QtWidgets.QFrame()
		separator01.setFrameShape(QtWidgets.QFrame.HLine)
		self.mainLayout.addWidget(separator01,6,0,1,4)

		self.heightMapCheckBox = QtWidgets.QCheckBox()
		self.heightMapCheckBox.setText('heightMapAsDisplacement')
		self.storableUIs.append(['heightMapCheckBox',self.heightMapCheckBox])
		

		self.mainLayout.addWidget(self.heightMapCheckBox,7,1)



		self.heightMapWidget = QtWidgets.QWidget()
		heightMapLayout = QtWidgets.QGridLayout(self.heightMapWidget)

		#space03 = QtWidgets.QSpacerItem(50,50)
		#heightMapLayout.addItem(space03,0,0)

		zeroHeightLabel = QtWidgets.QLabel('zeroHeight')
		heightMapLayout.addWidget(zeroHeightLabel,0,1,QtCore.Qt.AlignRight)

		self.zeroHeightLineEdit = QtWidgets.QLineEdit('0.5')
		self.zeroHeightLineEdit.setMaximumWidth(120)
		heightMapLayout.addWidget(self.zeroHeightLineEdit,0,2)
		self.storableUIs.append(['zeroHeightLineEdit',self.zeroHeightLineEdit])

		space04 = QtWidgets.QSpacerItem(85,50)
		heightMapLayout.addItem(space04,0,3)

		heightDepthLabel = QtWidgets.QLabel('heightDepth')
		heightMapLayout.addWidget(heightDepthLabel,1,1,QtCore.Qt.AlignRight)

		self.heightDepthLineEdit = QtWidgets.QLineEdit('1')
		self.heightDepthLineEdit.setMaximumWidth(120)
		heightMapLayout.addWidget(self.heightDepthLineEdit,1,2)
		self.storableUIs.append(['heightDepthLineEdit',self.heightDepthLineEdit])
		

		self.intHeightRadioButton = QtWidgets.QRadioButton('8bit height')
		self.intHeightRadioButton.setChecked(1)
		heightMapLayout.addWidget(self.intHeightRadioButton,2,1,QtCore.Qt.AlignRight)
		self.storableUIs.append(['intHeightRadioButton',self.intHeightRadioButton])

		self.floatHeightRadioButton = QtWidgets.QRadioButton('32bit height')
		heightMapLayout.addWidget(self.floatHeightRadioButton,2,2,QtCore.Qt.AlignCenter)
		self.storableUIs.append(['floatHeightRadioButton',self.floatHeightRadioButton])


		
		self.mainLayout.addWidget(self.heightMapWidget,8,0,1,2)
		
		self.heightMapWidget.setVisible(0)




		separator02 = QtWidgets.QFrame()
		separator02.setFrameShape(QtWidgets.QFrame.HLine)
		self.mainLayout.addWidget(separator02,9,0,1,4)
		
		texturePathLabel = QtWidgets.QLabel('TexturePath ')
		self.mainLayout.addWidget(texturePathLabel,10,0)
		self.mainLayout.setAlignment(texturePathLabel,QtCore.Qt.AlignRight)

		self.texturePathLineEdit = QtWidgets.QLineEdit()
		self.texturePathLineEdit.setMinimumWidth(300)
		self.mainLayout.addWidget(self.texturePathLineEdit,10,1)
		self.storableUIs.append(['texturePathLineEdit',self.texturePathLineEdit])


		openDirectoryButton = QtWidgets.QPushButton('...')
		openDirectoryButton.setMaximumWidth(50)
		self.mainLayout.addWidget(openDirectoryButton,10,2)

		materialNameLabel = QtWidgets.QLabel('MaterialName ')
		self.mainLayout.addWidget(materialNameLabel,11,0)
		self.mainLayout.setAlignment(materialNameLabel,QtCore.Qt.AlignRight)

		self.materialNameLineEdit = QtWidgets.QLineEdit()
		self.materialNameLineEdit.setMinimumWidth(300)
		self.mainLayout.addWidget(self.materialNameLineEdit,11,1)
		self.storableUIs.append(['materialNameLineEdit',self.materialNameLineEdit])

		import_assignButton = QtWidgets.QPushButton('Import/Assign')
		import_assignButton.setMinimumHeight(60)
		self.mainLayout.addWidget(import_assignButton,12,1)
		

		space = QtWidgets.QSpacerItem(10,50,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
		self.mainLayout.addItem(space,20,0,1,4,QtCore.Qt.AlignTop)


		'''the function part'''
		self.heightMapCheckBox.toggled.connect(self.show_hide_HeightMapUI)
		
	def show_hide_HeightMapUI(self):
		 
		self.heightMapWidget.setVisible(not self.heightMapUIVisible)
		self.heightMapUIVisible = not self.heightMapUIVisible
	

		#getattr(self,'')
		

class RenderExpertMainUI(QtWidgets.QDialog):
	def __init__(self):
		super(RenderExpertMainUI,self).__init__()
		self.scriptPath = mc.internalVar(usd = 1 )
		self.UILanguagePath = os.path.join(self.scriptPath,r'DW_MaterialManager\\UI\\languages')
		self.setWindowTitle('DW_RenderExpert')
		self.resize(600,500)
		self.storableUIs = []
		
		self.buildUI()
		self.mainUIManager = RegisterUIManager(self)



	def setLanguageTotal(self,languageName):
		self.mainUIManager.setLanguage(languageName)
		self.materialImporter.UIManager.setLanguage(languageName)
	def buildUI(self):
		self.mainLayout = QtWidgets.QVBoxLayout(self)
		self.mainLayout.setSpacing(1)
		#self.mainLayout.setMargin(1)
		self.mainLayout.setContentsMargins(0,0,0,0)
		
		#self.mainLayout.addWidget(widget)
		#button = QtWidgets.QPushButton('test')
		#self.mainLayout.addWidget(button)
		self.mainMenu = QtWidgets.QMenuBar()
		self.mainMenu_right = QtWidgets.QMenuBar()

		self.mainMenu.setStyleSheet(" QMenuBar{background-color : dark grey  ; border : 1px }");
		UIMenu = self.mainMenu.addMenu('UI')
		UIMenu.setMinimumWidth(90)
		UIMenu.addAction('reset')


		self.languageMenu = self.mainMenu.addMenu('Language')
		self.languageMenu.setMinimumWidth(180)
		self.languageConfigFiles = os.listdir(self.UILanguagePath)
		for file in self.languageConfigFiles:
			filePath = os.path.join(self.UILanguagePath,file)
			fileName = os.path.splitext(file)[0]
			thisAction = QtWidgets.QAction(fileName,self)
			print fileName,'    fileName'
			thisAction.triggered.connect(partial(self.setLanguageTotal,fileName))
			self.languageMenu.addAction(thisAction)


		self.mainMenu.setCornerWidget(self.mainMenu_right, QtCore.Qt.TopRightCorner)
		self.mainMenu_right.addMenu('Help')
		
		self.mainLayout.addWidget(self.mainMenu)





		self.tabWidget = QtWidgets.QTabWidget()

		self.materialImporter = MaterialImporterUI()
		self.materialConverter = QtWidgets.QWidget()
		self.materialPresets = QtWidgets.QWidget()
		self.lightManager = QtWidgets.QWidget()
		self.miscTools = QtWidgets.QWidget()

		
		
		self.tabWidget.addTab(self.materialImporter,'Material Importer')
		self.tabWidget.addTab(self.materialConverter,'Material Converter')
		self.tabWidget.addTab(self.materialPresets,'Material Preset')
		self.tabWidget.addTab(self.lightManager,'Light Manager')
		self.tabWidget.addTab(self.miscTools,'MiscTools')

		self.storableUIs.append(['tabWidget',self.tabWidget])


		self.mainLayout.addWidget(self.tabWidget)

		





if __name__ == '__main__':
	ui = UI()

	ui.show()
