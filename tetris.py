from st7920 import ST7920
from random import randint
from time import sleep
import curses
import copy

s = ST7920()
s.set_rotation(3)

textfont = s.fontsheet
blockfont = s.load_font_sheet("tetris.png", 4, 4)
smallfont = s.load_font_sheet("tim-4.png", 4, 5)

layoutbuf = None
score = 0
lines = 0
alive = True

redraw = True
redrawtiles = []

WIDTH = (s.width-2)/4
HEIGHT = (s.height-18)/4

ofx = (64 - (WIDTH*4))/2
ofy = (128 - (HEIGHT*4) - 18) / 2

board = [[0]*WIDTH for i in range(HEIGHT)]

blocks = [
	[[[1,6,8],[9,0,0]],[[7,2],[0,5],[0,9]],[[0,0,10],[7,6,4]],[[10,0],[5,0],[3,8]]], # L
	[[[7,6,2],[0,0,9]],[[0,10],[0,5],[7,4]],[[10,0,0],[3,6,8]],[[1,8],[5,0],[9,0]]], # R
	[[[15,16],[17,18]]], # O
	[[[7,2,0],[0,3,8]],[[0,10],[1,4],[9,0]]], # Z
	[[[0,1,8],[7,4,0]],[[10,0],[3,2],[0,9]]], # S
	[[[0,10,0],[7,11,8]],[[10,0],[13,8],[9,0]],[[7,12,8],[0,9,0]],[[0,10],[7,14],[0,9]]], # T
	[[[10],[5],[5],[9]],[[7,6,6,8]]] # I
	]

blocktype = randint(0, len(blocks)-1)
blockrot = 0
blockpos = [(WIDTH-len(blocks[blocktype][blockrot][0]))/2, -4]
blockstyle = randint(0, 2)

def update():
	if willfit(blockpos[0], blockpos[1] + 4, blockrot):
		blockpos[1] += 4
	else:
		next_piece()
	draw()

def fall_faster():
	for i in range(5):
		if willfit(blockpos[0], blockpos[1] + 1, blockrot):
			blockpos[1] += 1
		else:
			break

def move_left():
	if willfit(blockpos[0]-1, blockpos[1], blockrot):
		blockpos[0] -= 1

def move_right():
	if willfit(blockpos[0]+1, blockpos[1], blockrot):
		blockpos[0] += 1

def rotate():
	global blockrot
	r = (blockrot + 1) % len(blocks[blocktype])
	if willfit(blockpos[0], blockpos[1], r):
		blockrot = r

def willfit(x, y, rot):
	for dy in range(len(blocks[blocktype][rot])):
		row = blocks[blocktype][rot][dy]
		for dx in range(len(row)):
			cell = row[dx]
			if ((y/4)+dy)<0 or (x+dx)<0 or ((y/4)+dy)>=HEIGHT or (x+dx)>=WIDTH or (board[(y/4)+dy][x+dx]>0 and cell>0):
				return False
	return True

def next_piece():
	global blocktype, blockrot, blockpos, blockstyle, redrawtiles, redraw, lines, score
	for dy in range(len(blocks[blocktype][blockrot])):
		row = blocks[blocktype][blockrot][dy]
		for dx in range(len(row)):
			cell = row[dx]
			if cell>0:
				board[(blockpos[1]/4)+dy][blockpos[0]+dx] = cell + (blockstyle*24)
				redrawtiles.append((blockpos[0]+dx, (blockpos[1]/4)+dy))
				redraw = True
		flag = True
		removerows = []
		for dx in range(WIDTH):
			if board[(blockpos[1]/4)+dy][dx] == 0:
				flag = False
				break
		if flag:
			removerows.append((blockpos[1]/4)+dy)
	if len(removerows)>0:
		for row in removerows:
			for i in range(row, 1, -1):
				board[i] = copy.deepcopy(board[i-1])
				redrawtiles = []
		for i in range(len(removerows)):
			board[i] = [0]*WIDTH
		lines += len(removerows)
		if len(removerows)==1:
			score += 40
		elif len(removerows)==2:
			score += 100
		elif len(removerows)==3:
			score += 300
		elif len(removerows)==4:
			score += 1200
	blocktype = randint(0, len(blocks)-1)
	blockrot = 0
	blockstyle = randint(0, 2)
	blockpos = [(WIDTH-len(blocks[blocktype][blockrot][0]))/2, 0]
	if not willfit(blockpos[0], blockpos[1], blockrot):
		gameover()

def gameover():
	s.fontsheet = textfont
	s.put_text("Game", (64-24)/2, (128/2)-8)
	s.put_text("over!", (64-30)/2, (128/2))
	s.redraw()
	exit()

def drop():
	while willfit(blockpos[0], blockpos[1], blockrot):
		blockpos[1] += 1
	blockpos[1] -= 1
	next_piece()
	draw()

def drawtile(x,y):
	cell = board[y][x]
	if cell>0:
		s.put_text(chr(cell), ofx + (x*4), ofy + 16 + (y*4))

def draw():
	global redrawtiles, layoutbuf, redraw
	s.fontsheet = blockfont
	if redraw:
		redraw = False
		if len(redrawtiles)>0:
			s.fbuff = copy.deepcopy(layoutbuf)
			for tile in redrawtiles:
				drawtile(tile[0], tile[1])
		else:
			generatebuf()
			s.fontsheet = blockfont
			for x in range(WIDTH):
				for y in range(HEIGHT):
					drawtile(x,y)
		layoutbuf = copy.deepcopy(s.fbuff)
	else:
		s.fbuff = copy.deepcopy(layoutbuf)
	s.fontsheet = textfont
	if len(str(score))>4:
		s.fontsheet = smallfont
		s.put_text(str(score), 36, 2)
		s.fontsheet = textfont
	else:
		s.put_text(str(score), 36, 0)
	s.put_text(str(lines), 36, 8)
	dy = 0
	s.fontsheet = blockfont
	for row in blocks[blocktype][blockrot]:
		for x in range(len(row)):
			if row[x]!=0:
				s.put_text(chr(row[x] + (blockstyle*24)), ofx + (blockpos[0]+x)*4, ofy + 16 + blockpos[1]+(dy*4))
		dy += 1
	s.redraw()

def showsplash(screen):
	s.clear()
	s.fontsheet = textfont
	s.put_text("TETRIS", (64-36)/2, (128/2)-24)
	s.put_text("L/R: move", (64-54)/2, (128/2)-8)
	s.put_text("U: rotate", (64-54)/2, (128/2))
	s.put_text("D: drop", (64-42)/2, (128/2)+8)
	s.redraw()
	sleep(1)
	while screen.getch() != -1: # clear the input buffer
		pass

def generatebuf():
	global layoutbuf
	s.clear()
	s.rect(ofx,ofy + 16,ofx + WIDTH*4,ofy + (HEIGHT*4)+16)
	s.fontsheet = textfont
	s.put_text("Score ", 0, 0)
	s.put_text("Lines ", 0, 8)

def main(screen):
	screen.nodelay(1)
	
	showsplash(screen)
	
	generatebuf()
	
	while alive:
		char = screen.getch()
		while screen.getch()!=-1:
			pass
		if char==113: exit()
		elif char==32: fall_faster()
		elif char==curses.KEY_RIGHT: move_right()
		elif char==curses.KEY_DOWN: drop()
		elif char==curses.KEY_LEFT: move_left()
		elif char==curses.KEY_UP: rotate()
		update()
		sleep(0.05)
	s.clear()
	s.redraw()

curses.wrapper(main)