# -*- coding: utf-8 -*-
# Python bytecode 2.7
#zaomujin
from pyfbsdk import *
from pyfbsdk_additions import *
import sys
import os
import json
import threading
import shutil
import ctypes
from ctypes import wintypes
print("输出FBX")
print(sys.argv)

class MotionBuilder():
    def __init__(self):
        self.bones = [
                    u"Shoulder_R",
                    u"Elbow_R",
                    u'Wrist_R',
                    u'PinkyFinger1_R',
                    u'PinkyFinger2_R',
                    u'PinkyFinger3_R',
                    u'PinkyFinger4_R',
                    u'RingFinger1_R',
                    u'RingFinger2_R',
                    u'RingFinger3_R',
                    u'RingFinger4_R',
                    u'IndexFinger4_R',
                    u'IndexFinger3_R',
                    u'IndexFinger2_R',
                    u'IndexFinger1_R',
                    u'MiddleFinger4_R',
                    u'MiddleFinger3_R',
                    u'MiddleFinger2_R',
                    u'MiddleFinger1_R',
                    u'Hip_R',
                    u'Knee_R',
                    u'Ankle_R',
                ]
        self.getDocumentspath()
        self.readFbx = {}
        if not os.path.exists(self.Documentspath+"/motionbuilderoutFBX.json"):
            return
        else:
            self.readFbx = self.readjson(self.Documentspath+"/motionbuilderoutFBX.json")
        self.setBonesTposeS()
    def getDocumentspath(self):
        CSIDL_PERSONAL = 5	   # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value
        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        self.Documentspath = buf.value.replace("\\","/")
        self.local_directory = self.Documentspath+"/directory/"
        if self.local_directory not in sys.path:
            sys.path.append(self.local_directory)
    def setBonesTposeS(self):
        Threadtext = self.readFbx["threading"]
        if Threadtext == u'单线程':
            number = 1
        elif Threadtext == u'双线程':
            number = 2
        elif Threadtext == u'三线程':
            number = 3
        elif Threadtext == u'四线程':
            number = 4
        elif Threadtext == u'五线程':
            number = 5
        elif Threadtext == u'十线程':
            number = 10
        else:
            number = len(self.readFbx.keys())
        if Threadtext == u'单线程':
            self.setBonesTposeOne()
        elif Threadtext == u'全部线程':
            for i in range(number):
                t = threading.Thread(target = self.onetsetBones,args=(self.readFbx["motionbuilderoutFBX"][i],))
                t.start()
        else:
            num = len(self.readFbx.keys())/number
            kf = self.split_list(self.readFbx.values(),int(num))
            if len(kf) == number:
                for i in range(number):
                    t = threading.Thread(target = self.onetsetBones,args=(self.readFbx.values()[i],))
                    t.start()
            elif len(kf) == number + 1:
                for i in range(number+1):
                    t = threading.Thread(target = self.onetsetBones,args=(self.readFbx.values()[i],))
                    t.start()
    def split_list(self,lst,num):
        return [lst[i:i+num] for i in range(0, len(lst), num)]
    def setBonesTposeOne(self):
        for i,v in self.readFbx.items():
            print(i,v)
            for k in v:
                self.onetsetBones(k)
    def clear_scene(self):
        system = FBSystem()
        # 清除场景中的所有内容。
        system.Scene.Clear()
    def onetsetBones(self,k):
        ath,feo = os.path.split(k)
        charname = feo.split(".")[0]
        self.setBonesTpose(k)
        self.CharacterizeHiRes(str(charname),"adv")
        self.SaveFBX(k)
        lajipath = ath+"/"+feo.split(".")[0]+".bck"
        #print(lajipath)
        if os.path.exists(lajipath):
            try:
                shutil.rmtree(lajipath)
            except:
                pass
    def SaveFBX(self,file_path):
        save_result = self.lApp.FileSave(str(file_path))
        self.lApp.FileExit(False)
    def OpenFBX(self,file_path):
        #print(file_path)
        self.lApp = FBApplication()
        result = self.lApp.FileOpen(str(file_path))
    def setBonesTpose(self,fbxpath):
        self.OpenFBX(fbxpath)
        for i in self.bones:
            ByLabelNameofbone_L = FBFindModelByLabelName(str(i))
            ByLabelNameofbone_R = FBFindModelByLabelName(str(i.replace("_R","_L")))
            if ByLabelNameofbone_L and ByLabelNameofbone_R:
                if i == "Hip_R" or  i == "Knee_R" or  i == "Ankle_R":
                    ByLabelNameofbone = FBFindModelByLabelName(str(i))
                    ByLabelNameofbone.SetVector( FBVector3d( 90, 0, -90 ), FBModelTransformationType.kModelRotation, True )
                    ByLabelNameofbone = FBFindModelByLabelName(str(i.replace("_R","_L")))
                    ByLabelNameofbone.SetVector( FBVector3d( -90, 0, 90 ), FBModelTransformationType.kModelRotation, True )
                else:
                    ByLabelNameofbone = FBFindModelByLabelName(str(i))
                    ByLabelNameofbone.SetVector( FBVector3d( 90, 0, -180 ), FBModelTransformationType.kModelRotation, True )
                    ByLabelNameofbone = FBFindModelByLabelName(str(i.replace("_R","_L")))
                    ByLabelNameofbone.SetVector( FBVector3d( -90, 0, -180 ), FBModelTransformationType.kModelRotation, True )
    def CharacterizeHiRes(self,charName,Type):
        characters = FBSystem().Scene.Characters
        if characters:
            for character in characters:
                if character.LongName == charName:
                    #print "aready chexk %s"%(charName)
                    character.FBDelete()
        myCharacter = FBCharacter(charName)
        # NameMap
        # print Type
        if Type == "adv":
            self.addJointToCharacter (myCharacter, 'Reference', 'root')
            self.addJointToCharacter (myCharacter, 'Hips', 'Root_M')
            if "nw06" in charName:
                self.addJointToCharacter (myCharacter, 'LeftUpLeg', 'LegAim_L')
                self.addJointToCharacter (myCharacter, 'LeftLeg', 'Hip_L')
                self.addJointToCharacter (myCharacter, 'LeftFoot', 'Ankle_L')
                self.addJointToCharacter (myCharacter, 'LeftToeBase', 'Toes_L')
                self.addJointToCharacter (myCharacter, 'LeftFootMiddle1', 'ToesEnd_L')
            elif "nw56" in charName:
                self.addJointToCharacter (myCharacter, 'LeftUpLeg', 'Rump_L')
                self.addJointToCharacter (myCharacter, 'LeftLeg', 'Hip_L')
                self.addJointToCharacter (myCharacter, 'LeftFoot', 'Ankle_L')
                self.addJointToCharacter (myCharacter, 'LeftToeBase', 'Toes_L')
                self.addJointToCharacter (myCharacter, 'LeftFootMiddle1', 'ToesEnd_L')
            elif "nw57" in charName:
                self.addJointToCharacter (myCharacter, 'LeftUpLeg', 'Hip1_L')
                self.addJointToCharacter (myCharacter, 'LeftLeg', 'Knee_L')
                self.addJointToCharacter (myCharacter, 'LeftFoot', 'Toes1_L')
                self.addJointToCharacter (myCharacter, 'LeftToeBase', 'Toes2_L')
                self.addJointToCharacter (myCharacter, 'LeftFootMiddle1', 'ToesEnd_L')
            else:
                self.addJointToCharacter (myCharacter, 'LeftUpLeg', 'Hip_L')
                self.addJointToCharacter (myCharacter, 'LeftLeg', 'Knee_L')
                self.addJointToCharacter (myCharacter, 'LeftFoot', 'Ankle_L')
                self.addJointToCharacter (myCharacter, 'LeftToeBase', 'Toes_L')
                self.addJointToCharacter (myCharacter, 'LeftFootMiddle1', 'ToesEnd_L')
            if "nw06" in charName:
                self.addJointToCharacter (myCharacter, 'RightUpLeg', 'LegAim_R')
                self.addJointToCharacter (myCharacter, 'RightLeg', 'Hip_R')
                self.addJointToCharacter (myCharacter, 'RightFoot', 'Ankle_R')
                self.addJointToCharacter (myCharacter, 'RightToeBase', 'Toes_R')
                self.addJointToCharacter (myCharacter, 'RightFootMiddle1', 'ToesEnd_R')
            elif "nw56" in charName:
                self.addJointToCharacter (myCharacter, 'RightUpLeg', 'Rump_R')
                self.addJointToCharacter (myCharacter, 'RightLeg', 'Hip_R')
                self.addJointToCharacter (myCharacter, 'RightFoot', 'Ankle_R')
                self.addJointToCharacter (myCharacter, 'RightToeBase', 'Toes_R')
                self.addJointToCharacter (myCharacter, 'RightFootMiddle1', 'ToesEnd_R')
            elif "nw57" in charName:
                self.addJointToCharacter (myCharacter, 'RightUpLeg', 'Hip1_R')
                self.addJointToCharacter (myCharacter, 'RightLeg', 'Knee_R')
                self.addJointToCharacter (myCharacter, 'RightFoot', 'Toes1_R')
                self.addJointToCharacter (myCharacter, 'RightToeBase', 'Toes2_R')
                self.addJointToCharacter (myCharacter, 'RightFootMiddle1', 'ToesEnd_R')
            else:
                self.addJointToCharacter (myCharacter, 'RightUpLeg', 'Hip_R')
                self.addJointToCharacter (myCharacter, 'RightLeg', 'Knee_R')
                self.addJointToCharacter (myCharacter, 'RightFoot', 'Ankle_R')
                self.addJointToCharacter (myCharacter, 'RightToeBase', 'Toes_R')
                self.addJointToCharacter (myCharacter, 'RightFootMiddle1', 'ToesEnd_R')
            self.addJointToCharacter (myCharacter, 'LeftShoulder', 'Scapula_L')
            self.addJointToCharacter (myCharacter, 'LeftArm', 'Shoulder_L')
            self.addJointToCharacter (myCharacter, 'LeftForeArm', 'Elbow_L')
            self.addJointToCharacter (myCharacter, 'LeftHand', 'Wrist_L')
            #self.addJointToCharacter (myCharacter, 'LeftInHandIndex', 'LeftHandIndex')
            self.addJointToCharacter (myCharacter, 'LeftHandIndex1', 'IndexFinger1_L')
            self.addJointToCharacter (myCharacter, 'LeftHandIndex2', 'IndexFinger2_L')
            self.addJointToCharacter (myCharacter, 'LeftHandIndex3', 'IndexFinger3_L')
            #self.addJointToCharacter (myCharacter, 'LeftHandIndex4', 'LeftHandIndex4')
            self.addJointToCharacter (myCharacter, 'LeftHandThumb1', 'ThumbFinger1_L')
            self.addJointToCharacter (myCharacter, 'LeftHandThumb2', 'ThumbFinger2_L')
            self.addJointToCharacter (myCharacter, 'LeftHandThumb3', 'ThumbFinger3_L')
            #self.addJointToCharacter (myCharacter, 'LeftHandThumb4', 'LeftHandThumb4')
            self.addJointToCharacter (myCharacter, 'LeftHandMiddle1', 'MiddleFinger1_L')
            self.addJointToCharacter (myCharacter, 'LeftHandMiddle2', 'MiddleFinger2_L')
            self.addJointToCharacter (myCharacter, 'LeftHandMiddle3', 'MiddleFinger3_L')
            #self.addJointToCharacter (myCharacter, 'LeftHandMiddle4', 'LeftHandMiddle4')
            #self.addJointToCharacter (myCharacter, 'LeftInHandRing', 'LeftHandRing')
            self.addJointToCharacter (myCharacter, 'LeftHandRing1', 'RingFinger1_L')
            self.addJointToCharacter (myCharacter, 'LeftHandRing2', 'RingFinger2_L')
            self.addJointToCharacter (myCharacter, 'LeftHandRing3', 'RingFinger3_L')
            #self.addJointToCharacter (myCharacter, 'LeftHandRing4', 'LeftHandRing4')
            #self.addJointToCharacter (myCharacter, 'LeftInHandPinky', 'LeftHandPinky')
            self.addJointToCharacter (myCharacter, 'LeftHandPinky1', 'PinkyFinger1_L')
            self.addJointToCharacter (myCharacter, 'LeftHandPinky2', 'PinkyFinger2_L')
            self.addJointToCharacter (myCharacter, 'LeftHandPinky3', 'PinkyFinger3_L')
            #self.addJointToCharacter (myCharacter, 'LeftHandPinky4', 'LeftHandPinky4')
            self.addJointToCharacter (myCharacter, 'RightShoulder', 'Scapula_R')
            self.addJointToCharacter (myCharacter, 'RightArm', 'Shoulder_R')
            self.addJointToCharacter (myCharacter, 'RightForeArm', 'Elbow_R')
            self.addJointToCharacter (myCharacter, 'RightHand', 'Wrist_R')
            #self.addJointToCharacter (myCharacter, 'RightInHandIndex', 'RightHandIndex')
            self.addJointToCharacter (myCharacter, 'RightHandIndex1', 'IndexFinger1_R')
            self.addJointToCharacter (myCharacter, 'RightHandIndex2', 'IndexFinger2_R')
            self.addJointToCharacter (myCharacter, 'RightHandIndex3', 'IndexFinger3_R')
            #self.addJointToCharacter (myCharacter, 'RightHandIndex4', 'RightHandIndex4')
            self.addJointToCharacter (myCharacter, 'RightHandThumb1', 'ThumbFinger1_R')
            self.addJointToCharacter (myCharacter, 'RightHandThumb2', 'ThumbFinger2_R')
            self.addJointToCharacter (myCharacter, 'RightHandThumb3', 'ThumbFinger3_R')
            #self.addJointToCharacter (myCharacter, 'RightHandThumb4', 'RightHandThumb4')
            self.addJointToCharacter (myCharacter, 'RightHandMiddle1', 'MiddleFinger1_R')
            self.addJointToCharacter (myCharacter, 'RightHandMiddle2', 'MiddleFinger2_R')
            self.addJointToCharacter (myCharacter, 'RightHandMiddle3', 'MiddleFinger3_R')
            #self.addJointToCharacter (myCharacter, 'RightHandMiddle4', 'RightHandMiddle4')
            #self.addJointToCharacter (myCharacter, 'RightInHandRing', 'RightHandRing')
            self.addJointToCharacter (myCharacter, 'RightHandRing1', 'RingFinger1_R')
            self.addJointToCharacter (myCharacter, 'RightHandRing2', 'RingFinger2_R')
            self.addJointToCharacter (myCharacter, 'RightHandRing3', 'RingFinger3_R')
            #self.addJointToCharacter (myCharacter, 'RightHandRing4', 'RightHandRing4')
            #self.addJointToCharacter (myCharacter, 'RightInHandPinky', 'RightHandPinky')
            self.addJointToCharacter (myCharacter, 'RightHandPinky1', 'PinkyFinger1_R')
            self.addJointToCharacter (myCharacter, 'RightHandPinky2', 'PinkyFinger2_R')
            self.addJointToCharacter (myCharacter, 'RightHandPinky3', 'PinkyFinger3_R')
            #self.addJointToCharacter (myCharacter, 'RightHandPinky4', 'RightHandPinky4')
            self.addJointToCharacter (myCharacter, 'Spine', 'Spine1_M')
            self.addJointToCharacter (myCharacter, 'Spine1', 'Spine2_M')
            self.addJointToCharacter (myCharacter, 'Spine2', 'Chest_M')
            self.addJointToCharacter (myCharacter, 'Spine3', 'Spine3')
            self.addJointToCharacter (myCharacter, 'Neck', 'Neck_M')
            self.addJointToCharacter (myCharacter, 'Neck1', 'Neck1')
            self.addJointToCharacter (myCharacter, 'Head', 'Head_M')
            #turn character on, for some reason this often causes mB2012 to crash.
        elif Type == "Hips":

            self.addJointToCharacter (myCharacter, 'Reference', 'root')
            #print 'Hips'
            self.addJointToCharacter (myCharacter, 'Hips', ':Hips' )

            self.addJointToCharacter (myCharacter, 'LeftUpLeg', 'LeftUpLeg')
            self.addJointToCharacter (myCharacter, 'LeftLeg', 'LeftLeg')
            self.addJointToCharacter (myCharacter, 'LeftFoot', 'LeftFoot')
            self.addJointToCharacter (myCharacter, 'LeftToeBase', 'LeftToeBase')
            self.addJointToCharacter (myCharacter, 'LeftFootMiddle1', 'LeftToeBaseEnd')

            self.addJointToCharacter (myCharacter, 'RightUpLeg', 'RightUpLeg')
            self.addJointToCharacter (myCharacter, 'RightLeg', 'RightLeg')
            self.addJointToCharacter (myCharacter, 'RightFoot', 'RightFoot')
            self.addJointToCharacter (myCharacter, 'RightToeBase', 'RightToeBase')
            self.addJointToCharacter (myCharacter, 'RightFootMiddle1', 'RightToeBaseEnd')

            self.addJointToCharacter (myCharacter, 'LeftShoulder', 'LeftShoulder')
            self.addJointToCharacter (myCharacter, 'LeftArm', 'LeftArm')
            self.addJointToCharacter (myCharacter, 'LeftForeArm', 'LeftForeArm')
            self.addJointToCharacter (myCharacter, 'LeftHand', 'LeftHand')
            self.addJointToCharacter (myCharacter, 'LeftInHandIndex', 'LeftHandIndex')
            self.addJointToCharacter (myCharacter, 'LeftHandIndex1', 'LeftHandIndex1')
            self.addJointToCharacter (myCharacter, 'LeftHandIndex2', 'LeftHandIndex2')
            self.addJointToCharacter (myCharacter, 'LeftHandIndex3', 'LeftHandIndex3')
            self.addJointToCharacter (myCharacter, 'LeftHandIndex4', 'LeftHandIndex4')
            self.addJointToCharacter (myCharacter, 'LeftHandThumb1', 'LeftHandThumb1')
            self.addJointToCharacter (myCharacter, 'LeftHandThumb2', 'LeftHandThumb2')
            self.addJointToCharacter (myCharacter, 'LeftHandThumb3', 'LeftHandThumb3')
            self.addJointToCharacter (myCharacter, 'LeftHandThumb4', 'LeftHandThumb4')
            self.addJointToCharacter (myCharacter, 'LeftHandMiddle1', 'LeftHandMiddle1')
            self.addJointToCharacter (myCharacter, 'LeftHandMiddle2', 'LeftHandMiddle2')
            self.addJointToCharacter (myCharacter, 'LeftHandMiddle3', 'LeftHandMiddle3')
            self.addJointToCharacter (myCharacter, 'LeftHandMiddle4', 'LeftHandMiddle4')
            self.addJointToCharacter (myCharacter, 'LeftInHandRing', 'LeftHandRing')
            self.addJointToCharacter (myCharacter, 'LeftHandRing1', 'LeftHandRing1')
            self.addJointToCharacter (myCharacter, 'LeftHandRing2', 'LeftHandRing2')
            self.addJointToCharacter (myCharacter, 'LeftHandRing3', 'LeftHandRing3')
            self.addJointToCharacter (myCharacter, 'LeftHandRing4', 'LeftHandRing4')
            self.addJointToCharacter (myCharacter, 'LeftInHandPinky', 'LeftHandPinky')
            self.addJointToCharacter (myCharacter, 'LeftHandPinky1', 'LeftHandPinky1')
            self.addJointToCharacter (myCharacter, 'LeftHandPinky2', 'LeftHandPinky2')
            self.addJointToCharacter (myCharacter, 'LeftHandPinky3', 'LeftHandPinky3')
            self.addJointToCharacter (myCharacter, 'LeftHandPinky4', 'LeftHandPinky4')

            self.addJointToCharacter (myCharacter, 'RightShoulder', 'RightShoulder')
            self.addJointToCharacter (myCharacter, 'RightArm', 'RightArm')
            self.addJointToCharacter (myCharacter, 'RightForeArm', 'RightForeArm')
            self.addJointToCharacter (myCharacter, 'RightHand', 'RightHand')
            #self.addJointToCharacter (myCharacter, 'RightInHandIndex', 'RightHandIndex')
            self.addJointToCharacter (myCharacter, 'RightHandIndex1', 'RightHandIndex1')
            self.addJointToCharacter (myCharacter, 'RightHandIndex2', 'RightHandIndex2')
            self.addJointToCharacter (myCharacter, 'RightHandIndex3', 'RightHandIndex3')
            self.addJointToCharacter (myCharacter, 'RightHandIndex4', 'RightHandIndex4')
            self.addJointToCharacter (myCharacter, 'RightHandThumb1', 'RightHandThumb1')
            self.addJointToCharacter (myCharacter, 'RightHandThumb2', 'RightHandThumb2')
            self.addJointToCharacter (myCharacter, 'RightHandThumb3', 'RightHandThumb3')
            self.addJointToCharacter (myCharacter, 'RightHandThumb4', 'RightHandThumb4')
            self.addJointToCharacter (myCharacter, 'RightHandMiddle1', 'RightHandMiddle1')
            self.addJointToCharacter (myCharacter, 'RightHandMiddle2', 'RightHandMiddle2')
            self.addJointToCharacter (myCharacter, 'RightHandMiddle3', 'RightHandMiddle3')
            self.addJointToCharacter (myCharacter, 'RightHandMiddle4', 'RightHandMiddle4')
            #self.addJointToCharacter (myCharacter, 'RightInHandRing', 'RightHandRing')
            self.addJointToCharacter (myCharacter, 'RightHandRing1', 'RightHandRing1')
            self.addJointToCharacter (myCharacter, 'RightHandRing2', 'RightHandRing2')
            self.addJointToCharacter (myCharacter, 'RightHandRing3', 'RightHandRing3')
            self.addJointToCharacter (myCharacter, 'RightHandRing4', 'RightHandRing4')
            #self.addJointToCharacter (myCharacter, 'RightInHandPinky', 'RightHandPinky')
            self.addJointToCharacter (myCharacter, 'RightHandPinky1', 'RightHandPinky1')
            self.addJointToCharacter (myCharacter, 'RightHandPinky2', 'RightHandPinky2')
            self.addJointToCharacter (myCharacter, 'RightHandPinky3', 'RightHandPinky3')
            self.addJointToCharacter (myCharacter, 'RightHandPinky4', 'RightHandPinky4')

            self.addJointToCharacter (myCharacter, 'Spine', 'Spine')
            self.addJointToCharacter (myCharacter, 'Spine1', 'Spine1')
            self.addJointToCharacter (myCharacter, 'Spine2', 'Spine2')
            self.addJointToCharacter (myCharacter, 'Spine3', 'Spine3')
            self.addJointToCharacter (myCharacter, 'Neck', 'Neck')
            self.addJointToCharacter (myCharacter, 'Neck1', 'Neck1')
            self.addJointToCharacter (myCharacter, 'Head', 'Head')
            # turn character on, for some reason this often causes mB2012 to crash.
        myCharacter.SetCharacterizeOn(True)
        #myCharacter.CreateControlRig(True)
        #myCharacter.ActiveInput = True
    def readjson(self,jsonpath):
        with open(jsonpath) as json_file:
            #print json_file
            data = json.load(json_file)
        return data
    def addJointToCharacter(self,characterObject,slot,jointName ):
        myJoint = FBFindObjectByFullName('Model::' + jointName)
        if myJoint:
            property = characterObject.PropertyList.Find(slot + "Link")
            property.removeAll()
            property.append(myJoint)
MB = MotionBuilder()
