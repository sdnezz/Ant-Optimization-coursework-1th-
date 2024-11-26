import random
import numpy as np


class AntColonyAlgorithm:
    def __init__(self, graph, evaporation_rate, pheromone_intensity, alpha, beta):
        self.graph = graph
        self.evaporation_rate = evaporation_rate
        self.pheromone_intensity = pheromone_intensity
        self.alpha = alpha
        self.beta = beta

    def calculate_path_length(self, path):
        """Вычисляет длину пути."""
        return sum(self.graph[u][v]['weight'] for u, v in zip(path, path[1:]))

    def generate_ant_path(self, start_node, end_node):
        """Генерация пути для одного муравья."""
        current_node = start_node
        path = [current_node]
        visited_nodes = {current_node}

        while current_node != end_node:
            neighbors = list(self.graph.neighbors(current_node))
            probabilities = self.calculate_probabilities(current_node, neighbors, visited_nodes)

            if not probabilities:  # Если нет доступных узлов, тупик
                return path

            next_node = random.choices(neighbors, weights=probabilities)[0]
            path.append(next_node)
            visited_nodes.add(next_node)
            current_node = next_node

        return path

    def run_iteration(self, num_ants, start_node, end_node=None):
        all_paths = []
        best_path = None
        best_path_length = float('inf')

        for _ in range(num_ants):
            path, path_length = self.find_path(start_node, end_node)
            all_paths.append((path, path_length))
            if path_length < best_path_length:
                best_path = path
                best_path_length = path_length

        return all_paths, best_path

    def find_path(self, start_node, end_node=None):
        current_node = start_node
        visited_nodes = {current_node}
        path = [current_node]
        total_length = 0

        while True:
            if end_node is not None and current_node == end_node:
                break

            next_node = self.select_next_node(current_node, visited_nodes)
            if next_node is None:  # Dead end
                return path, float('inf')

            visited_nodes.add(next_node)
            path.append(next_node)
            total_length += self.graph[current_node][next_node]['weight']
            current_node = next_node

        return path, total_length

    def select_next_node(self, current_node, visited_nodes):
        neighbors = [node for node in self.graph.neighbors(current_node) if node not in visited_nodes]

        if not neighbors:
            return None

        probabilities = []
        for neighbor in neighbors:
            pheromone = self.graph[current_node][neighbor]['pheromone']
            distance = self.graph[current_node][neighbor]['weight']
            if distance == 0:  # Защита от деления на ноль
                probabilities.append(0)
            else:
                probabilities.append((pheromone ** self.alpha) * ((1 / distance) ** self.beta))

        probabilities = np.array(probabilities)
        probabilities /= probabilities.sum()

        return random.choices(neighbors, weights=probabilities, k=1)[0]

    def update_pheromones(self, all_paths, best_path=None):
        """Обновляет феромоны на основе пройденных путей."""
        for u, v in self.graph.edges:
            print(f"Before evaporation ({u}, {v}): {self.graph[u][v]['pheromone']}")  # Перед обновлением
            self.graph[u][v]['pheromone'] *= (1 - self.evaporation_rate)

        for path, path_length in all_paths:
            for u, v in zip(path, path[1:]):
                self.graph[u][v]['pheromone'] += self.pheromone_intensity / path_length
                print(f"After update ({u}, {v}): {self.graph[u][v]['pheromone']}")  # После обновления

        if best_path:
            best_length = sum(self.graph[u][v]['weight'] for u, v in zip(best_path, best_path[1:]))
            for u, v in zip(best_path, best_path[1:]):
                self.graph[u][v]['pheromone'] += 2 * (self.pheromone_intensity / best_length)
                print(f"Boost best path ({u}, {v}): {self.graph[u][v]['pheromone']}")  # Усиление лучшего пути

    def evaporate_pheromones(self):
        """Уменьшает феромон на всех рёбрах графа."""
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] *= (1 - self.evaporation_rate)
            # Гарантируем, что феромон не опустится ниже минимального уровня
            if self.graph[u][v]['pheromone'] < 0.1:
                self.graph[u][v]['pheromone'] = 0.1

