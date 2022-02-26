#from importlib import *
#reload(zspcScript)

from contextlib import AsyncExitStack
from subprocess import NORMAL_PRIORITY_CLASS
import unreal
import re

def autoPBR(createMaterial = True):
    #with unreal.ScopedEditorTransaction("My Transaction Test") as trans: #Make undoable transaction
    albedoTexture = unreal.AssetData('')
    normalTexture = unreal.AssetData('')
    ormTexture = unreal.AssetData('')

    selection = unreal.EditorUtilityLibrary.get_selected_asset_data()
    if createMaterial == True:
        if len(selection) != 3 or any(a.asset_class != 'Texture2D' for a in selection):
            unreal.log_error('Select 3 textures!')
        else:
            prefixList = []
            for i in selection:
                nameStr = str(i.asset_name)
                prefix = nameStr[:2]
                #name = unreal.Name(nameStr)
                prefixList.append(prefix)
                unreal.log(nameStr)
                if 'Base_Color' in nameStr or 'base_color' in nameStr or 'Base_color' in nameStr:
                    iterSuffix = nameStr.rsplit('_', 2)[1] + '_' + nameStr.rsplit('_', 1)[1]
                else:
                    iterSuffix = nameStr.rsplit('_', 1)[1]
                unreal.log(iterSuffix)
                if iterSuffix == 'Albedo' or iterSuffix == 'albedo' or iterSuffix == 'BaseColor' or iterSuffix == 'basecolor' or iterSuffix == 'Base_Color' or iterSuffix == 'base_color' or iterSuffix == 'Base_color':
                    albedoTexture = i
                if iterSuffix == 'Normal' or iterSuffix == 'normal':
                    normalTexture = i
                if iterSuffix == 'ORM' or iterSuffix == 'orm' or iterSuffix == 'OcclusionRoughnessMetallic' or iterSuffix == 'occlusionroughnessmetallic':
                    ormTexture = i

            if albedoTexture.asset_name == '' or ormTexture.asset_name == '' or normalTexture.asset_name == '':
                unreal.log('Select textures with "_Normal", "_ORM"/"_OcclusionRoughnessMetallic", and "_Albedo"/"_BaseColor" as their suffixes!')
            else:
                tPrefixCount = prefixList.count('T_')
                firstObjectNameStr = str(selection[0].asset_name)
                suffix = firstObjectNameStr.rsplit('_', 1)[1]
                startSubString = 'T_'
                endSubString = '_' + suffix
                objectName = firstObjectNameStr[firstObjectNameStr.find(startSubString)+len(startSubString):firstObjectNameStr.rfind(endSubString)]
                matName = 'M_' + objectName
                matPath = str(selection[0].object_path).rsplit('/', 1)[0]

                if not tPrefixCount == 3:
                    unreal.log_error('Selected textures must have the prefix "T_"!')
                else:
                    unreal.log('Automatically setting up PBR Material...')
                    assetTools = unreal.AssetToolsHelpers.get_asset_tools()
                    mf = unreal.MaterialFactoryNew()
                    mat_closure = assetTools.create_asset(matName, matPath, unreal.Material, mf)
                    print(mat_closure)

                    ts_node_albedo = unreal.MaterialEditingLibrary.create_material_expression(mat_closure,unreal.MaterialExpressionTextureSample,-384,-200)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_albedo, "RGBA", unreal.MaterialProperty.MP_BASE_COLOR)
                    ts_node_albedo.texture = albedoTexture.get_asset()

                    ts_node_normal = unreal.MaterialEditingLibrary.create_material_expression(mat_closure,unreal.MaterialExpressionTextureSample,-384,-200)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
                    ts_node_normal.sampler_type = unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
                    ts_node_normal.texture = normalTexture.get_asset()

                    ts_node_orm = unreal.MaterialEditingLibrary.create_material_expression(mat_closure,unreal.MaterialExpressionTextureSample,-384,-200)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_orm, "B", unreal.MaterialProperty.MP_METALLIC)
                    ts_node_orm.sampler_type = unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
                    ts_node_orm.texture = ormTexture.get_asset()
                    
    else:
        #if len(selection) != 4:
        selectionAssetClass = []
        for i in selection:
            selectionAssetClass.append(i.asset_class)
            if i.asset_class == 'Material':
                mat_closure = i.get_asset()

        assetClassDict = {a:selectionAssetClass.count(a) for a in selectionAssetClass}
        print(assetClassDict)

        proceed = True

        for assetClass, count in assetClassDict.items(): #assetclass = key, count = value
            if assetClass == 'Texture2D':
                if assetClassDict.get(assetClass) == 3:
                    pass
                else:
                    proceed = False
                    unreal.log_error('You must select 3 Textures!')
            if assetClass == 'Material':
                if assetClassDict.get(assetClass) == 1:
                    pass
                else:
                    proceed = False
                    unreal.log_error('You must select 1 Material!')                    
            if len(assetClassDict.keys()) == 2:
                pass
            else:
                proceed = False
                unreal.log_error('You must select 3 Textures and 1 Material!')

        if proceed:
            prefixList = []
            for i in selection:
                nameStr = str(i.asset_name)
                prefix = nameStr[:2]
                #name = unreal.Name(nameStr)
                prefixList.append(prefix)
                if 'Base_Color' in nameStr or 'base_color' in nameStr or 'Base_color' in nameStr:
                    iterSuffix = nameStr.rsplit('_', 2)[1] + '_' + nameStr.rsplit('_', 1)[1]
                else:
                    iterSuffix = nameStr.rsplit('_', 1)[1]
                if iterSuffix == 'Albedo' or iterSuffix == 'albedo' or iterSuffix == 'BaseColor' or iterSuffix == 'basecolor' or iterSuffix == 'Base_Color' or iterSuffix == 'base_color' or iterSuffix == 'Base_color':
                    albedoTexture = i
                if iterSuffix == 'Normal' or iterSuffix == 'normal':
                    normalTexture = i
                if iterSuffix == 'ORM' or iterSuffix == 'orm' or iterSuffix == 'OcclusionRoughnessMetallic' or iterSuffix == 'occlusionroughnessmetallic':
                    ormTexture = i

            if albedoTexture.asset_name == '' or ormTexture.asset_name == '' or normalTexture.asset_name == '':
                unreal.log('Select textures with "_Normal", "_ORM"/"_OcclusionRoughnessMetallic", and "_Albedo"/"_BaseColor" as their suffixes!')
            else:
                tPrefixCount = prefixList.count('T_')
                mPrefixCount = prefixList.count('M_')
                firstObjectNameStr = str(selection[0].asset_name)
                suffix = firstObjectNameStr.rsplit('_', 1)[1]
                startSubString = 'T_'
                endSubString = '_' + suffix
                objectName = firstObjectNameStr[firstObjectNameStr.find(startSubString)+len(startSubString):firstObjectNameStr.rfind(endSubString)]
                matName = 'M_' + objectName
                matPath = str(selection[0].object_path).rsplit('/', 1)[0]

                if not tPrefixCount == 3 and mPrefixCount == 1:
                    unreal.log_error('Selected textures must have the prefix "T_"!')
                else:
                    unreal.log('Automatically setting up PBR Material...')
                    #mat_closure = 

                    ts_node_albedo = unreal.MaterialEditingLibrary.create_material_expression(mat_closure,unreal.MaterialExpressionTextureSample,-384,-200)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_albedo, "RGBA", unreal.MaterialProperty.MP_BASE_COLOR)
                    ts_node_albedo.texture = albedoTexture.get_asset()

                    ts_node_normal = unreal.MaterialEditingLibrary.create_material_expression(mat_closure,unreal.MaterialExpressionTextureSample,-384,-200)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
                    ts_node_normal.sampler_type = unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
                    ts_node_normal.texture = normalTexture.get_asset()

                    ts_node_orm = unreal.MaterialEditingLibrary.create_material_expression(mat_closure,unreal.MaterialExpressionTextureSample,-384,-200)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
                    unreal.MaterialEditingLibrary.connect_material_property(ts_node_orm, "B", unreal.MaterialProperty.MP_METALLIC)
                    ts_node_orm.sampler_type = unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
                    ts_node_orm.texture = ormTexture.get_asset()

def addPrefix(p='', u=True):
    if p == '':
        unreal.log_error("Correct syntax: zspcScript.addPrefix(p='<PREFIX>'')")
    else:
        lastChar = p[-1]
        if u == True:
            if lastChar == '_':
                unreal.log_warning('Duplicate underscores added to name! No need to add an underscore at the end of the name!')
                unreal.log_warning('(To add a prefix without an automatic underscore, add u=False in the parenthesis of the command)')
            prefix = p + '_'
        else:
            prefix = p
        selection = unreal.EditorUtilityLibrary.get_selected_asset_data()

        if selection == []:
            unreal.log_error('Select assets in the content browser!')
        else:
            for i in selection:
                assetName = str(i.asset_name)
                newName = prefix + assetName    
                objectPathStr = str(i.object_path)
                newPath = objectPathStr.rsplit('/', 1)[0] + '/' + newName
                unreal.log_warning(objectPathStr)
                with unreal.ScopedEditorTransaction("Batch Prefix") as trans: #Make undoable transaction
                    unreal.EditorAssetLibrary.rename_asset(objectPathStr, newPath)
            
def psychoPrefix(p='', u=True, targetClass='Texture2D'): #Get folders: unreal.ZspcCpp.get_selected_folders() #Get All Subfolders Paths: unreal.ZspcCpp.get_sub_folders_paths_of_selected_folders() #Disk Path To Game Path: unreal.ZspcCpp.disk_path_to_game_path(<diskPath>)
    if p == '':
        unreal.log_error("Correct syntax: zspcScript.addPrefix(p='<PREFIX>'')")
    else:
        lastChar = p[-1]
        if u == True:
            if lastChar == '_':
                unreal.log_warning('Duplicate underscores added to name! No need to add an underscore at the end of the name!')
                unreal.log_warning('(To add a prefix without an automatic underscore, add u=False in the parenthesis of the command)')
            prefix = p + '_'
        else:
            prefix = p
        selectedFolders = unreal.ZspcCpp.get_selected_folders()

        if selectedFolders == []:
            unreal.log_error('Select folder(s) in the content browser!')
        else:
            subFolders=[]
            subFoldersDisk = unreal.ZspcCpp.get_sub_folders_paths_of_selected_folders()

            if subFoldersDisk == []:
                allFolders = selectedFolders
            else:
                for i in subFoldersDisk:
                    currentGamePath = unreal.ZspcCpp.disk_path_to_game_path(i)
                    subFolders.append(currentGamePath)
                allFolders = selectedFolders + subFolders

            for i in allFolders:
                asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
                assets = asset_reg.get_assets_by_path(i)
                if assets == []:
                    #unreal.log_warning("EMPTY FOLDER")
                    pass
                else:
                    for asset in assets:
                        if asset.asset_class == targetClass:
                            if str(asset.asset_name)[:len(prefix)] == prefix:
                                print('Matches already!')
                            else:
                                assetName = str(asset.asset_name)
                                newName = prefix + assetName
                                objectPathStr = str(asset.object_path)
                                newPath = objectPathStr.rsplit('/', 1)[0] + '/' + newName
                                unreal.EditorAssetLibrary.rename_asset(objectPathStr, newPath)
                #for asset in assets:
                #    print(asset)
                # assetName = str(i.asset_name)
                # newName = prefix + assetName
                # objectPathStr = str(i.object_path)
                # newPath = objectPathStr.rsplit('/', 1)[0] + '/' + newName
                # with unreal.ScopedEditorTransaction("Batch Prefix") as trans: #Make undoable transaction
                #     unreal.EditorAssetLibrary.rename_asset(objectPathStr, newPath)

def textureManage(textureFolderName = 'Textures'):
    selectedFolders = unreal.ZspcCpp.get_selected_folders()

    validTypes = ["BaseColor", "Albedo", "Base_Color", "Diffuse",
                  "Normal",
                  "_ORM", "OcclusionRoughnessMetallic", "Occlusion_Roughness_Metallic",
                  "Roughness",
                  "Opacity"]

    BaseColorTypes = ["BaseColor", "Albedo", "Base_Color", "Diffuse"]
    NormalTypes = ["Normal"]
    OrmTypes = ["_ORM", "OcclusionRoughnessMetallic", "Occlusion_Roughness_Metallic"]
    RoughnessTypes = ["Roughness"]
    OpacityTypes = ["Opacity"]

    noTypeTextures = []
    validTextures = []
    duplicateTypeTextures = []

    if selectedFolders == []:
        unreal.log_error('Select folder(s) in the content browser!')
    else:
        subFolders=[]
        subFoldersDisk = unreal.ZspcCpp.get_sub_folders_paths_of_selected_folders()

        if subFoldersDisk == []:
            allFolders = selectedFolders
        else:
            for i in subFoldersDisk:
                currentGamePath = unreal.ZspcCpp.disk_path_to_game_path(i)
                subFolders.append(currentGamePath)
            allFolders = selectedFolders + subFolders

        for i in allFolders:
            asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
            assets = asset_reg.get_assets_by_path(i)
            if assets == []:
                pass
            else:
                for asset in assets:
                    assetNameStr = str(asset.asset_name)
                    if asset.asset_class == 'Texture2D':
                        if any(substring.lower() in assetNameStr.lower() for substring in validTypes):
                            if 'Textures' in str(asset.object_path):
                                validTextures.append(asset)
                            else:
                                unreal.log_warning("TEXTURE OUTSIDE OF TEXTURES FOLDER: " + str(asset.asset_name))
                        else:
                            noTypeTextures.append(asset)

        for valid in validTextures:
            objPathStr = str(valid.object_path).rsplit('.', 1)[0]
            assetNameStr = str(valid.asset_name)
            if any(substring.lower() in assetNameStr.lower() for substring in BaseColorTypes):
                validType = 'BaseColor'
            if any(substring.lower() in assetNameStr.lower() for substring in NormalTypes):
                validType = 'Normal'
            if any(substring.lower() in assetNameStr.lower() for substring in OrmTypes):
                validType = 'OcclusionRoughnessMetallic'
            if any(substring.lower() in assetNameStr.lower() for substring in RoughnessTypes):
                if not any(substring.lower() in assetNameStr.lower() for substring in OrmTypes): #Prevent ORM being overridden by roughness
                    validType = 'Roughness'
            if any(substring.lower() in assetNameStr.lower() for substring in OpacityTypes):
                validType = 'Opacity'
            
            parentFolder = (objPathStr.rsplit('/', 1)[0]).rsplit('/', 1)[1]
            if not parentFolder == textureFolderName:
                iterInt = 2
                scanFolder = ''
                while not scanFolder == textureFolderName:
                    scanFolder = (objPathStr.rsplit('/', iterInt)[0]).rsplit('/', 1)[1]
                    if not scanFolder == textureFolderName:
                        iterInt += 1
                AssetName = (objPathStr.rsplit('/', iterInt + 1)[0]).rsplit('/', 1)[1]
                subFolderNameList = []
                for i in reversed(range(iterInt - 1)):
                    subFolderNameList.append((objPathStr.rsplit('/', i + 1)[0]).rsplit('/', 1)[1])
                subFolderNameList_i = ['_'] * (len(subFolderNameList) * 2 - 1)
                subFolderNameList_i[0::2] = subFolderNameList
                subFoldersName = ''.join(subFolderNameList_i)
                BaseName = AssetName + '_' + subFoldersName
            else:
                AssetName = (objPathStr.rsplit('/', 2)[0]).rsplit('/', 1)[1]
                BaseName = AssetName
            NewName = 'T_' + BaseName + '_' + validType
            unreal.log('Renaming: ' + str(valid.asset_name) + ' ---> ' + NewName)
            newPath = objPathStr.rsplit('/', 1)[0] + '/' + NewName
            newPathEmpty = not (unreal.EditorAssetLibrary.does_asset_exist(newPath))
            if newPathEmpty:
                unreal.EditorAssetLibrary.rename_asset(objPathStr, newPath)
            else:
                duplicateTypeTextures.append(valid)

        for i in noTypeTextures:
            unreal.log_warning("MANUALLY RENAME: '{}', ".format(str(i.asset_name)) + " PATH: {}".format(str(i.object_path).rsplit('.', 1)[0]))
        
        for i in duplicateTypeTextures:
            unreal.log_warning("DUPLICATE TYPES WITHOUT SUBFOLDERS, '{}' MUST BE MANUALLY RENAMED! PATH: {}".format(i.asset_name, i.object_path))