import networkx as nx
import pyqtgraph as pg
from app.view.window_view import GraphWindow

class GraphModel:
    def __init__(self, controller):
        self.graph = None
        self.positions = {}
        self.start_node = None
        self.end_node = None
        self.controller = controller
        self.view = None
        self.evaporation_rate = None
        self.alpha = None
        self.beta = None
        self.num_ants = None

    def setup_connections(self):
         """Связывает сигналы интерфейса с действиями контроллера."""
         self.view.start_node_combo.currentIndexChanged.connect(self.controller.update_start_node)
         self.view.end_node_combo.currentIndexChanged.connect(self.controller.update_end_node)
         self.view.set_param_button.clicked.connect(self.controller.set_parameters)
         self.view.load_button.clicked.connect(self.controller.load_graph)
         # self.view.start_button.clicked.connect(self.controller.start_algorithm)
         # self.view.stop_button.clicked.connect(self.controller.stop_algorithm)

    def set_view(self):
        self.view = GraphWindow(self)
        self.setup_connections()
        return self.view

    def graph_to_view(self, nodes):
        self.view.update_start_node_combo(nodes)
        self.view.update_end_node_combo(nodes)
        self.view.update_canvas()

    def update_start_node(start_node):
        """Передает начальную в контроллер."""
        self.controller.update_start_node(start_node)

    def update_end_node(end_node):
        """Передает конечную точку в контроллер."""
        self.controller.update_end_node(end_node)

    def initialize_pheromones(self):
        """Инициализация феромонов для всех рёбер графа."""
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] = 1.0