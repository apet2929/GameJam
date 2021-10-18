import pygame
import pygame.sprite as Sprite
from pygame.sprite import RenderUpdates
from enum import Enum
import pygame.freetype
from pygame.math import Vector2
import pickle
import os
import math
from sys import maxsize
from pygame import Rect

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

# if getattr(sys, 'frozen', False):
#     os.chdir(sys._MEIPASS)

#  Constant Variables
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

FPS = 60
clock = pygame.time.Clock()
TILE_SIZE = 50

NUMTILES = 2

level = 1
max_levels = 28
musicplaying = False

current_line = 0

water_group = pygame.sprite.Group()
trigger_group = pygame.sprite.Group()
rope_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
person_group = pygame.sprite.Group()
falling_spike_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

wind_trigger = 18

map_img = pygame.image.load(os.path.join('assets', 'img', 'map_scroll.png'))
sun_img = pygame.image.load(os.path.join('assets', 'img', 'sun.png'))
bg_img = pygame.image.load(os.path.join('assets', 'img', 'sky.png'))
restart_img = pygame.image.load(os.path.join('assets', 'img', 'restart_btn.png'))

cutscene_1_img = pygame.image.load(os.path.join('assets', 'img','cutscene_1.png'))
cutscene_2_img = pygame.image.load(os.path.join('assets', 'img','cutscene_2.png'))
cutscene_3_img = pygame.image.load(os.path.join('assets', 'img','cutscene_3.png'))
cutscene_4_img = pygame.image.load(os.path.join('assets', 'img','cutscene_4.png'))

#Cutscenes: (level trigger, start line, end line)
#Level trigger = level + 1
cutscene_1 = (9, 1, 9)
cutscene_2 = (12, 12, 21)
cutscene_3 = (18, 24, 42)
cutscene_4 = (28, 45, 60)

class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1
    NEXT_LEVEL = 2
    CUTSCENE = 3
    NEXT_LINE = 4
    RETURN = 5
    MAP = 6

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        #  get mouse pos
        pos = pygame.mouse.get_pos()

        #  check mouse over and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action


class UIElement(pygame.sprite.Sprite):

    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        super().__init__()

        self.mouse_over = False

        default_image = create_surface_with_text(
            text, font_size, text_rgb, bg_rgb)

        highlighted_image = create_surface_with_text(
            text, font_size * 1.2, text_rgb, bg_rgb)

        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position)]

        self.action = action

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False


class Camera():
    def __init__(self, x, y):
        self.pos = Vector2()
        self.pos.x = x
        self.pos.y = y

    def lerp(self, other, t):
        self.pos.x += (other.x - self.pos.x) * t
        self.pos.y += (other.y - self.pos.y) * t


class Person(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(os.path.join('assets', 'img', 'kelsey.png'))
        img = pygame.transform.scale(img, (40, 80))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 20
        self.text = text


class Trigger(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(os.path.join('assets', 'img', 'exit.png'))
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Rope(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(os.path.join('assets', 'img', 'rope_2.png'))
        img = pygame.transform.scale(img, (TILE_SIZE*2, TILE_SIZE*2))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x - TILE_SIZE//2
        self.rect.y = y
        self.rect.width = 2


class FallingSpike(pygame.sprite.Sprite):
    def __init__(self, x, y, id):
        pygame.sprite.Sprite.__init__(self)
        self.original_pos = (x,y)
        self.reset()
        
    def update(self, player):
        temp = player.rect.copy()
        temp.height = player.rect.y
        temp.top = 0

        # pygame.draw.rect(screen, (255, 255, 255, 155), player.bounding_box)
        if pygame.Rect.colliderect(temp, self.rect):
            self.falling = True
        if self.falling:
            self.rect.y += 6
            self.bounding_box.y += 6

    def reset(self):
        img = pygame.image.load(os.path.join('assets', 'img', 'stalactite.png'))
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = self.original_pos[0]
        self.rect.y = self.original_pos[1]
        self.bounding_box = self.rect.copy()
        self.bounding_box.height -= 20
        self.bounding_box.y += 10
        self.bounding_box.width -= 10
        self.bounding_box.x += 10
        self.falling = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(os.path.join('assets', 'img', 'platform.png'))
        self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, id):
        pygame.sprite.Sprite.__init__(self)
        if id == 0:
            img = pygame.image.load(os.path.join('assets', 'img', 'ice_spike.png'))
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        if id == 1:
            img = pygame.image.load(os.path.join('assets', 'img', 'stalagmite.png'))
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        if id == 2:
            img = pygame.image.load(os.path.join('assets', 'img', 'stalactite.png'))
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        self.image = img
        self.rect = self.image.get_rect()
        center = self.rect.center
        self.rect.width -= 5
        self.rect.height -= 5
        self.rect.center = center
        self.rect.x = x
        self.rect.y = y
        self.bounding_box = self.rect.copy()
        self.bounding_box.height -= 20
        self.bounding_box.y += 10
        self.bounding_box.width -= 10
        self.bounding_box.x += 10


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []

        self.idle = True
        self.index = 0
        self.counter = 0
        self.map_button = UIElement(
            center_position=(0, 0),
            font_size=30,
            bg_rgb=(0, 0, 0),
            text_rgb=(0, 0, 125),
            text="",
            action=GameState.MAP
        )
        self.map_button.images[0] = map_img
        self.map_button.images[1] = map_img
        self.map_rect = map_img.get_rect()
        self.map_rect.center = (SCREEN_WIDTH-50, 50)
        self.map_button.rects[0] = self.map_rect
        self.map_button.rects[1] = self.map_rect

        for num in range(1, 5):
            img_right = pygame.image.load(os.path.join('assets','img', f'run{num}.png'))
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        img = pygame.image.load(os.path.join('assets', 'img', 'idle1.png'))
        img = pygame.transform.scale(img, (40, 80))
        img_left = pygame.transform.flip(img, True, False)
        self.idle_image_right = img
        self.idle_image_left = img_left

        self.walljump_img_left = pygame.image.load(os.path.join('assets', 'img', 'walljump.png'))
        self.walljump_img_left = pygame.transform.scale(self.walljump_img_left, (40, 80))
        self.walljump_img_right = pygame.transform.flip(self.walljump_img_left, True, False)

        self.image = self.idle_image_right
        self.rect = self.image.get_rect()
        self.rect.x = x + 5
        self.rect.y = y + 10
        self.width = self.image.get_width()
        self.height = self.image.get_height() 
        self.rect.height = self.height

        self.bounding_box = self.rect.copy()
        self.bounding_box.inflate_ip(-100.5, -100.5)

        self.vel_y = 0
        self.vel_x = 0
        self.jumped = False
        self.jumping = False
        self.direction = 0
        self.walljump_flag = -1  #  -1 = can walljump, -2 = touching wall, -3 = did walljump and cannot any more
        self.game_over = 0
        self.friction = 0
        self.in_air = False

    def update(self, world, camera, key, last_keys, map_img, mouse_button_up=False):
        dx = 0
        dy = 0
        col_thresh = 20

        walk_cooldown = 5
        self.idle = False
        #   Update player position
        if self.game_over == 0:
            grabbing_rope = False
            for rope in rope_group:
                if pygame.sprite.collide_rect(self, rope):
                    grabbing_rope = True
                    self.jumped = False

            if level > wind_trigger:
                dx += 3

            if key[pygame.K_LEFT]:
                self.vel_x -= 2
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                self.vel_x += 2
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.idle = True

            self.friction += 1
            if self.friction > 4:
                self.friction = 0
                if self.vel_x > 0:
                    self.vel_x -= self.vel_x // 2 + 1
                elif self.vel_x < 0:
                    self.vel_x -= self.vel_x // 2 - 1
                    if self.vel_x > 0:
                        self.vel_x = 0

            #  Cap speed
            if self.vel_x > 8:
                self.vel_x = 8
            if self.vel_x < -8:
                self.vel_x = -8
            dx += self.vel_x

            if key[pygame.K_SPACE]:
                if not self.jumped:
                    self.vel_y = -17
                    self.jumping = True
                    self.jumped = True

                if self.walljump_flag == -1 and last_keys is not None:
                    if not last_keys[pygame.K_SPACE] and not self.jumping:
                        self.walljump_flag = -2
                else:
                    time = clock.get_rawtime()
                    if self.walljump_flag > 0 and time - self.walljump_flag < 100:
                        # wall jump
                        self.vel_y = -17
                        self.walljump_flag = -3
                        self.jumping = True

                        if self.direction == 1:
                            self.vel_x = -20
                            self.direction = -1
                        elif self.direction == -1:
                            self.vel_x = 20
                            self.direction = 1
                        
            else:
                self.jumping = False

            #  Ropes
            if grabbing_rope:
                self.vel_x *= 0.5
                if key[pygame.K_SPACE]:
                    grabbing_rope = False
                    pass
                elif key[pygame.K_UP]:
                    self.vel_y = -20
                elif key[pygame.K_DOWN]:
                    self.vel_y = 17
                else:
                    self.vel_y = 0
                self.walljump_flag = -1

            #  Handle animations
            if self.idle:
                if self.direction == 1:
                    self.image = self.idle_image_right
                elif self.direction == -1:
                    self.image = self.idle_image_left

            else:
                if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_right):
                        self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index % 4]
                    if self.direction == -1:
                        self.image = self.images_left[self.index % 4]

            #  Add gravity
            self.vel_y += 1

            if self.vel_y == 0:  # Reached top of jump
                self.jumping = False

            if not self.jumping:
                self.vel_y += 1

            if self.vel_y > 10 and not grabbing_rope:
                self.vel_y = 10

            dy += self.vel_y

            #  Check for collision
            for tile in world.tile_list:
                #  Check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                    if self.walljump_flag == -2:
                        self.walljump_flag = clock.get_rawtime()
                    elif self.walljump_flag == -1:
                        dy -= 5 
                        if self.direction == 1:
                            self.image = self.walljump_img_right
                        elif self.direction == -1:
                            self.image = self.walljump_img_left

                #  Check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #  Check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #  Check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.jumped = False
                        self.walljump_flag = -1

            for person in person_group:
                if pygame.sprite.collide_rect(self, person):
                    draw_speech_bubble(
                        screen, person.text.strip(), person.rect, (0, 0, 0), camera)

            if pygame.sprite.spritecollide(self, trigger_group, False):
                if level+1 == cutscene_1[0] or level+1 == cutscene_2[0] or level == cutscene_3[0] or level == cutscene_4[0]:
                    return GameState.CUTSCENE
                return GameState.NEXT_LEVEL
                
            self.bounding_box = self.rect.copy()
            self.bounding_box.x += dx
            self.bounding_box.y += dy
            self.bounding_box = self.bounding_box.inflate(-10, -20)
            # pygame.draw.rect(screen, (0, 0, 255), self.rect, 2)

            for spike in spike_group:
                if pygame.Rect.colliderect(self.bounding_box, spike.bounding_box):
                    self.game_over = -1
            
            #  Check for collision with platforms
            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #  Check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    #  Check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.jumped = False
                        self.jumping = False
                        self.walljump_flag = -1
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            #  Update player coordinates
            self.rect.x += dx
            self.rect.y += dy
            self.bounding_box.x = self.rect.x
            self.bounding_box.y = self.rect.y

            if self.rect.y > SCREEN_HEIGHT:
                self.game_over = -1

            # draw_speech_bubble(screen, str(self.vel_y), self.rect, (0, 0, 0), camera)

        #  Draw player onto screen
        screen.blit(self.image, (self.rect.x + camera.pos.x,
                                 self.rect.y + camera.pos.y))

        #  Handle map
        screen.blit(map_img, self.map_rect)
        ui_action = self.map_button.update(
            pygame.mouse.get_pos(), mouse_button_up)
        if ui_action is GameState.MAP:
            map()

        return self.game_over


class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, body):
        pygame.sprite.Sprite.__init__(self)
        self.body = body
        if body:
            alpha = 128
            temp = pygame.image.load(os.path.join('assets', 'img', 'water_body.png'))
            img = pygame.transform.scale(temp, (TILE_SIZE, TILE_SIZE))
            img.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        else:
            self.images = []
            self.counter = 0
            alpha = 128

            temp = pygame.image.load(os.path.join('assets', 'img', 'water_1.png'))
            img = pygame.transform.scale(temp, (TILE_SIZE, TILE_SIZE))

            temp_2 = temp = pygame.image.load(
                os.path.join('assets', 'img', 'water_2.png'))
            img2 = pygame.transform.scale(temp_2, (TILE_SIZE, TILE_SIZE))

            img.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            img2.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

            self.images.append(img)
            self.images.append(img2)

        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.index = True

    def update(self):
        self.counter += 1
        if self.counter > 20:
            self.counter = 0
            if self.index:
                self.index = False
                self.image = self.images[1]

            else:
                self.index = True
                self.image = self.images[0]

#  Constant, does not change


class World():
    def __init__(self, data, level):
        self.tile_list = []
        self.width = 20
        self.height = 20

        #  Load images
        dirt_img = pygame.image.load(os.path.join('assets', 'img', 'dirt.png'))
        grass_img = pygame.image.load(os.path.join('assets', 'img', 'grass.png'))
        water_img = pygame.image.load(os.path.join('assets', 'img', 'water_body.png'))
        rock_img = pygame.image.load(os.path.join('assets', 'img', 'rock.jpeg'))
        stalactite_img = pygame.image.load(
            os.path.join('assets', 'img', 'stalactite.png'))
        stalagmite_img = pygame.image.load(
            os.path.join('assets', 'img', 'stalagmite.png'))
        ice_img = pygame.image.load(os.path.join('assets', 'img', 'ice.jpeg'))
        exit_img = pygame.image.load(os.path.join('assets', 'img', 'exit.png'))
        row_count = 0
        for row in data:
            col_count = 0

            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(
                        dirt_img, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(
                        grass_img, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    #  Water
                    water = Water(col_count * TILE_SIZE,
                                  row_count * TILE_SIZE, False)
                    water_group.add(water)
                if tile == 4:
                    #  Water
                    water = Water(col_count * TILE_SIZE,
                                  row_count * TILE_SIZE, True)
                    water_group.add(water)
                if tile == 5:
                    temp = ice_img.convert_alpha()
                    img = pygame.transform.scale(temp, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 6:
                    rope = Rope(col_count * TILE_SIZE, row_count*TILE_SIZE)
                    rope_group.add(rope)

                if tile == 7:
                    spike = Spike(col_count * TILE_SIZE, row_count*TILE_SIZE, 0)
                    spike_group.add(spike)

                if tile == 8:
                    exit = Trigger(col_count * TILE_SIZE, row_count * TILE_SIZE)
                    trigger_group.add(exit)

                if tile == 9:
                    text = get_line("dialogue.txt", level-1)
                    person = Person(col_count * TILE_SIZE,
                                    row_count * TILE_SIZE, text)
                    person_group.add(person)
                if tile == 10:
                    temp = rock_img.convert_alpha()
                    img = pygame.transform.scale(temp, (TILE_SIZE, TILE_SIZE))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * TILE_SIZE
                    img_rect.y = row_count * TILE_SIZE
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 11:
                    spike = Spike(col_count * TILE_SIZE,
                                  row_count*TILE_SIZE, 1)
                    spike_group.add(spike)
                if tile == 12:
                    spike = Spike(col_count * TILE_SIZE,
                                  row_count*TILE_SIZE, 2)
                    spike_group.add(spike)
                if tile == 13:
                    falling_spike = FallingSpike(
                        col_count * TILE_SIZE, row_count*TILE_SIZE, 2)
                    falling_spike_group.add(falling_spike)
                    spike_group.add(falling_spike)
                if tile == 14:
                    # Platform X
                    platform_x = Platform(
                        col_count * TILE_SIZE, row_count*TILE_SIZE, 1, 0)
                    platform_group.add(platform_x)
                if tile == 15:
                    # Platform Y
                    platform_x = Platform(
                        col_count * TILE_SIZE, row_count*TILE_SIZE, 0, 1)
                    platform_group.add(platform_x)
                col_count += 1
            row_count += 1

    def draw(self, camera):
        for tile in self.tile_list:
            screen.blit(tile[0], (tile[1].x + camera.pos.x,
                                  tile[1].y + camera.pos.y))

def clamp(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

def load_level(level):
    path = os.path.join('assets', 'levels', f'level{level}_data')
    if os.path.exists(path):
        pickle_in = open(path, 'rb')
        world_data = pickle.load(pickle_in)
    w = World(world_data, level)
    return w


def get_coord_from_point(position, width, height):
    x = int((position[0] / SCREEN_WIDTH) * width)
    y = int((position[1] / SCREEN_HEIGHT) * height)

    return (x, y)


def index_from_tuple(width, index):
    return index[1] * width + index


def create_surface_with_text(text, font_size, text_rgb, bg_rgb=None):
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


def reset_level(player, level):
    player.reset(50, SCREEN_HEIGHT-130)
    water_group.empty()
    trigger_group.empty()
    person_group.empty()
    rope_group.empty()
    spike_group.empty()
    falling_spike_group.empty()
    platform_group.empty()
    return load_level(level)


def draw_speech_bubble(screen, text, rect, color, camera):
    font = pygame.font.SysFont('Arial', 20, False)
    label = font.render(text, True, (255, 255, 255))
    containing_rect = pygame.Rect(rect.x - (label.get_width() + 20), rect.y - (
        label.get_height() + 20), label.get_width() + 10, label.get_height() + 20)
    containing_rect.centerx = rect.centerx + camera.pos.x
    containing_rect.top = rect.top - (label.get_height() + 20) + camera.pos.y
    pygame.draw.rect(screen, color, containing_rect)
    screen.blit(label, (containing_rect.x + 5, containing_rect.y + 10))


def get_line(file_name, c_line):
    file = open(os.path.join('assets', file_name), "r")
    for i, line in enumerate(file):
        if i == c_line:
            file.close()
            return line

def get_num_lines():
    file = open(os.path.join('assets', 'cutscenes.txt'), "r")
    return len(file.readlines())


def cutscene(c_line, textbox_img, cutscene_img, font):
    text_btn = UIElement(
        center_position=(0, 0),
        font_size=30,
        bg_rgb=(0, 0, 0),
        text_rgb=(0, 0, 125),
        text="",
        action=GameState.NEXT_LINE
    )

    quit_btn = UIElement(
        center_position=(SCREEN_WIDTH-40, 20),
        font_size=30,
        bg_rgb=(0, 0, 255),
        text_rgb=(255, 255, 255),
        text="Quit",
        action=GameState.QUIT
    )

    text_btn.images[0] = textbox_img
    text_btn.images[1] = textbox_img
    rect = textbox_img.get_rect()
    rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
    text_btn.rects[0] = rect
    text_btn.rects[1] = rect

    text_rect = rect.copy()
    text_rect.x += 50
    text_rect.y += 40
    text_rect.width -= 75
    text_rect.height -= 50

    buttons = RenderUpdates(text_btn, quit_btn)

    cur_line = get_line("cutscenes.txt", c_line).strip()

    cutscene_img = pygame.transform.scale(cutscene_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    return game_loop(buttons, cur_line, font, text_rect, cutscene_img)

def end():
    quit_btn = UIElement(
        center_position=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2),
        font_size=30,
        bg_rgb=(0, 0, 255),
        text_rgb=(255, 255, 255),
        text="THE END",
        action=GameState.QUIT
    )
    pygame.mixer.music.pause()
    end_fx = pygame.mixer.Sound(os.path.join('assets', 'img','end.mp3'))
    end_fx.set_volume(0.5)
    end_fx.play()
    buttons = RenderUpdates(quit_btn)
    end_img = pygame.image.load(os.path.join('assets', 'img','cutscene_3.png'))
    end_img = pygame.transform.scale(end_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    return game_loop(buttons, img=end_img)


def map():
    quit_btn = UIElement(
        center_position=(SCREEN_WIDTH - 50, 50),
        font_size=30,
        bg_rgb=(0, 0, 255),
        text_rgb=(255, 255, 255),
        text="Quit",
        action=GameState.RETURN
    )

    buttons = RenderUpdates(quit_btn)

    map_img = pygame.image.load(os.path.join('assets', 'img', 'map.png'))
    map_img = pygame.transform.scale(map_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    return game_loop(buttons, img=map_img)


def title_screen(title_screen_img):
    start_btn = UIElement(
        center_position=(500, 400),
        font_size=30,
        bg_rgb=(0, 0, 255, 255),
        text_rgb=(255, 255, 255),
        text="Start",
        action=GameState.NEWGAME
    )

    quit_btn = UIElement(
        center_position=(500, 500),
        font_size=30,
        bg_rgb=(0, 0, 255),
        text_rgb=(255, 255, 255),
        text="Quit",
        action=GameState.QUIT
    )

    title_text = UIElement(
        center_position=(500, 250),
        font_size=60,
        bg_rgb=(0, 0, 255),
        text_rgb=(255, 255, 255),
        text="Mt. Better-Than-Everest",
        action=None
    )

    buttons = RenderUpdates(start_btn, quit_btn, title_text)

    return game_loop(buttons, img=title_screen_img)


def game_loop(buttons, text=None, font=None, pos=None, img=None):
    # Handles game loop until an action is return by a button in the buttons sprite renderer.
    running = True
    while running:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameState.QUIT
                running = False

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True

        screen.fill((0, 0, 255))
        if img is not None:
            screen.blit(img, (0, 0))

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action

        buttons.draw(screen)

        if text is not None and pos is not None:
            drawText(screen, text, (0,0,255), pos, font, True)
    

        pygame.display.flip()


def play_level(player, world):
    game_over = 0
    keys_pressed = []
    last_keys = []
    running = True

    restart_button = Button(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 100, restart_img)

    wind_sfx = pygame.mixer.Sound(os.path.join('assets', 'img','wind.mp3'))
    wind_sfx.set_volume(0.2)
    global level

    while running:
        clock.tick(FPS)
        screen.blit(bg_img, (0, 0))
        mouse_button_up = False
        camera = Camera(0, 0)
        for event in pygame.event.get():
            if event == pygame.QUIT:
                running = False

                return GameState.QUIT
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                    return GameState.QUIT

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_button_up = True

        world.draw(camera)

        if keys_pressed is not None:
            last_keys = keys_pressed
        keys_pressed = pygame.key.get_pressed()

        for trigger in trigger_group:
            screen.blit(trigger.image, (trigger.rect.x +
                                        camera.pos.x, trigger.rect.y + camera.pos.y))

        for spike in spike_group:
            screen.blit(spike.image, (spike.rect.x + camera.pos.x, spike.rect.y + camera.pos.y))
            # pygame.draw.rect(screen, (255, 255, 255), spike.bounding_box)

        game_over = player.update(world, camera, keys_pressed, last_keys, map_img, mouse_button_up)

        if game_over == GameState.CUTSCENE:
            if level < max_levels:
                level += 1
                world_data = []
                world = reset_level(player, level)
                game_over = 0
            return GameState.CUTSCENE

        if game_over == 0:
            falling_spike_group.update(player)
            platform_group.update()

        for person in person_group:
            screen.blit(person.image, (person.rect.x + camera.pos.x, person.rect.y + camera.pos.y))

        for platform in platform_group:
            screen.blit(platform.image, (platform.rect.x + camera.pos.x, platform.rect.y + camera.pos.y))

        for water in water_group:
            img = water.image
            if not water.body:
                water.update()
            screen.blit(water.image, (water.rect.x + camera.pos.x, water.rect.y + camera.pos.y))

        for rope in rope_group:
            screen.blit(rope.image, (rope.rect.x + camera.pos.x, rope.rect.y + camera.pos.y))
        if game_over == -1:  # Died
            if restart_button.draw():
                game_over = 0
                player.reset(50, SCREEN_HEIGHT-130)
                for spike in falling_spike_group:
                    spike.reset()
        if game_over == GameState.NEXT_LEVEL:  # Beat the level
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(player, level)
                game_over = 0
                if level > wind_trigger:
                    wind_sfx.play(-1)
            else:
                level = 1
                world_data = []
                world = reset_level(player, level)
                game_over = 0

        pygame.display.flip()


def main():
    pygame.display.set_caption("Climbing Adventure")
    current_line = 0
    num_lines = get_num_lines()
    game_state = GameState.TITLE
    running = True
    title_screen_img = pygame.image.load(
        os.path.join('assets', 'img', 'title_screen.jpeg'))
    title_screen_img = pygame.transform.scale(
        title_screen_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # textbox_img = pygame.image.load(os.path.join('assets', 'img', 'textbox.png'))
    textbox_img = pygame.transform.scale(textbox_img, (600, 200))
    in_cutscene = False
    cutscene_font = pygame.font.SysFont('Courier', 25, False)

    while running:
        if game_state == GameState.TITLE:
            game_state = title_screen(title_screen_img)

        if game_state == GameState.NEWGAME:
            global musicplaying
            if not musicplaying:
                # pygame.mixer.music.load(os.path.join('assets', 'img', 'music.mp3'))
                # pygame.mixer.music.play(-1)
                # pygame.mixer.music.set_volume(0.5)
                musicplaying = True
            player = Player(50, SCREEN_HEIGHT-100)
            world = load_level(level)
            game_state = play_level(player, world)

        if game_state == GameState.CUTSCENE:
            if not in_cutscene:
                cutscene_img = title_screen_img
                end_line = 0
                if level == cutscene_1[0]:
                    cutscene_img = cutscene_1_img
                    current_line = cutscene_1[1] - 1
                    end_line = cutscene_1[2]
                elif level == cutscene_2[0]:
                    cutscene_img = cutscene_2_img
                    current_line = cutscene_2[1] - 1
                    end_line = cutscene_2[2]
                elif level-1 == cutscene_3[0]:
                    cutscene_img = cutscene_3_img
                    current_line = cutscene_3[1] - 1
                    end_line = cutscene_3[2]
                elif level == cutscene_4[0]:
                    cutscene_img = cutscene_4_img
                    current_line = cutscene_4[1] - 1
                    end_line = cutscene_4[2]

            in_cutscene = True

            state = cutscene(current_line, textbox_img, cutscene_img, cutscene_font)
            if state == GameState.NEXT_LINE:
                current_line += 1
                if current_line >= end_line:
                    in_cutscene = False
                    if level == cutscene_4[0]:
                        game_state = end()
                    else:
                        game_state = GameState.NEWGAME

            else:
                game_state = state
               
        if game_state == GameState.QUIT:
            running = False

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
main()
pygame.quit()
