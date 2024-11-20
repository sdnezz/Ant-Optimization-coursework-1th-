import sys
import networkx as nx
import pyqtgraph as pg
from ant_colony import AntColonyAlgorithm
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox

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
        self.ant_colony = None  # Экземпляр муравьиного алгоритма
        self.start_node = None

        # Инициализация элементов интерфейса
        self.create_controls()
        self.create_buttons()

        # Создаем виджет для графика с использованием pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground('w')  # Устанавливаем белый фон для графика

    def load_styles(self, style_file):
        """Загружает стили из указанного файла."""
        with open(style_file, "r") as file:
            self.setStyleSheet(file.read())

    def create_controls(self):
        controls_layout = QFormLayout()

        # Выпадающий список для выбора начальной точки
        self.start_node_combo = QComboBox(self)
        self.start_node_combo.currentIndexChanged.connect(self.update_start_node)
        controls_layout.addRow("Начальная точка:", self.start_node_combo)

        # Параметры алгоритма
        self.evaporation_rate_input = QLineEdit("0.5", self)
        self.pheromone_intensity_input = QLineEdit("1.0", self)
        self.alpha_input = QLineEdit("1", self)
        self.beta_input = QLineEdit("2", self)

        controls_layout.addRow("Коэффициент испарения:", self.evaporation_rate_input)
        controls_layout.addRow("Интенсивность феромонов:", self.pheromone_intensity_input)
        controls_layout.addRow("Вес феромонов (alpha):", self.alpha_input)
        controls_layout.addRow("Вес расстояния (beta):", self.beta_input)

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
        buttons_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton('Сброс')
        self.reset_button.clicked.connect(self.reset_graph)
        buttons_layout.addWidget(self.reset_button)

        self.update_params_button = QPushButton('Изменить параметры')
        self.update_params_button.clicked.connect(self.update_parameters)
        buttons_layout.addWidget(self.update_params_button)

        self.layout.addLayout(buttons_layout)

    def load_graph(self):
        """Загрузка графа из файла."""
        file_name, _ = QFileDialog.getOpenFileName(self, 'Открыть файл графа', '', 'Text Files (*.txt);;All Files (*)')

        if file_name:
            self.graph = self.load_graph_from_file(file_name)
            self.initialize_pheromones()
            self.update_start_node_combo()
            self.start_node = self.get_start_node()
            self.update_canvas()

    def load_graph_from_file(self, file_path):
        """Загрузка графа из файла."""
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
        """Инициализация феромонов на всех рёбрах графа."""
        for u, v in self.graph.edges:
            self.graph[u][v]['pheromone'] = 1.0

    def update_start_node_combo(self):
        self.start_node_combo.clear()
        for node in sorted(self.graph.nodes):
            self.start_node_combo.addItem(str(node))

    def get_start_node(self):
        """Получает текущую начальную точку из выпадающего списка."""
        current_text = self.start_node_combo.currentText()
        if current_text:
            return int(current_text)
        return None

    def update_start_node(self):
        self.start_node = self.get_start_node()
        if self.start_node is not None:
            self.update_canvas()

    def update_parameters(self):
        """Обновляет параметры алгоритма."""
        self.evaporation_rate = float(self.evaporation_rate_input.text())
        self.pheromone_intensity = float(self.pheromone_intensity_input.text())
        self.alpha = int(self.alpha_input.text())
        self.beta = int(self.beta_input.text())

    def start_algorithm(self):
        """Запуск муравьиного алгоритма."""
        self.update_parameters()
        self.ant_colony = AntColonyAlgorithm(
            graph=self.graph,
            evaporation_rate=self.evaporation_rate,
            pheromone_intensity=self.pheromone_intensity,
            alpha=self.alpha,
            beta=self.beta
        )
        # Пример работы алгоритма (с реальной логикой добавим позже)
        print("Алгоритм запущен.")
        current_node = self.start_node
        probabilities = self.ant_colony.calculate_probabilities(current_node, visited_nodes=[current_node])
        print("Вероятности переходов:", probabilities)

    def reset_graph(self):
        """Сбрасывает граф и параметры к начальному состоянию."""
        self.load_graph()

    def update_canvas(self):
        """Очищает и перерисовывает граф на виджете pyqtgraph."""
        self.plot_widget.clear()

        pos = nx.spring_layout(self.graph)  # Позиции для узлов
        edges = self.graph.edges(data=True)

        # Отрисовка рёбер
        for u, v, data in edges:
            x = [pos[u][0], pos[v][0]]
            y = [pos[u][1], pos[v][1]]
            line = pg.PlotCurveItem(x, y, pen=pg.mkPen('gray', width=2))  # Серые линии для рёбер
            self.plot_widget.addItem(line)

            # Добавляем текст для расстояния
            mid_x = (pos[u][0] + pos[v][0]) / 2
            mid_y = (pos[u][1] + pos[v][1]) / 2
            distance_text = pg.TextItem(str(data['weight']), anchor=(0.5, 0.5), color='black')  # Черный текст
            distance_text.setFont(pg.QtGui.QFont("Arial", 10, pg.QtGui.QFont.Bold))  # Устанавливаем шрифт
            distance_text.setPos(mid_x, mid_y)
            self.plot_widget.addItem(distance_text)

        # Отрисовка узлов
        for node in self.graph.nodes:
            x, y = pos[node]
            color = '#6fcf97' if node == self.start_node else '#eb5757'  # Зеленый для начальной вершины, красный для остальных
            scatter = pg.ScatterPlotItem([x], [y], symbol='o', size=30, brush=color)
            self.plot_widget.addItem(scatter)

            # Текст внутри узлов
            text = pg.TextItem(str(node), anchor=(0.5, 0.5), color='white')
            text.setFont(pg.QtGui.QFont("Arial", 12, pg.QtGui.QFont.Bold))
            text.setPos(x, y)
            self.plot_widget.addItem(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec_())
