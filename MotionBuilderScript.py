# coding=utf-8
# Python bytecode 2.7

import sys
import maya.cmds as cmds
import maya.mel as mel
import os
import ctypes.wintypes
import maya.standalone as std
import shutil

std.initialize(name='python')
# pyrcc5 -o qrc_resources.py resources.qrc
mayapath = sys.argv[1]

class ExportFBX_C():
    def __init__(self):
        mayaOutpath,mayafieldername = os.path.split(mayapath)
        self.selecttion = []
        if sys.argv[3]  == "Ani":
            self.mayaOutpath = mayaOutpath+"/"+mayafieldername.split(".")[0]+"/"
            if not os.path.exists(self.mayaOutpath):
                os.makedirs(self.mayaOutpath)
            self.OpenAndExportPath(mayapath)
        elif sys.argv[3]  == "Rig":
            self.mayaOutpath = mayaOutpath+"/"
            self.outFbxname = mayafieldername.split(".")[0]+".fbx"
            self.ExportFBX_Rig(self.mayaOutpath+self.outFbxname)
    def ExportFBX_Rig(self,fbxpath):
        self.skinbone = []
        self.OpneMayaCmd(mayapath)
        self.listBlendShape()
        self.disConnectlistAllbone()
        cmds.select(self.selecttion)
        self.ouputFBx(fbxpath)
    def disConnectlistAllbone(self):
        allboen = cmds.ls(type = "joint",long=True)
        for i in allboen:
            self.disconnect_all_connections(i)
        for i in self.skinbone:
            mod = self.findSkinnedMeshesFromJoint(i)
            for mm in mod:
                if mm not in self.selecttion:
                    self.selecttion.append(mm)
            self.selecttion.append(i)
    def clearAllconstanc(self):
        typelist = ["parentConstraint","pointConstraint","orientConstraint","scaleConstraint" ,"aimConstraint"]
        for i in typelist:
            cmds.delete(cmds.ls(type = i))
    def disconnect_all_connections(self,joint):
        self.clearAllconstanc()
        connections = cmds.listConnections(joint, s=1,d=1,p=1)
        con = [".tx",".ty",".tz",".rx",".ry",".rz",".sx",".sy",".sz",".v",".t",".r",".s"]
        if connections:
            for conn in connections:
                obj = conn.split(".")[0]
                if cmds.nodeType(obj) == "skinCluster":
                    self.skinbone.append(joint)
                for i in con:
                    listx = cmds.listConnections(joint+i, s=1,d=1,p=1)
                    if listx:
                        for kk in listx:
                            try:
                                cmds.disconnectAttr(kk, joint+i)
                            except:
                                pass
    def OpneMayaCmd(self,path):
        if ".ma" in path:
            cmds.file(  path,
                        f = True,
                        options = "v=0;",
                        ignoreVersion = True,
                        typ = "mayaAscii",
                        o = True
                    )
        elif ".mb" in path:
            cmds.file(  path,
                        f = True,
                        options = "v=0;",
                        ignoreVersion = True,
                        typ = "mayaBinary",
                        o = True
                    )
    def OpenAndExportPath(self,path):
        if ".ma" in path:
            cmds.file(  path,
                        f = True,
                        options = "v=0;",
                        ignoreVersion = True,
                        typ = "mayaAscii",
                        o = True
                    )
        elif ".mb" in path:
            cmds.file(  path,
                        f = True,
                        options = "v=0;",
                        ignoreVersion = True,
                        typ = "mayaBinary",
                        o = True
                    )
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')
        self.setcurrentUnit(int(sys.argv[2]))
        self.setAllctrlZero()
        #cmds.file(force=True, save=True, options="v=0", type="mayaAscii")
        self.listCam()
        self.listAllbone()
        self.bakeAni(self.selecttion)
        self.listAllRigBone()
        self.Fbx = {}
        if self.skonbone:
            for i in self.skonbone:
                skelect = self.listAllJoints(i)
                Charmesh = []
                for bone in skelect:
                    objk = self.findSkinnedMeshesFromJoint(bone)
                    for k in objk:
                        if k not in Charmesh:
                            Charmesh.append(k)
                if Charmesh:
                    charname = i.split(":")[0]
                    charOutput = self.mayaOutpath+charname+".fbx"
                    self.Fbx[charname] = [charOutput,skelect,Charmesh]
                    referenceNode = self.getReferenceNodeFromSelection(i)
                    if referenceNode:
                        self.importReferenceByNode(referenceNode)
                    cmds.select(skelect)
                    cmds.select(Charmesh,add = 1)
                    self.ouputFBx(charOutput)
                    charnameallobj = cmds.ls(charname+":*")
                    if charnameallobj:
                        for i in charnameallobj:
                            try:
                                cmds.delete(i)
                            except:
                                pass
            for cam in self.Camerm:
                charOutput = self.mayaOutpath+cam.replace(":","_")+"_outPutCam.fbx"
                cmds.select(cam)
                self.ouputFBx(charOutput)
            #others
            othersJoint = cmds.ls(type = "joint")
            if othersJoint:
                othersmesh = []
                for i in othersJoint:
                    objk = self.findSkinnedMeshesFromJoint(i)
                    for k in objk:
                        if k not in othersmesh:
                            othersmesh.append(k)
                if othersmesh:
                    cmds.select(othersJoint)
                    cmds.select(othersmesh,add = 1)
                    charOutput = self.mayaOutpath+"other.fbx"
                    self.ouputFBx(charOutput)
                    for i in othersJoint:
                        try:
                            cmds.delete(i)
                        except:
                            pass
                    for i in othersmesh:
                        try:
                            cmds.delete(i)
                        except:
                            pass
            #cmds.file(force=True, save=True, options="v=0", type="mayaAscii")
            #outputTxt = self.mayaOutpath+"output.txt"
            #sys.stdout = open(outputTxt, "w")
            #print (sys.stdout)
            for key,vou in self.Fbx.items():
                self.OpneFBx(vou[0])
                cmds.select(cl = 1)
                for i in vou[1]:
                    if cmds.objExists(i):
                        cmds.select(i,add = 1)
                for i in vou[2]:
                    if cmds.objExists(i):
                        cmds.select(i,add = 1)
                self.ouputFBx(vou[0])
                self.OpneFBx(vou[0])
                self.removeAllNamespaces()
                container = cmds.ls(type = "container")
                if container:
                    cmds.delete(container)
                if cmds.objExists("Root_M") or cmds.objExists("hips") :
                    cmds.polyCube(n = "Box")
                    if cmds.objExists("Root_M"):
                        cmds.parentConstraint( 'Root_M', 'Box', mo = 0 )
                    elif cmds.objExists("hips"):
                        cmds.parentConstraint( 'hips', 'Box', mo = 0 )
                    self.bakeAni("Box")
                    cmds.select("Box")
                self.ouputFBxAll(vou[0])
    def OpneFBx(self,fbxpath):
        #cmds.file(new=True, force=True)
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')
        cmds.file(  fbxpath,
                    f = True,
                    typ = "FBX",
                    ignoreVersion = True,
                    options = "fbx",
                    o = True
                )
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')
    def removeAllNamespaces(self):
        namespaces = [ ns for ns in cmds.namespaceInfo( lon=1, r=1 ) if ns not in [ 'UI', 'shared' ] ]
        # Reverse Iterate through the contents of the list to remove the deepest layers first
        for ns in reversed(namespaces):
            cmds.namespace( rm=ns, mnr=1 )
        namespaces[:] = []
    def ouputFBxAll(self,ath):
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')
        cmds.file(ath,force = True,options = "v=0;",type = "FBX export",pr = True,ea = True)
    def ouputFBx(self,pathFBx):
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')
        cmds.file(pathFBx, force=True, options="v=0;", typ="FBX export", pr=True, es=True)
    def importReferenceByNode(self,referenceNode):
        if cmds.nodeType(referenceNode) == "reference":
            refFile = cmds.referenceQuery(referenceNode, filename=True)
            cmds.file(refFile, importReference=True)
    def getReferenceNodeFromSelection(self,selectio):
        cmds.select(selectio)
        selection = cmds.ls(sl = True)
        if len(selection) == 1:
            selectedObject = selection[0]
            if cmds.referenceQuery(selectedObject, isNodeReferenced=True):
                refNode = cmds.referenceQuery(selectedObject, referenceNode=True)
                return refNode
        return None
    def listAllRigBone(self):
        self.skonbone = cmds.ls("*:DeformationSystem")
    def findSkinnedMeshesFromJoint(self,jointName):
        skinnedMeshes = []
        skinClusters = cmds.listConnections(jointName, type='skinCluster')
        if skinClusters:
            for cluster in skinClusters:
                geometries = cmds.skinCluster(cluster, query=True, geometry=True)
                if geometries:
                    geometriesparent = self.getTransformFromShape(geometries)
                    if geometriesparent:
                        skinnedMeshes.append(geometriesparent)
        return skinnedMeshes
    def getTransformFromShape(self,shapeName):
        parents = cmds.listRelatives(shapeName, parent=True)
        if parents:
            return parents[0]
        else:
            return None
    def listAllbone(self):
        allboen = cmds.ls(type = "joint",long=True)
        for i in allboen:
            if i not in self.selecttion:
                self.selecttion.append(i)
    def listAllJoints(self,startJoint=None):
        if not startJoint:
            allJoints = cmds.ls(type='joint', long=True)
        else:
            allJoints = cmds.listRelatives(startJoint, allDescendents=True, fullPath=True) or []
        return allJoints
    def listBlendShape(self):
        for i in cmds.ls(type = "blendshape"):
            if i not in self.selecttion:
                self.selecttion.append(i)
    def listCam(self):
        listCam = cmds.ls(type = "camera")
        self.Camerm = []
        defoutCam = [
                         u'backShape',
                         u'leftShape',
                         u'frontShape',
                         u'perspShape',
                         u'sideShape',
                         u'topShape'
                        ]
        if listCam:
            for i in listCam:
                if i.split(":")[-1] not in defoutCam and i not in self.Camerm:
                    camparent = cmds.listRelatives(i, parent=True)
                    self.Camerm.append(camparent[0])
                    self.selecttion.append(camparent[0])
    def bakeAni(self,selecttion):
        cmds.select(selecttion)
        #self.getMaxAndMinframe(selecttion[0])
        minTime = cmds.playbackOptions(query=True, minTime=True)
        maxTime = cmds.playbackOptions(query=True, maxTime=True)
        cmds.bakeResults(selecttion,
                        simulation = True,
                        t = (minTime,maxTime),
                        sampleBy = 1,
                        oversamplingRate = 1,
                        disableImplicitControl = True,
                        preserveOutsideKeys = True,
                        sparseAnimCurveBake = False ,
                        removeBakedAttributeFromLayer = False ,
                        removeBakedAnimFromLayer = False ,
                        bakeOnOverrideLayer = False ,
                        minimizeRotation = True ,
                        controlPoints = False ,
                        shape = True,)
    def getMaxAndMinframe(self,selection_list):
        min_frame = None
        max_frame = None
        keyframes = cmds.keyframe(selection_list, query=True)
        if keyframes:
            obj_min_frame = min(keyframes)
            obj_max_frame = max(keyframes)
            if min_frame is None or obj_min_frame < min_frame:
                min_frame = obj_min_frame
            if max_frame is None or obj_max_frame > max_frame:
                max_frame = obj_max_frame
            self.min_frame = min_frame
            self.max_frame = max_frame
        else:
            self.min_frame = 0
            self.max_frame = 0
    def setcurrentUnit(self,timeed):
        if timeed == 24:
            cmds.currentUnit(time='film')
        elif timeed == 25:
            cmds.currentUnit(time='pal')
        elif timeed == 30:
            cmds.currentUnit(time='ntsc')
        elif timeed == 48:
            cmds.currentUnit(time='show')
        elif timeed == 60:
            cmds.currentUnit(time='ntscf')
    def getAllctrl(self):
        nurbsCurves = cmds.ls(type='nurbsCurve',long = 1)
        curveTransforms = []
        for curve in nurbsCurves:
            parent = cmds.listRelatives(curve, parent=True,fullPath=True)
            if parent:
                curveTransforms.append(parent[0])
        return curveTransforms
    def setAllctrlZero(self):
        allCtrlnurbsCurves = self.getAllctrl()
        if allCtrlnurbsCurves:
            cmds.currentTime(100)
            for ctrl in allCtrlnurbsCurves:
                self.SetKey(ctrl+".tx")
                self.SetKey(ctrl+".ty")
                self.SetKey(ctrl+".tz")

                self.SetKey(ctrl+".rx")
                self.SetKey(ctrl+".ry")
                self.SetKey(ctrl+".rz")
            self.getAllMain()
            if self.AllmainCtrl:
                AllmainCtrlidck = {}
                for i in self.AllmainCtrl:
                    tx = cmds.getAttr(i+".tx")
                    ty = cmds.getAttr(i+".ty")
                    tz = cmds.getAttr(i+".tz")
                    rx = cmds.getAttr(i+".rx")
                    ry = cmds.getAttr(i+".ry")
                    rz = cmds.getAttr(i+".rz")
                    AllmainCtrlidck[i] = [tx,ty,tz,rx,ry,rz]
                for ctrl in allCtrlnurbsCurves:
                    cmds.currentTime(0)
                    self.setV(ctrl+".tx",0)
                    self.setV(ctrl+".ty",0)
                    self.setV(ctrl+".tz",0)
                    self.setV(ctrl+".rx",0)
                    self.setV(ctrl+".ry",0)
                    self.setV(ctrl+".rz",0)
                    self.SetKey(ctrl+".tx")
                    self.SetKey(ctrl+".ty")
                    self.SetKey(ctrl+".tz")
                    self.SetKey(ctrl+".rx")
                    self.SetKey(ctrl+".ry")
                    self.SetKey(ctrl+".rz")
                    cmds.currentTime(1)
                    self.setV(ctrl+".tx",0)
                    self.setV(ctrl+".ty",0)
                    self.setV(ctrl+".tz",0)
                    self.setV(ctrl+".rx",0)
                    self.setV(ctrl+".ry",0)
                    self.setV(ctrl+".rz",0)
                    self.SetKey(ctrl+".tx")
                    self.SetKey(ctrl+".ty")
                    self.SetKey(ctrl+".tz")
                    self.SetKey(ctrl+".rx")
                    self.SetKey(ctrl+".ry")
                    self.SetKey(ctrl+".rz")
                    cmds.currentTime(2)
                    self.setV(ctrl+".tx",0)
                    self.setV(ctrl+".ty",0)
                    self.setV(ctrl+".tz",0)
                    self.setV(ctrl+".rx",0)
                    self.setV(ctrl+".ry",0)
                    self.setV(ctrl+".rz",0)
                    self.SetKey(ctrl+".tx")
                    self.SetKey(ctrl+".ty")
                    self.SetKey(ctrl+".tz")
                    self.SetKey(ctrl+".rx")
                    self.SetKey(ctrl+".ry")
                    self.SetKey(ctrl+".rz")
                for i in self.AllmainCtrl:
                    cmds.currentTime(1)
                    print(i.split("|")[-1])
                    self.setV(i+".tx",AllmainCtrlidck[i][0])
                    self.setV(i+".ty",AllmainCtrlidck[i][1])
                    self.setV(i+".tz",AllmainCtrlidck[i][2])

                    self.setV(i+".rx",AllmainCtrlidck[i][3])
                    self.setV(i+".ry",AllmainCtrlidck[i][4])
                    self.setV(i+".rz",AllmainCtrlidck[i][5])

                    self.SetKey(i+".tx")
                    self.SetKey(i+".ty")
                    self.SetKey(i+".tz")

                    self.SetKey(i+".rx")
                    self.SetKey(i+".ry")
                    self.SetKey(i+".rz")

                    cmds.currentTime(2)

                    self.setV(i+".tx",AllmainCtrlidck[i][0])
                    self.setV(i+".ty",AllmainCtrlidck[i][1])
                    self.setV(i+".tz",AllmainCtrlidck[i][2])

                    self.setV(i+".rx",AllmainCtrlidck[i][3])
                    self.setV(i+".ry",AllmainCtrlidck[i][4])
                    self.setV(i+".rz",AllmainCtrlidck[i][5])

                    self.SetKey(i+".tx")
                    self.SetKey(i+".ty")
                    self.SetKey(i+".tz")

                    self.SetKey(i+".rx")
                    self.SetKey(i+".ry")
                    self.SetKey(i+".rz")
            FKIKLeg_L = cmds.ls("*:FKIKLeg_L",long = 1)
            if FKIKLeg_L:
                for i in FKIKLeg_L:
                    cmds.currentTime(1)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
                    cmds.currentTime(2)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
            FKIKLeg_R = cmds.ls("*:FKIKLeg_R",long = 1)
            if FKIKLeg_R:
                for i in FKIKLeg_R:
                    cmds.currentTime(1)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
                    cmds.currentTime(2)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
            FKIKLeg_L = cmds.ls("*:FKIKArm_L",long = 1)
            if FKIKLeg_L:
                for i in FKIKLeg_L:
                    cmds.currentTime(1)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
                    cmds.currentTime(2)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
            FKIKLeg_R = cmds.ls("*:FKIKArm_R",long = 1)
            if FKIKLeg_R:
                for i in FKIKLeg_R:
                    cmds.currentTime(1)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
                    cmds.currentTime(2)
                    self.setV(i+".FKIKBlend",0)
                    self.SetKey(i+".FKIKBlend")
        self.setKeyCurve()
    def setKeyCurve(self):
        animCurveTA = cmds.ls(type = "animCurveTA")
        cmds.select(animCurveTA)
        cmds.filterCurve(animCurveTA)
    def setV(self,ctrl,v):
        try:
            cmds.setAttr(ctrl,v)
        except:
            pass
    def SetKey(self,ctrl):
        try:
            cmds.setKeyframe(ctrl)
        except:
            pass
    def getAllMain(self):
        self.AllmainCtrl = []
        allmain = cmds.ls("*:Main",long = True)
        if allmain:
            for i in allmain:
                self.AllmainCtrl.append(i)
        allRootX_M = cmds.ls("*:RootX_M",long = True)
        if allRootX_M:
            for i in allRootX_M:
                self.AllmainCtrl.append(i)
    def listCurvesInGroup(self,groupName):
        allDescendents = cmds.listRelatives(groupName, allDescendents=True, fullPath=True) or []
        allCurves = cmds.ls(allDescendents, type='nurbsCurve', long=True)
        curveTransforms = list(set([cmds.listRelatives(curve, parent=True, fullPath=True)[0] for curve in allCurves]))
        return curveTransforms
ExportFBX_C()
