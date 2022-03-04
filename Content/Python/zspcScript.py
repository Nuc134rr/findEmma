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

#Psycho Prefix is retired
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

def batchAssetName(assetFolderName = 'Zauto', p='Zauto', u=True, ouw=False, assetType = 'Texture2D', enumerateDuplicates = False):

    if p == 'Zauto':
        if assetType == 'Texture2D':
            p = 'T'
        if assetType == 'Material':
            p = 'M'
        if assetType == 'MaterialInstanceConstant':
            p = 'MI'
        if assetType == 'StaticMesh':
            p = 'SM'
        if not u:
            p = p + '_'
    
    if assetFolderName == 'Zauto':
        if assetType == 'Texture2D':
            assetFolderName = 'Textures'
        if assetType == 'Material' or assetType == 'MaterialInstanceConstant':
            assetFolderName = 'Materials'
        if assetType == 'StaticMesh':
            assetFolderName = 'Meshes'

    #Prefix setup
    if p == '':
        unreal.log_error("Correct syntax: zspcScript.batchAssetName(p='<PREFIX>'')")
        exit
    
    lastChar = p[-1]
    if u == True:
        if lastChar == '_':
            if not ouw:
                unreal.log_error('Duplicate underscores for the prefix! No need to add an underscore at the end of the prefix!')
                unreal.log_error('(To add a prefix without an automatic underscore, add u=False in the parenthesis of the command)')
                unreal.log_error('To override this error and add multiple underscores, add the argument ouw=False')
                exit()
            else:
                unreal.log_error('Duplicate underscores added in the prefix! No need to add an underscore at the end of the prefix!')
                unreal.log_warning('(To add a prefix without an automatic underscore, add u=False in the parenthesis of the command)')
        prefix = p + '_'
    else:
        prefix = p
    
    selectedFolders = unreal.ZspcCpp.get_selected_folders()
    validAssetTypes = ['Texture2D', 'Material', 'StaticMesh', 'MaterialInstanceConstant']

    if not assetType in validAssetTypes:
        unreal.log_error('Invalid assetType, currently supported types are Texture2D, Material, StaticMesh, and MaterialInstanceConstant')
        exit()

    #Substrings that identify a type of texture
    validTextureTypes = ["BaseColor", "Albedo", "Base_Color", "Diffuse",
                  "Normal",
                  "_ORM", "OcclusionRoughnessMetallic", "Occlusion_Roughness_Metallic",
                  "Roughness",
                  "Opacity"]

    #Substrings that identify a specific type of texture
    BaseColorSubstrings = ["BaseColor", "Albedo", "Base_Color", "Diffuse"] 
    NormalSubstrings = ["Normal"]
    OrmSubstrings = ["_ORM", "OcclusionRoughnessMetallic", "Occlusion_Roughness_Metallic"]
    RoughnessSubstrings = ["Roughness"]
    OpacitySubstrings = ["Opacity"]

    noTypeTextures = []
    validAssets = []
    duplicateTypeTextures = []
    duplicateAssets = []

    if selectedFolders == []:
        unreal.log_error('Select folder(s) in the content browser!')
        exit()

    subFolders=[]
    #List of disk paths for subfolders
    subFoldersDisk = unreal.ZspcCpp.get_sub_folders_paths_of_selected_folders()

    #If there are no subfolders the operable folders are just the selected ones, if there are the operable folders are the selected folders and their subfolders
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
                if asset.asset_class == assetType:
                    if assetType == 'Texture2D':
                        if any(substring.lower() in assetNameStr.lower() for substring in validTextureTypes):
                            if assetFolderName in str(asset.object_path):
                                validAssets.append(asset)
                            else:
                                unreal.log_warning("ASSET OUTSIDE OF SPECIFIED FOLDER: " + str(asset.asset_name))
                        else:
                            noTypeTextures.append(asset)
                    else:
                        if assetFolderName in str(asset.object_path):
                                validAssets.append(asset)
                        else:
                            unreal.log_warning("ASSET OUTSIDE OF SPECIFIED FOLDER: " + str(asset.asset_name))

    for valid in validAssets:
        objPathStr = str(valid.object_path).rsplit('.', 1)[0]
        assetNameStr = str(valid.asset_name)
        if assetType == 'Texture2D':
            if any(substring.lower() in assetNameStr.lower() for substring in BaseColorSubstrings):
                validType = 'BaseColor'
            if any(substring.lower() in assetNameStr.lower() for substring in NormalSubstrings):
                validType = 'Normal'
            if any(substring.lower() in assetNameStr.lower() for substring in OrmSubstrings):
                validType = 'OcclusionRoughnessMetallic'
            if any(substring.lower() in assetNameStr.lower() for substring in RoughnessSubstrings):
                if not any(substring.lower() in assetNameStr.lower() for substring in OrmSubstrings): #Prevent ORM being overridden by roughness
                    validType = 'Roughness'
            if any(substring.lower() in assetNameStr.lower() for substring in OpacitySubstrings):
                validType = 'Opacity'
        else:
            validType = ''
        
        parentFolder = (objPathStr.rsplit('/', 1)[0]).rsplit('/', 1)[1]
        if not parentFolder == assetFolderName:
            iterInt = 2
            scanFolder = ''
            while not scanFolder == assetFolderName:
                scanFolder = (objPathStr.rsplit('/', iterInt)[0]).rsplit('/', 1)[1]
                if not scanFolder == assetFolderName:
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
        if not validType == '':
            underscoreValidType = '_' + validType
        else:
            underscoreValidType = ''
        NewName = prefix + BaseName + underscoreValidType
        unreal.log('Renaming: ' + str(valid.asset_name) + ' ---> ' + NewName)
        newPath = objPathStr.rsplit('/', 1)[0] + '/' + NewName
        newPathEmpty = not (unreal.EditorAssetLibrary.does_asset_exist(newPath))
        if newPathEmpty:
            unreal.EditorAssetLibrary.rename_asset(objPathStr, newPath)
        else:
            if enumerateDuplicates:
                newEnumeratedPathEmpty = False
                iterInt_1 = 1
                while not newEnumeratedPathEmpty:
                    enumeratedPath = newPath + '_' + str(iterInt_1)
                    newEnumeratedPathEmpty = not (unreal.EditorAssetLibrary.does_asset_exist(enumeratedPath))
                    iterInt_1 += 1
                unreal.EditorAssetLibrary.rename_asset(objPathStr, enumeratedPath)
            else:
                if assetType == 'Texture2D':
                    duplicateTypeTextures.append(valid)
                else:
                    duplicateAssets.append(valid)

    for i in noTypeTextures:
        unreal.log_warning("MANUALLY RENAME: '{}', ".format(str(i.asset_name)) + " PATH: {}".format(str(i.object_path).rsplit('.', 1)[0]))
    
    for i in duplicateTypeTextures:
        unreal.log_warning("DUPLICATE TEXTURE TYPES WITHOUT SUBFOLDERS OR ASSET ALREADY PROPERLY NAMED, '{}' NEEDS MANUAL ATTENTION! PATH: {}".format(i.asset_name, i.object_path))
    for i in duplicateAssets:
        unreal.log_warning("DUPLICATE ASSETS WITHOUT SUBFOLDERS OR ASSET ALREADY PROPERLY NAMED, '{}' NEEDS MANUAL ATTENTION! PATH: {}".format(i.asset_name, i.object_path))


def changeMaker(targetClass='Texture2D'):
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
                        objectPathStr = str(asset.object_path)
                        assetObj = unreal.EditorAssetLibrary.load_asset(objectPathStr)
                        if asset.asset_class == 'Texture2D':
                            changeValue = assetObj.get_editor_property("never_stream")
                            changeValue_reverse = not changeValue
                            unreal.log_warning('srgb = ' + str(changeValue))
                            unreal.log_warning('srgb /= ' + str(changeValue_reverse))
                            unreal.log_warning('assetObj = ' + str(assetObj))
                            assetObj.set_editor_property("never_stream", changeValue_reverse)
                            unreal.EditorAssetLibrary.save_asset(objectPathStr)
                            assetObj.set_editor_property("never_stream", changeValue)
                            unreal.EditorAssetLibrary.save_asset(objectPathStr)