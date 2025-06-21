import bpy

from .export_meshes import ExportAssets
from .utils import shelf_name


class VIEW3D_PT_AssetManager(bpy.types.Panel):
    """Shows a panel in the "Edit" tab of the 3D View"""

    bl_label = "Asset Exporter"
    bl_idname = "VIEW3D_PT_AssetManager"
    bl_category = shelf_name
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
            export_properties = obj.export_properties
            layout.prop(export_properties, "enable_export")

            layout = layout.column(align=True)
            layout.enabled = export_properties.enable_export
            layout.prop(export_properties, "vertex_animation")

            scene = context.scene
            layout.use_property_split = True
            layout.use_property_decorate = False
            col = layout.column(align=True)
            col.enabled = export_properties.vertex_animation
            col.prop(scene, "frame_start", text="Frame Start")
            col.prop(scene, "frame_end", text="End")
            col.prop(scene, "frame_step", text="Step")


def get_active_mesh():
    """Get the active mesh object in the scene."""
    if active_object := bpy.context.active_object:
        if active_object and active_object.type == "MESH" and active_object.select_get():
            return active_object
    return None
