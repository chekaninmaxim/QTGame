import random

import window


class Block:
    def __init__(self, i, j, nominal, map, animator):
        self.y = i
        self.x = j
        self._nominal = nominal
        self.map = map
        self.graphic_block = window.GraphicBlock(i, j, nominal, animator)
        self.brother = None

    @property
    def nominal(self):
        return self._nominal

    @nominal.setter
    def nominal(self, value):
        self._nominal = value
        self.graphic_block.nominal = value

    def move_x(self, direction):
        old_x = self.x
        new_x = self.x + direction
        while new_x in range(len(self.map)) and (not self.map[self.y][new_x]):
            new_x += direction
        if new_x in range(len(self.map)) and self.map[self.y][new_x] \
                and self.map[self.y][new_x].is_couple(self):
            self.x = new_x
            self.graphic_block.j = new_x
            self.map[self.y][old_x] = None
        else:
            new_x -= direction
            if old_x != new_x:
                self.x = new_x
                self.map[self.y][self.x] = self
                self.map[self.y][old_x] = None
                self.graphic_block.j = new_x


    def move_y(self, direction):
        old_y = self.y
        new_y = self.y + direction
        while new_y in range(len(self.map)) and (not self.map[new_y][self.x]):
            new_y += direction
        if new_y in range(len(self.map)) \
                and self.map[new_y][self.x] \
                and self.map[new_y][self.x].is_couple(self):
            if old_y == new_y:
                return
            self.y = new_y
            self.map[old_y][self.x] = None
            self.graphic_block.i = new_y
        else:
            new_y -= direction
            if old_y != new_y:
                self.y = new_y
                self.map[self.y][self.x] = self
                self.map[old_y][self.x] = None
                self.graphic_block.i = new_y

    def remove(self):
        self.graphic_block.remove()

    def is_couple(self, block):
        if self.brother:
            return False
        if self._nominal == block.nominal:
            self.brother = block
            return True
        return False


class Logic:
    def __init__(self, game_size, animator):
        self.map = [[None for _ in range(game_size)] for _ in range(game_size)]
        self.moved_blocks = {}
        self.game_size = game_size
        self.__states = []
        self.lose = False
        self.animator = animator
        self.add_block(0,0,2)

    def _next_step(self):
        if self.moved_blocks:
            self.__states.append(self.moved_blocks)
            self.moved_blocks = {}
        else:
            for i, line in enumerate(self.map):
                for j, block in enumerate(line):
                    self.moved_blocks[(i, j)] = block.nominal if block else None

    def _finish_step(self):
        self.animator.animate()
        self.refresh_nominals()
        self.add_random_blocks()

    def move_all_blocks_down(self):
        self._next_step()
        lines = list(zip(*self.map))
        for line in lines:
            self._move_one_line_blocks_forward(line, "y")
        self._finish_step()

    def move_all_blocks_up(self):
        lines = zip(*self.map)
        for line in lines:
            self._move_one_line_blocks_back(line, "y")
        self._finish_step()

    def move_all_blocks_right(self):
        self._next_step()
        for line in self.map:
            self._move_one_line_blocks_forward(line, "x")
        self._finish_step()

    def move_all_blocks_left(self):
        self._next_step()
        for line in self.map:
            self._move_one_line_blocks_back(line, "x")
        self._finish_step()

    def undo(self):
        pass

    def _move_one_line_blocks_forward(self, array, coord):
        for block in reversed(array):
            if block:
                block.__getattribute__("move_" + coord)(1)

    def _move_one_line_blocks_back(self, array, coord):
        for block in array:
            if block:
                block.__getattribute__("move_" + coord)(-1)

    def add_random_blocks(self):
        counter = 0
        for i, line in enumerate(self.map):
            for j, block in enumerate(line):
                if not self.map[i][j]:
                    counter += 1
                    chance = random.randint(1, 10)
                    if chance < 2:
                        nominal = 2 * random.randint(0, 1) + 2
                        self.add_block(i, j, nominal)
        if counter == 0:
            self.lose = True

    def add_block(self, i, j, nominal):
        self.map[i][j] = Block(i, j, nominal, self.map, self.animator)

    def refresh_nominals(self):
        for line in self.map:
            for block in line:
                if block and block.brother:
                    block.nominal = block.nominal * 2
                    block.brother.remove()
                    block.brother = None

    def game_over(self):
        self.animator.scene.clear()

    def print_map(self):
          for line in self.map:
              print([str(block.graphic_block) if block else "None" for block in line])
