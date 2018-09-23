# --------------------------------------------------------------------
# --- FLOWPIPE GRAPH ---------------
# --------------------------------------------------------------------

import sys
sys.path.append("C:\\PROJECTS\\flowpipe")

from flowpipe.graph import Graph
from flowpipe.node import Node


@Node(outputs=["baked_script"])
def Bake(settings):
    pass


@Node(outputs=["rendered_sequence"])
def Render(nuke_script):
    pass


@Node(outputs=["transcode_id"])
def Transcode(image_sequence):
    pass


@Node(outputs=["version_id"])
def Update(data):
    pass


graph = Graph()
bake = Bake(graph=graph)
render = Render(graph=graph)
transcode = Transcode(graph=graph)
update = Update(graph=graph)

bake.outputs["baked_script"] >> render.inputs["nuke_script"]
render.outputs["rendered_sequence"] >> transcode.inputs["image_sequence"]
render.outputs["rendered_sequence"] >> update.inputs["data"]

print graph

# --------------------------------------------------------------------
# --- UI ---------------
# --------------------------------------------------------------------

# import os
import sys

# import networkx
from thirdparty.Qt import QtWidgets

from nodegraph.scene import Scene
from nodegraph.view import View


class NodeGraphDialog(QtWidgets.QMainWindow):

    """
    Handles top level dialog of Node grap

    """

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.parent = parent or self

        self.nodegraph = NodeGraphWidget("main", parent=self.parent)
        self.setCentralWidget(self.nodegraph)
        self.resize(800, 600)
        self.setWindowTitle("Node graph -")

        # Create Nodes
        #
        x = 0
        ui_nodes = {}
        for column in graph.evaluation_matrix:
            y = 0
            x_diff = 0
            for row, node in enumerate(column):
                ui_node = self.nodegraph.graph_scene.create_node(
                    node.name,
                    inputs=node.inputs.keys())
                ui_nodes[node.name] = ui_node

                x_diff = (ui_node.boundingRect().left() - ui_node.boundingRect().x() + 4 if
                          ui_node.boundingRect().left() - ui_node.boundingRect().x() + 4 > x_diff else x_diff)

                y += ui_node.boundingRect().right() - ui_node.boundingRect().y()

                ui_node.setPos(x*75, y)

            x += x_diff

        # Connect them / Add egdes
        #
        for node in graph.nodes:
            ui_node = ui_nodes[node.name]
            for input_plug in node.inputs.values():
                if input_plug.connections:
                    upstream_plug = input_plug.connections[0]
                    upstream_ui_node = ui_nodes[upstream_plug.node.name]

                    self.nodegraph.graph_scene.create_edge(
                        upstream_ui_node._output, ui_node._inputs[0])


class NodeGraphWidget(QtWidgets.QWidget):

    """
    Handles node graph view

    """

    def __init__(self, name, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.name = name
        self.parent = parent

        self.graph_scene = Scene(parent=self.parent,
                                 nodegraph_widget=self)
        self.graph_view = View(self.graph_scene, parent=self.parent)
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.graph_view)

        self.button = QtWidgets.QPushButton("Serialize")
        self.horizontal_layout.addWidget(self.button)
        self.button.clicked.connect(self.serialize_graph)

    def serialize_graph(self):
        node_types = {
            "Bake": Bake,
            "Render": Render,
            "Transcode": Transcode,
            "Update": Update,
        }
        fp_nodes = []
        for node in self.graph_view.scene().nodes:
            fp_node = node_types[node._name]()
            fp_nodes.append(fp_node)

        graph = Graph(nodes=fp_nodes)

        for edge in self.graph_view.scene()._edges_by_hash.values():
            source = edge._source_slot
            target = edge._target_slot

            source_node = graph[source.parent._name]
            target_node = graph[target.parent._name]

            source_node.outputs[source_node.outputs.keys()[0]] >> target_node.inputs[target._name]


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = NodeGraphDialog()
    dialog.show()

    sys.exit(app.exec_())
