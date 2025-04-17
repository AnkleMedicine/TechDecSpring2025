from MayaUtil import IsJoint, QMayaWindow
from PySide2.QtWidgets import QMessageBox, QPushButton, QVBoxLayout, QLineEdit
import maya.cmds as mc

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""

    def SetSelectedAsRootJnt(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("Nothing Selected, Please Select the Root Joint of the Rig!")

        selectedJnt = selection[0]
        if not IsJoint(selectedJnt):
            raise Exception(f"{selectedJnt} is not a Joint, Please Select the Root Joint of the Rig!")
        
        self.rootJnt = selectedJnt

    def AddRootJoint(self):
        if not self.rootJnt or (not mc.objExists(self.rootJnt)):
            raise Exception("No Root Joint Assigned, please set the current root joint of the rig first!")
        
        currentRootJntPosX, currentRootJntPosY, currentRootJntPosZ = mc.xform(self.rootJnt, q=True, t=True, ws=True)
        if currentRootJntPosX ==0 and currentRootJntPosY == 0 and currentRootJntPosZ == 0:
            raise Exception("current root joint is already at origin, no need to make a new one!")

        mc.select(cl=True)
        rootJntName = self.rootJnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName

class MayaToUEWidget(QMayaWindow):
    def GetWindowHash(self):
        return "MayatoUE417204745ARM"
    
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()
        self.setWindowTitle("Maya to UE")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectionAsRootJntBtn = QPushButton("Set Root Joint")
        setSelectionAsRootJntBtn.clicked.connect(self.SetSelectionAsRootJointBtnClicked)
        self.masterLayout.addWidget(setSelectionAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntButtonCLicked)
        self.masterLayout.addWidget(addRootJntBtn)

    def AddRootJntButtonCLicked(self):
        try:
            self.mayaToUE.AddRootJoint()
            self.rootJntText.setText(self.mayaToUE.rootJnt)
        except Exception as e:
            QMessageBox().critical(self, "Error", f"{e}")

    def SetSelectionAsRootJointBtnClicked(self):
        try:
            self.mayaToUE.SetSelectedAsRootJnt()
            self.rootJntText.setText(self.mayaToUE.rootJnt)
        except Exception as e:
            QMessageBox().critical(self, "Error", f"{e}")


MayaToUEWidget().show()