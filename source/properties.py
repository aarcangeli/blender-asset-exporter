import os

import bpy

from .utils import clean_dir_name


def set_clean_path(self, new_path, use_relative):
    export_path = new_path

    if use_relative:
        export_path = bpy.path.relpath(export_path)
        export_path = export_path.replace("\\", "/")
    else:
        export_path = bpy.path.abspath(export_path)
        export_path = export_path.replace("\\", os.path.sep)
        export_path = export_path.replace("/", os.path.sep)

    self["export_path"] = clean_dir_name(export_path)


def update_path(self, new_path):
    use_relative = self.use_relative_path

    if use_relative and not new_path.startswith("//"):
        use_relative = False

    set_clean_path(self, new_path, use_relative)


class ExportSceneProperties(bpy.types.PropertyGroup):
    """
    Properties applied to the entire scene.
    Usage: context.scene.asset_settings.export_path
    """

    export_path: bpy.props.StringProperty(
        name="Output Path",
        description="Path to export assets to",
        options={"PATH_SUPPORTS_BLEND_RELATIVE"},
        default="//",
        subtype="DIR_PATH",
    )

    use_relative_path: bpy.props.BoolProperty(
        name="Use Relative Path",
        default=True,
        description="Use relative path for export",
        get=lambda self: self.export_path.startswith("//"),
        set=lambda self, value: set_clean_path(self, self.export_path, value),
    )

    # Duplicate property for custom get/set behavior
    export_path_prop: bpy.props.StringProperty(
        name="Output Path",
        description="Path to export assets to",
        options={"PATH_SUPPORTS_BLEND_RELATIVE"},
        default="//",
        subtype="DIR_PATH",
        get=lambda self: self.export_path,
        set=lambda self, value: update_path(self, value),
    )


class ObjectProperties(bpy.types.PropertyGroup):
    """
    Properties applied to the entire scene.
    Usage: context.scene.asset_settings.export_path
    """

    enable_export: bpy.props.BoolProperty(
        name="Enable Export",
        description="Enable export for this object",
        default=False,
    )

    combine_child: bpy.props.BoolProperty(
        name="Combine child meshes",
        description="Combine child meshes into a single mesh for export",
        default=False,
    )

    vertex_animation: bpy.props.BoolProperty(
        name="Vertex Animation",
        description="Enable vertex animation export for this object",
        default=False,
    )
