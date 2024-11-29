import sys
import time
import networkx as nx
import pyqtgraph as pg
from app.view.window_view import GraphWindow
from app.model.ant_colony import AntColonyAlgorithm
from app.model.graph_model import GraphModel
from app.model.ant import  Ant
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox
from PyQt5.QtCore import QTimer

class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.num_ants = 10
        self.iteration = 0
        self.timer = None
        self.global_timer = None  # Таймер для глобального уменьшения феромонов
        self.acceleration = 0.3  # Коэффициент ускорения
        self.start_time = time.time()


        # Связываем действия в представлении с методами контроллера
        self.view.load_button.clicked.connect(self.load_graph)
        self.view.start_button.clicked.connect(self.start_algorithm)
        self.view.stop_button.clicked.connect(self.stop_algorithm)
        self.view.start_node_combo.currentIndexChanged.connect(self.update_start_node)
        self.view.end_node_combo.currentIndexChanged.connect(self.update_end_node)

    def load_graph(self):
        """Загружает граф из файла и обновляет интерфейс."""
        file_name, _ = QFileDialog.getOpenFileName(self.view, 'Открыть файл графа', '','Text Files (*.txt);;All Files (*)')
        if file_name:
            # Загружаем граф из файла
            graph = self.model.load_graph_from_file(file_name)
            # Рассчитываем позиции узлов (spring_layout) и сохраняем их в модели
            self.model.positions = nx.spring_layout(graph)
            # Инициализация феромонов
            self.model.initialize_pheromones()
            # Обновляем модель и представление
            self.model.graph = graph
            self.view.update_start_node_combo()
            self.view.update_end_node_combo()
            # Немедленно обновляем канвас, чтобы отобразить граф
            self.view.update_canvas()  # Обновляем граф на экране сразу после загрузки

    def start_algorithm(self):
        """Запуск алгоритма муравьиной колонии."""
        self.model.ant_colony = AntColonyAlgorithm(
            graph=self.model.graph,
            evaporation_rate=float(self.view.evaporation_rate_input.text()),
            pheromone_intensity=float(self.view.pheromone_intensity_input.text()),
            alpha=int(self.view.alpha_input.text()),
            beta=int(self.view.beta_input.text())
        )
        self.num_ants = int(self.view.num_ants_input.text())
        # Запуск глобального таймера для уменьшения феромонов
        self.global_timer = QTimer()
        self.global_timer.timeout.connect(self.update_pheromones_globally)
        self.global_timer.start(1000)  # Таймер уменьшает феромоны каждую секунду
        # Добавляем муравьёв
        self.add_ants(self.num_ants)
    def stop_algorithm(self):
        """Остановка алгоритма."""
        if self.timer and self.timer.isActive():
            self.timer.stop()
        if self.global_timer and self.global_timer.isActive():
            self.global_timer.stop()  # Останавливаем глобальный таймер

    # def run_iterations(self, acceleration):
    #     """Запуск итераций алгоритма."""
    #     self.iteration = 0
    #     self.timer = QTimer()
    #     self.timer.timeout.connect(lambda: self.run_single_iteration(acceleration))
    #     self.timer.start(100)  # Итерации идут быстрее, например каждые 100мс
    #
    # def run_single_iteration(self):
    #     """Обработка одной итерации муравьиной колонии."""
    #     if self.iteration >= 20:  # Завершаем после 20 итераций
    #         self.timer.stop()
    #         return
    #
    #     all_paths = []
    #     for _ in range(self.num_ants):
    #         ant = Ant(self.model.graph, self.model.positions, acceleration=acceleration)
    #         self.model.ants.append(ant)
    #         path = ant.move()  # Двигаем муравья по графу
    #         all_paths.append(path)
    #
    #     # Обновление феромонов на рёбрах
    #     self.model.update_pheromones(all_paths)  # Обновляем феромоны на основе путей
    #     self.view.update_canvas()  # Перерисовываем граф с феромонами
    #     self.iteration += 1

    # def update_pheromones(self, ants):
    #     """Обновление феромонов на рёбрах"""
    #     all_paths = [ant.path for ant in ants]  # Получаем все пути муравьёв
    #     self.model.update_pheromones(all_paths)  # Обновляем феромоны на основе путей

    def add_ants(self, num_ants):
        """Добавление муравьёв в систему."""
        for _ in range(num_ants):
            ant = Ant(self.model.graph, self.model.positions, self.acceleration)
            self.model.ants.append(ant)
            # Теперь не используем метод start(), а сразу вызываем move()
            self.timer = QTimer()
            self.timer.timeout.connect(self.move_ants)
            self.timer.start(100)  # Таймер для движения муравьёв, например, 100 мс

    def move_ants(self):
        """Двигаем всех муравьёв."""
        all_paths = []
        delta_time = time.time() - self.start_time  # Считаем время, прошедшее с последнего обновления

        for ant in self.model.ants:
            path = ant.move(delta_time)  # Передаем время, прошедшее с последнего обновления
            if path:  # Проверяем, что путь не пустой
                all_paths.append(path)

        # Обновляем феромоны на рёбрах
        self.model.update_pheromones(all_paths)  # Обновляем феромоны на основе путей
        self.view.update_canvas()  # Перерисовываем граф с феромонами

        self.start_time = time.time()  # Обновляем время старта для следующего движения

    def update_pheromones_globally(self):
        """Глобальное уменьшение феромонов на рёбрах"""
        self.model.update_pheromones_globally()  # Уменьшаем феромоны
        self.view.update_canvas()  # Обновляем канвас

    def update_start_node(self):
        """Обновление начальной вершины."""
        start_node = self.view.start_node_combo.currentText()
        if start_node:
            self.model.start_node = int(start_node)
        self.view.update_canvas()

    def update_end_node(self):
        """Обновление конечной вершины."""
        end_node = self.view.end_node_combo.currentText()
        if end_node:
            self.model.end_node = int(end_node)
        self.view.update_canvas()

    def update_start_node_combo(self):
        """Обновляет комбобокс начальной вершины в представлении."""
        self.view.start_node_combo.clear()
        for node in sorted(self.model.graph.nodes):
            self.view.start_node_combo.addItem(str(node))

    def update_end_node_combo(self):
        """Обновляет комбобокс конечной вершины в представлении."""
        self.view.end_node_combo.clear()
        for node in sorted(self.model.graph.nodes):
            self.view.end_node_combo.addItem(str(node))