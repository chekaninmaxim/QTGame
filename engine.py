from PyQt5.QtCore import Qt

import gamelogic


class GameEngine:

    def __init__(self, game_size, animator):
        self.game_size = game_size
        self.__logic = gamelogic.Logic(game_size, animator)
        self.animator = animator
        self._things_to_do = {
            Qt.Key_Down: self.__logic.move_all_blocks_down,
            Qt.Key_Up: self.__logic.move_all_blocks_up,
            Qt.Key_Right: self.__logic.move_all_blocks_right,
            Qt.Key_Left: self.__logic.move_all_blocks_left
        }

    def do_thing(self, key):
        if self.animator.locked:
            return
        if self.__logic.lose:
            self.__logic.game_over()
            return
        self._things_to_do[key]()

    def get_map(self):
        return self.__logic.map
