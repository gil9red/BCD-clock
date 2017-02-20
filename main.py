#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


"""
Скрипт для рисования часов с двоично-десятичным представлением.

Пример: https://upload.wikimedia.org/wikipedia/commons/2/27/Binary_clock.svg
Статья: https://ru.wikipedia.org/wiki/Двоично-десятичный_код

"""


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# Для отлова всех исключений, которые в слотах Qt могут "затеряться" и привести к тихому падению
def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)

    import traceback
    text += ''.join(traceback.format_tb(tb))

    print('Error: ', text)
    QMessageBox.critical(None, 'Error', text)
    quit()


import sys
sys.excepthook = log_uncaught_exceptions


class BCDClock(QWidget):
    DECIMAL_NUMBER_BY_BCD = {
        #   1  2  4  8
        0: (0, 0, 0, 0),
        1: (1, 0, 0, 0),
        2: (0, 1, 0, 0),
        3: (1, 1, 0, 0),
        4: (0, 0, 1, 0),
        5: (1, 0, 1, 0),
        6: (0, 1, 1, 0),
        7: (1, 1, 1, 0),
        8: (0, 0, 0, 1),
        9: (1, 0, 0, 1),
    }

    def __init__(self):
        super().__init__()

        self.setWindowTitle('BCD (Binary-coded decimal) clock')

        self._space_between_cell = 10
        self._indent_x = 20
        self._indent_y = 70
        self._size_cell = 50

        #    1  2  4  8
        self._grid = (
            # HH
            (0, 0, 0, 0),
            (0, 0, 0, 0),

            # MM
            (0, 0, 0, 0),
            (0, 0, 0, 0),

            # SS
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )

        self.hours = 0
        self.minutes = 0
        self.seconds = 0

        self._update_time_of_clock()

        self._timer = QTimer()
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._update_time_of_clock)
        self._timer.start()

    def _update_time_of_clock(self):
        from datetime import datetime
        now = datetime.now()

        self.hours = now.hour
        self.minutes = now.minute
        self.seconds = now.second

        c1, c2 = divmod(self.hours, 10)
        c3, c4 = divmod(self.minutes, 10)
        c5, c6 = divmod(self.seconds, 10)

        self._grid = (
            # HH
            self.DECIMAL_NUMBER_BY_BCD[c1],
            self.DECIMAL_NUMBER_BY_BCD[c2],

            # MM
            self.DECIMAL_NUMBER_BY_BCD[c3],
            self.DECIMAL_NUMBER_BY_BCD[c4],

            # SS
            self.DECIMAL_NUMBER_BY_BCD[c5],
            self.DECIMAL_NUMBER_BY_BCD[c6],
        )

        # Вызов перерисовки
        self.update()

    def _get_pos_size_cell(self, row, col):
        x = self._indent_x + (self._size_cell + self._space_between_cell) * col
        y = self._indent_y + (self._size_cell + self._space_between_cell) * row
        w = self._size_cell
        h = self._size_cell

        return x, y, w, h

    @staticmethod
    def calc_from_bcd(bcd: [int, int, int, int]) -> (int, str):
        """
        Функция принимает последовательность разрядов в BCD, считает в десятичном виде,
        записывает расчеты в виде суммы например: "1+2+0+8" и возвращает строку с расчетами
        и само итоговое десятичное значение. Для примера расчета это: 11.

        """

        # 1 2 4 8
        num = 0

        calculation_str = "1" if bcd[0] else "0"
        if bcd[0]:
            num += 1

        calculation_str += "+" + ("2" if bcd[1] else "0")
        if bcd[1]:
            num += 2

        calculation_str += "+" + ("4" if bcd[2] else "0")
        if bcd[2]:
            num += 4

        calculation_str += "+" + ("8" if bcd[3] else "0")
        if bcd[3]:
            num += 8

        return num, calculation_str

    def _draw_balls(self, painter, grid):
        painter.save()

        # Перебор по столбцам
        for j, cols in enumerate(grid):
            for i, row in enumerate(reversed(cols)):
                if row:
                    color = Qt.darkGray
                else:
                    color = QColor("#EDEDEB")

                painter.setPen(color)
                painter.setBrush(color)

                x, y, w, h = self._get_pos_size_cell(i, j)
                painter.drawEllipse(x, y, w, h)

        painter.restore()

    def _draw_vertical_lines(self, painter):
        painter.save()

        painter.setPen(QPen(Qt.darkGray, 2))

        x, y, w, h = self._get_pos_size_cell(0, 2)
        x -= self._space_between_cell / 2
        painter.drawLine(x, 0, x, self.height())

        x, y, w, h = self._get_pos_size_cell(0, 4)
        x -= self._space_between_cell / 2
        painter.drawLine(x, 0, x, self.height())

        painter.restore()

    def _draw_weight_of_number(self, painter):
        painter.save()

        painter.setPen(Qt.lightGray)
        painter.setFont(QFont("Arial", 26))

        for i, c in enumerate(['8', '4', '2', '1']):
            x, y, w, h = self._get_pos_size_cell(i, 6)
            painter.drawText(x, y, w, h, Qt.AlignCenter, c)

        painter.restore()

    def _draw_time_format(self, painter):
        painter.save()

        painter.setPen(QColor('#555753'))
        painter.setFont(QFont("Arial", 30, QFont.Bold))

        y = self._indent_y - 70
        h = self._size_cell
        w = self._size_cell * 2 + self._space_between_cell

        x = self._indent_x
        painter.drawText(x, y, w, h, Qt.AlignCenter, "HH")

        x = self._indent_x + w
        painter.drawText(x, y, 10, h, Qt.AlignCenter, ":")

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 2
        painter.drawText(x, y, w, h, Qt.AlignCenter, "MM")

        x = self._indent_x + w * 2 + self._space_between_cell / 2
        painter.drawText(x, y, 20, h, Qt.AlignCenter, ":")

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 4
        painter.drawText(x, y, w, h, Qt.AlignCenter, "SS")

        painter.restore()

    def _draw_calc_decimal(self, painter, x, y, bsd_grid_column_index):
        value, calc = self.calc_from_bcd(self._grid[bsd_grid_column_index])

        h = self._size_cell
        w = self._size_cell

        painter.setPen(Qt.gray)
        painter.setFont(QFont("Arial", 7))

        painter.drawText(x, y, w, h, Qt.AlignCenter, calc)
        painter.drawText(x, y + 15, w, h, Qt.AlignCenter, '=')

        painter.setFont(QFont("Arial", 20))
        painter.drawText(x, y + 40, w, h, Qt.AlignCenter, str(value))

    def _draw_calculation(self, painter):
        painter.save()

        x = self._indent_x
        y = self._indent_y + 250

        self._draw_calc_decimal(painter, x, y, 0)

        x = self._indent_x + self._size_cell + self._space_between_cell
        self._draw_calc_decimal(painter, x, y, 1)

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 2
        self._draw_calc_decimal(painter, x, y, 2)

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 3
        self._draw_calc_decimal(painter, x, y, 3)

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 4
        self._draw_calc_decimal(painter, x, y, 4)

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 5
        self._draw_calc_decimal(painter, x, y, 5)

        painter.restore()

    def _draw_time(self, painter):
        painter.save()

        painter.setPen(QColor('#555753'))
        painter.setFont(QFont("Arial", 44, QFont.Bold))

        y = self._indent_y + 350
        h = self._size_cell
        w = self._size_cell * 2 + self._space_between_cell

        x = self._indent_x
        painter.drawText(x, y, w, h, Qt.AlignCenter, str(self.hours).zfill(2))

        x = self._indent_x + w
        painter.drawText(x, y, 10, h, Qt.AlignCenter, ":")

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 2
        painter.drawText(x, y, w, h, Qt.AlignCenter, str(self.minutes).zfill(2))

        x = self._indent_x + w * 2 + self._space_between_cell / 2
        painter.drawText(x, y, 20, h, Qt.AlignCenter, ":")

        x = self._indent_x + (self._size_cell + self._space_between_cell) * 4
        painter.drawText(x, y, w, h, Qt.AlignCenter, str(self.seconds).zfill(2))

        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.white)
        painter.setBrush(Qt.white)

        painter.drawRect(self.rect())

        # Рисование шариков
        self._draw_balls(painter, self._grid)

        # Рисование вертикальных линий для разделения часов, минут и секунд
        self._draw_vertical_lines(painter)

        # Рисование цифр в последнем столбце
        self._draw_weight_of_number(painter)

        # Рисование надписи "HH:MM:SS"
        self._draw_time_format(painter)

        # Рисование рассчетов
        self._draw_calculation(painter)

        # Рисование времени в формате "HH:MM:SS"
        self._draw_time(painter)


if __name__ == '__main__':
    app = QApplication([])

    w = BCDClock()
    w.show()
    w.resize(430, 480)

    app.exec()
