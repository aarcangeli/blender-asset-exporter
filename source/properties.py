import bpy


class ExportSceneProperties(bpy.types.PropertyGroup):
    """
    Properties applied to the entire scene.
    Usage: context.scene.asset_settings.export_path
    """

    export_path: bpy.props.StringProperty(
        name="Output Path",
        description="Path to export assets to",
        default="//",
        subtype="DIR_PATH",
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

    vertex_animation: bpy.props.BoolProperty(
        name="Vertex Animation",
        description="Enable vertex animation export for this object",
        default=False,
    )
