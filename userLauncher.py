#encoding:utf-8
#material converter
import maya.cmds as mc
import sys,os
mc.about(windows = 1)
scriptPath = mc.internalVar(usd = 1)
RenderAFeverPath = os.path.join(scriptPath,'RenderAFever')

# if the systerm is windows,then use \\ replace /
if mc.about(windows = 1):
	RenderAFeverPath = RenderAFeverPath.replace(r'/','\\')
else:
	pass
	
if RenderAFeverPath not in sys.path:
    sys.path.insert(0,RenderAFeverPath)
import UI.mainUI
try:
    import UI.mainUI
    
except:
    mc.error('the RenderAFever folder is placed wrong,the right path is : {0}'.format(scriptPath))
    
reload(UI.mainUI)
renderAFeverUI = UI.mainUI.RenderAFeverMainUI()

if vars().has_key('lastUI'):
    lastUI.close()
ui = renderAFeverUI.show()
lastUI = renderAFeverUI