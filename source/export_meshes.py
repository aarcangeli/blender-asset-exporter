import time
from pathlib import Path

import bpy

from .utils import run_in_object_mode


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

        bpy.context.scene.frame_current = 0
        bpy.context.workspace.status_text_set_internal("Exporting assets...")
        export_path = Path(bpy.path.abspath(props.export_path))

        count = 0
        for mesh in list_meshes():
            file_output = export_path / f"{mesh.name}.fbx"
            self.report({"INFO"}, f"Exporting mesh: '{mesh.name}' to '{file_output}'")
            count = count + 1

            with run_in_object_mode():
                bpy.ops.object.select_all(action="DESELECT")
                mesh.select_set(True)
                bpy.ops.export_scene.fbx(
                    filepath=str(file_output),
                    use_selection=True,
                    object_types={"MESH"},
                    apply_scale_options="FBX_SCALE_ALL",
                    bake_space_transform=True,
                    axis_forward="X",
                    axis_up="Y",
                )

        elapsed = time.time() - start
        bpy.context.workspace.status_text_set_internal(f"Exported {count} meshes in {elapsed:.2f} seconds.")
        return {"FINISHED"}


def list_meshes():
    """List all meshes in the current Blender scene."""
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.export_properties.enable_export]
    return sorted(meshes, key=lambda x: x.name.lower())
