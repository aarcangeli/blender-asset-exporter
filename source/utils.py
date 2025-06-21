from contextlib import contextmanager

import bpy

shelf_name = "Tools"


def show_message_box(message="", title="Message Box", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


@contextmanager
def run_in_object_mode():
    # Backup the current selection and active object
    selected_objects = [obj for obj in bpy.context.selected_objects]
    active_object = bpy.context.view_layer.objects.active
    mode = active_object.mode if active_object else "OBJECT"
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
