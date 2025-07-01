from contextlib import contextmanager

import bpy
import bmesh

shelf_name = "Tools"
relevant_objects = ["MESH", "EMPTY"]
temp_suffix = "__temp__"

FT_VertexAnimation = False


def show_message_box(message="", title="Message Box", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


@contextmanager
def run_in_object_mode(enabled=True):
    if not enabled:
        yield
        return

    # Backup the current selection and active object
    selected_objects = [obj for obj in bpy.context.selected_objects]
    active_object = bpy.context.view_layer.objects.active
    mode = active_object.mode if active_object else "OBJECT"
    bpy.ops.object.select_all(action="DESELECT")
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    old_frame = bpy.context.scene.frame_current

    yield

    bpy.ops.object.select_all(action="DESELECT")

    for obj in selected_objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = active_object
    if active_object and active_object.mode != mode:
        bpy.ops.object.mode_set(mode=mode)

    bpy.context.scene.frame_current = old_frame


@contextmanager
def set_temp_name(object):
    original_name = object.name
    if temp_suffix not in original_name:
        object.name = f"{original_name}{temp_suffix}"
    try:
        yield object
    finally:
        object.name = original_name


def remove_temp_name(name):
    return name.replace(temp_suffix, "")


def get_with_children(data_object):
    """
    Selects all child meshes of a given parent object.
    """

    result = []
    if data_object.type == "MESH":
        result.append(data_object)
    result.extend([parent for parent in data_object.children_recursive if parent.type == "MESH"])
    return result


def combine_children(name: str, mesh_object):
    """
    Combines multiple mesh objects into a single mesh object.
    """

    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()

    for child in get_with_children(mesh_object):
        eval_object = child.evaluated_get(depsgraph)
        it_data = bpy.data.meshes.new_from_object(eval_object)
        it_data.transform(child.matrix_world)
        it_data.transform(mesh_object.matrix_world.inverted())
        bm.from_mesh(it_data)
        bpy.data.meshes.remove(it_data)

    mesh_data = bpy.data.meshes.new("combined_mesh")
    bm.normal_update()
    bm.to_mesh(mesh_data)
    bm.free()
    mesh_data.update()

    ob = bpy.data.objects.new(name, mesh_data)
    bpy.context.scene.collection.objects.link(ob)
    return ob

def get_or_create_export_collection():
    """
    Gets or creates the export collection in the current Blender scene.
    """
    collection = bpy.data.collections.get("Export")
    if not collection:
        collection = bpy.data.collections.new("Export")
        bpy.context.scene.collection.children.link(collection)
    return collection
