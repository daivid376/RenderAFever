#encoding:utf-8
import maya.cmds as mc
import maya.mel
import UI.materialImporter
from basicOperater import FileNode
import basicOperater
from material.materialConverter import Material 
import dataClass

import material.materialConverter
#global var
class MaterialImporter():
    def __init__(self):

        mayaVersion = int(mc.about(version = 1)[:4])

        self.textureTemplateUsing = ''
        self.userDefinedPath = ''
        self.materialName = ''
        self.targetMaterialType = None
        self.usingMayaColorManagement = True
        self.isUdim = False
        self.dataDict = None

        self.openGLNormal = True
        self.heightMapAsDisplacement = True
        self.heightMap_8bit = True
        affectColorSwitch = False
        self.zeroHeight = 0.5
        self.heightDepth = 0.05



    def prepareGlobalVars(self):
        #global self.textureTemplateUsing
        #get userDifinedPath from UI input
        #only get the path info from UI,get the real path used by basicOperater  function getFileInfoFrom line 22
        self.userDefinedPath = mc.textFieldGrp('userDefinedPathTextField',q= 1 ,tx = 1) 

        #get self.materialName from UI input
        self.materialName = mc.textFieldGrp('materialNameInput',q= 1 ,tx = 1)

        self.targetMaterialType = mc.optionMenuGrp('createMaterial',q = 1 ,v = 1)

        self.textureTemplateUsing = mc.optionMenuGrp('useTemplate',q = 1 ,v = 1)

        self.usingMayaColorManagement = mc.checkBox('self.usingMayaColorManagement',q = 1,v = 1)

        self.openGLNormal = mc.checkBox('self.openGLNormal',q = 1 ,v =1)

        self.isUdim =  mc.checkBox('udim',q = 1,v = 1)

        self.heightMapAsDisplacement = mc.checkBox('self.heightMapAsDisplacement',q = 1,v = 1)

        self.heightMap_8bit = mc.checkBox('self.heightMap_8bit',q = 1,v = 1)

        self.zeroHeight = float(mc.textFieldGrp('self.zeroHeight',q = 1, tx = 1 ))

        self.heightDepth = float(mc.textFieldGrp('self.heightDepth',q = 1,tx = 1))

    def __setAbstractMaterial(self,thisAbstractMaterial,defaultAttr_specificAttr_dict,materialName,materialAttrsData,textureTemplatesData):
        fileNodes = []

        reverse = None
        haveFresnelTypeTexture = False

        selfOperater = textureTemplatesData[self.textureTemplateUsing]['primaryReflectionGlossiness']  #rough or gloss
        targetOperater = materialAttrsData[self.targetMaterialType]['primaryReflectionGlossiness'][1]  #default gloss    reverse rough
        
        if 'rough' in selfOperater.lower() :
            reverse = True
        else:
            reverse = False


        #thisAbstractMaterial.attrs['primaryReflectionBRDF'].value = 'ggx'
        for defaultAttr in defaultAttr_specificAttr_dict.keys():
            specificAttrName = defaultAttr_specificAttr_dict[defaultAttr]

            if specificAttrName != 'none':
                fileNode = FileNode()
                fileNode.getFileInfoFrom(self.userDefinedPath, materialName, defaultAttr,specificAttrName)
                
                
                fileNode.createFileNode(self.usingMayaColorManagement,self.isUdim)
                if defaultAttr == 'primaryReflectionF0' and fileNode.specificFileNode is not None:
                    thisAbstractMaterial.primaryFresnelType = 'F0'
                    thisAbstractMaterial.primaryF0Attr = material.materialConverter.Attr(defaultAttr_specificAttr_dict[defaultAttr], 'default')
                    thisAbstractMaterial.primaryF0Attr.inputNode = fileNode.outNode
                    thisAbstractMaterial.primaryF0Attr.inputAttr = fileNode.outAttr
                    haveFresnelTypeTexture = True

                elif defaultAttr == 'primaryReflectionIOR' and fileNode.specificFileNode is not None:
                    thisAbstractMaterial.primaryFresnelType = 'IOR'
                    thisAbstractMaterial.primaryIORAttr = material.materialConverter.Attr(defaultAttr_specificAttr_dict[defaultAttr], 'default')
                    thisAbstractMaterial.primaryIORAttr.inputNode = fileNode.outNode
                    thisAbstractMaterial.primaryIORAttr.inputAttr = fileNode.outAttr
                    haveFresnelTypeTexture = True

                elif defaultAttr == 'primaryMetalness' and fileNode.specificFileNode is not None:
                    thisAbstractMaterial.primaryFresnelType = 'Metal'
                    thisAbstractMaterial.primaryMetalnessAttr = material.materialConverter.Attr(defaultAttr_specificAttr_dict[defaultAttr], 'default')
                    thisAbstractMaterial.primaryMetalnessAttr.inputNode = fileNode.outNode
                    thisAbstractMaterial.primaryMetalnessAttr.inputAttr = fileNode.outAttr
                    haveFresnelTypeTexture = True

                if fileNode.specificFileNode is not None:
                    fileNodes.append(fileNode)
                    if fileNode.defaultAttr == 'height':
                        thisAbstractMaterial.heightFileNode = fileNode

                if defaultAttr != 'height':
                    if defaultAttr != 'primaryReflectionGlossiness':
                        thisAbstractMaterial.attrs[defaultAttr] = material.materialConverter.Attr(thisAbstractMaterial.attrs[defaultAttr],materialAttrsData)
                    elif defaultAttr== 'primaryReflectionGlossiness' and reverse is not None:
                        if reverse:
                            thisAbstractMaterial.attrs[defaultAttr] = material.materialConverter.Attr(thisAbstractMaterial.attrs[defaultAttr],'reverse')
                    thisAbstractMaterial.attrs[defaultAttr].inputNode = fileNode.outNode
                    thisAbstractMaterial.attrs[defaultAttr].inputAttr = fileNode.outAttr
       
        if not haveFresnelTypeTexture:
            if materialAttrsData[self.targetMaterialType]['primaryReflectionIOR'][0] != 'none':
            #if there are no texture connected to determin the fresnel type ,use ior 1.5 
            #ior is more accuacy than f0, ior has a higher priority
                thisAbstractMaterial.primaryFresnelType = 'IOR'
                thisAbstractMaterial.attrs['primaryReflectionIOR'] = material.materialConverter.Attr('primaryReflectionIOR','default')
                thisAbstractMaterial.attrs['primaryReflectionIOR'].value = 1.5
            else:
                thisAbstractMaterial.primaryFresnelType = 'F0'
                thisAbstractMaterial.attrs['primaryReflectionF0'] = material.materialConverter.Attr('primaryReflectionF0','default')
                thisAbstractMaterial.attrs['primaryReflectionF0'].value = 0.04
        return fileNodes

    def __createDisplacement_connect(self,heightFileNode,targetMaterial):

        disNode = mc.shadingNode('displacementShader',asShader = 1)
        self.heightDepth = float(self.heightDepth)
        mc.setAttr(disNode + '.scale',self.heightDepth)
        mc.connectAttr(heightFileNode.outAttr,disNode + '.displacement')

        if self.heightMap_8bit:
            self.zeroHeight = float(self.zeroHeight)
            mc.setAttr(heightFileNode.specificFileNode + '.alphaOffset',-self.zeroHeight)

        sgNode = basicOperater.createShadingGroup_connectDisplacement(targetMaterial, disNode)
        renderer = material.materialConverter.getRendererName(self.targetMaterialType)
        if renderer =='Redshift':
            basicOperater.convertMayaDisNodeToRsDisNode(sgNode)

    def import_replaceMaterialsByName(self,*args):
        #self.prepareGlobalVars()
        materialNames = self.materialName.split(';')
        if len(materialNames) >1:
            for material in materialNames:
                mc.hyperShade(o = material)
                objects = mc.ls(sl = 1)
                self.import_assignToSelectedObjects(material,objects)
        else:
            objects = mc.ls(sl = 1)
            self.import_assignToSelectedObjects(materialNames[0],objects)



    def import_assignToSelectedObjects(self,thisMaterial,thisObjects,*args):
        sels = thisObjects
        objSelected = False
        if sels != []:
            for sel in sels:
                if mc.objectType(sel) == 'transform' or mc.objectType(sel) == 'mesh':
                    objSelected = True
                    break

        #self.prepareGlobalVars()

        import_assignToSelectedObjectsNeedData = dataClass.Data(['textureTemplates','materialAttrs','bumpAttrs','subdiv_displacementAttrs'])
        self.dataDict = import_assignToSelectedObjectsNeedData.prepareData()
        materialDataClass = dataClass.Data(['materialAttrs'])
        materialAttrsDataDict = materialDataClass.prepareData()

        textureTemplatesClass = dataClass.Data(['textureTemplates'])
        textureTemplatesData = textureTemplatesClass.prepareData()

        bumpData = self.dataDict['bumpAttrs']
        materialAttrsData = materialAttrsDataDict


        subdiv_displacementData = self.dataDict['subdiv_displacementAttrs']
        defaultAttr_specificAttr_dict =  textureTemplatesData[self.textureTemplateUsing]


        for key in defaultAttr_specificAttr_dict:
            if defaultAttr_specificAttr_dict[key] == '':
                defaultAttr_specificAttr_dict[key] = 'none'
        renderer = material.materialConverter.getRendererName(self.targetMaterialType)


        thisAbstractMaterial = Material('Default', materialAttrsData['Default'])
        thisAbstractMaterial.attrs['primaryReflectionBRDF'] = material.materialConverter.Attr('primaryReflectionBRDF',"{0:'default',1:'ggx'}")
        thisAbstractMaterial.attrs['primaryReflectionBRDF'].value = 1
        thisAbstractMaterial.attrs['primaryReflectionWeight'] = material.materialConverter.Attr('primaryReflectionWeight','default')
        thisAbstractMaterial.attrs['primaryReflectionWeight'].value = 1
        thisAbstractMaterial.attrs['primaryReflectionColor'] = material.materialConverter.Attr('primaryReflectionColor','default')
        thisAbstractMaterial.attrs['primaryReflectionColor'].value = [1,1,1]
        thisAbstractMaterial.attrs['diffuseWeight'] = material.materialConverter.Attr('diffuseWeight','default')
        thisAbstractMaterial.attrs['diffuseWeight'].value = 1
        thisAbstractMaterial.attrs['diffuseColor'] = material.materialConverter.Attr('diffuseColor','default')
        thisAbstractMaterial.attrs['diffuseColor'].value = [1,1,1]
        fileNodes = self.__setAbstractMaterial(thisAbstractMaterial,defaultAttr_specificAttr_dict, thisMaterial,materialAttrsData,textureTemplatesData)
        

        targetMaterial = Material(self.targetMaterialType, materialAttrsData[self.targetMaterialType])

        thisAbstractMaterial.convertTo(targetMaterial)
        targetMaterial = thisAbstractMaterial.createShader(name = thisMaterial)
        wastedBumpNode = None
        bumpFileNode = None
        #create and connect uv node
        uvNode = mc.shadingNode('place2dTexture',au = 1)
        for fileNode in fileNodes:
            if fileNode.bumpNode is not None:
                bumpFileNode = fileNode
                wastedBumpNode = fileNode.bumpNode
            basicOperater.connectUVNodeToTextureNode(uvNode, fileNode.specificFileNode)

        
        #create correct bump node for material
        if renderer == 'vray':
            inputBumpTextureNode = mc.listConnections(wastedBumpNode + '.bumpValue')[0]
            inputAttr = inputBumpTextureNode + '.outColor'
            outputAttr = mc.listConnections(wastedBumpNode + '.outNormal',p = 1)[0]
            mc.connectAttr(inputAttr , outputAttr,f = 1)

        bumpNode = material.materialConverter.convertConnect_BumpNode(bumpData, materialAttrsData, [targetMaterial], self.targetMaterialType)
        if bumpNode is not None:
            if self.openGLNormal:
                if renderer == 'Redshift':
                    mc.setAttr(bumpNode + '.flipY', 0)
                if renderer == 'arnold':
                    mc.setAttr(bumpNode + '.aiFlipR',0)
                    mc.setAttr(bumpNode + '.aiFlipG',0)
                if renderer == 'vray':
                    pass
            else:
                if renderer == 'Redshift':
                    mc.setAttr(bumpNode + '.flipY', 1)
                if renderer == 'arnold':
                    mc.setAttr(bumpNode + '.aiFlipR',0)
                    mc.setAttr(bumpNode + '.aiFlipG',1)
                if renderer == 'vray':
                    normalFileNode = mc.listConnections(bumpNode + '.bumpMap')[0]
                    outNode = material.materialConverter.createVrayDirectXNormalConnect(normalFileNode)
                    mc.connectAttr(outNode + '.outColor',bumpNode + '.bumpMap',f = 1)
                    #outNode = material.materialConverter.createVrayDirectXNormalConnect(bumpFileNode.specificFileNode)

                    #mc.connectAttr(outNode + '.outColor' ,bumpNode + '.bumpMap')

        #delete unused bump node 
        if wastedBumpNode is not None:
            mc.delete(wastedBumpNode)


        #create disNode

        if self.heightMapAsDisplacement and thisAbstractMaterial.heightFileNode is not None:
            self.__createDisplacement_connect(thisAbstractMaterial.heightFileNode,targetMaterial)
            
            
            #if something selected,set the selected objects' subdiv_dis attrs
            if objSelected:
                mc.select(sels)
                material.materialConverter.convertSet_SudivsDisplacementForSelected(subdiv_displacementData,'Default',renderer)
        if objSelected:
            
            mc.select(sels)
            mc.hyperShade(a = targetMaterial)


        mc.select(targetMaterial)

        #mc.nodeEditor('hyperShadePrimaryNodeEditor',e = 1, nodeViewMode = 'connected') 
        '''
        try:
            maya.mel.eval('hyperShadePanelGraphCommand("hyperShadePanel1", "rearrangeGraph")')
        except:
            pass
        '''