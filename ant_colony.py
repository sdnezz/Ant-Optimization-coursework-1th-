import numpy as np

class AntColonyAlgorithm:
    def __init__(self, graph, evaporation_rate=0.5, pheromone_intensity=1.0, alpha=1, beta=2):
        """
        Инициализация муравьиного алгоритма.
        :param graph: Граф в формате NetworkX.
        :param evaporation_rate: Коэффициент испарения феромонов (0 < evaporation_rate <= 1).
        :param pheromone_intensity: Интенсивность феромонов.
        :param alpha: Вес влияния феромонов.
        :param beta: Вес влияния расстояния.
        """
        self.graph = graph
        self.evaporation_rate = evaporation_rate
        self.pheromone_intensity = pheromone_intensity
        self.alpha = alpha
        self.beta = beta

        # Инициализация феромонов на всех рёбрах
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] = 1.0  # Начальное значение феромонов

    def calculate_probabilities(self, current_node, visited_nodes):
        """
        Рассчитывает вероятности перехода в соседние узлы.
        :param current_node: Текущий узел муравья.
        :param visited_nodes: Узлы, которые муравей уже посетил.
        :return: Словарь {узел: вероятность}.
        """
        probabilities = {}
        neighbors = [n for n in self.graph.neighbors(current_node) if n not in visited_nodes]

        if not neighbors:  # Если нет доступных соседей
            return probabilities

        total = 0
        for neighbor in neighbors:
            pheromone = self.graph[current_node][neighbor]['pheromone']
            distance = self.graph[current_node][neighbor]['weight']
            attractiveness = (pheromone ** self.alpha) * ((1 / distance) ** self.beta)
            probabilities[neighbor] = attractiveness
            total += attractiveness

        # Нормализация вероятностей
        for neighbor in probabilities:
            probabilities[neighbor] /= total

        return probabilities

    def update_pheromones(self, paths, best_path):
        """
        Обновляет феромоны на рёбрах графа.
        :param paths: Все пройденные пути (список списков узлов).
        :param best_path: Кратчайший путь, найденный за итерацию.
        """
        # Испарение феромонов
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] *= (1 - self.evaporation_rate)

        # Увеличение феромонов на пройденных рёбрах
        for path in paths:
            path_length = self.calculate_path_length(path)
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.graph[u][v]['pheromone'] += self.pheromone_intensity / path_length

        # Увеличение феромонов на лучшем пути
        best_length = self.calculate_path_length(best_path)
        for i in range(len(best_path) - 1):
            u, v = best_path[i], best_path[i + 1]
            self.graph[u][v]['pheromone'] += 2 * (self.pheromone_intensity / best_length)

    def calculate_path_length(self, path):
        """
        Вычисляет длину пути.
        :param path: Список узлов пути.
        :return: Длина пути.
        """
        length = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            length += self.graph[u][v]['weight']
        return length
