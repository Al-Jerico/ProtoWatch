# main.py -- put your code here!

from pyb import Pin, ADC, Timer
import time
import ssd1306
import machine
import random

led = pyb.LED(2)

i2c = machine.SoftI2C(scl=machine.Pin('A15'), sda=machine.Pin('C10'))

machine.Pin('C13', machine.Pin.OUT).low() #mettre courant entrant
machine.Pin('A8', machine.Pin.OUT).high() #mettre courant sortant

haut = machine.Pin('SW1', machine.Pin.IN, machine.Pin.PULL_UP)
bas = machine.Pin('SW2', machine.Pin.IN, machine.Pin.PULL_UP)
menu = machine.Pin('SW3', machine.Pin.IN, machine.Pin.PULL_UP)
init_jx = 50
init_jy = 30

display = ssd1306.SSD1306_I2C(128, 64, i2c)

MAX_HISTORY = 250
TOTAL_BEATS = 30

rtc = machine.RTC()
Pin(Pin.cpu.A0, mode=Pin.IN)

last_y = 40

def calculate_bpm(beats, minima, maxima, v):
	global last_y
	beats = beats[-TOTAL_BEATS:]
	beat_time = beats[-1] - beats[0]
	if beat_time:
		bpm = (len(beats) / (beat_time)) * 60
		display.fill_rect(0,0,128,16,0)
		display.text(" bpm:%d" % bpm, 55, 1, 1)
		ttim = rtc.datetime()
		ttim = str(ttim[4]) + ":" + str(ttim[5]) + ":" + str(ttim[6])
		display.text(ttim, 0, 1, 1)
		for i in range(4):
			slide_left(display)
		if maxima-minima > 0:
			y = 64 - int(16 * (v-minima) / (maxima-minima))
			display.line(121, last_y, 122, y, 1)
			last_y = y
		display.show()

		
def slide_left(display):
	width = display.width
	height = display.height
	for y in range(height):
		for x in range(width-1):
			color = display.pixel(x+1, y)
			display.pixel(x, y, color)
	for y in range(height):
		display.pixel(width-1, y, 0)
	display.show()
	
def moveUP(y):
	print("UP")
	display.pixel(init_jx, y, 0)
	y -= 2
	if(y < 0):
		y = 0
	display.pixel(init_jx, y, 1)
	return y
		
def moveDAWN(y):
	print("DOWN")
	display.pixel(init_jx, y, 0)
	y += 2
	if(y > display.height):
		y = display.height
	display.pixel(init_jx, y, 1)
	return y

def generateAst():
	ny = random.randint(2, display.height-1)
	print(ny)
	display.pixel(display.width-10, ny, 1)
	display.pixel(display.width-10, ny-1, 1)
	display.pixel(display.width-10, ny+1, 1)
	display.pixel(display.width-11, ny, 1)
	display.pixel(display.width-9, ny, 1)
	display.pixel(display.width-11, ny+1, 1)
	display.pixel(display.width-11, ny-1, 1)
	display.pixel(display.width-9, ny+1, 1)
	display.pixel(display.width-9, ny-1, 1)
	display.show()
	
def collide(jy):
	if(display.pixel(init_jx+1, jy) == 1):
		display.clear()
		print("gameover")

def lil_game():
	display.clear()
	display.pixel(init_jx, init_jy, 1)
	jy = init_jy
	while True:
		print("dans le jeux")
		display.pixel(init_jx, jy, 1)
		if random.randint(1, 10) == 5:
			generateAst()
		if haut.value() == 0:
			jy = moveUP(jy)
		if bas.value() == 0:
			jy = moveDAWN(jy)
		if menu.value() == 0 or collide(jy):
			break
		slide_left(display)
		display.show()
	display.clear()

	
def detect():
	histo_bpm = []
	beats = []
	beat = False
	bpm = None
	display.line(0, 40, 120, 40, 1)
	
	while True:
		v = ADC("A0").read()
		histo_bpm.append(v)
		histo_bpm = histo_bpm[-MAX_HISTORY:]
		
		mini, maxi = min(histo_bpm), max(histo_bpm)
		lim_on = (mini + maxi * 3) // 4
		lim_off = (mini + maxi) // 2
		
		if v > lim_on and beat == False:
			beat = True
			beats.append(time.time())
			
			beats = beats[-TOTAL_BEATS:]
			calculate_bpm(beats, mini, maxi, v)
		
		if v < lim_off and beat == True:
			beat = False
		
		if menu.value() == 0:
			lil_game()
		
detect()