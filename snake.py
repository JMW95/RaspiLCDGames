from st7920 import ST7920
from random import randint
from time import sleep
import curses
import collections

SCALE = 4
WIDTH = 128/SCALE
HEIGHT = 64/SCALE

score = 0
alive = True

s = ST7920()

def newfoodpos():
	return [randint(0,WIDTH-1), randint(0,HEIGHT-1)]

def update():
	global headpos, foodpos, score
	if headdir == 0:
		newpos = [headpos[0]+1, headpos[1]]
	elif headdir == 1:
		newpos = [headpos[0], headpos[1]+1]
	elif headdir == 2:
		newpos = [headpos[0]-1, headpos[1]]
	else:
		newpos = [headpos[0], headpos[1]-1]
	if newpos[0]<0: newpos[0] += WIDTH
	if newpos[0]>=WIDTH: newpos[0] = 0
	if newpos[1]<0: newpos[1] += HEIGHT
	if newpos[1]>=HEIGHT: newpos[1] = 0
	if (newpos in snakebits):
		dead()
	if newpos[0]==foodpos[0] and newpos[1]==foodpos[1]:
		foodpos = newfoodpos() # don't remove if we hit the food
		score += 1
	else:
		snakebits.popleft() #remove the last tail bit
	snakebits.append(newpos)
	headpos = newpos
	draw()
	s.redraw()

def dead():
	global alive
	alive = False
	s.clear()
	s.put_text("You died!", ((WIDTH*SCALE)-54)/2, ((HEIGHT*SCALE)/2)-8)
	msg = "Score: " + str(score)
	s.put_text(msg, ((WIDTH*SCALE)-(6*len(msg)))/2, ((HEIGHT*SCALE)/2))
	s.redraw()
	exit()

def draw():
	s.clear()
	s.rect(foodpos[0]*SCALE, foodpos[1]*SCALE, ((foodpos[0]+1)*SCALE)-1, ((foodpos[1]+1)*SCALE)-1)
	for bit in snakebits:
		s.fill_rect(bit[0]*SCALE, bit[1]*SCALE, ((bit[0]+1)*SCALE)-1, ((bit[1]+1)*SCALE)-1)

def showsplash(screen):
	s.clear()
	s.put_text("SNAKE!", ((WIDTH*SCALE)-36)/2, ((HEIGHT*SCALE)/2)-16)
	s.put_text("Arrow keys", ((WIDTH*SCALE)-60)/2, ((HEIGHT*SCALE)/2))
	s.put_text("to control!", ((WIDTH*SCALE)-66)/2, ((HEIGHT*SCALE)/2)+8)
	s.redraw()
	sleep(3)
	while screen.getch() != -1: # clear the input buffer
		pass

def main(screen):
	global headdir
	screen.nodelay(1)
	
	showsplash(screen)
	
	while alive:
		char = screen.getch()
		if char==113: exit()
		elif char==curses.KEY_RIGHT and headdir!=2 : headdir = 0
		elif char==curses.KEY_DOWN and headdir!=3: headdir = 1
		elif char==curses.KEY_LEFT and headdir!=0: headdir = 2
		elif char==curses.KEY_UP and headdir!=1: headdir = 3
		update()
		sleep(0.05)
	s.clear()
	s.redraw()

foodpos = newfoodpos()
snakebits = collections.deque()
headpos = [5,5]
snakebits.append([2,5])
snakebits.append([3,5])
snakebits.append([4,5])
snakebits.append(headpos)
headdir = 0 #0:east, 1:south, 2:west, 3:north

curses.wrapper(main)
