# shift alt M to send code to Maya!
from PySide2.QtGui import QColor
import maya.cmds as mc #imports maya cmd module so we can use it to do stuff in maya
import maya.mel as mel
import maya.OpenMayaUI as omui # imports maya open may ui module, it can help finding the maya main window
from maya.OpenMaya import MVector

from PySide2.QtWidgets import (QColorDialog, QHBoxLayout,
                               QLineEdit,
                               QMessageBox,
                               QPushButton,
                               QWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QLabel,
                               QSlider,
                               QMainWindow
                               ) # imports all the widgets needed to build our UI
from PySide2.QtCore import Qt # has some values we can use to configure our widget like window type, or orientation
from MayaUtil import QMayaWindow

    
class LimbRigger: # limb rigger tool
    def __init__(self): #constructor for jnts
        self.root = "" 
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
        self.controllerColor = (0,0,0)

    def AutoFindJnts(self):
        self.root = mc.ls(sl=True, type="joint")[0] # finds the root joint
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0] #uses the root to find the mid joint
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0] #uses the mid to find the end root

    def CreateFKControlForJnt(self, jntName):
        ctrlName = "ac_fk_" + jntName #adds a prefix to each controler name created
        ctrlGrpName = ctrlName + "_grp" #adds a suffix to the controler group
        mc.circle(n=ctrlName, r=self.controllerSize, nr = (1,0,0))

        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName) #matches the control grps transformation to the corosponding joint
        mc.orientConstraint(ctrlName, jntName) #constrains the conterolers rotation to the corosponding joint
        return ctrlName, ctrlGrpName #finishes contols
    
    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply = True) #this is freeze transformation

        grpName = name +"_grp"
        mc.group(name, n=grpName)
        return name, grpName
    
    def CreatePlusController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p 0 70 0 -p -10 70 0 -p -10 60 0 -p -20 60 0 -p -20 50 0 -p -10 50 0 -p -10 40 0 -p 0 40 0 -p 0 50 0 -p 10 50 0 -p 10 60 0 -p 0 60 0 -p 0 70 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;")
        # mc.scale(self.controllerSize/3, self.controllerSize/3, self.controllerSize/3)
        # mc.makeIdentity(name, apply = True)

        grpName = name + "_grp"
        mc.group(name, n=grpName)
        return name, grpName

    def GetObjectLoc(self, objectName)->MVector:
        x, y, z = mc.xform(objectName, q=True, t=True, ws=True) #get the world space translation of the objectName
        return MVector(x, y, z)
    
    def PrintMVector(self, vectorToPrint):
        print(f"<{vectorToPrint.x}, {vectorToPrint.y}, {vectorToPrint.z}>")

    def SetCtrlColor(self,ctrlName):
        shapes = mc.listRelatives(ctrlName, shapes=True, type="nurbsCurve")
        if not shapes:
            return
        for shape in shapes:
            mc.setAttr(f"{shape}.overrideEnabled", 1)
            mc.setAttr(f"{shape}.overrideRGBColors", 1)
            mc.setAttr(f"{shape}.overrideColorRGB", self.controllerColor[0], self.controllerColor[1], self.controllerColor[2])

    def RigLimb(self, r, g, b):
       rootFKCtrl, rootFKCtrlGrp = self.CreateFKControlForJnt(self.root) # creates the FK Controler for root jnt
       midFKCtrl, midFKCtrlGrp = self.CreateFKControlForJnt(self.mid) # creates the FK Controler for mid jnt
       endFKCtrl, endFKCtrlGrp = self.CreateFKControlForJnt(self.end) # creates the FK Controler for the end jnt

       mc.parent(midFKCtrlGrp, rootFKCtrl) #parents the midCtrlGrp under the rootCtrl
       mc.parent(endFKCtrlGrp, midFKCtrl) #parents the end CtrlGrp under the midCtrl

       ikEndCtrl = "ac_ik_" + self.end
       ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
       mc.matchTransform(ikEndCtrlGrp, self.end)
       endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

       rootJntLoc = self.GetObjectLoc(self.root)
       endJntLoc = self.GetObjectLoc(self.end)

       rootToEndVec = endJntLoc - rootJntLoc

       ikHandleName = "ikHandle_" + self.end
       mc.ikHandle(n=ikHandleName, sj=self.root, ee = self.end, sol="ikRPsolver")
       ikPoleVectorVals = mc.getAttr(ikHandleName + ".poleVector")[0]
       ikPoleVector = MVector(ikPoleVectorVals[0], ikPoleVectorVals[1], ikPoleVectorVals[2])

       ikPoleVector.normalize()
       ikPoleVectorCtrlLoc = rootJntLoc + rootToEndVec / 2 +ikPoleVector * rootToEndVec.length()

       ikPoleVectorCtrlName = "ac_ik_" + self.mid
       mc.spaceLocator(n=ikPoleVectorCtrlName)
       ikPoleVectorCtrlGrp = ikPoleVectorCtrlName + "_grp"
       mc.group(ikPoleVectorCtrlName, n=ikPoleVectorCtrlGrp)
       mc.setAttr(ikPoleVectorCtrlGrp+".t", ikPoleVectorCtrlLoc.x, ikPoleVectorCtrlLoc.y, ikPoleVectorCtrlLoc.z, typ = "double3")
       mc.poleVectorConstraint(ikPoleVectorCtrlName, ikHandleName)

       ikfkBlendCtrlName = "ac_ikfk_blend_" + self.root
       ikfkBlendCtrlName, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrlName)
       ikfkBlendCtrlLoc = rootJntLoc + MVector(rootJntLoc.x, 0, rootJntLoc.z)
       mc.setAttr(ikfkBlendCtrlGrp+".t", ikfkBlendCtrlLoc.x, ikfkBlendCtrlLoc.y, ikfkBlendCtrlLoc.z, typ="double3")

       ikfkBlendAttrName = "ikfkBlend"
       mc.addAttr(ikfkBlendCtrlName, ln=ikfkBlendAttrName, min=0, max=1, k=True)
       ikfkBlendAttr = ikfkBlendCtrlName + "." +ikfkBlendAttrName

       mc.expression(s=f"{ikHandleName}.ikBlend = {ikfkBlendAttr}")
       mc.expression(s=f"{ikEndCtrlGrp}.v = {ikPoleVectorCtrlGrp}.v = {ikfkBlendAttr}")
       mc.expression(s=f"{rootFKCtrlGrp}.v = 1 - {ikfkBlendAttr}")
       mc.expression(s=f"{endOrientConstraint}.{endFKCtrl}W0 = 1-{ikfkBlendAttr}")
       mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}W1 = {ikfkBlendAttr}")

       mc.parent(ikHandleName, ikEndCtrl)
       mc.setAttr(ikHandleName+".v", 0)

       topGrpName = self.root + "_rig_grp"
       mc.group([rootFKCtrlGrp,ikEndCtrlGrp, ikPoleVectorCtrlGrp, ikfkBlendCtrlGrp], n= topGrpName)
       mc.setAttr(topGrpName+".overrideEnabled", 1)
       mc.setAttr(topGrpName+".overrideRGBColors", 1)
       mc.setAttr(topGrpName+".overrideColorRGB", r, g, b, type="double3")

class ColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.colorPickerBtn = QPushButton()
        self.colorPickerBtn.setStyleSheet(f"background-color:black")
        self.masterLayout.addWidget(self.colorPickerBtn)
        self.colorPickerBtn.clicked.connect(self.ColorPickerBtnClicked)
        self.color = QColor(0,0,0)

    def ColorPickerBtnClicked(self):
        self.color = QColorDialog.getColor()
        self.colorPickerBtn.setStyleSheet(f"background-color:{self.color.name()}")

class LimbRigToolWidget(QMayaWindow): #Limb rigger UI Window
    def __init__(self): #creates constructor for UI Window
        super().__init__()
        self.rigger = LimbRigger() # gives the function to rigger variable

        self.masterLayout = QVBoxLayout() #gets the layout from QT
        self.setLayout(self.masterLayout) #sets the layout as current layout

        self.tipLabel = QLabel("Select the First Joint of the Limb, and click on the Auto Find Button") # creates instruction text
        self.masterLayout.addWidget(self.tipLabel) # adds the instruction text to the window

        self.jointSelectionText = QLineEdit() #creates text box for selected joints found by the auto rigger
        self.masterLayout.addWidget(self.jointSelectionText) #adds the selected joints text box to the window
        self.jointSelectionText.setEnabled(False) #makes it for you cant interact with the text box

        self.autoFindBtn = QPushButton("Auto Find") # creates and names the auto find button
        self.masterLayout.addWidget(self.autoFindBtn) # adds the auto find button to the window
        self.autoFindBtn.clicked.connect(self.AutoFindBtnClicked) #when the button is clicked it runs the AutoFindBtnClicked function

        ctrlSliderLayout = QHBoxLayout() # 

        ctrlSizeSlider = QSlider() #creates a ui slider to adjust size of joint controller
        ctrlSizeSlider.setValue(self.rigger.controllerSize) #lets the slider control the controller size
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeValueChanged) #connects the slider to the value shown
        ctrlSizeSlider.setRange(1, 30) #sets the sliders range from 1 to 30
        ctrlSizeSlider.setOrientation(Qt.Horizontal) #sets the slider horizontal in the window
        ctrlSliderLayout.addWidget(ctrlSizeSlider) #adds the size slider to the window
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}") #creates label text for the slider
        ctrlSliderLayout.addWidget(self.ctrlSizeLabel) #adds slider text to the window

        self.masterLayout.addLayout(ctrlSliderLayout) #Adds slider layout to the window

        self.colorPicker = ColorPicker()
        self.masterLayout.addWidget(self.colorPicker)

        self.setColorBtn = QPushButton("Set Ctrl Color")
        self.masterLayout.addWidget(self.setColorBtn)
        self.setColorBtn.clicked.connect(self.SetColorBtnClicked)

        self.rigLimbBtn = QPushButton("Rig Limb") # creates and names the rig limb button
        self.masterLayout.addWidget(self.rigLimbBtn) # adds the rig limb button to the window
        self.rigLimbBtn.clicked.connect(self.RigLimbBtnClicked) # when the button is clicked it runs the RigLimbBtnClicked function

        self.setWindowTitle("Limb Rigging Tool") # sets the title of the new window as "Limb Rigging Tool"

    def CtrlSizeValueChanged(self, newValue):# shows the number text corosponding to the controler size
        self.rigger.controllerSize = newValue 
        self.ctrlSizeLabel.setText(f"{self.rigger.controllerSize}") 
    
    def RigLimbBtnClicked(self):
        self.rigger.RigLimb(self.colorPicker.color.redF(), self.colorPicker.color.greenF(), self.colorPicker.color.blueF()) #runs the RigLimb function 

    def SetColorBtnClicked(self):
        print("Self Color Button Cicked!")
        color = self.colorPicker.color
        self.rigger.controllerColor = (color.redF(), color.greenF(), color.blueF())
        ctrl = mc.ls(sl=True)
        self.rigger.SetCtrlColor(ctrl[0])

    def AutoFindBtnClicked(self):
        try:
            self.rigger.AutoFindJnts() # runs the AutoFindJnts function
            self.jointSelectionText.setText(f"{self.rigger.root}, {self.rigger.mid}, {self.rigger.end}") # shows joint order (root, mid, end) of found jnts in the selection text box
        except Exception as e:
            QMessageBox.critical(self, "Error", "Wrong Selection, please select the frist joint of the limb!") # shows error message to user if they dont click the root joint when using the autofind btn


limbRigToolWidget = LimbRigToolWidget()
limbRigToolWidget.show()

#HW: comment on each line what they do