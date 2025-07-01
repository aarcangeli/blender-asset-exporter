import time
from pathlib import Path

import bpy

from .utils import run_in_object_mode, combine_children, relevant_objects, FT_VertexAnimation, \
    get_or_create_export_collection

from .vertex_animation import export_vertex_animation, remove_debug_meshes


class ExportAssets(bpy.types.Operator):
    bl_idname = "object.export_assets"
    bl_label = "Export Assets"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        start = time.time()
        props = context.scene.asset_settings

        bpy.context.workspace.status_text_set_internal("Exporting assets...")
        export_path = Path(bpy.path.abspath(props.export_path))

        remove_debug_meshes(context)

        count = 0
        for mesh_object in list_meshes():
            file_output = export_path / f"{mesh_object.name}.fbx"
            self.report({"INFO"}, f"Exporting mesh: '{mesh_object.name}' to '{file_output}'")
            count = count + 1

            props = mesh_object.export_properties

            with run_in_object_mode():
                temp_object = None

                # Rename the mesh object temporarily to avoid conflicts
                original_name = mesh_object.name
                original_object = mesh_object
                mesh_object.name = f"{original_name}__temp__"

                try:
                    # bpy.context.scene.frame_current = 0

                    if props.combine_child:
                        mesh_object = temp_object = combine_children(original_name, mesh_object)

                    if FT_VertexAnimation and props.vertex_animation:
                        # Experimental feature
                        mesh_object = export_vertex_animation(context, mesh_object, export_path)

                    bpy.ops.object.select_all(action="DESELECT")
                    mesh_object.select_set(True)

                    bpy.ops.export_scene.fbx(
                        filepath=str(file_output),
                        use_selection=True,
                        object_types={"MESH"},
                        apply_scale_options="FBX_SCALE_ALL",
                        bake_space_transform=True,
                        axis_forward="X",
                        axis_up="Y",
                    )

                finally:
                    if temp_object:
                        bpy.data.objects.remove(temp_object, do_unlink=True)
                    original_object.name = original_name

        elapsed = time.time() - start
        bpy.context.workspace.status_text_set_internal(f"Exported {count} meshes in {elapsed:.2f} seconds.")
        return {"FINISHED"}


def list_meshes():
    """List all meshes in the current Blender scene."""
    collection = get_or_create_export_collection()
    meshes = [obj for obj in collection.objects if obj.type in relevant_objects and obj.export_properties.enable_export]
    return sorted(meshes, key=lambda x: x.name.lower())
