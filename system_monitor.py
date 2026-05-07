#!/usr/bin/env python3
import sys
import psutil
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QMenu, QAction)
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QFont

class SystemMonitorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.85)               # прозрачность 85%
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # Метка для отображения информации
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0,0,0,150);
                border-radius: 8px;
                padding: 8px;
                font-family: monospace;
                font-size: 12pt;
            }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedSize(240, 110)   # чуть больше под три строки

        # Переменные для расчёта скорости сети
        self.prev_net = psutil.net_io_counters()
        self.first_net = True

        # Таймер обновления (1 секунда)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

        self.update_metrics()

        # Для перетаскивания окна
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        menu.exec_(event.globalPos())

    def update_metrics(self):
        cpu = self.get_cpu_usage()
        ram = self.get_ram_usage()
        net = self.get_network_speed()
        self.label.setText(f"CPU: {cpu}\nRAM: {ram}\n{net}")

    def get_cpu_usage(self):
        # psutil возвращает процент за интервал с прошлого вызова
        # но если мы вызываем каждую секунду, можно использовать psutil.cpu_percent()
        return f"{psutil.cpu_percent(interval=None):.1f}%"

    def get_ram_usage(self):
        mem = psutil.virtual_memory()
        return f"{mem.percent:.1f}%"

    def get_network_speed(self):
        cur = psutil.net_io_counters()
        if self.first_net:
            self.prev_net = cur
            self.first_net = False
            return "↓ 0.0 KB/s  ↑ 0.0 KB/s"

        # Скорость в байтах/сек -> КБайт/сек
        rx_speed = (cur.bytes_recv - self.prev_net.bytes_recv) / 1024.0
        tx_speed = (cur.bytes_sent - self.prev_net.bytes_sent) / 1024.0

        self.prev_net = cur
        return f"↓ {rx_speed:.1f} KB/s  ↑ {tx_speed:.1f} KB/s"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitorWindow()
    window.show()
    sys.exit(app.exec_())
