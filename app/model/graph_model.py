import networkx as nx
from app.model.ant_colony import AntColonyAlgorithm
import sys
import pyqtgraph as pg
import time
class GraphModel:
    def __init__(self):
        self.graph = nx.Graph()  # Храним граф
        self.positions = {}  # Позиции узлов
        self.pheromones = {}  # Феромоны на рёбрах (инициализация)
        self.ants = []  # Список муравьёв
        self.start_node = None
        self.end_node = None
        self.path_timers = {}  # Словарь с таймерами для каждого пути

    def initialize_pheromones(self):
        """Инициализация феромонов на рёбрах графа."""
        for u, v in self.graph.edges():
            self.pheromones[(u, v)] = 1.0  # Изначально феромоны равны 1

    def load_graph_from_file(self, file_path):
        """Загружаем граф из файла."""
        G = nx.Graph()
        with open(file_path, 'r') as file:
            for line in file:
                u, v, weight = map(int, line.split())
                G.add_edge(u, v, weight=weight)
        self.initialize_pheromones()
        return G

    def update_pheromones(self, all_paths):
        """Обновляем феромоны на рёбрах."""
        for path in all_paths:
            if len(path) < 2:
                continue  # Пропускаем пустые пути или пути с одной вершиной

            # Проверяем, что все рёбра на пути существуют
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])
                if edge not in self.graph.edges():  # Проверяем, существует ли рёбро
                    print(f"Ребро {edge} не существует в графе. Пропускаем путь.")
                    break
            else:
                # Если все рёбра существуют, вычисляем длину пути и обновляем феромоны
                path_length = sum(self.graph[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))
                pheromone_deposit = 1.0 / path_length  # Добавление феромонов зависит от длины пути

                for i in range(len(path) - 1):
                    edge = (path[i], path[i + 1])
                    if edge not in self.pheromones:
                        self.pheromones[edge] = 1.0  # Если нет, инициализируем с 1.0 феромонами
                    self.pheromones[edge] += pheromone_deposit  # Добавляем феромоны на ребро

                    # Для каждого пути создаем таймер, который будет уменьшать феромоны через заданное время
                    if edge not in self.path_timers:
                        self.path_timers[edge] = time.time()

    def update_pheromones_locally(self):
        """Уменьшаем феромоны на каждом пути, где прошло достаточно времени."""
        current_time = time.time()
        for edge, start_time in list(self.path_timers.items()):
            if current_time - start_time >= 5:  # Например, уменьшение феромонов через 5 секунд
                self.pheromones[edge] *= 0.95  # Уменьшаем феромоны на 5%
                self.path_timers[edge] = current_time  # Обновляем время последнего уменьшения

    def update_pheromones_globally(self):
        """Глобальное уменьшение феромонов."""
        for key in self.pheromones:
            self.pheromones[key] *= 0.95  # Уменьшаем феромоны на 5% каждую секунду
