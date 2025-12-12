import bpy

from .auto_reload import reload_recursively_from
from .armature_tools import armature_classes
from .properties import ExportSceneProperties, ObjectProperties
from .right_panel import VIEW3D_PT_GlobalSettings, VIEW3D_PT_AssetManager
from .export_meshes import ExportAssets
from .utils import auto_create_export_collection

operator_classes = [
    ExportAssets,
    VIEW3D_PT_GlobalSettings,
    VIEW3D_PT_AssetManager,
    ExportSceneProperties,
    ObjectProperties,
    *armature_classes,
]


def register():
    # Reload all modules, including this one
    reload_recursively_from(__name__)

    # Reload the new list of operator classes
    for cls in operator_classes:
        bpy.utils.register_class(cls)

    # Set up properties for the scene and objects
    bpy.types.Scene.asset_settings = bpy.props.PointerProperty(type=ExportSceneProperties)
    bpy.types.Object.export_properties = bpy.props.PointerProperty(type=ObjectProperties)

    # Ensure the Export collection exists
    bpy.app.timers.register(auto_create_export_collection, first_interval=0.1)


def unregister():
    for cls in reversed(operator_classes):
        bpy.utils.unregister_class(cls)
