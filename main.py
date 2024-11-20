import sys
import networkx as nx
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox
import pyqtgraph as pg


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Граф доставки для алгоритма муравьиной колонии')
        self.setGeometry(100, 100, 1000, 700)

        # Главный Layout
        self.layout = QVBoxLayout(self)

        # Изначально граф пустой
        self.graph = nx.Graph()
        self.start_node = None

        # Инициализация элементов интерфейса
        self.create_controls()
        self.create_buttons()

        # Создаем виджет для графика с использованием pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground('w')  # Устанавливаем белый фон для графика

    def create_controls(self):
        controls_layout = QFormLayout()

        # Выпадающий список для выбора начальной точки
        self.start_node_combo = QComboBox(self)
        self.start_node_combo.currentIndexChanged.connect(self.update_start_node)
        controls_layout.addRow("Начальная точка:", self.start_node_combo)

        # Параметры алгоритма
        self.evaporation_rate_input = QLineEdit("0.5", self)
        self.pheromone_intensity_input = QLineEdit("1.0", self)
        self.num_ants_input = QLineEdit("10", self)

        controls_layout.addRow("Коэффициент испарения:", self.evaporation_rate_input)
        controls_layout.addRow("Интенсивность феромонов:", self.pheromone_intensity_input)
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
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Остановка')
        buttons_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton('Сброс')
        self.reset_button.clicked.connect(self.reset_graph)
        buttons_layout.addWidget(self.reset_button)

        self.update_params_button = QPushButton('Изменить параметры')
        buttons_layout.addWidget(self.update_params_button)

        self.layout.addLayout(buttons_layout)

    def load_graph(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Открыть файл графа', '', 'Text Files (*.txt);;All Files (*)')

        if file_name:
            print("Загрузка нового графа")
            self.graph = self.load_graph_from_file(file_name)
            self.initialize_pheromones()
            self.update_start_node_combo()
            self.start_node = self.get_start_node()
            self.update_canvas()

    def load_graph_from_file(self, file_path):
        G = nx.Graph()
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    u, v, weight = map(int, line.split())
                    G.add_edge(u, v, weight=weight, pheromone=1.0)
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
        return G

    def initialize_pheromones(self):
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] = 1.0

    def update_start_node_combo(self):
        self.start_node_combo.clear()
        for node in sorted(self.graph.nodes):  # Сортируем узлы по порядку
            self.start_node_combo.addItem(str(node))

    def get_start_node(self):
        """Получает текущую начальную точку из выпадающего списка."""
        current_text = self.start_node_combo.currentText()
        if current_text:
            return int(current_text)  # Преобразуем в int, если не пустое значение
        return None  # Если список пуст

    def update_start_node(self):
        self.start_node = self.get_start_node()
        if self.start_node is not None:
            self.update_canvas()

    def reset_graph(self):
        self.load_graph()
        print("Сброс графа и параметров")

    def update_canvas(self):
        """Очищает и перерисовывает граф на виджете pyqtgraph."""
        self.plot_widget.clear()  # Очистка текущего графика

        pos = nx.spring_layout(self.graph)  # Позиции для узлов
        edges = self.graph.edges(data=True)

        # Отрисовка рёбер
        for u, v, data in edges:
            x = [pos[u][0], pos[v][0]]
            y = [pos[u][1], pos[v][1]]
            line = pg.PlotCurveItem(x, y, pen=pg.mkPen('b', width=2))  # Синие линии для рёбер
            self.plot_widget.addItem(line)

        # Отрисовка узлов
        for node in self.graph.nodes:
            x, y = pos[node]
            color = 'orange' if node == self.start_node else 'lightblue'
            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            # Добавляем текстовые метки внутри узлов
            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='k')  # Черный жирный текст
            text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))  # Устанавливаем шрифт
            text.setPos(x, y)
            self.plot_widget.addItem(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec_())
