import sys
import networkx as nx
import pyqtgraph as pg
from app.model.ant_colony import AntColonyAlgorithm
from app.model.ant import Ant
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox
from PyQt5.QtCore import QTimer

class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = None  # Инициализация контроллера как None
        self.setWindowTitle('Граф доставки для алгоритма муравьиной колонии')
        self.setGeometry(100, 100, 1000, 700)

        self.layout = QVBoxLayout(self)

        # Загрузка стилей
        self.load_styles("styles.qss")

        # Инициализация интерфейса
        self.create_controls()
        self.create_buttons()

        # Виджет для графика с использованием pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground('w')

        self.graph = None  # Граф
        self.positions = None  # Позиции узлов

    def load_styles(self, style_file):
        """Загружает стили из указанного файла"""
        with open(style_file, "r") as file:
            self.setStyleSheet(file.read())

    def create_controls(self):
        controls_layout = QFormLayout()

        self.start_node_combo = QComboBox(self)
        if self.controller:
            self.start_node_combo.currentIndexChanged.connect(self.controller.update_start_node)
        controls_layout.addRow("Начальная точка:", self.start_node_combo)

        self.end_node_combo = QComboBox(self)
        if self.controller:
            self.end_node_combo.currentIndexChanged.connect(self.controller.update_end_node)
        controls_layout.addRow("Конечная точка:", self.end_node_combo)

        # Параметры алгоритма
        self.evaporation_rate_input = QLineEdit("1.3", self)
        self.pheromone_intensity_input = QLineEdit("1.0", self)
        self.alpha_input = QLineEdit("2", self)
        self.beta_input = QLineEdit("1", self)
        self.num_ants_input = QLineEdit("10", self)
        self.acceleration_input = QLineEdit("0.3", self)  # Добавляем поле для коэффициента ускорения

        controls_layout.addRow("Коэффициент испарения:", self.evaporation_rate_input)
        controls_layout.addRow("Интенсивность феромонов:", self.pheromone_intensity_input)
        controls_layout.addRow("Вес феромонов (alpha):", self.alpha_input)
        controls_layout.addRow("Вес расстояния (beta):", self.beta_input)
        controls_layout.addRow("Количество муравьёв:", self.num_ants_input)
        controls_layout.addRow("Коэффициент ускорения:", self.acceleration_input)  # Добавляем строку для коэффициента

        controls_group = QGroupBox("Настройки алгоритма")
        controls_group.setLayout(controls_layout)
        self.layout.addWidget(controls_group)

    def create_buttons(self):
        buttons_layout = QHBoxLayout()

        self.load_button = QPushButton('Загрузить граф')
        if self.controller:
            self.load_button.clicked.connect(self.controller.load_graph)
        buttons_layout.addWidget(self.load_button)

        self.start_button = QPushButton('Запуск')
        if self.controller:
            self.start_button.clicked.connect(self.controller.start_algorithm)
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Остановка')
        if self.controller:
            self.stop_button.clicked.connect(self.controller.stop_algorithm)
        buttons_layout.addWidget(self.stop_button)

        self.layout.addLayout(buttons_layout)

    def update(self):
        """Обновление состояния, движение муравьёв и феромонов"""
        # Двигаем всех муравьёв
        for ant in self.ants:
            ant.move()  # Двигаем муравья
        self.controller.update_pheromones(self.ants)  # Обновляем феромоны
        self.update_canvas()

    def add_ants(self, num_ants):
        """Добавление муравьёв"""
        for _ in range(num_ants):
            ant = Ant(self.graph, self.positions)
            self.ants.append(ant)
            ant.start()  # Запускаем движение муравья

    def update_canvas(self):
        """Очищает и перерисовывает граф на виджете pyqtgraph."""
        self.plot_widget.clear()

        pos = self.controller.model.positions  # Позиции узлов
        edges = self.controller.model.graph.edges(data=True)

        # Отрисовка рёбер с феромонами
        for u, v, data in edges:
            pheromone = self.controller.model.pheromones.get((u, v), 1.0)  # Получаем феромоны на рёбре
            weight = data['weight']  # Время на рёбре

            # Устанавливаем цвет рёбер в зависимости от феромонов
            line_color = pg.mkColor(pheromone * 255, 0,
                                    (1 - pheromone) * 255)  # Зелёный для феромона, серый для малых значений
            line = pg.PlotCurveItem([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], pen=pg.mkPen(line_color, width=2))
            self.plot_widget.addItem(line)

            # Добавляем текст для времени (вместо расстояния)
            mid_x = (pos[u][0] + pos[v][0]) / 2
            mid_y = (pos[u][1] + pos[v][1]) / 2
            text_item = pg.TextItem(f"{weight}s", anchor=(0.5, 0.5), color='black')
            text_item.setFont(pg.QtGui.QFont("Arial", 10))
            text_item.setPos(mid_x, mid_y)
            self.plot_widget.addItem(text_item)

        # Отрисовка узлов с жирными цифрами
        for node in self.controller.model.graph.nodes:
            x, y = pos[node]
            color = '#6fcf97' if node == self.controller.model.start_node else '#f2994a' if node == self.controller.model.end_node else '#eb5757'
            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            # Жирный шрифт для номера вершины
            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='white')
            text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))  # Сделаем шрифт жирным
            text.setPos(x, y)
            self.plot_widget.addItem(text)

        # Отображаем движение муравьёв (пути, которые они прошли)
        for ant in self.controller.model.ants:
            self.plot_widget.addItem(ant.scatter)

    def load_graph(self):
        """Загрузить граф из файла"""
        if self.controller:
            self.controller.load_graph_from_file()

    def update_start_node(self):
        if self.controller:
            self.controller.update_start_node(self.start_node_combo)

    def update_end_node(self):
        if self.controller:
            self.controller.update_end_node(self.end_node_combo)

    def update_start_node_combo(self):
        if self.controller:
            self.controller.update_start_node_combo()

    def update_end_node_combo(self):
        if self.controller:
            self.controller.update_end_node_combo()