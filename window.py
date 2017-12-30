import sys
import math

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import QParallelAnimationGroup
from PyQt5 import QtCore
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QGraphicsScene

import engine


class MainWindow(QWidget):
    label = None

    def __init__(self, game_size):
        super().__init__()
        self.setWindowTitle("2048")
        self.resize(game_size*150, game_size*150)
        self.init_UI(game_size)

    def init_UI(self, game_size):
        label = QLabel("0", parent=self)
        label.move(295, 550)
        self.scene = MainScene(game_size)
        self.view = QGraphicsView(self.scene, parent = self)
        self.view.setGeometry(65, 10, 420, 420)
        self.setFocus()
        self.engine = engine.GameEngine(game_size, Animator(game_size, self.scene))
        self.show()

    def keyPressEvent(self, e):
        self.engine.do_thing(e.key())


class MainScene(QGraphicsScene):

    def __init__(self, game_size):
        super().__init__(0, 0, game_size * 100 + 15, game_size * 100 + 15)
        self.prepare_scene(game_size)

    def prepare_scene(self, game_size):
        self.setBackgroundBrush(QBrush(QColor(200, 200, 210)))
        brush = QBrush(QColor(100, 100, 255))
        self.add_vertical_lines(game_size, brush)
        self.add_horizontal_lines(game_size, brush)

    def add_vertical_lines(self, game_size, brush):
        height = self.height()
        for i in range(1, game_size):
            x = i * 100 + (i - 1) * 5
            y = 0
            self.addRect(x, y, 5, height, brush=brush)

    def add_horizontal_lines(self, game_size, brush):
        width = self.width()
        for i in range(1, game_size):
            x = 0
            y = i * 100 + (i - 1) * 5
            self.addRect(x, y, width, 5, brush=brush)


class GraphicBlock(QObject):

    def __init__(self, y, x, nominal=2, animator = None):
        super().__init__()
        self._i = y
        self._j = x
        self.graphic_rect = QGraphicsRectItem(105 * x, 105 * y, 100, 100)
        # self.graphic_rect.setBrush(QBrush(QColor(255, 255 - nominal*20, 0))
        self.move_animation = None
        self._nominal = nominal
        self.animator = animator
        self.pin()
        self.refresh_color()

    def __str__(self):
        x = self.graphic_rect.rect().x()
        y = self.graphic_rect.rect().y()
        return "Nominal: {0}  x: {1}  y: {2}".format(self.nominal, x, y)

    @property
    def nominal(self):
        return self._nominal

    @nominal.setter
    def nominal(self,value):
        self._nominal = value
        self.animator.brush_list.append(self)

    @property
    def i(self):
        return self._i

    @i.setter
    def i(self, value):
        self.move_animation = QPropertyAnimation(self, b"geometry")
        self.move_animation.setDuration(int(math.fabs(self._i - value))*100)
        self.move_animation.setEndValue(QRectF(self.j * 105, value * 105, 100, 100))
        self.animator.animations.addAnimation(self.move_animation)
        self._i = value

    @property
    def j(self):
        return self._j

    @j.setter
    def j(self, value):
        self.move_animation = QPropertyAnimation(self, b"geometry")
        self.move_animation.setDuration(int(math.fabs(self._j - value))*100)
        self.move_animation.setEndValue(QRectF(value * 105, self.i * 105, 100, 100))
        self.animator.animations.addAnimation(self.move_animation)
        self._j = value

    def pin(self):
        self.animator.recent_added.append(self)

    def remove(self):
        self.animator.black_list.append(self)

    @QtCore.pyqtProperty(QRectF)
    def geometry(self):
        return self.graphic_rect.rect()

    @geometry.setter
    def geometry(self, qrect):
        self.graphic_rect.setRect(qrect)

    def refresh_color(self):
        rgb_tuple = (math.log(self.nominal, 2) * 15, 0, 200 - math.log(self.nominal, 2) * 15)
        self.graphic_rect.setBrush(QBrush(QColor(*rgb_tuple)))



class Animator:
    def __init__(self, game_size, scene):
        self.game_size = game_size
        self.scene = scene
        self.refresh_animations()
        self.black_list = []
        self.brush_list = []
        self.recent_added = []
        self.pin_animation = None
        self.locked = False

    def refresh_animations(self):
        self.animations = QParallelAnimationGroup()
        self.animations.finished.connect(self.refresh_blocks)

    def animate(self):
        self.locked = True
        self.animations.start()


    def refresh_blocks(self):

        for block in self.black_list:
            self.unpin_from_scene(block)
        self.black_list = []

        for block in self.brush_list:
            # block.graphic_rect.setBrush(QBrush(QColor(255, 255-block.nominal * 20, 0)))
            block.refresh_color()
        self.brush_list = []

        for block in self.recent_added:
            self.pin_to_scene(block)
        self.recent_added = []

        self.locked = False

        self.refresh_animations()

    def pin_to_scene(self, block):
        self.scene.addItem(block.graphic_rect)

    def unpin_from_scene(self, block):
        self.scene.removeItem(block.graphic_rect)






if __name__ == '__main__':

    game_size = 4
    app = QApplication(sys.argv)
    window = MainWindow(game_size)

    sys.exit(app.exec_())
