# coding=utf-8
# Python bytecode 2.7

import os
import maya.cmds as cmds
import json
import ctypes
from ctypes import wintypes

class Getinfo_C():
    def __init__(self):
        self.getDocumentspath()
        self.loginfo = self.Documentspath+"LogInfo.json"
        if not os.path.exists(self.loginfo):
            self.logdick = {}
            self.writjson(self.loginfo,self.logdick)
        self.logdick = self.readjson(self.loginfo)
        self.current_file_path = cmds.file(q=True, sn=True)
        self.current_file_path_info = {}
    #引用的查询并写入
    def onoffreference(self):
        references = cmds.ls(type='reference')
        for refNode in references:
            if refNode != 'sharedReferenceNode':
                if refNode != "_UNKNOWN_REF_NODE_":
                    try:
                        refFilePath = cmds.referenceQuery(refNode, filename=True)
                        refFilePathpath = refFilePath.split("{")[0]
                        if not os.path.exists(refFilePathpath):
                            self.current_file_path_info[refNode] = [u"路径丢失文件",refFilePath]
                        else:
                            isUnloaded = cmds.referenceQuery(refNode, isLoaded=True)
                            if not isUnloaded:
                                self.current_file_path_info[refNode] = [u"警告关闭的引用",refFilePath]
                    except:
                        print("没用的")
                else:
                    self.current_file_path_info[refNode] = [u"垃圾引用节点",refFilePath]
        if self.current_file_path_info == {}:
            self.current_file_path_info[u"完成"] = [u"reference检查通过"]
        self.logdick[self.current_file_path] = self.current_file_path_info
        self.writjsonlogdick()
    def writjsonlogdick(self):
        self.writjson(self.loginfo,self.logdick)
    def readjson(self,jsonpath):
        with open(jsonpath) as json_file:
            data = json.load(json_file)
        return data
    def writjson(self,pathsaveName,dictA):
        newpath = pathsaveName
        final_json = json.dumps(dictA, sort_keys=True, indent=4)
        with open(newpath, 'w') as f:
            f.write(final_json)
    def getDocumentspath(self):
        CSIDL_PERSONAL = 5	   # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value
        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        self.Documentspath = buf.value.replace("\\","/")+"/"
