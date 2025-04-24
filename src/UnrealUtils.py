import unreal
import os

def CreateBaseImportTask(importPath):
    importTask = unreal.AssetImportTask()
    importTask.filename = importPath

    fileName = os.path.basename(importPath).split(".")[0]
    importTask.destination_path = '/Game/' + fileName
    importTask.automated = True
    importTask.save = True
    importTask.replace_existing = True

    return importTask

def ImportSkeletalMesh(meshPath):
    importTask = CreateBaseImportTask(meshPath)

    importOption = unreal.FbxImportUI()
    importOption.import_mesh = True
    importOption.import_as_skeletal = True


    #tells unreal to import blendshapes
    importOption.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)

    #tells unreal to use frame 0 as default pose
    importOption.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', True)

    importTask.options = importOption

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])

    # for imported in importTask.get_objects():
    #     pathName = imported.get_path_name()
    #     importedData = unreal.EditorAssetLibrary.find_asset_data(pathName)
    #     assetClass = importedData.get_class()
    #     if assetClass == unreal.SkeletalMesh:
    #         return imported

    return importTask.get_objects()[-1]

def ImportAnimation(mesh: unreal.SkeletalMesh, animPath):
    print(f"importing animation: {animPath}")
    importTask = CreateBaseImportTask(animPath)
    meshDir = os.path.dirname(mesh.get_path_name())
    importTask.destination_path = meshDir + "/Animations"
    print(f"importing into {importTask.destination_path}")

    importOptions = unreal.FbxImportUI()
    importOptions.import_mesh = False
    importOptions.import_as_skeletal = True
    importOptions.import_animations = True
    importOptions.skeleton = mesh.skeleton

    importOptions.set_editor_property('automated_import_should_detect_type', False)
    importOptions.set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    importOptions.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION)

    importTask.options = importOptions

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])
    for item in importTask.get_objects():
        print(f"imported: {item.get_path_name()}")  

def ImportMeshAndAnimation(meshPath, animDir):
    mesh = ImportSkeletalMesh(meshPath)
    print(mesh)
    for filename in os.listdir(animDir):
        if ".fbx" in filename:
            animPath = os.path.join(animDir, filename)
            ImportAnimation(mesh, animPath)

# ImportMeshAndAnimation("d:/profile redirect/armedin1/Desktop/Spring 2025/Tech Dec/Alex!!/MayaToUE File Export Tests/Alex_a.fbx", "d:/profile redirect/armedin1/Desktop/Spring 2025/Tech Dec/Alex!!/MayaToUE File Export Tests/Animations")