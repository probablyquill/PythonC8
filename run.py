from chip8 import Chip8
#TODO Cut Numpy dependency.
import numpy as np
from pathlib import Path
import pygame
import time

"""

Memory Map:
0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
0x200-0xFFF - Program ROM and work RAM

"""

#Load rom
rom_path = Path("Brix [Andreas Gustafsson, 1990].ch8")
rom = ""

with open(rom_path, "rb") as f:
    rom = f.read()

chip8 = Chip8()

pygame.init()

SCREEN_HEIGHT = 256
SCREEN_WIDTH = 512

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
w = pygame.Surface([64, 32])

pygame.display.set_caption("PythonC8 - A Chip8 Emulator")

screen.fill(0)

white = (255, 255, 255)
black = (0,0,0)

def pygame_display(array):
    array = np.reshape(array, (32,64))
    pixel_array = pygame.PixelArray(w)
    color = white

    for y in range(32):
        for x in range(64):
            if (array[y][x] == 1):
                color = white
            else:
                color = black

            pixel_array[x][y] = color

    frame = pygame.transform.scale(w, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(frame, frame.get_rect())
    pixel_array.close()
    pygame.display.flip()

#Gameplay loop.
#Setup for io and whatever is used to output the graphics will need to go here.
chip8.initialize()
chip8.loadGame(rom)

# Keys:
# 1 2 3 4
# q w e r
# a s d f
# z x c v

then = time.time()

running = True
while running:
    #Check for key presses
    keys = pygame.key.get_pressed()
    
    keys_to_check = [
        pygame.K_x, 
        pygame.K_1, pygame.K_2, pygame.K_3, 
        pygame.K_q, pygame.K_w, pygame.K_e, 
        pygame.K_a, pygame.K_s, pygame.K_d, 
        pygame.K_z, pygame.K_c, pygame.K_4, 
        pygame.K_r, pygame.K_f, pygame.K_v
        ]

    for i in range(len(keys_to_check)):
        if keys[keys_to_check[i]]:
            chip8.key[i] = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = time.time()
    delta = (now - then) 

    if (delta > 0.0018):
        then = time.time()
        chip8.emulateCycle()

        for i in range(16):
            chip8.key[i] = 0

    if (chip8.drawFlag):
        pygame_display(chip8.gfx)
        chip8.drawFlag = False

pygame.quit()