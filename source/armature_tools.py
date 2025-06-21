import math

import bpy
import bmesh
from mathutils import Vector
import sys
import time

from .utils import shelf_name

# Options
last_print = 0


def single_element(seq):
    """Utility function to assert that a sequence has only one element"""

    assert len(seq) == 1, f"Expected a single element, got {len(seq)} elements"
    return seq[0]


class AT_Constraint_Toogle(bpy.types.Operator):
    """Constraint Toogle"""

    bl_idname = "blendertools.toogle_constraint"
    bl_label = "Toogle Constraints"
    bl_options = {"REGISTER", "UNDO"}

    mute: bpy.props.BoolProperty()
    use_selected: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones is not None

    def execute(self, context):
        if self.use_selected:
            target_bones = context.selected_pose_bones
        else:
            for obj in context.selected_objects:
                if obj.type == "ARMATURE":
                    target_bones = obj.pose.bones

        for bone in target_bones:
            for constraint in bone.constraints:
                constraint.mute = self.mute

        return {"FINISHED"}


def dot_product_edges(edge1, edge2):
    """Calculate the abs dot product between two edges"""

    dir1 = (edge1.verts[1].co - edge1.verts[0].co).normalized()
    dir2 = (edge2.verts[1].co - edge2.verts[0].co).normalized()

    # dot product
    return abs(dir1.dot(dir2))


def update_progress(job_title, progress):
    global last_print
    if time.time() - last_print < 0.1 and progress < 1:
        return
    last_print = time.time()

    length = 20  # modify this to change the length
    block = int(round(length * progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "#" * block + "-" * (length - block), round(progress * 100, 2))
    if progress >= 1:
        msg += " DONE\r\n"
    sys.stdout.write(msg)
    sys.stdout.flush()


class AT_SymmetrizeTool(bpy.types.Operator):
    """Symmetrize Tool"""

    bl_idname = "blendertools.symmetrize"
    bl_label = "Symmetrize"
    bl_options = {"REGISTER", "UNDO"}

    tolerance: bpy.props.FloatProperty(
        name="Tolerance",
        description="Tolerance",
        default=0.001,
    )

    @classmethod
    def poll(cls, context):
        return context.edit_object is not None and context.edit_object.type == "MESH"

    def execute(self, context):
        obj = context.edit_object

        print("=== Symmetrize Start ===")
        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        # Get UV layer
        if len(obj.data.uv_layers) == 0:
            self.report({"ERROR"}, "No UV layer found")
            return {"CANCELLED"}
        uv_layer = bm.loops.layers.uv.active
        self.report({"INFO"}, f"UV layer: {uv_layer.name}")

        def get_uv(vert):
            uv_values = []
            for loop in vert.link_loops:
                uv_values.append(loop[uv_layer].uv)
            assert len(uv_values) > 0, "No loop found"
            return sum(uv_values, Vector((0, 0))) / len(uv_values)

        selected_verts = [v for v in bm.verts if v.select and v.co.x <= self.tolerance]

        all_uvs = [get_uv(v) for v in bm.verts]

        count_matched = 0
        count_unmatched = 0
        bpy.ops.mesh.select_all(action="DESELECT")
        for (
            i,
            v,
        ) in enumerate(selected_verts):
            update_progress("Symmetrize", i / len(selected_verts))

            uv = all_uvs[v.index]

            # If the uv is in the center, move the vertex to the center
            if math.isclose(uv.x, 0.5, abs_tol=self.tolerance):
                v.co.x = 0
                continue

            # Find a vertex with the same uv
            expected_uv = Vector((1 - uv.x, uv.y))
            similiar_verts = [
                v2 for v2 in bm.verts if v2 != v and (all_uvs[v2.index] - expected_uv).length < self.tolerance
            ]
            if len(similiar_verts) >= 1:
                # Find the closest one
                similiar_verts.sort(key=lambda v2: (all_uvs[v2.index] - expected_uv).length)

                v2 = similiar_verts[0]
                v.co = Vector((-v2.co.x, v2.co.y, v2.co.z))
                count_matched += 1
            else:
                count_unmatched += 1
                v.select = True

        update_progress("Symmetrize", 1)

        self.report({"INFO"}, f"Matched: {count_matched}, Unmatched: {count_unmatched}")

        # Find all vertices that are on the center line
        bmesh.update_edit_mesh(obj.data)
        return {"CANCELLED"}


class AT_TrisToQuads(bpy.types.Operator):
    """Tris to Quads"""

    bl_idname = "blendertools.tris_to_quads"
    bl_label = "Tris to Quads"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.edit_object is not None and context.edit_object.type == "MESH"

    def execute(self, context):
        obj = context.edit_object

        print("=== Tris to Quads Start ===")
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        if bm.select_history.active is None:
            self.report({"ERROR"}, "No active edge found")
            return {"CANCELLED"}

        # This set contains all the edges that cannot be dissolved
        confirmed_edges = set()
        for edge in bm.edges:
            if edge.select:
                confirmed_edges.add(edge)

        # This list contains all the edges that should be selected at the end of the operation
        edges_to_select = set()

        # This set contains all the edges that should be dissolved at the end of the operation
        edges_to_dissolve = set()

        active_edge = bm.select_history.active
        bpy.ops.mesh.select_all(action="DESELECT")

        # Start from the active edge
        remaining_edges = [active_edge]
        while len(remaining_edges) > 0:
            edge = remaining_edges.pop()
            confirmed_edges.add(edge)
            print("Edge: ", edge)
            for face in list(edge.link_faces):
                if not face.is_valid:
                    continue

                def not_near_current_edge(e):
                    for v in e.verts:
                        if v in edge.verts:
                            return False
                    return True

                edge_to_dissolve = None
                edge_to_recurse = None
                edge_to_select = None

                if len(face.verts) == 4:
                    # Already a quad
                    other_edges = [f_edge for f_edge in face.edges if f_edge not in confirmed_edges]
                    if len(other_edges) == 2:
                        edge_to_recurse = single_element([f for f in other_edges if not_near_current_edge(f)])
                        edge_to_select = single_element([f for f in other_edges if f != edge_to_recurse])
                    pass

                if len(face.verts) == 3:
                    other_edges = [f_edge for f_edge in face.edges if f_edge not in confirmed_edges]

                    # Find the edge to dissolve
                    if len(other_edges) == 1:
                        target_edge = other_edges[0]

                        # The edge should have another face of 3 vertices
                        other_faces = [f_face for f_face in target_edge.link_faces if f_face != face]
                        if len(other_faces) == 1 and len(other_faces[0].verts) == 3:
                            target_face = other_faces[0]
                            edge_to_dissolve = target_edge
                            edge_to_recurse = single_element(
                                [it for it in target_face.edges if it != edge_to_dissolve and not_near_current_edge(it)]
                            )
                            edge_to_select = single_element(
                                [it for it in target_face.edges if it != edge_to_dissolve and it != edge_to_recurse]
                            )

                    elif len(other_edges) == 2:
                        for f_edge in other_edges:
                            if edge_to_dissolve is not None:
                                break

                            for f_face in f_edge.link_faces:
                                # Ignore the current face
                                if f_face != face and len(f_face.verts) == 3:
                                    other_edges_2 = [
                                        f_edge_2
                                        for f_edge_2 in f_face.edges
                                        if f_edge_2 not in confirmed_edges and f_edge_2 != f_edge
                                    ]
                                    if len(other_edges_2) == 1:
                                        edge_to_dissolve = f_edge
                                        edge_to_recurse = other_edges_2[0]
                                        edge_to_select = [f for f in other_edges if f != f_edge][0]
                                        break

                if edge_to_dissolve is not None:
                    edges_to_dissolve.add(edge_to_dissolve)
                    confirmed_edges.add(edge_to_dissolve)

                if edge_to_recurse is not None:
                    remaining_edges.append(edge_to_recurse)

                if edge_to_select is not None:
                    edges_to_select.add(edge_to_select)
                    confirmed_edges.add(edge_to_select)

        # Dissolve edges
        if len(edges_to_dissolve) > 0:
            print("Dissolving edges: ", len(edges_to_dissolve))
            for edge in edges_to_dissolve:
                edge.select = True
            bpy.ops.mesh.dissolve_edges(use_verts=False)

        # Select and exit
        for edge in edges_to_select:
            edge.select = True

        # Find another active edge
        vert = single_element([v for v in active_edge.verts if any(e in edges_to_select for e in v.link_edges)])
        candidates = [e for e in vert.link_edges if e not in confirmed_edges]
        if len(candidates) > 0:
            # Get the candidate most parallel to the active edge
            print("Candidates: ", len(candidates))
            candidates.sort(key=lambda e: dot_product_edges(e, active_edge), reverse=True)
            bm.select_history.add(candidates[0])

        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}


class AT_ArmatureTools(bpy.types.Panel):
    bl_label = "Armature Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = shelf_name

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)

        operator = row.operator("blendertools.toogle_constraint", text="Mute", icon="HIDE_ON")
        operator.mute = True

        operator = row.operator("blendertools.toogle_constraint", text="Unmute", icon="HIDE_OFF")
        operator.mute = False

        row = layout.row(align=True)
        row.operator("blendertools.symmetrize")

        row = layout.row(align=True)
        row.operator("blendertools.tris_to_quads")


armature_classes = [
    AT_Constraint_Toogle,
    AT_SymmetrizeTool,
    AT_TrisToQuads,
    AT_ArmatureTools,
]
