import networkx as nx
import pyqtgraph as pg
from app.view.window_view import GraphWindow

class GraphModel:
    def __init__(self, controller):
        self.graph = None
        self.positions = {}
        self.start_node = None
        self.end_nodes = set()
        self.controller = controller
        self.view = None
        self.evaporation_rate = None
        self.alpha = None
        self.beta = None
        self.num_ants = None

    def setup_connections(self):
        """Связывает сигналы интерфейса с действиями контроллера."""
        self.view.start_node_combo.currentIndexChanged.connect(self.controller.update_start_node)
        self.view.set_end_nodes_button.clicked.connect(self.controller.update_end_nodes)
        self.view.set_param_button.clicked.connect(self.controller.set_parameters)
        self.view.load_button.clicked.connect(self.controller.load_graph)
        self.view.start_button.clicked.connect(self.controller.start_algorithm)
        self.view.stop_button.clicked.connect(self.controller.stop_algorithm)
        self.view.reset_button.clicked.connect(self.controller.reset_graph)


    def set_view(self):
        self.view = GraphWindow(self)
        self.setup_connections()
        return self.view

    def graph_to_view(self, nodes):
        self.view.update_start_node_combo(nodes)
        self.view.update_canvas()

    def initialize_pheromones(self):
        """Инициализация феромонов для всех рёбер графа."""
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] = 1.0