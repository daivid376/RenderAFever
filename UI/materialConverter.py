from Qt import QtCore,QtWidgets,QtGui
from functools import partial
import sys
import maya.cmds as mc
import UI.mainUI 

import os,json,inspect,gc


class MaterialConverterMainUI(QtWidgets.QWidget):
	def __init__(self,mainUI):
		super(MaterialConverterMainUI,self).__init__()
		self.scriptPath = mc.internalVar(usd = 1 )
		self.heightMapUIVisible = False
		self.path = os.path.join('RenderAFever','data','materialAttrs')
		self.iconPath = os.path.join(self.scriptPath,'RenderAFever','icon')
		self.materialAttrsConfigFilesPath = os.path.join(self.scriptPath,'RenderAFever','data','materialAttrs')
		self.textureTemplatesConfigFilesPath = os.path.join(self.scriptPath,'RenderAFever','data','textureTemplates')
		self.UILanguagePath = os.path.join(self.scriptPath,'RenderAFever','UI','languages')
		self.customTemplateUINamesPath =  os.path.join(self.scriptPath,'RenderAFever','UI','customTemplateUINames')
		self.customTemplateUINamesFilePath = os.path.join(self.customTemplateUINamesPath,'customTemplateUINames.json')
		self.customTemplateConfigFilePath = os.path.join(self.textureTemplatesConfigFilesPath,'__Custom__.json')

		self.supportedMaterials = [os.path.splitext( file)[0] for file in os.listdir(self.materialAttrsConfigFilesPath) if 'Default' not in file]
		self.supportedTemplates = [os.path.splitext( file)[0] for file in os.listdir(self.textureTemplatesConfigFilesPath) if 'Default' not in file]
		
		self.mainUI = mainUI
		
		self.buildUI()
		self.storableUIs = self.mainUI.storableUIs
		self.UIManager = UI.mainUI.RegisterUIManager(self)
		self.UIManager.start()
		self.convertButton.clicked.connect(self.materialConvert)
	
	def materialConvert(self):
		sourceMaterialType = self.convertFromCB.currentText()
		targetMaterialType = self.convertToCB.currentText()

		material.materialConverter.materialConvert(sourceMaterialType,targetMaterialType,'orig_use_maya_colorSpace','orig_use_maya_colorSpace',0)
	def getConvertToMaterial(self):
		currentConvertFromMaterial = self.convertFromCB.currentText()
		tempConvertToMaterialList = []
		for item in self.supportedMaterials:
			tempConvertToMaterialList.append(item)
		if currentConvertFromMaterial in tempConvertToMaterialList:
			tempConvertToMaterialList.remove(currentConvertFromMaterial)
		self.convertToCB.clear()
		self.convertToCB.addItems(tempConvertToMaterialList)


	def buildUI(self):
		self.mainLayout = QtWidgets.QGridLayout(self)
		#self.mainLayout.setVerticalSpacing(10)
		#self.mainLayout.setHorizontalSpacing(20)
		self.mainLayout.setColumnStretch(5, 1)

		self.convertFromLabel = QtWidgets.QLabel('From: ')
		self.mainLayout.addWidget(self.convertFromLabel)

		self.convertFromCB = QtWidgets.QComboBox()
		self.mainUI.storableUIs.append(['convertFromCB',self.convertFromCB])
		self.mainLayout.addWidget(self.convertFromCB)

		self.convertFromCB.addItems(self.supportedMaterials)
		self.convertFromCB.currentTextChanged.connect(self.getConvertToMaterial)


		self.convertToLabel = QtWidgets.QLabel('To: ')
		self.mainLayout.addWidget(self.convertToLabel)
		self.mainLayout.setAlignment(self.convertToLabel,QtCore.Qt.AlignRight)

		self.convertToCB = QtWidgets.QComboBox()
		#self.convertToCB.currentTextChanged.connect(self.getConvertToMaterial)
		self.mainUI.storableUIs.append(['convertToCB',self.convertToCB])
		self.mainLayout.addWidget(self.convertToCB)

		self.convertToCB.addItems(self.supportedMaterials)
		
		#innerSpace = QtWidgets.QSpacerItem(10,50,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
		#self.mainLayout.addItem(innerSpace,1,0,1,4,QtCore.Qt.AlignTop)

		self.convertButton = QtWidgets.QPushButton('Convert')
		self.mainLayout.addWidget(self.convertButton,2,1,1,3)
		self.convertButton.setMinimumHeight(60)

		#space = QtWidgets.QSpacerItem(10,10,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
		#self.mainLayout.addItem(space,23,0,1,4,QtCore.Qt.AlignTop)