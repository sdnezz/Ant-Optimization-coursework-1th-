import sys
import time
import networkx as nx
import pyqtgraph as pg
import numpy as np
from app.model.graph_model import GraphModel
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QObject,QTimer


class Controller(QObject):
    """Класс контроллера, координирующий модель и представление."""

    def __init__(self):
        super().__init__()
        # Инициализация модели и представления
        self.model = GraphModel(self)  # Модель для работы с графом
        # Таймер для симуляции работы алгоритма
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)  # Подключаем таймер к обновлению времени
        self.elapsed_time = 0  # Начальное время в миллисекундах
        self.running = False  # Состояние работы алгоритма
        self.start_time = None  # Время старта алгоритма

    def show_error_message(self, title, message):
        """Показывает окно с ошибкой."""
        msg_box = QMessageBox(self.model.view)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.exec_()

    def run(self):
        """Запуск приложения."""
        self.model.set_view()
        self.model.view.show()

    def load_graph(self):
        """Загружает граф из файла и проверяет правильность формата."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(self.model.view, 'Открыть файл графа', '',
                                                       'Text Files (*.txt);;All Files (*)')

            if file_name:
                G = nx.Graph()
                with open(file_name, 'r') as file:
                    for line in file:
                        # Попробуем разделить строку на 3 компонента и проверить их на корректность
                        parts = line.split()
                        if len(parts) != 3:
                            raise ValueError(
                                f"Неверное количество элементов в строке: {line.strip()}. Ожидается 3 целочисленных элемента в каждой строке.")

                        try:
                            u, v, weight = map(int, parts)
                        except ValueError:
                            raise ValueError(f"Некорректные данные в строке: {line.strip()}. Ожидаются целые числа.")

                        # Добавляем ребро в граф с весом и феромоном
                        G.add_edge(u, v, weight=weight, pheromone=1.0)

                # Получаем вершины и сортируем их по возрастанию
                sorted_nodes = sorted(G.nodes)
                self.model.graph = G
                self.model.start_node = sorted_nodes[0]  # Пример начальной точки
                self.model.positions = nx.spring_layout(G)  # Генерация позиций узлов
                self.model.graph_to_view(sorted_nodes)
                self.set_parameters()
                # Отображаем статус в статус-баре
                self.model.view.status_bar.showMessage(f"Граф загружен: {file_name}")
            else:
                raise ValueError("Не выбран файл для загрузки.")

        except Exception as e:
            # Поймать любые исключения и вывести сообщение об ошибке
            self.model.view.status_bar.showMessage(f"Ошибка загрузки графа: {e}")
            self.show_error_message("Ошибка загрузки", f"Не удалось загрузить граф: {str(e)}")

    def get_start_node(self):
        current_text = self.model.view.start_node_combo.currentText()
        return int(current_text) if current_text else None

    def update_start_node(self):
        """Обновить начальную точку в модели."""
        self.model.start_node = self.get_start_node()
        self.model.view.update_canvas()

    def update_end_nodes(self):
        """Обновить конечные точки в модели и выполнить проверки."""

        # Получаем текст из поля ввода конечных точек
        current_text = self.model.view.end_nodes_input.text()

        try:
            # Преобразуем введенный текст в список целых чисел
            end_nodes = [int(x.strip()) for x in current_text.split(',') if x.strip().isdigit()]

            # Проверка на пустой список
            if not end_nodes:
                raise ValueError("Необходимо ввести хотя бы одну конечную точку.")

            # Проверка, что все введенные вершины существуют в графе
            for node in end_nodes:
                if node not in self.model.graph.nodes:
                    raise ValueError(f"Вершина {node} не существует в графе.")

            # Проверка на выбор всех точек, кроме начальной
            total_nodes = len(self.model.graph.nodes)
            if len(end_nodes) >= total_nodes:
                raise ValueError(f"Можно выбрать не более {total_nodes - 1} конечных точек.")

            # Проверка, что конечные точки не совпадают с начальной
            if self.model.start_node in end_nodes:
                raise ValueError(f"Начальная точка {self.model.start_node} не может быть конечной.")

            # Проверка на повторяющиеся точки
            if len(end_nodes) != len(set(end_nodes)):
                raise ValueError("Конечные точки не могут повторяться.")

            # Если все проверки прошли успешно, обновляем конечные точки в модели
            self.model.end_nodes = end_nodes
            self.model.view.update_canvas()  # Обновление графа

        except ValueError as e:
            # Если возникла ошибка, показываем сообщение в статус-баре
            self.model.view.status_bar.showMessage(f"Ошибка: {str(e)}")

    def set_parameters(self):
        """Обработчик для задания параметров."""
        try:
            # Получаем параметры из view
            evaporation_rate = float(self.model.view.evaporation_rate_input.text())
            pheromone_intensity = float(self.model.view.pheromone_intensity_input.text())
            alpha = float(self.model.view.alpha_input.text())
            beta = float(self.model.view.beta_input.text())
            num_ants = int(self.model.view.num_ants_input.text())

            # Проверка на корректность значений
            if evaporation_rate <= 0 or pheromone_intensity <= 0 or alpha <= 0 or beta <= 0 or num_ants <= 0:
                raise ValueError("Все параметры должны быть положительными числами.")

            # Передаем параметры в модель
            self.model.evaporation_rate = evaporation_rate
            self.model.pheromone_intensity = pheromone_intensity
            self.model.alpha = alpha
            self.model.beta = beta
            self.model.num_ants = num_ants

            # Выводим сообщение в статус-бар
            self.model.view.status_bar.showMessage("Параметры алгоритма успешно заданы.")
        except ValueError as e:
            # Если возникла ошибка при преобразовании значения, показываем ошибку
            self.model.view.status_bar.showMessage(f"Ошибка: {str(e)}")
            self.show_error_message("Ошибка", f"Некорректные параметры: {str(e)}")
        except Exception as e:
            # Для любых других ошибок
            self.model.view.status_bar.showMessage(f"Ошибка: {str(e)}")
            self.show_error_message("Ошибка", f"Не удалось задать параметры: {str(e)}")

    def update_time(self):
        """Обновление времени каждую миллисекунду с использованием time.time()."""
        if self.running and self.start_time is not None:
            current_time = time.time()  # Текущее время в секундах
            elapsed_seconds = current_time - self.start_time  # Время в секундах с начала старта

            minutes = int(elapsed_seconds // 60)
            seconds = int(elapsed_seconds % 60)
            milliseconds = int((elapsed_seconds * 1000) % 1000)  # Миллисекунды

            time_str = f"{minutes:02}:{seconds:02}:{milliseconds:03}"
            self.model.view.time_label.setText(time_str)

    def start_algorithm(self):
        """Запуск алгоритма и старта таймера."""
        if not self.running:
            self.running = True
            self.start_time = time.time()  # Фиксируем время старта
            self.timer.start(10)  # Обновляем каждую десятую миллисекунду
            self.model.run_aco()
            self.model.view.status_bar.showMessage("Алгоритм запущен.")

    def stop_algorithm(self):
        if self.running:
            self.running = False
            self.timer.stop()
            self.model.view.status_bar.showMessage("Алгоритм остановлен.")

    def reset_graph(self):
        """Сброс состояния алгоритма, таймера и начальных/конечных точек."""
        self.stop_algorithm()
        self.elapsed_time = 0
        self.model.view.time_label.setText("00:00:000")  # Сбрасываем метку времени
        self.model.start_node = None
        self.model.end_nodes = []
        self.model.view.start_node_combo.setCurrentIndex(0)
        self.model.view.end_nodes_input.clear()
        self.model.view.status_bar.showMessage("Работа сброшена.")
        self.model.view.update_canvas()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = Controller()
    controller.run()
    sys.exit(app.exec_())