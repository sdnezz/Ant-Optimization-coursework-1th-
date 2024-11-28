import sys
import networkx as nx
import pyqtgraph as pg
from app.model.ant_colony import AntColonyAlgorithm
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox
from PyQt5.QtCore import QTimer


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Граф доставки для алгоритма муравьиной колонии')
        self.setGeometry(100, 100, 1000, 700)

        # Главный Layout
        self.layout = QVBoxLayout(self)

        # Загрузка стилей из файла
        self.load_styles("styles.qss")

        # Изначально граф пустой
        self.graph = nx.Graph()
        self.ant_colony = None
        self.start_node = None
        self.end_node = None

        # Инициализация элементов интерфейса
        self.create_controls()
        self.create_buttons()

        # Создаем виджет для графика с использованием pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground('w')

    def load_styles(self, style_file):
        """Загружает стили из указанного файла."""
        with open(style_file, "r") as file:
            self.setStyleSheet(file.read())

    def create_controls(self):
        controls_layout = QFormLayout()

        # Начальная точка
        self.start_node_combo = QComboBox(self)
        self.start_node_combo.currentIndexChanged.connect(self.update_start_node)
        controls_layout.addRow("Начальная точка:", self.start_node_combo)

        # Конечная точка
        self.end_node_combo = QComboBox(self)
        self.end_node_combo.currentIndexChanged.connect(self.update_end_node)
        controls_layout.addRow("Конечная точка:", self.end_node_combo)

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
        self.load_button.clicked.connect(self.load_graph)
        buttons_layout.addWidget(self.load_button)

        self.start_button = QPushButton('Запуск')
        self.start_button.clicked.connect(self.start_algorithm)
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Остановка')
        self.stop_button.clicked.connect(self.stop_algorithm)
        buttons_layout.addWidget(self.stop_button)

        self.layout.addLayout(buttons_layout)

    def load_graph(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Открыть файл графа', '', 'Text Files (*.txt);;All Files (*)')
        if file_name:
            self.graph = self.load_graph_from_file(file_name)
            self.positions = nx.spring_layout(self.graph)
            self.initialize_pheromones()
            self.update_start_node_combo()
            self.update_end_node_combo()
            self.start_node = self.get_start_node()
            self.end_node = self.get_end_node()
            self.visualize_initial_graph()

    def load_graph_from_file(self, file_path):
        G = nx.Graph()
        with open(file_path, 'r') as file:
            for line in file:
                u, v, weight = map(int, line.split())
                G.add_edge(u, v, weight=weight, pheromone=1.0)
        return G

    def initialize_pheromones(self):
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] = 1.0

    def update_start_node_combo(self):
        self.start_node_combo.clear()
        for node in sorted(self.graph.nodes):
            self.start_node_combo.addItem(str(node))

    def update_end_node_combo(self):
        self.end_node_combo.clear()
        for node in sorted(self.graph.nodes):
            self.end_node_combo.addItem(str(node))

    def update_canvas(self):
        """Очищает и перерисовывает граф на виджете pyqtgraph."""
        self.plot_widget.clear()

        pos = self.positions  # Используем фиксированные позиции узлов
        edges = self.graph.edges(data=True)

        # Отрисовка рёбер
        for u, v, data in edges:
            pheromone = data['pheromone']
            weight = data['weight']
            line = pg.PlotCurveItem(
                [pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                pen=pg.mkPen(color=(200, 200, 200), width=2)
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
        for node in self.graph.nodes:
            x, y = pos[node]
            if node == self.start_node:
                color = '#6fcf97'  # Зеленый для начальной вершины
            elif node == self.end_node:
                color = '#f2994a'  # Оранжевый для конечной вершины
            else:
                color = '#eb5757'  # Красный для остальных узлов

            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            # Текст внутри узлов
            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='white')
            text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))
            text.setPos(x, y)
            self.plot_widget.addItem(text)
    def get_start_node(self):
        current_text = self.start_node_combo.currentText()
        return int(current_text) if current_text else None

    def get_end_node(self):
        current_text = self.end_node_combo.currentText()
        return int(current_text) if current_text else None

    def update_start_node(self):
        self.start_node = self.get_start_node()
        self.update_canvas()

    def update_end_node(self):
        self.end_node = self.get_end_node()
        self.update_canvas()

    def start_algorithm(self):
        self.ant_colony = AntColonyAlgorithm(
            graph=self.graph,
            evaporation_rate=float(self.evaporation_rate_input.text()),
            pheromone_intensity=float(self.pheromone_intensity_input.text()),
            alpha=int(self.alpha_input.text()),
            beta=int(self.beta_input.text())
        )
        self.num_ants = int(self.num_ants_input.text())
        self.run_iterations()

    def stop_algorithm(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()

    def run_iterations(self):
        self.iteration = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_single_iteration)
        self.timer.start(1000)

    def run_single_iteration(self):
        """Итерация: моделирование движения муравьев и обновление феромонов."""
        if self.iteration >= 20:  # Завершаем после 20 итераций
            self.timer.stop()
            return

        all_paths = []
        for _ in range(self.num_ants):
            path, path_length = self.ant_colony.find_path(self.start_node, self.end_node)
            print(f"Ant path: {path}, Length: {path_length}")  # Вывод пути муравья
            if path_length < float('inf'):  # Исключаем тупиковые пути
                all_paths.append((path, path_length))

            self.visualize_ant_movement(path)

        if all_paths:
            best_path = min(all_paths, key=lambda x: x[1])[0]  # Берём путь с минимальной длиной
            print(f"Best path: {best_path}")  # Вывод лучшего пути
            self.ant_colony.update_pheromones(all_paths, best_path)

        self.plot_widget.clear()  # Удаляем предыдущие рёбра
        self.visualize_pheromones()  # Отображаем текущее состояние

        self.iteration += 1

    def visualize_ant_movement(self, path):
        """Отображение движения муравья по графу."""
        if not path:
            return

        pos = self.positions
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            x = [pos[u][0], pos[v][0]]
            y = [pos[u][1], pos[v][1]]

            # Рисуем путь муравья
            line = pg.PlotCurveItem(x, y, pen=pg.mkPen('yellow', width=3))
            self.plot_widget.addItem(line)
            QApplication.processEvents()  # Обновление интерфейса
            QTimer.singleShot(300, lambda: self.plot_widget.removeItem(line))  # Удаляем линию через 300 мс

    # Удаляем линию через 300 мс
    def visualize_initial_graph(self):
        """Отображает граф с начальным состоянием."""
        self.plot_widget.clear()
        pos = self.positions  # Фиксированные позиции узлов

        # Отрисовка рёбер с одинаковой толщиной
        for u, v, data in self.graph.edges(data=True):
            line = pg.PlotCurveItem(
                [pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                pen=pg.mkPen(color=(200, 200, 200), width=2)  # Начальная ширина
            )
            self.plot_widget.addItem(line)

        # Отрисовка узлов
        for node in self.graph.nodes:
            x, y = pos[node]
            color = '#6fcf97' if node == self.start_node else '#f2994a' if node == self.end_node else '#eb5757'
            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='white')
            text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))
            text.setPos(x, y)
            self.plot_widget.addItem(text)

    def visualize_best_path(self, best_path):
        self.plot_widget.clear()
        pos = self.positions
        edges = self.graph.edges(data=True)

        for u, v, data in edges:
            pheromone = data['pheromone']
            line = pg.PlotCurveItem(
                [pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                pen=pg.mkPen(color=(200, 200, 200, int(pheromone * 255)), width=2)
            )
            self.plot_widget.addItem(line)

        for node in self.graph.nodes:
            x, y = pos[node]
            if node == self.start_node:
                color = '#6fcf97'
            elif node == self.end_node:
                color = '#f2994a'
            else:
                color = '#eb5757'

            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='white')
            text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))
            text.setPos(x, y)
            self.plot_widget.addItem(text)

        if best_path:
            for i in range(len(best_path) - 1):
                u, v = best_path[i], best_path[i + 1]
                x = [pos[u][0], pos[v][0]]
                y = [pos[u][1], pos[v][1]]
                path_line = pg.PlotCurveItem(x, y, pen=pg.mkPen('blue', width=4))
                self.plot_widget.addItem(path_line)

    def visualize_pheromones(self):
        """Обновляет граф с отображением феромонов на рёбрах."""
        self.plot_widget.clear()
        pos = self.positions

        # Отрисовка рёбер с толщиной, зависящей от уровня феромонов
        for u, v, data in self.graph.edges(data=True):
            pheromone = data['pheromone']
            intensity = max(50, min(int(pheromone * 255), 255))  # Для прозрачности
            width = max(1, int(pheromone * 10))  # Толщина зависит от феромонов
            line = pg.PlotCurveItem(
                [pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                pen=pg.mkPen(color=(200, 0, 0, intensity), width=width)
            )
            self.plot_widget.addItem(line)

        # Отображение узлов
        for node in self.graph.nodes:
            x, y = pos[node]
            color = '#6fcf97' if node == self.start_node else '#f2994a' if node == self.end_node else '#eb5757'
            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='white')
            text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))
            text.setPos(x, y)
            self.plot_widget.addItem(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec_())
