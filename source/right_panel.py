import bpy

from .export_meshes import ExportAssets


class VIEW3D_PT_AssetManager(bpy.types.Panel):
    """Shows a panel in the "Edit" tab of the 3D View"""

    bl_label = "Unity Asset"
    bl_idname = "VIEW3D_PT_AssetManager"
    bl_category = "Asset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = set()

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        props = context.scene.asset_settings

        layout = self.layout
        layout.column(align=True)

        layout.label(text="Unity Asset Export", icon="EXPORT")

        layout.operator(ExportAssets.bl_idname)
        layout.prop(props, "export_path")

        if obj := get_active_mesh():
            layout.separator()
            layout.label(text=obj.name, icon="OBJECT_DATA")
            layout.prop(obj.export_properties, "enable_export", text="Enable Export")


def get_active_mesh():
    """Get the active mesh object in the scene."""
    if active_object := bpy.context.active_object:
        if active_object and active_object.type == "MESH" and active_object.select_get():
            return active_object
    return None
