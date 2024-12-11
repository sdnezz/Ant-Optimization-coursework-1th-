import networkx as nx
import pyqtgraph as pg
import random
import math
from PyQt5.QtWidgets import QApplication
from app.view.window_view import GraphWindow

class GraphModel:
    def __init__(self, controller):
        self.graph = None
        self.positions = {}
        self.start_node = None
        self.end_nodes = set()
        self.controller = controller
        self.view = None
        self.pheromone_intensity = None
        self.evaporation_rate = None
        self.alpha = None
        self.beta = None
        self.num_ants = None
        self.num_iterations = 20
        self.best_path = None
        self.best_length = math.inf
        self.min_pheromone = 0.1

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

    def calculate_path_length(self, path):
        """Вычисляет длину пути."""
        return sum(self.graph[u][v]['weight'] for u, v in zip(path, path[1:]))

    def generate_ant_path(self):
        """Генерация пути для одного муравья."""
        current_node = self.start_node
        path = [current_node]
        visited_nodes = {current_node}
        end_node = next(iter(self.end_nodes))  # Предполагаем, что пока только одна конечная вершина

        while current_node != end_node:
            neighbors = list(self.graph.neighbors(current_node))
            probabilities = self.calculate_probabilities(current_node, neighbors, visited_nodes)

            if not probabilities:  # Если нет доступных узлов, тупик
                return path, float('inf')

            next_node = random.choices(neighbors, weights=probabilities)[0]
            path.append(next_node)
            visited_nodes.add(next_node)
            current_node = next_node

        path_length = self.calculate_path_length(path)
        return path, path_length

    def calculate_probabilities(self, current_node, neighbors, visited_nodes):
        """Рассчитывает вероятности перехода к соседним узлам."""
        probabilities = []
        for neighbor in neighbors:
            if neighbor in visited_nodes:
                probabilities.append(0)
            else:
                pheromone = self.graph[current_node][neighbor]['pheromone']
                distance = self.graph[current_node][neighbor]['weight']
                eta = 1 / distance if distance > 0 else 1e-10  # Защита от деления на 0
                probabilities.append((pheromone ** self.alpha) * (eta ** self.beta))

        total = sum(probabilities)
        if total == 0:
            return []
        return [p / total for p in probabilities]

    def update_pheromones(self, all_paths):
        """Обновляет феромоны на основе пройденных путей."""
        # Шаг 1: Испарение феромонов
        for u, v in self.graph.edges():
            self.graph[u][v]['pheromone'] *= (1 - self.evaporation_rate)
            if self.graph[u][v]['pheromone'] < self.min_pheromone:
                self.graph[u][v]['pheromone'] = self.min_pheromone

        # Шаг 2: Обновление феромонов
        for path, path_length in all_paths:
            if path_length == float('inf'):
                continue
            pheromone_contribution = self.pheromone_intensity / path_length
            for u, v in zip(path, path[1:]):
                self.graph[u][v]['pheromone'] += pheromone_contribution

    def run_aco(self):
        """Запуск муравьиного алгоритма."""
        if self.graph is None or self.start_node is None or not self.end_nodes:
            self.controller.show_error_message("Ошибка", "Граф, начальная или конечная вершина не заданы.")
            return

        self.initialize_pheromones()

        for iteration in range(self.num_iterations):
            all_paths = []
            for _ in range(self.num_ants):
                path, path_length = self.generate_ant_path()
                all_paths.append((path, path_length))

            # Определение лучшего пути в этой итерации
            for path, path_length in all_paths:
                if path_length < self.best_length:
                    self.best_length = path_length
                    self.best_path = path

            # Обновление феромонов
            self.update_pheromones(all_paths)

            # Визуализация процесса
            self.view.update_canvas()
            QApplication.processEvents()

        # Итоговая визуализация лучшего пути
        if self.best_path:
            for u, v in zip(self.best_path, self.best_path[1:]):
                if self.graph.has_edge(u, v):
                    self.graph[u][v]['pheromone'] += 2 * self.pheromone_intensity / self.best_length
            self.view.update_canvas()
            self.controller.model.view.status_bar.showMessage(
                f"Лучший путь: {self.best_path}, длина: {self.best_length}")
