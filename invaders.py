from datetime import datetime
from enum import Enum
import pygame as pg

WINSIZE = [640, 480]
WINCENTER = [320, 240]


class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.step = 0
        self.last_moved_at = None

        self.unpack_sprites()

    def is_enemy(self):
        return False

    def is_destroyable(self, el):
        # is object destroyable by el
        return False

    def draw(self, surface, color):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.sprites[self.sprite_step][y][x] == 1:
                    position = (x + self.x, y + self.y)
                    surface.set_at(position, color)

    # an object does nothing unless it's overriden in a child class
    def react(self, world, key, time, frame):
        pass

    def next_sprite(self):
        self.sprite_step = (self.sprite_step + 1) % len(self.sprites)

    def unpack_sprites(self):
        self.sprites = []

        # sprites could be loaded from an external file, but for
        # simplicity i'm keeping them in classes
        for pattern in self.SPRITES:
            sprite = []
            for y in pattern:
                line = []
                for x in y:
                    line += [int(x), int(x)]  # scale up sprites
                sprite += [line, line]
            self.sprites.append(sprite)

        self.WIDTH *= 2
        self.HEIGHT *= 2
        self.sprite_step = 0


class Player(GameObject):
    STEP_X = 10

    WIDTH = 13
    HEIGHT = 8

    GUN_POINT = (13, -8)

    SPRITES = [[
        '0000001000000',
        '0000011100000',
        '0000011100000',
        '0111111111110',
        '1111111111111',
        '1111111111111',
        '1111111111111',
        '1111111111111',
    ]]

    def __init__(self, x, y):
        super().__init__(x, y)

        self.last_shoot_at = None

    def react(self, world, key, time, frame):
        if key[pg.K_LEFT] and self.x - self.STEP_X > 0:
            self.x -= self.STEP_X
        elif key[pg.K_RIGHT] and self.x + self.WIDTH + self.STEP_X < WINSIZE[0]:
            self.x += self.STEP_X
        elif key[pg.K_SPACE]:
            # sort or reloading delay
            if self.last_shoot_at is None or frame - self.last_shoot_at > 20:
                bullet = Bullet(self.x + self.GUN_POINT[0], self.y + self.GUN_POINT[1])
                world.add_object(bullet)

                self.last_shoot_at = frame


class Enemy(GameObject):
    STEP_X = 3
    STEP_Y = 10

    def __init__(self, x, y):
        super().__init__(x, y)

        # enemies have different width, so i'm precalculating number
        # of steps they can make in one direction
        self.STEPS = 20

    def is_destroyable(self, el):
        # enemy is always destroyable since we have only a bullet class
        return True

    def is_enemy(self):
        return True

    def react(self, world, key, time, frame):
        if frame % 10 == 0:
            self.last_moved_at = time
            self.step += 1

            if self.step < self.STEPS:
                self.x += self.STEP_X
            elif self.step == self.STEPS:
                self.y += self.STEP_Y
            elif self.step > self.STEPS and self.step < 2 * self.STEPS:
                self.x -= self.STEP_X
            elif self.step >= 2 * self.STEPS:
                self.y += self.STEP_Y
                self.step = 0

            # destroy shields if enemies are dangerously close
            if self.y >= 370:
                world.destroy_shilds()

            if self.y >= 410:
                world.game_over()

            self.next_sprite()


class Bullet(GameObject):
    STEP_Y = 5

    WIDTH = 3
    HEIGHT = 5
    SPRITES = [[
        '001',
        '010',
        '100',
        '010',
        '001',
    ], [
        '010',
        '101',
        '010',
        '101',
        '010',
    ]]

    def react(self, world, key, time, frame):
        if frame % 2 == 0:
            self.y -= self.STEP_Y

            # a bullet destroys enemies
            for el in world.objects:
                if el.is_destroyable(self):
                    rect1 = ((self.x, self.y), (self.x + self.WIDTH, self.y + self.HEIGHT))
                    rect2 = ((el.x, el.y), (el.x + el.WIDTH, el.y + el.HEIGHT))

                    # collision detection
                    if ((rect1[0][0] > rect2[0][0] and rect1[0][0] < rect2[1][0]) or
                        (rect1[1][0] > rect2[0][0] and rect1[1][0] < rect2[1][0])) and \
                        ((rect1[0][1] > rect2[0][1] and rect1[0][1] < rect2[1][1]) or
                         (rect1[1][1] > rect2[0][1] and rect1[1][1] < rect2[1][1])):
                        world.remove_object(el)
                        world.remove_object(self)
                        world.increment_score()
                        break

            self.next_sprite()


class Enemy1(Enemy):
    WIDTH = 8
    HEIGHT = 8

    SPRITES = [[
        '00011000',
        '00111100',
        '01111110',
        '11011011',
        '11111111',
        '01011010',
        '10000001',
        '01000010',
    ], [
        '00011000',
        '00111100',
        '01111110',
        '11011011',
        '11111111',
        '00100100',
        '01011010',
        '10100101',
    ]]


class Enemy2(Enemy):
    WIDTH = 11
    HEIGHT = 8

    SPRITES = [[
        '00100000100',
        '00010001000',
        '00111111100',
        '01101110110',
        '11111111111',
        '10111111101',
        '10100000101',
        '00011011000',
    ], [
        '00100000100',
        '10010001001',
        '10111111101',
        '11101110111',
        '11111111111',
        '01111111110',
        '00100000100',
        '01000000010',
    ]]


class Enemy3(Enemy):
    WIDTH = 12
    HEIGHT = 8

    SPRITES = [[
        '000011110000',
        '011111111110',
        '111111111111',
        '111001100111',
        '111111111111',
        '001110011100',
        '011001100110',
        '001100001100',
    ], [
        '000011110000',
        '011111111110',
        '111111111111',
        '111001100111',
        '111111111111',
        '000110011000',
        '001101101100',
        '110000000011',
    ]]

class Shield(GameObject):
    WIDTH = 22
    HEIGHT = 15

    SPRITES = [[
        '0000111111111111110000',
        '0001111111111111111000',
        '0011111111111111111100',
        '0111111111111111111110',
        '1111111111111111111111',
        '1111111111111111111111',
        '1111111111111111111111',
        '1111111111111111111111',
        '1111111111111111111111',
        '1111111111111111111111',
        '1111111111111111111111',
        '1111111000000001111111',
        '1111110000000000111111',
        '1111100000000000011111',
        '1111100000000000011111',
    ]]


class GameState(Enum):
    PLAYING = 1
    GAMEOVER = 2


class World:
    def __init__(self):
        self.score = 0

        self.player = Player(20, WINSIZE[1] - 40)
        self.shields = [
            Shield(WINSIZE[0] // 3 - 140, WINSIZE[1] - 100),
            Shield(WINSIZE[0] * 2 // 3 - 140, WINSIZE[1] - 100),
            Shield(WINSIZE[0] - 140, WINSIZE[1] - 100),
        ]

        self.enemies = []
        for y in range(2):
            for x in range(11):
                self.enemies.append(Enemy1(34 + x * 50, 20 + y * 50))
        for y in range(2):
            for x in range(11):
                self.enemies.append(Enemy2(31 + x * 50, 120 + y * 50))
        for x in range(11):
            self.enemies.append(Enemy3(30 + x * 50, 170 + y * 50))

        self.objects = []

        self.add_object(self.player)
        for el in self.enemies:
            self.add_object(el)
        for el in self.shields:
            self.add_object(el)

        self.game_state = GameState.PLAYING

    def add_object(self, el):
        self.objects.append(el)

    def increment_score(self):
        self.score += 1

    def remove_object(self, o):
        for i, el in enumerate(self.objects):
            if el == o:
                del self.objects[i]
                break

    def destroy_shilds(self):
        for i, el in enumerate(self.objects):
            if type(el) == Shield:
                del self.objects[i]

    def game_over(self):
        self.game_state = GameState.GAMEOVER

    def react(self, key, local_time, frame):
        for el in self.objects:
            el.react(self, key, local_time, frame)

        # wining condition
        enemies_left = sum(el.is_enemy() for el in self.objects)
        if enemies_left == 0:
            self.game_over()

    def render(self, surface):
        self.scoring(surface)
        self.draw(surface, WHITE)

    def scoring(self, surface):
        font = pg.font.SysFont(None, 24)
        img = font.render(str(self.score), True, WHITE)
        surface.blit(img, (20, 20))


    def reset(self, surface):
        # it's faster to paint the entire surface black than reset
        # object individually
        # self.draw(surface, BLACK)
        surface.fill(BLACK)

    def draw(self, surface, color):
        for el in self.objects:
            el.draw(surface, color)


WHITE = 255, 240, 200
BLACK = 20, 20, 40


def main():
    clock = pg.time.Clock()

    pg.init()

    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("Space Invaders")
    screen.fill(BLACK)

    frame = 0

    world = World()

    done = False
    while not done:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                done = True
                break

        # reset world
        world.reset(screen)

        # world events
        frame += 1
        time = datetime.utcnow()
        key_input = pg.key.get_pressed()

        # react is a function of signals. it's up to an object how to
        # interpret them, e.g. we can pass a random number to summon
        # UFO objects
        world.react(key_input, time, frame)

        # draw world
        world.render(screen)

        pg.display.update()

        clock.tick(50)

        # process post-events
        if world.game_state == GameState.GAMEOVER:
            done = True


if __name__ == "__main__":
    main()
