from Qt import QtWidgets, QtCore ,QtGui
import light.lightingLibrary as lightingLibrary
import UI.mainUI
import maya.cmds as mc

reload(lightingLibrary)

import pprint,os

class CollapsibleFrame(QtWidgets.QToolButton):
	def __init__(self,text = '',isCollapsed = False,toggleFunc = None):
		super (CollapsibleFrame,self).__init__()
		def __emptyFunc():
			pass

		self.isCollapsed = isCollapsed
		if toggleFunc is not None:
			self.toggleFunc = toggleFunc
		else:
			self.toggleFunc = __emptyFunc
			#self.toggleFunc = 'aaaa'


		self.buildButton(text)


	def buildButton(self,test):
		self.setText(test)
		self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.Maximum)
		self.setIconSize(QtCore.QSize(4, 4))
		self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

		self.setArrowType(QtCore.Qt.DownArrow)
		self.setStyleSheet("QToolButton{background-color: #555555;border-sytle :solid ;border-sytle : solid;}")
		self.clicked.connect(self.buttonClicked)
	

	def buttonClicked(self):
		if not self.isCollapsed:
			self.toggleFunc(0)
			self.setArrowType(QtCore.Qt.RightArrow)
		elif  self.isCollapsed:
			self.toggleFunc(300)
			self.setArrowType(QtCore.Qt.DownArrow)

		self.isCollapsed = not self.isCollapsed
class MyListWidget(QtWidgets.QListWidget):
	def __init(self):
		super(MyListWidget, self).__init__()
		self.itemClicked.connect(self.on_item_clicked)

	def mousePressEvent(self,event):
		
		#self.focusOutEvent() = lambda _:self.hide()
		print self
		self.clearSelection()

		self._mouse_button = event.button()
		super(MyListWidget, self).mousePressEvent(event)
	def on_item_clicked(self,item):
		print item.text(),self._mouse_button
class LightCatagoryUI():
	def __init__(self,parent = None,catagoryName = ''):
		#super(LightCatagoryUI, self).__init__()
		self.scriptPath = mc.internalVar(usd =1)
		self.parent = parent
		self.catagoryName = catagoryName
		self.niceName = self.catagoryName + 'Light'
		self.assetsPath = os.path.join(self.scriptPath,r'RenderAFever\data\\lightPresets') 
		self.defaultIconPath =  os.path.join(self.scriptPath,r'RenderAFever\data\lightPresets\_tmpkettle_05.png')  

		self.storableUIs = []
		self.buildUI()
		self.populate()


	def buildUI(self):
		self.lightsWidget = QtWidgets.QWidget()
		self.parent.addWidget(self.lightsWidget)
		lightsLayout = QtWidgets.QGridLayout(self.lightsWidget)
		#lightsLayout.setMargin(0)
		#lightsLayout.setSpacing(0)

		self.baseLightFrame = CollapsibleFrame(self.catagoryName,toggleFunc = lambda x : self.scrollArea.setMaximumHeight(x))
		lightsLayout.addWidget(self.baseLightFrame)

		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		lightsLayout.addWidget(self.scrollArea)


		self.groupWidget = QtWidgets.QWidget()

		self.groupLayout = QtWidgets.QVBoxLayout(self.groupWidget)

		iconSize = 120
		gap = 16
		self.listWidget = MyListWidget()
		self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
		self.listWidget.setIconSize(QtCore.QSize(iconSize,iconSize))
		self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
		self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.listWidget.setGridSize(QtCore.QSize(iconSize + gap,iconSize + gap))
		self.groupLayout.addWidget(self.listWidget)


		self.scrollArea.setWidget(self.groupWidget)


		#publish
		self.publishWidget = QtWidgets.QWidget()
		self.publishLayout =  QtWidgets.QHBoxLayout(self.publishWidget)
		self.groupLayout.addWidget(self.publishWidget)

		self.folderPathField = QtWidgets.QLineEdit()
		self.publishLayout.addWidget(self.folderPathField)
		self.storableUIs.append(['folderPathField',self.folderPathField])


		def openDirectory():
			returnDirectory = mc.fileDialog2(fm = 3,ff = None,ds = 1)
			if returnDirectory != None:
				returnDirectory = returnDirectory[0]
			else:
				returnDirectory = ''
			self.folderPathField.setText(returnDirectory)
		self.chooseFolderButton = QtWidgets.QPushButton('...')
		self.chooseFolderButton.setFixedWidth(25)
		self.chooseFolderButton.clicked.connect(openDirectory)

		


		self.publishLayout.addWidget(self.chooseFolderButton)

		self.publishButton = QtWidgets.QPushButton('PUBLISH')
		self.publishLayout.addWidget(self.publishButton)

	def populate(self):
		catagoryPath = os.path.join(self.assetsPath,self.catagoryName)
		lightNames = os.listdir(catagoryPath)
		for lightName in lightNames:
			light = lightingLibrary.LightingLibrary()
			#print baseLights
			#print baseLight + '    baseLight'
			light.readLightData(catagoryPath)
			#print os.path.join(baseLightsPath,baseLight)

			
			for lightType,data in light.items():
				iconPath = data['thumbnailFilePath']
				if lightType is not None:
					if iconPath is None:
						iconPath = self.defaultIconPath 
					icon = QtGui.QIcon(iconPath)
					item = QtWidgets.QListWidgetItem()
					item.setText(lightName)
					item.setData(QtCore.Qt.UserRole,data)
					item.setIcon(icon)
					lightFileName = data['lightName']
					lightFilePath = data['lightFilePath']
					item.setToolTip('lightFileName:  ' + lightName + '\n' + '\n' + 'lightFilePath:   ' + lightFilePath)
					self.listWidget.addItem(item)

class LightManagerMainUI(QtWidgets.QWidget):
	allListWidgets = []
	"""docstring for LightingLibraryUI"""
	def __init__(self):
		super(LightManagerMainUI, self).__init__()
		self.scriptPath = mc.internalVar(usd = 1)
		self.assetsPath = os.path.join(self.scriptPath,r'RenderAFever\data\lightPresets')  

		self.storableUIs = []
		self.buildUI()
		self.UIManager = UI.mainUI.RegisterUIManager(self)
		#self.childUIManagers = []
		#self.allListWidgets = []

	def buildUI(self):
		self.windowWidth = 1000

		layout = QtWidgets.QGridLayout(self)
		self.setWindowTitle('LightingLibrary')
		self.resize(self.windowWidth,600)
		#testWidget = QtWidgets.QWidget()

		lightCatagoriesScrollArea = QtWidgets.QScrollArea()
		lightCatagoriesScrollArea.setWidgetResizable(True)
		layout.addWidget(lightCatagoriesScrollArea,0,0)

		lightCatagoriesWidget = QtWidgets.QWidget()
		lightCatagoriesWidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Minimum)
		layout.addWidget(lightCatagoriesWidget)
		lightCatagoriesScrollArea.setWidget(lightCatagoriesWidget)

		catagoriesLayout = QtWidgets.QVBoxLayout(lightCatagoriesWidget)
		#catagoriesLayout.setMargin(0)
		catagoriesLayout.setSpacing(0)
		#catagoriesLayout.setAlignment(QtWidgets.AlignLeft)

		#catagories are folders!
		lightCatagories = os.listdir(self.assetsPath)
		lightCatagories = [lightCatagory for lightCatagory in lightCatagories\
		if not os.path.isfile(os.path.join(self.assetsPath,lightCatagory))]


		
		for lightCatagory in lightCatagories:
			lightCatagoryWidget = LightCatagoryUI(parent = catagoriesLayout,catagoryName = lightCatagory)
			self.allListWidgets.append(lightCatagoryWidget.listWidget)
			#self.childUIManagers.append(MainUI.RegisterUIManager(lightCatagoryWidget)) 

			#tempStorableUIs = map(lambda thisList: ['lightCatagoryWidget.' + thisList[0],thisList[1]],lightCatagoryWidget.storableUIs)

			#self.storableUIs += tempStorableUIs
		

		

		#self.baseLightFrame = CollapsibleFrame('baseLight',toggleFunc = lambda x : self.scrollArea.setMaximumHeight(x))

		referenceButton = QtWidgets.QPushButton('CreateReference')
		#referenceButton.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Maximum)
		referenceButton.setFixedHeight(38)
		referenceButton.setStyleSheet("QPushButton{color: rgb(255,124,28);font-size :16pt;font-weight:bold;font-family :Kalinga;}")
		referenceButton.clicked.connect(self.createReference)
		layout.addWidget(referenceButton,1,0)



	def createReference(self):
		#print self.allListWidgets
		#print 'allListWidgets'
		#print ''
		selectedItems = []
		for listWidget in self.allListWidgets:
			tempSelected = listWidget.selectedItems()
			if tempSelected is not None:
				for t in tempSelected:
					selectedItems.append(t)

		if selectedItems == []:
			return

		for selectedItem in selectedItems:
			name = selectedItem.text()

			selectedLightData = selectedItem.data(QtCore.Qt.UserRole)
			selectedLightFilePath = selectedLightData['lightFilePath']
			mc.file(selectedLightFilePath,reference =1,iv =1 )
			



