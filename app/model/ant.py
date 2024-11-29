import random
import numpy as np
import sys
import networkx as nx
import pyqtgraph as pg
import time

class Ant:
    def __init__(self, graph, positions, acceleration=0.3):
        self.graph = graph
        self.positions = positions
        self.x = random.choice(list(graph.nodes))  # Начальная позиция
        self.path = [self.x]  # Путь муравья
        self.color = pg.mkColor(random.randint(0, 255), random.randint(0, 255),
                                random.randint(0, 255))  # случайный цвет
        self.acceleration = acceleration
        self.time_spent = 0  # Общее время, потраченное муравьём
        self.start_time = time.time()
        # Создаем scatter-объект для отображения муравья
        self.scatter = pg.ScatterPlotItem([self.positions[self.x][0]], [self.positions[self.x][1]], symbol='o', size=10,
                                          brush=self.color)

    def move(self, delta_time):
        """Перемещаем муравья по графу с учетом времени на рёбе."""
        # Получаем список соседей текущей вершины
        neighbors = list(self.graph.neighbors(self.x))

        # Если у муравья есть соседи, выбираем случайного из них
        if neighbors:
            next_node = random.choice(neighbors)  # Простой случай: выбираем случайного соседа

            # Проверяем, существует ли рёбро между текущей и выбранной вершиной
            if self.graph.has_edge(self.x, next_node):
                self.path.append(next_node)

                # Получаем время на рёбре
                edge_time = self.graph[self.x][next_node]['weight']
                move_time = edge_time * self.acceleration  # Умножаем на коэффициент ускорения

                # Считаем, сколько времени прошло
                time_passed = time.time() - self.start_time

                if time_passed >= move_time:
                    # Обновляем позицию только если прошел достаточный интервал времени
                    self.x = next_node
                    self.start_time = time.time()  # Обновляем время начала движения

                # Обновляем позицию scatter-объекта
                self.scatter.setData([self.positions[self.x][0]], [self.positions[self.x][1]])

            else:
                print(f"Рёбро между {self.x} и {next_node} не существует!")
        else:
            print(f"У вершины {self.x} нет соседей!")

        return self.path  # Возвращаем путь

    def is_done(self, total_time_limit):
        """Проверка, завершил ли муравей свой путь, учитывая общее время"""
        return self.time_spent >= total_time_limit  # Завершаем путь, если время прошло