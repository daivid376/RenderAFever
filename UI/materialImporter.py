from Qt import QtCore,QtWidgets
from functools import partial
import sys
import maya.cmds as mc
import UI.mainUI 
import material.materialImporter
reload(material.materialImporter)
import os,json,inspect,gc
#import tkFileDialog

def readDataFromJsonFile(jsonFile):
	with open(jsonFile) as jsFile:
		jsonData = json.load(jsFile)
	return jsonData

def saveDataToJsonFile(content,jsonFile):
	with open(jsonFile, "w") as fp:
		json.dump(content, fp,indent = 4) 

class MaterialImporterMainUI(QtWidgets.QWidget):
	def __init__(self,mainUI):
		super(MaterialImporterMainUI,self).__init__()
		self.scriptPath = mc.internalVar(usd = 1 )
		self.heightMapUIVisible = False
		self.path = os.path.join('RenderAFever','data','materialAttrs')
		self.materialAttrsConfigFilesPath = os.path.join(self.scriptPath,'RenderAFever','data','materialAttrs')
		self.textureTemplatesConfigFilesPath = os.path.join(self.scriptPath,'RenderAFever','data','textureTemplates')
		self.UILanguagePath = os.path.join(self.scriptPath,'RenderAFever','UI','languages')
		self.customTemplateUINamesPath =  os.path.join(self.scriptPath,'RenderAFever','UI','customTemplateUINames')
		self.customTemplateUINamesFilePath = os.path.join(self.customTemplateUINamesPath,'customTemplateUINames.json')
		self.customTemplateConfigFilePath = os.path.join(self.textureTemplatesConfigFilesPath,'__Custom__.json')

		self.supportedMaterials = [os.path.splitext( file)[0] for file in os.listdir(self.materialAttrsConfigFilesPath) if 'Default' not in file]
		self.supportedTemplates = [os.path.splitext( file)[0] for file in os.listdir(self.textureTemplatesConfigFilesPath) if 'Default' not in file]
		
		self.mainUI = mainUI
		self.storableUIs = []
		self.buildUI()
		self.UIManager = UI.mainUI.RegisterUIManager(self)
		self.import_assignButton.clicked.connect(self.importMaterialFunctions)

	def importMaterialFunctions(self):
		materialImporter = material.materialImporter.MaterialImporter()
		materialImporter.textureTemplateUsing = self.useTemplateCB.currentText()
		materialImporter.userDefinedPath = self.texturePathLineEdit.text()
		materialImporter.materialName = self.materialNameLineEdit.text()
		materialImporter.targetMaterialType = self.createMaterialLabelCB.currentText()
		materialImporter.usingMayaColorManagement = self.usingMayaColorManagermentCheckBox.isChecked()
		materialImporter.isUdim = self.udimCheckBox.isChecked()
		#materialImporter.dataDict = None

		materialImporter.openGLNormal = self.openglRadioButton.isChecked()
		materialImporter.heightMapAsDisplacement = self.heightMapCheckBox.isChecked()
		materialImporter.heightMap_8bit = self.intHeightRadioButton.isChecked()
		#materialImporter.affectColorSwitch = False
		materialImporter.zeroHeight = self.zeroHeightLineEdit.text()
		materialImporter.heightDepth = self.heightDepthLineEdit.text()

		materialImporter.import_replaceMaterialsByName()

	def loadTemplate(self):
		#root = Tkinter.TK()
		fileFilter = '.json'
		startingDirectory = self.textureTemplatesConfigFilesPath
		filePath = mc.fileDialog2(fm =1 ,dialogStyle = 2,dir = startingDirectory)
		if isinstance(filePath,list):
			filePath = filePath[0]
		if filePath is not None:
			loadedData = readDataFromJsonFile(filePath)
			basicData = readDataFromJsonFile(self.customTemplateUINamesFilePath)
			for metaAttr in basicData:
				UIName = basicData[metaAttr][0]
				if hasattr(self,UIName + 'LineEdit'):
					thisUI = getattr(self,UIName+ 'LineEdit')
					thisValue = loadedData[metaAttr]
					if thisValue == 'none':
						thisValue = ''
					thisUI.setText(thisValue)

				else:
					print 'something about custom template UI goes wrong'

	def saveTemplate(self):
		startingDirectory = self.textureTemplatesConfigFilesPath
		filePath = mc.fileDialog2(fm =0 ,dialogStyle = 2,okc = 'save',dir = startingDirectory,caption = 'save',fileFilter = '*.json')
		if filePath is not None:
			if isinstance(filePath,list):
				filePath = filePath[0]
			print filePath
			self.saveCustomTemplateToFile(filePath)
			print 'yes'
		
	def saveCustomTemplateToFile(self,filePath = None,*argus):
		data = readDataFromJsonFile(self.customTemplateUINamesFilePath)
		dataTobeSaved = {}
		for metaAttr in data:
			UIName = data[metaAttr][0]
			if hasattr(self,UIName + 'LineEdit'):
				thisUI = getattr(self,UIName+ 'LineEdit')
				userDefinedName = thisUI.text()
				dataTobeSaved[metaAttr] = userDefinedName
			else:
				print 'something about custom template UI goes wrong'
		print dataTobeSaved
		if filePath is not None:
			saveDataToJsonFile(dataTobeSaved,filePath)

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

		self.useTemplateCB.currentIndexChanged.connect(self.useTemplateCBChanged)

		self.mainLayout.addWidget(self.useTemplateCB,1,1,1,2)
		self.storableUIs.append(['useTemplateCB',self.useTemplateCB])





		#customTemplateWidget
		

		self.customTemplateWidget = QtWidgets.QWidget()
		self.customTemplateLayout = QtWidgets.QGridLayout(self.customTemplateWidget)

		customTemplateSeparatorStart = QtWidgets.QFrame()
		customTemplateSeparatorStart.setFrameShape(QtWidgets.QFrame.HLine)
		self.customTemplateLayout.addWidget(customTemplateSeparatorStart,1,0,1,4)
		def __customAttrUI__(attrName,defaultValue,layout,row):
			thisLabel = QtWidgets.QLabel(attrName)
			layout.addWidget(thisLabel,row,1,QtCore.Qt.AlignRight)
			varName = attrName + 'LineEdit'
			print varName
			vars(self)[varName] = QtWidgets.QLineEdit(defaultValue)
			vars(self)[varName].setMaximumWidth(335)
			vars(self)[varName].textChanged.connect(partial(self.saveCustomTemplateToFile,self.customTemplateConfigFilePath))
			layout.addWidget(vars(self)[varName],row,2,1,3)
			self.storableUIs.append([varName,vars(self)[varName]])

		self.customAttrUIData = readDataFromJsonFile(self.customTemplateUINamesFilePath)

		for metaAttr in self.customAttrUIData:
			data = self.customAttrUIData[metaAttr]
			__customAttrUI__(data[0],data[1],self.customTemplateLayout,data[2])

		self.loadTemplateButton = QtWidgets.QPushButton("LoadTemplate")
		self.loadTemplateButton.clicked.connect(self.loadTemplate)
		self.customTemplateLayout.addWidget(self.loadTemplateButton,11,2)

		self.saveTemplateButton = QtWidgets.QPushButton('SaveTemplate')
		self.saveTemplateButton.clicked.connect(self.saveTemplate)
		self.customTemplateLayout.addWidget(self.saveTemplateButton,11,3)


		self.customTemplateWidget.setVisible(0)
		self.mainLayout.addWidget(self.customTemplateWidget,3,0,1,2)


		self.customTemplateSeparatorEnd = QtWidgets.QFrame()
		self.customTemplateSeparatorEnd.setFrameShape(QtWidgets.QFrame.HLine)
		self.customTemplateLayout.addWidget(self.customTemplateSeparatorEnd,12,0,1,4)
		#self.useTemplateCBChanged()
		






		space01 = QtWidgets.QSpacerItem(10,50,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
		self.mainLayout.addItem(space01,5,0,1,4,QtCore.Qt.AlignTop)


		self.udimCheckBox = QtWidgets.QCheckBox('udim textures')
		#self.udimCheckBox.stateChanged.connect(self.test)
		self.mainLayout.addWidget(self.udimCheckBox,6,1)
		self.storableUIs.append(['udimCheckBox',self.udimCheckBox])

		self.usingMayaColorManagermentCheckBox = QtWidgets.QCheckBox('usingMayaColorManagerment')
		self.mainLayout.addWidget(self.usingMayaColorManagermentCheckBox,7,1)
		self.storableUIs.append(['usingMayaColorManagermentCheckBox',self.usingMayaColorManagermentCheckBox])


		buttonGrp = QtWidgets.QWidget()

		self.openglRadioButton = QtWidgets.QRadioButton('opengl normal')
		self.openglRadioButton.setChecked(1)
		self.mainLayout.addWidget(self.openglRadioButton,8,1)
		self.storableUIs.append(['openglRadioButton',self.openglRadioButton])
		#buttonGrp.addButton(openglRadioButton)

		self.directXRadioButton = QtWidgets.QRadioButton('directX')
		self.mainLayout.addWidget(self.directXRadioButton,8,1,QtCore.Qt.AlignCenter)
		self.storableUIs.append(['directXRadioButton',self.directXRadioButton])
		#buttonGrp.addButton(directXRadioButton)

		separator01 = QtWidgets.QFrame()
		separator01.setFrameShape(QtWidgets.QFrame.HLine)
		self.mainLayout.addWidget(separator01,9,0,1,4)

		self.heightMapCheckBox = QtWidgets.QCheckBox()
		self.heightMapCheckBox.setText('heightMapAsDisplacement')
		self.storableUIs.append(['heightMapCheckBox',self.heightMapCheckBox])
		

		self.mainLayout.addWidget(self.heightMapCheckBox,10,1)





		#height map widget 
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


		
		self.mainLayout.addWidget(self.heightMapWidget,11,0,1,2)
		
		self.heightMapWidget.setVisible(0)




		separator02 = QtWidgets.QFrame()
		separator02.setFrameShape(QtWidgets.QFrame.HLine)
		self.mainLayout.addWidget(separator02,12,0,1,4)
		
		texturePathLabel = QtWidgets.QLabel('TexturePath ')
		self.mainLayout.addWidget(texturePathLabel,13,0)
		self.mainLayout.setAlignment(texturePathLabel,QtCore.Qt.AlignRight)

		self.texturePathLineEdit = QtWidgets.QLineEdit()
		self.texturePathLineEdit.setMinimumWidth(300)
		self.mainLayout.addWidget(self.texturePathLineEdit,13,1)
		self.storableUIs.append(['texturePathLineEdit',self.texturePathLineEdit])


		openDirectoryButton = QtWidgets.QPushButton('...')
		openDirectoryButton.setMaximumWidth(50)
		self.mainLayout.addWidget(openDirectoryButton,13,2)

		materialNameLabel = QtWidgets.QLabel('MaterialName ')
		self.mainLayout.addWidget(materialNameLabel,14,0)
		self.mainLayout.setAlignment(materialNameLabel,QtCore.Qt.AlignRight)

		self.materialNameLineEdit = QtWidgets.QLineEdit()
		self.materialNameLineEdit.setMinimumWidth(300)
		self.mainLayout.addWidget(self.materialNameLineEdit,14,1)
		self.storableUIs.append(['materialNameLineEdit',self.materialNameLineEdit])

		self.import_assignButton = QtWidgets.QPushButton('Import/Assign')
		self.import_assignButton.setMinimumHeight(60)
		self.mainLayout.addWidget(self.import_assignButton,15,1)
		

		space = QtWidgets.QSpacerItem(10,50,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
		self.mainLayout.addItem(space,23,0,1,4,QtCore.Qt.AlignTop)


		'''the function part'''
		self.heightMapCheckBox.toggled.connect(self.show_hide_HeightMapUI)
		
	def show_hide_HeightMapUI(self):
		 
		self.heightMapWidget.setVisible(not self.heightMapUIVisible)
		self.heightMapUIVisible = not self.heightMapUIVisible
	
	def useTemplateCBChanged(self):
		if self.useTemplateCB.currentText() == '__Custom__':
			self.customTemplateWidget.setVisible(1)
			if hasattr(self.mainUI,'UIManager'):
				self.mainUI.UIManager.refresh()
		else:
			self.customTemplateWidget.setVisible(0)
			if hasattr(self.mainUI,'UIManager'):
				self.mainUI.UIManager.refresh()
			