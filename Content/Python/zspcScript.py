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
                iterSuffix = nameStr.rsplit('_', 1)[1]
                if iterSuffix == 'Albedo' or iterSuffix == 'albedo' or iterSuffix == 'BaseColor' or iterSuffix == 'basecolor':
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
                iterSuffix = nameStr.rsplit('_', 1)[1]
                if iterSuffix == 'Albedo' or iterSuffix == 'albedo' or iterSuffix == 'BaseColor' or iterSuffix == 'basecolor':
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