import sys
import networkx as nx
import pyqtgraph as pg
from app.view.window_view import GraphWindow
from app.model.ant_colony import AntColonyAlgorithm
from app.model.ant import Ant
from app.model.graph_model import GraphModel
from app.controller.controller import Controller
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox
from PyQt5.QtCore import QTimer


def main():
    app = QApplication(sys.argv)

    # Создаем модель
    model = GraphModel()

    # Создаем представление (окно)
    view = GraphWindow()  # Создаем представление без контроллера

    # Создаем контроллер, связываем его с моделью и представлением
    controller = Controller(view, model)

    # Передаем контроллер в представление
    view.controller = controller

    # Показываем окно приложения
    view.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()