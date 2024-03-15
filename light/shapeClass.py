import maya.cmds as mc

class AbstractAttrs():
	def getData(jsonFile,filePath):
	    def __readJsonFile(jsonFile):
	        with open(jsonFile) as jsFile:
	            jsonData = json.load(jsFile)
	        return jsonData
	    dataDict = {}

	    filePath = filePath.replace(r'/','\\')
	    if filePath not in sys.path:
	        sys.path.insert(0,filePath)

	    for jsonFile in jsonFilesName:
	        data = __readJsonFile(DW_MaterialManagerPath + '\\' + jsonFile +'.json')
	        dataDict[jsonFile] = data

        self.dataDict = dataDict
	    return dataDict
	def convertData():
		pass
	def applyData():
		pass
class Attr(object):
        self.attrName = str(attrName)
        self.operater = operater
        self.value = None
        self.inputNode = None
        self.inputAttr = None
        self.superNode = None
        self.textureFileNode = None
    def __str__(self):
        return self.attrName
    def __add__(self,other):
        return self.attrName + other
    def __radd__ (self,other):
        return other+ self.attrName
    def getAttrFrom(self,superNode):
        self.superNode = superNode
        # if the attr is only for outpass data, this attr should not get data
        try:
            if self.attrName != 'outOnly':
                inputNode = mc.listConnections(superNode + '.' + self.attrName)
                inputAttr = mc.listConnections(superNode + '.' + self.attrName,p = 1)

                if inputNode is None:
                    self.value = pm.getAttr(superNode + '.' + self.attrName)
                else:
                    #maybe wrong here, one node can connect multi nodes
                    self.inputNode = inputNode[0]
                    self.inputAttr = inputAttr[0]
        except:
            pass

    def numberConvert(self,targetAttr):
        if (self.operater == 'reverse' and targetAttr.operater != 'reverse') or (self.operater != 'reverse' and targetAttr.operater == 'reverse'):
            self.value = 1 - self.value
        
        if self.operater == 'vector3ToScalar' and targetAttr.operater != 'vector3ToScalar':
            self.value = (self.value[0] + self.value[1] + self.value[2])/3.0
        if targetAttr.operater == 'vector3ToScalar' and self.operater != 'vector3ToScalar':
            self.value = (self.value,self.value,self.value)
        
        # boolize the value 0 to False,every other number to True
        if self.operater =='boolize' or self.operater =='ignoreTrueBoolize':
            if self.value != 0:
                self.value = 1
        if  'boolize_onlyTrue' in self.operater:
            trueValue = int(self.operater[-1])
            if self.value == trueValue:
                self.value = 1
            else:
                self.value = 0

        if self.operater[:7] =='outOnly':
            thisOutValue = self.operater[8:]
            self.value = int(thisOutValue)
        if 'boolize_default' in self.operater :
            defaultValue = int(self.operater[15:])

            if self.value != 0 and self.value != 1 and self.value != defaultValue:
                self.value = defaultValue

        if self.operater == 'getVrayNormalType':
            __getVrayNormalType()
        #for the arnold enableDisplacement and displacement scale both controlled by aiDispHeight
        if targetAttr.operater == 'F0_IOR':
            #keep divide zero safety
            if self.value == 1:
                self.value = 0.99
            self.value = (1 + math.sqrt(self.value))/ (1 - math.sqrt(self.value))
            #for vray ,the ior's max value is 100
            if self.value >100:
                self.value = 100
        if targetAttr.operater == 'IOR_F0':
            self.value = ((self.value -1)/(self.value + 1))**2
        if targetAttr.operater == 'Metal_F0':
            self.value = 0.96*self.value + 0.04
        if targetAttr.operater == 'DiffuseColor_ReflectionColor':

            [(1 - self.primaryMetalness) + colorChannel * self.primaryMetalness for colorChannel in self.value]
        # for some attr ,will be set two times,if false ,set to false 
        #if true don't touch it ,use the previous attr
        if targetAttr.operater == 'ignoreTrueBoolize':

            if self.value == 1:
                self.value = None
        if  'boolize_onlyTrue' in targetAttr.operater:
            trueValue = int(targetAttr.operater[-1])
            if self.value  == 1:
                self.value = trueValue
            else:
                self.value = 0
        if self.operater[0] == '{':
            thisDict = eval(self.operater)
            targetDict = eval(targetAttr.operater)
            targetDictReversed = {v:k for k,v in targetDict.items()}
            #if it is a translating attr, get the translated value
            if self.value in thisDict.keys():
                self.value = thisDict[self.value]
                self.value = targetDictReversed[self.value]
            #if it is not a translating attr, set the attr to default to translate
            else:
                thisDictReversed = {v:k for k,v in thisDict.items()}
                for key in thisDictReversed:
                    if 'default' in key:
                        self.value = thisDictReversed[key]
        
        if 'outOnly'in targetAttr.operater or 'none' == targetAttr.operater:
            'not using this ??????????????????????????'
            self.value = None
        if self.operater == 'none' :
            self.value = None

        if (self.operater == '1/x' and targetAttr.operater != '1/x') or (self.operater != '1/x' and targetAttr.operater == '1/x'):
            self.value = 1 / self.value
  
    #def __customConvert(self):

    def convertTo(self,targetAttr):
  
        #for the rs normal node , its bumpType cant get from specific obj
        #give it a name called outOnly , and the operater is outOnly_ with a number
        if self.value is None and 'outOnly_' in self.operater:
            self.numberConvert(targetAttr)
        elif self.inputNode is not None or self.attrName == 'tex0':
            self.nodeConvert(targetAttr)
        self.attrName = targetAttr.attrName


class Shape():
	"""docstring for ClassName"""
	def __init__(self, arg):
		self.arg = arg

class Transform():
	"""docstring for ClassName"""
	def __init__(self, arg):
		super(Transform, self).__init__()
		self.arg = arg

class Light():
	"""docstring for Light"""
	def __init__(self, lightData):
		self.shape = Shape()
		self.transform = Transform()
	def createLight(self):
		pass
class GetLightsInfo():
	def getRenderer(self,renderer):
		self.renderer = renderer
	def get
class MakeLights():
	"""docstring for ClassName"""
	def getRenderer(self,renderer):
		self.renderer = renderer
	def makeLightsForTargetRenderer():
		pass



		
class DomeLight(Light):
	"""docstring for DomeLight"""
	def __init__(self, arg):
		super(DomeLight, self).__init__()
		self.arg = arg
		