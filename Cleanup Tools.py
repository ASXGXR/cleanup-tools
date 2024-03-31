bl_info = {
    "name": "Cleanup Tools",
    "author": "Alex Sagar",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Shader Editor > Tools",
    "description": "Centers nodes in the Shader Editor and removes unused materials and images",
    "category": "Node",
}

import bpy

# Center Nodes Functionality
def center_nodes(nodes):
    avg_x = sum([node.location.x for node in nodes]) / len(nodes)
    avg_y = sum([node.location.y for node in nodes]) / len(nodes)
    for node in nodes:
        node.location.x -= avg_x
        node.location.y -= avg_y

class NODES_OT_Center(bpy.types.Operator):
    bl_idname = "nodes.center_nodes"
    bl_label = "Center Nodes"
    def execute(self, context):
        if context.space_data.type == 'NODE_EDITOR':
            center_nodes(context.space_data.edit_tree.nodes)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active node editor")
            return {'CANCELLED'}

# Find Nodes Functionality
def focus_on_node(context, nodes):
    if nodes:  # Check if there are any nodes at all
        # Store current selection
        selected_nodes = [node for node in nodes if node.select]
        
        # Deselect all nodes
        bpy.ops.node.select_all(action='DESELECT')
        
        first_node = nodes[0]  # Take the first node in the list
        first_node.select = True  # Select the first node
        
        # Center the Node Editor view on the selected node
        bpy.ops.node.view_selected()
        
        # Restore original selection state
        bpy.ops.node.select_all(action='DESELECT')
        for node in selected_nodes:
            node.select = True

class NODES_OT_Find(bpy.types.Operator):
    bl_idname = "nodes.find_nodes"
    bl_label = "Find Nodes"
    def execute(self, context):
        if context.space_data.type == 'NODE_EDITOR' and context.space_data.node_tree:
            focus_on_node(context, context.space_data.node_tree.nodes)
            self.report({'INFO'}, "View centered on first node")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active node editor or no nodes found")
            return {'CANCELLED'}

# Remove Unused Resources Functionality
class RemoveUnusedResources(bpy.types.Operator):
    bl_idname = "object.remove_unused_resources"
    bl_label = "Remove Unused Resources"
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.name in context.view_layer.objects:
                context.view_layer.objects.active = obj
                bpy.ops.object.material_slot_remove_unused()
        for mat in list(bpy.data.materials):
            if mat.users == 0:
                bpy.data.materials.remove(mat)
        for img in list(bpy.data.images):
            if img.users == 0:
                bpy.data.images.remove(img)
        self.report({'INFO'}, "Unused materials and images removed")
        return {'FINISHED'}

class CLEANUP_PT_Panel(bpy.types.Panel):
    """Creates a Panel in the Shader Editor"""
    bl_label = "Cleanup Tools"
    bl_idname = "CLEANUP_PT_Panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator("nodes.center_nodes")
        layout.operator("object.remove_unused_resources")
        layout.operator("nodes.find_nodes")  # Add the "Find Nodes" button

# Update the classes list to include the new NODES_OT_Find class
classes = [NODES_OT_Center, RemoveUnusedResources, CLEANUP_PT_Panel, NODES_OT_Find]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
