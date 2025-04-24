import unreal
import os

def ImportMeshAndAnimation(meshPath, animDir):
    print(f"loading files: {meshPath} and animations in {animDir}")
    importTask = unreal.AssetImportTask()
    importTask.filename = meshPath

    fileName = os.path.basename(meshPath).split(".")[0]
    importTask.destination_path = '/Game/' + fileName
    importTask.automated = True
    importTask.save = True
    importTask.replace_existing = True

    importOption = unreal.FbxImportUI()
    importOption.import_mesh = True
    importOption.import_as_skeletal = True

    #tells unreal to import blendshapes
    importOption.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)

    #tells unreal to use frame 0 as default pose
    importOption.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', True)

    importTask.options = importOption

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])

ImportMeshAndAnimation("d:/profile redirect/armedin1/Desktop/Spring 2025/Tech Dec/Alex!!/MayaToUE File Export Tests/Alex.fbx", "d:/profile redirect/armedin1/Desktop/Spring 2025/Tech Dec/Alex!!/MayaToUE File Export Tests/Animations")