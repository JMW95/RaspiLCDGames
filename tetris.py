import threading
import random
#from st7920 import ST7920
from random import randint
from time import sleep
import curses
#import numpy as np



import spidev
import png

class ST7920:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.cshigh = True # use inverted CS
        self.spi.max_speed_hz = 1800000 # set SPI clock to 1.8MHz, up from 125kHz
        
        self.send(0,0,0x30) # basic instruction set
        self.send(0,0,0x30) # repeated
        self.send(0,0,0x0C) # display on
        
        self.send(0,0,0x34) #enable RE mode
        self.send(0,0,0x34)
        self.send(0,0,0x36) #enable graphics display
        
        self.width = 128
        self.height = 64
        
        self.fbuff = [[0]*(self.width/8) for i in range(self.height)]
        
        self.fontsheet = self.loadfontsheet("fontsheet.png", 6, 8)
        
        self.clear()
        self.redraw()
    
    def loadfontsheet(self, filename, cw, ch):
        img = png.Reader(filename).read()
        rows = list(img[2])
        height = len(rows)
        width = len(rows[0])
        sheet = []
        for y in range(height/ch):
            for x in range(width/cw):
                char = []
                for sy in range(ch):
                    row = rows[(y*ch)+sy]
                    char.append(row[(x*cw):(x+1)*cw])
                sheet.append(char)
        return sheet
    
    def send(self, rs, rw, cmds):
        if type(cmds) is int: # if a single arg, convert to a list
            cmds = [cmds]
        b1 = 0b11111000 | ((rw&0x01)<<2) | ((rs&0x01)<<1)
        bytes = []
        for cmd in cmds:
            bytes.append(cmd & 0xF0)
            bytes.append((cmd & 0x0F)<<4)
        return self.spi.xfer2([b1] + bytes)
    
    def clear(self):
        self.fbuff = [[0]*(self.width/8) for i in range(self.height)]
    
    def line(self, x1, y1, x2, y2, set=True):
        diffX = abs(x2-x1)
        diffY = abs(y2-y1)
        shiftX = 1 if (x1 < x2) else -1
        shiftY = 1 if (y1 < y2) else -1
        err = diffX - diffY
        drawn = False
        while not drawn:
            self.plot(x1, y1, set)
            if x1 == x2 and y1 == y2:
                drawn = True
                continue
            err2 = 2 * err
            if err2 > -diffY:
                err -= diffY
                x1 += shiftX
            if err2 < diffX:
                err += diffX
                y1 += shiftY
    
    def fillrect(self, x1, y1, x2, y2, set=True):
        for y in range(y1,y2+1):
            self.line(x1,y,x2,y, set)
    
    def rect(self, x1, y1, x2, y2, set=True):
        self.line(x1,y1,x2,y1,set)
        self.line(x2,y1,x2,y2,set)
        self.line(x2,y2,x1,y2,set)
        self.line(x1,y2,x1,y1,set)
    
    def plot(self, x, y, set):
        if x<0 or x>=self.width or y<0 or y>=self.height:
            return
        if set:
            self.fbuff[y][x/8] |= 1 << (7-(x%8))
        else:
            self.fbuff[y][x/8] &= ~(1 << (7-(x%8)))
    
    def put_text(self, s, x, y):
        for c in s:
            try:
                char = self.fontsheet[ord(c)]
                sy = 0
                for row in char:
                    sx = 0
                    for px in row:
                        self.plot(x+sx, y+sy, px == 1)
                        sx += 1
                    sy += 1
            except KeyError:
                pass
            x += 6
    
    def redraw(self, dx1=0, dy1=0, dx2=127, dy2=63):
        for i in range(dy1, dy2+1):
            self.send(0,0,[0x80 + i%32, 0x80 + ((dx1/16) + (8 if i>=32 else 0))]) # set address
            self.send(1,0,self.fbuff[i][dx1/16:(dx2/8)+1])

class ST7920():
    def __init__(self):
        self.width = 128
        self.height = 64
        self.fbuff = [[0]*(self.width/8) for i in range(self.height)]
        #self.fbuff = np.array([[0]*self.width for i in range(self.height)])
        #self.fbuff = np.zeros((64, 16))
        self.lut = [(1<<(7-(x%8))) for x in range(128)]
    
    def plot(self, x, y, set):
        if x<0 or x>=self.width or y<0 or y>=self.height:
            return
        if set:
            #self.fbuff[y][x/8] |= 1 << (7-(x%8))
            #self.fbuff[y][x/8] |= 1 << (x%8)
            #self.fbuff[y][x] = 1
            self.fbuff[y][x/8] |= self.lut[x]
        #else:
            #self.fbuff[y][x/8] &= ~(1 << (7-(x%8)))

###############################################################################

class GridScreen(object):
    def __init__(self):
        self.symbols = {}
        self.shifted_symbols = {}
        self.buffer = numpy.zeros((64, 16), numpy.uint8)
        self.is_rotated = True

    def flush(self):
        buffer = self.buffer.copy()

    def add_symbols(self, symbols):
        self.symbols.update(symbols)
        def shift(symbol):
            return [row << 4 for row in symbol]
        self.shifted_symbols.update(dict(
            (name, shift(symbol)) for name, symbol in symbols
        ))

    def draw(self, x, y, name)
        assert x % 4 == 0
        if x % 8 == 0:
            shifted_symbol = self.shifted_symbols[name]
            for i in range(0, 4):
                byte = self.buffer[y + i]
                self.buffer[j] = (byte & 0x0f) | shifted_symbol[i]
        else:
            symbol = self.symbols[name]
            for i in range(0, 4):
                byte = self.buffer[y + i]
                self.buffer[j] = (byte & 0xf0) | symbol[i]

symbols = [
    'blank': [0b0000,
              0b0000,
              0b0000,
              0b0000],
    'box': [0b1111,
            0b1001,
            0b1001,
            0b1111],

    '0':   [0b0110,
            0b1001,
            0b1001,
            0b0110],
]

def main(screen):
    s = Screen()
    s.load_symbols(symbols)
    pass

