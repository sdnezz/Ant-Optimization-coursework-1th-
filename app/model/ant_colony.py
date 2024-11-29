import networkx as nx
import random
import sys
import pyqtgraph as pg

class AntColonyAlgorithm:
    def __init__(self, graph, evaporation_rate, pheromone_intensity, alpha, beta):
        self.graph = graph
        self.evaporation_rate = evaporation_rate
        self.pheromone_intensity = pheromone_intensity
        self.alpha = alpha
        self.beta = beta
        self.pheromones = {edge: 1.0 for edge in self.graph.edges}  # начальные феромоны на рёбрах
        self.num_ants = 10  # по умолчанию 10 муравьёв

    def initialize_graph(self, edges_data):
        """Инициализируем граф с рёбрами, на которых будет время."""
        for u, v, data in edges_data:
            self.graph.add_edge(u, v, weight=data['time'])  # вес рёбер — это время
            self.pheromones[(u, v)] = 1.0  # начальный феромон

    def select_next_node(self, current_node, visited_nodes):
        """Выбирает следующий узел на основе феромонов и времени."""
        neighbors = list(self.graph.neighbors(current_node))
        probabilities = []

        total_pheromone = sum(self.pheromones[(current_node, neighbor)] ** self.alpha /
                              (self.graph[current_node][neighbor]['weight'] ** self.beta)
                              for neighbor in neighbors if neighbor not in visited_nodes)

        for neighbor in neighbors:
            if neighbor not in visited_nodes:
                pheromone = self.pheromones.get((current_node, neighbor), 1.0) ** self.alpha
                distance = self.graph[current_node][neighbor]['weight'] ** self.beta
                probability = pheromone / distance if total_pheromone > 0 else 0
                probabilities.append((neighbor, probability))

        # Выбираем следующий узел на основе вероятностей
        next_node = random.choices([node for node, _ in probabilities], [prob for _, prob in probabilities])[0]
        return next_node

    def update_pheromones(self, all_paths):
        """Обновляем феромоны на рёбрах."""
        for path in all_paths:
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

    def move_ant(self, start_node, end_node):
        """Движение муравья по графу"""
        current_node = start_node
        path = [current_node]
        visited_nodes = set(path)

        while current_node != end_node:
            next_node = self.select_next_node(current_node, visited_nodes)
            path.append(next_node)
            visited_nodes.add(next_node)
            current_node = next_node

        return path
