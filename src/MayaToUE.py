from MayaUtil import IsJoint, IsMesh, QMayaWindow
from PySide2.QtWidgets import QListWidget, QMessageBox, QPushButton, QVBoxLayout, QLineEdit
import maya.cmds as mc

def TryAction(action):
    def wrapper(*args, **kwargs):
        try:
            action(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error", f"{e}")
    
    return wrapper

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.meshes = []

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

    def AddMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("No Mesh Selected")
        
        meshes = set()

        for sel in selection:
            if IsMesh(sel):
                meshes.add(sel)

        if len(meshes) == 0:
            raise Exception("No Mesh Selected")
        
        self.meshes = list(meshes)

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

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        self.meshList.setFixedHeight(80)
        addMeshBtn = QPushButton("Add Meshes")
        addMeshBtn.clicked.connect(self.AddMeshButtonCLicked)
        self.masterLayout.addWidget(addMeshBtn)


    @TryAction
    def AddMeshButtonCLicked(self):
            self.mayaToUE.AddMeshes()
            self.meshList.clear()
            self.meshList.addItems(self.mayaToUE.meshes)
    
    @TryAction
    def AddRootJntButtonCLicked(self):
            self.mayaToUE.AddRootJoint()
            self.rootJntText.setText(self.mayaToUE.rootJnt)

    @TryAction
    def SetSelectionAsRootJointBtnClicked(self):
            self.mayaToUE.SetSelectedAsRootJnt()
            self.rootJntText.setText(self.mayaToUE.rootJnt)


MayaToUEWidget().show()