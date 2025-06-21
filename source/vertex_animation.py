from pathlib import Path

import bpy
from mathutils import Vector


def get_per_frame_mesh_data(context, mesh_object):
    """Return a list of combined mesh data per frame"""
    meshes = []
    for i in frame_range(context.scene):
        context.scene.frame_set(i)

        # Creates a new mesh data frm the evaluated mesh object
        eval_object = mesh_object.evaluated_get(context.evaluated_depsgraph_get())
        mesh_data = bpy.data.meshes.new_from_object(eval_object)
        # mesh_data.transform(mesh_object.matrix_world)
        mesh_data.name = f"{mesh_object.name}_frame_{i}"

        meshes.append(mesh_data)

    return meshes


def create_export_mesh_object(context, mesh_data):
    """Return a mesh object with correct UVs"""
    while len(mesh_data.uv_layers) < 2:
        mesh_data.uv_layers.new()
    uv_layer = mesh_data.uv_layers[1]

    uv_layer.name = "vertex_anim"
    for loop in mesh_data.loops:
        uv_layer.data[loop.index].uv = ((loop.vertex_index + 0.5) / len(mesh_data.vertices), 128 / 255)
    ob = bpy.data.objects.new("export_mesh", mesh_data)
    context.scene.collection.objects.link(ob)
    return ob


def get_vertex_data(mesh_per_frame):
    """Return lists of vertex offsets and normals from a list of mesh data"""
    original = mesh_per_frame[0].vertices
    offsets = []
    normals = []
    for mesh in reversed(mesh_per_frame):
        for v in mesh.vertices:
            offset = v.co - original[v.index].co
            x, y, z = offset
            # The order must be aligned with bpy.ops.export_scene.fbx
            offsets.extend((-y, z, x, 1))
            x, y, z = v.normal
            normals.extend(((x + 1) * 0.5, (-y + 1) * 0.5, (z + 1) * 0.5, 1))
    return offsets, normals


def frame_range(scene):
    """Return a range object with with scene's frame start, end, and step"""
    return range(scene.frame_start, scene.frame_end, scene.frame_step)


def bake_vertex_data(offsets, normals, size):
    """Stores vertex offsets and normals in seperate image textures"""

    width, height = size

    offset_texture = bpy.data.images.new(name="offsets", width=width, height=height, alpha=True, float_buffer=True)

    normal_texture = bpy.data.images.new(name="normals", width=width, height=height, alpha=True)

    offset_texture.pixels = offsets
    normal_texture.pixels = normals

    return offset_texture, normal_texture


def remove_debug_meshes(context):
    """Remove all debug meshes from the scene"""
    objects_to_remove = [ob for ob in context.scene.collection.objects if ob.name.startswith("__debug__")]
    for ob in objects_to_remove:
        context.scene.collection.objects.unlink(ob)
        bpy.data.objects.remove(ob, do_unlink=True)


def debug_create_meshes(context, mesh_object, mesh_per_frame):
    """Create debug meshes for each frame in the scene"""

    for i, mesh_data in enumerate(mesh_per_frame):
        name = f"__debug__{mesh_object.name}_{i:03d}"
        ob = bpy.data.objects.new(name, mesh_data)
        context.scene.collection.objects.link(ob)
        ob.location = mesh_object.location + Vector([1, 0, 0]) + Vector([0, 1, 0]) * i


def export_vertex_animation(context, mesh_object, export_path: Path):
    # Export the mesh data per frame
    mesh_per_frame = get_per_frame_mesh_data(context, mesh_object)
    frame_count = len(mesh_per_frame)
    vertex_count = len(mesh_per_frame[0].vertices)

    # This mesh contains the UV coordinates for the vertex animation
    mesh_to_export = create_export_mesh_object(context, mesh_per_frame[0].copy())
    offsets, normals = get_vertex_data(mesh_per_frame)

    # debug_create_meshes(context, mesh_object, mesh_per_frame)

    offset_texture, normal_texture = bake_vertex_data(offsets, normals, (vertex_count, frame_count))

    save_path = export_path / f"{mesh_object.name}_offsets.exr"
    offset_texture.file_format = "OPEN_EXR"

    with bpy.context.temp_override(edit_image=offset_texture):
        bpy.ops.image.save_as(
            filepath=str(save_path),
            save_as_render=True,
            check_existing=False,
            copy=True,
        )

    # for m in mesh_per_frame:
    #     bpy.data.meshes.remove(m)

    return mesh_to_export
