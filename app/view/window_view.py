import sys
import networkx as nx
import pyqtgraph as pg
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel,QStatusBar,QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox
from PyQt5.QtCore import QTimer, QSize

class GraphWindow(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model  # GraphModel будет присваиваться через Controller

        self.setWindowTitle('Поиск оптимального маршрута доставки клиентам')
        self.setGeometry(100, 100, 1150, 800)
        self.layout = QVBoxLayout(self)
        # Загрузка стилей из файла
        self.load_styles("styles.qss")
        icon = QIcon()
        icon.addFile('ant_picture.png', QSize(64, 64))
        self.setWindowIcon(icon)
        # Таймер отображения
        self.time_label = QLabel("00:00:000", self)
        self.layout.addWidget(self.time_label)
        # Создаем виджет для графика с использованием pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground('w')
        # Создаем статус-бар
        self.status_bar = QStatusBar(self)
        self.layout.addWidget(self.status_bar)
        # Инициализация элементов интерфейса
        self.create_controls()
        self.create_buttons()

    def load_styles(self, style_file):
        """Загружает стили из указанного файла."""
        with open(style_file, "r") as file:
            self.setStyleSheet(file.read())

    def create_controls(self):
        controls_layout = QFormLayout()
        # Начальная точка
        self.start_node_combo = QComboBox(self)
        controls_layout.addRow("Начальная точка:", self.start_node_combo)

        # Конечные точки и кнопка "Ок"
        self.end_nodes_input = QLineEdit(self)
        self.end_nodes_input.setPlaceholderText("Введите конечные точки через запятую")

        self.set_end_nodes_button = QPushButton("Ок", self)
        self.set_end_nodes_button.clicked.connect(self.model.controller.update_end_nodes)

        # Мы используем QHBoxLayout, чтобы разместить кнопку рядом с полем ввода
        end_nodes_layout = QHBoxLayout()
        end_nodes_layout.addWidget(self.end_nodes_input)
        end_nodes_layout.addWidget(self.set_end_nodes_button)

        controls_layout.addRow("Конечные точки:", end_nodes_layout)

        # Параметры алгоритма
        self.evaporation_rate_input = QLineEdit("1.3", self)
        self.pheromone_intensity_input = QLineEdit("1.0", self)
        self.alpha_input = QLineEdit("2", self)
        self.beta_input = QLineEdit("1", self)
        self.num_ants_input = QLineEdit("10", self)

        controls_layout.addRow("Коэффициент испарения:", self.evaporation_rate_input)
        controls_layout.addRow("Интенсивность феромонов:", self.pheromone_intensity_input)
        controls_layout.addRow("Вес феромонов (alpha):", self.alpha_input)
        controls_layout.addRow("Вес расстояния (beta):", self.beta_input)
        controls_layout.addRow("Количество муравьёв:", self.num_ants_input)

        controls_group = QGroupBox("Настройки алгоритма")
        controls_group.setLayout(controls_layout)
        self.layout.addWidget(controls_group)

    def create_buttons(self):
        buttons_layout = QHBoxLayout()

        self.load_button = QPushButton('Загрузить граф')
        buttons_layout.addWidget(self.load_button)

        self.set_param_button = QPushButton('Задать параметры')
        buttons_layout.addWidget(self.set_param_button)

        self.start_button = QPushButton('Запуск')
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Остановка')
        buttons_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton('Сброс')
        buttons_layout.addWidget(self.reset_button)

        self.layout.addLayout(buttons_layout)

    def update_start_node_combo(self, nodes):
        """Обновляет список доступных начальных точек."""
        self.start_node_combo.clear()
        for node in nodes:
            self.start_node_combo.addItem(str(node))

    def update_canvas(self):
        """Очищает и перерисовывает граф на виджете pyqtgraph."""
        self.plot_widget.clear()
        pos = self.model.positions  # Получаем позиции из модели
        edges = self.model.graph.edges(data=True)

        # Отрисовка рёбер с учетом феромонов
        for u, v, data in edges:
            pheromone = data['pheromone']
            weight = data['weight']
            line = pg.PlotCurveItem(
                [pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                pen=pg.mkPen(color=(200, 200, 200), width=pheromone * 5)  # Толщина линии пропорциональна феромонам
            )
            self.plot_widget.addItem(line)

            # Добавляем текст для расстояния
            mid_x = (pos[u][0] + pos[v][0]) / 2
            mid_y = (pos[u][1] + pos[v][1]) / 2
            text_item = pg.TextItem(f"{weight}", anchor=(0.5, 0.5), color='black')
            text_item.setFont(pg.QtGui.QFont("Arial", 10))
            text_item.setPos(mid_x, mid_y)
            self.plot_widget.addItem(text_item)

        # Отрисовка узлов
        for node in self.model.graph.nodes:
            x, y = pos[node]
            color = '#eb5757'  # Красный для всех узлов, кроме стартового и конечного
            if node == self.model.start_node:
                color = '#6fcf97'  # Зеленый для стартового узла
            elif node in self.model.end_nodes:  # Проверяем, является ли узел конечной точкой
                color = '#f2994a'

            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            # Текст внутри узлов
            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='white')
            text.setFont(pg.QtGui.QFont("Arial", 14, pg.QtGui.QFont.Bold))
            text.setPos(x, y)
            self.plot_widget.addItem(text)
