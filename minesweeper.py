from st7920 import ST7920
from random import randint
from time import sleep
import curses

WIDTH = 21
HEIGHT = 10

alive = True
selected = [0,0]
blink = 0

s = ST7920()
redraw = True
redrawtiles = []
toreveal = 0

mines = [[0] * WIDTH for i in range(HEIGHT)] #0:empty, 255:mine, 1-8:mine adjacent
flags = [[0] * WIDTH for i in range(HEIGHT)] #0:no flag, 1:flag, 2:revealed

textfont = s.fontsheet
minefont = s.load_font_sheet("mines.png",5,5)

def generate(nummines):
	global mines, toreveal
	toreveal = (WIDTH * HEIGHT) - nummines
	for i in range(nummines):
		if i > WIDTH * HEIGHT: break
		while True:
			mx = randint(0,WIDTH-1)
			my = randint(0,HEIGHT-1)
			if mines[my][mx] != 255: # if there isnt a mine already there
				mines[my][mx] = 255
				for x in range(-1,2):
					for y in range(-1,2):
						if x==0 and y==0: continue
						if (my+y)<0 or (my+y)>=HEIGHT or (mx+x)<0 or (mx+x)>=WIDTH: continue
						if mines[my+y][mx+x] != 255:
							mines[my+y][mx+x] += 1
				break

def drawtile(x,y):
	global alive
	cell = mines[y][x]
	flag = flags[y][x]
	if alive:
		if flag==2: # if tile is revealed
			if cell>0:
				s.put_text(chr(cell), (x*6)+1, (y*6)+1)
			else:
				s.put_text(chr(13), (x*6)+1, (y*6)+1)
		elif flag==1:
			s.put_text(chr(10), (x*6)+1, (y*6)+1)
		else:
			s.put_text(chr(0), (x*6)+1, (y*6)+1)
	else:
		if flag==2: # if tile is revealed
			if cell>0:
				s.put_text(chr(cell), (x*6)+1, (y*6)+1)
			else:
				s.put_text(chr(13), (x*6)+1, (y*6)+1)
		elif flag==1:
			if cell==255:
				s.put_text(chr(10), (x*6)+1, (y*6)+1)
			else:
				s.put_text(chr(11), (x*6)+1, (y*6)+1)
		else:
			if cell==255:
				s.put_text(chr(9), (x*6)+1, (y*6)+1)
			else:
				s.put_text(chr(0), (x*6)+1, (y*6)+1)
			

def draw():
	global blink, redrawtiles
	if len(redrawtiles)>0:
		for tile in redrawtiles:
			drawtile(tile[0],tile[1])
	else:
		s.clear()
		for x in range(0, WIDTH + 1):
			s.line(x*6,0,x*6,HEIGHT*6)
		for y in range(0, HEIGHT + 1):
			s.line(0,y*6,WIDTH*6,y*6)
		for y in range(HEIGHT):
			for x in range(WIDTH):
				drawtile(x,y)
	if blink>=8 or not alive:
		s.put_text(chr(12), (selected[0]*6)+1, (selected[1]*6)+1)
	s.redraw()
	redrawtiles = []

def showsplash(screen):
	s.clear()
	s.put_text("MINESWEEPER!", (128-72)/2, (64/2)-16)
	s.put_text("Arrows to select", (128-96)/2, (64/2))
	s.put_text("F to flag", (128-54)/2, (64/2)+8)
	s.put_text("Space to clear", (128-84)/2, (64/2)+16)
	s.redraw()
	sleep(3)
	while screen.getch() != -1: # clear the input buffer
		pass

def moveselected(dx, dy):
	global selected, blink, redraw, redrawtiles
	blink = 8
	sx = selected[0]
	sy = selected[1]
	if sx+dx < 0 or sx+dx>=WIDTH or sy+dy<0 or sy+dy>=HEIGHT:
		return
	selected = [sx + dx, sy + dy]
	redrawtiles += [[sx,sy], selected]
	redraw = True

def countflags(x, y):
	numflags = 0
	for dx in range(x-1,x+2):
		for dy in range(y-1,y+2):
			if dx<0 or dx>=WIDTH or dy<0 or dy>=HEIGHT:
				continue
			if flags[dy][dx]==1:
				numflags += 1
	return numflags

def tryreveal(x, y, recursive=False):
	global selected, alive, toreveal, redraw, redrawtiles
	if x<0 or x>=WIDTH or y<0 or y>=HEIGHT: return
	if recursive and flags[y][x] != 0: return
	if flags[y][x] == 1: return
	if flags[y][x] == 2:
		if countflags(x,y) == mines[y][x]: # autoreveal
			for dx in range(-1,2):
				for dy in range(-1,2):
					tryreveal(x+dx, y+dy, True)
	else:
		cell = mines[y][x]
		if cell == 255: #hit a mine
			alive = False
		else:
			flags[y][x] = 2
			toreveal -= 1
			redraw = True
			redrawtiles += [[x,y]]
			if cell == 0: # empty, so reveal recursively
				for dx in range(-1,2):
					for dy in range(-1,2):
						tryreveal(x+dx, y+dy, True)

def flag():
	global selected
	if flags[selected[1]][selected[0]] == 1:
		flags[selected[1]][selected[0]] = 0
	elif flags[selected[1]][selected[0]] == 0:
		flags[selected[1]][selected[0]] = 1

def win():
	s.fillrect( (128-48)/2 - 1, (64/2)-4 - 1, (128+48)/2 + 1, (64/2)+4 + 1, False )
	s.fontsheet = textfont
	s.put_text("You win!", (128-48)/2, (64/2)-4)
	s.redraw()
	exit()

def dead():
	draw()

def main(screen):
	global redraw, redrawtiles, blink, minefont
	screen.nodelay(1)
	
	showsplash(screen)
	s.fontsheet = minefont
	
	generate(43)
	draw()
	
	while alive:
		char = screen.getch()
		if char==113: exit()
		elif char==curses.KEY_RIGHT: moveselected(1,0)
		elif char==curses.KEY_DOWN: moveselected(0,1)
		elif char==curses.KEY_LEFT: moveselected(-1,0)
		elif char==curses.KEY_UP: moveselected(0,-1)
		elif char==32: tryreveal(selected[0], selected[1])
		elif char==102: flag()
		if (blink%8)==0:
			redraw = True
			redrawtiles += [ selected ]
		blink = (blink+1)%16
		if redraw:
			draw()
			redraw = False
		if toreveal==0: # win!
			win()
	dead()

curses.wrapper(main)