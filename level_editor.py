import pygame
import pickle
import os
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 40
cols = 20
margin = 100
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Level Editor')

#load images
sun_img = pygame.image.load('assets/img/sun.png')
sun_img = pygame.transform.scale(sun_img, (tile_size, tile_size))
bg_img = pygame.image.load('assets/img/sky.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
dirt_img = pygame.image.load('assets/img/dirt.png')
grass_img = pygame.image.load('assets/img/grass.png')
water_img = pygame.image.load('assets/img/water_1.png')
water_body_img = pygame.image.load('assets/img/water_body.png')
rock_img = pygame.image.load('assets/img/rock.jpeg')
stalactite_img = pygame.image.load('assets/img/stalactite.png')
stalagmite_img = pygame.image.load('assets/img/stalagmite.png')
ice_img = pygame.image.load('assets/img/ice.jpeg')
rope_img = pygame.image.load('assets/img/rope_2.png')
spike_img = pygame.image.load('assets/img/ice_spike.png')
exit_img = pygame.image.load('assets/img/exit.png')
kelsey_img = pygame.image.load('assets/img/kelsey.png')
platform_img = pygame.image.load('assets/img/platform.png')
save_img = pygame.image.load('assets/img/save_btn.png')
load_img = pygame.image.load('assets/img/load_btn.png')


#define game variables
clicked = False
level = 1
num_tiles = 15
cur_tile = 0
tiles = ["dirt", "grass", "water top", "water body", "ice",
	"rope", "spike", "exit", "person", "rock", "stalagmite", "stalactite", "falling spike", "platform x", 
	"platform_y"]
mode = True   #  True = mouse click to change, False = enter id, paintbrush mode

#define colours
white = (255, 255, 255)
green = (144, 201, 120)

font = pygame.font.SysFont('Futura', 24)

#create empty tile list
world_data = []
for row in range(20):
	r = [0] * 20
	world_data.append(r)

#create boundary
# for tile in range(0, 20):
# 	world_data[19][tile] = 2
# 	world_data[0][tile] = 1
# 	world_data[tile][0] = 1
# 	world_data[tile][19] = 1

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def swap():
	print("Which levels would you like to swap? ! to escape")
	inp = input("Level 1: ")
	if inp != "!":
		level1 = int(inp)
		level2 = int(input("Level 2: "))
		file1 = f"level{level1}_data"
		file2 = f"level{level2}_data"
		if path.exists(file1) and path.exists(file2):
			os.rename(file1, "temp")
			os.rename(file2, f"level{level1}_data")
			os.rename("temp", f"level{level2}_data")
			print("Renaming done")
		else:
			print("Files could not be found")
	else:
		print("Escaping")




def draw_grid():
	for c in range(21):
		#vertical lines
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		#horizontal lines
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


def draw_world():
	for row in range(20):
		for col in range(20):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					#dirt blocks
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					#grass blocks
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					#water top blocks
					img = pygame.transform.scale(water_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 4:
					#water body blocks
					img = pygame.transform.scale(water_body_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					#ice blocks
					img = pygame.transform.scale(ice_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 6:
					#ropes
					img = pygame.transform.scale(rope_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 7:
					#spikes
					img = pygame.transform.scale(spike_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 8:
					#exit
					img = pygame.transform.scale(exit_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))
				if world_data[row][col] == 9:
					#person 1
					img = pygame.transform.scale(kelsey_img, (tile_size, int(tile_size * 2)))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 10:
					#rock blocks
					img = pygame.transform.scale(rock_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 11:
					#stalagmite (up spikes)
					img = pygame.transform.scale(stalagmite_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 12:
					#stalactite (down spikes)
					img = pygame.transform.scale(stalactite_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 13:
					#falling spikes
					img = pygame.transform.scale(stalactite_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size-2, row * tile_size-2))
				if world_data[row][col] == 14:
					#platform_x
					img = pygame.transform.scale(platform_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 15:
					#platform_y
					img = pygame.transform.scale(platform_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#create load and save buttons
save_button = Button(screen_width // 2 - 150, screen_height - 80, save_img)
load_button = Button(screen_width // 2 + 50, screen_height - 80, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill(green)
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (tile_size * 2, tile_size * 2))

	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'assets/levels/level{level}_data'):
			pickle_in = open(f'assets/levels/level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	#show the grid and draw the level tiles
	draw_grid()
	draw_world()


	#text showing current level
	draw_text(f'Level: {level}', font, white, tile_size, screen_height - 60)
	draw_text('Press UP or DOWN to change level', font, white, tile_size, screen_height - 40)

	#event handler
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#mouseclicks to change tiles
		
		if event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			if mode:
				if clicked == False:
					clicked = True
					#check that the coordinates are within the tile area
					if x < 20 and y < 20:
						#update tile value
						if pygame.mouse.get_pressed()[0] == 1:
							world_data[y][x] += 1
							if world_data[y][x] > num_tiles:
								world_data[y][x] = 0
						elif pygame.mouse.get_pressed()[2] == 1:
							world_data[y][x] -= 1
							if world_data[y][x] < 0:
								world_data[y][x] = num_tiles
			else:
				if x < 20 and y < 20:
					if pygame.mouse.get_pressed()[0] == 1:
							world_data[y][x] = cur_tile
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#up and down key presses to change level number
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1
			if event.key == pygame.K_SPACE:
				cur_tile = int(input("Enter Tile ID: "))
				print("You have selected a: " + tiles[cur_tile-1])
			if event.key == pygame.K_LALT:
				mode = not mode
				print("Mode switching to: " + str(mode))
			if event.key == pygame.K_RALT:
				swap()
			if event.key == pygame.K_LCTRL:
				level = int(input("Enter the level you would like to go to: "))

	#update game display window
	pygame.display.update()

pygame.quit()