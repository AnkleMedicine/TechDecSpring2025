# shift alt M to send code to Maya!

import maya.OpenMayaUI as omui # imports maya open may ui module, it can help finding the maya main window
import shiboken2
import maya.cmds as mc
from PySide2.QtWidgets import (QMainWindow, QWidget) # imports all the widgets needed to build our UI
from PySide2.QtCore import Qt # has some values we can use to configure our widget like window type, or orientation

def GetMayaMainWindow()->QMainWindow:#retreives window from maya
    mayaMainWindow = omui.MQtUtil.mainWindow() 
    return shiboken2.wrapInstance(int(mayaMainWindow), QMainWindow) 

def DeleteWindowWithName(name):# deletes previous window and opens a new one with same name
    for window in GetMayaMainWindow().findChildren(QWidget, name):
        window.deleteLater() 

class QMayaWindow(QWidget):
    def __init__(self): #makes the new window follow maya
        DeleteWindowWithName(self.GetWindowHash())
        super().__init__(parent = GetMayaMainWindow()) 
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWindowHash())

    def GetWindowHash(self):# gives ID to the window
        return "fjhdaofih"
    
def IsMesh(obj):
    shapes = mc.listRelatives(obj, s=True)
    if not shapes:
        return False
    
    for s in shapes:
        if mc.objectType(s) == "mesh":
            return True
        
    return False

def IsSkin(obj):
    return mc.objectType(obj) == "skinCluster"

def IsJoint(obj):
    return mc.objectType(obj) == "joint"

def GetUpperStream(obj):
    return mc.listConnections(obj, s=True, d=False, sh=True)

def GetLowerStream(obj):
    return mc.listConnections(obj, s=False, d=True, sh=True )

def GetAllConnectIn(obj, NextFunc, searchDeapth = 10, Filter = None):
    AllFound = set()
    nexts = NextFunc(obj)
    while nexts and searchDeapth > 0:
        for next in nexts:
            AllFound.add(next)

        nexts = NextFunc(nexts)
        if nexts:
            nexts = [x for x in nexts if x not in AllFound]

        searchDeapth -=1

    if not Filter:
        return list(AllFound)
    
    filtered = []
    for found in AllFound:
        if Filter(found):
            filtered.append(found)

    return filtered

