from tkinter import *
from random import randint
from PIL import Image, ImageTk
import time

DEFAULT_SIZE = 25 # in pixels
C_WIDTH = 1280
C_HEIGHT = 720
EYE_WIDTH = DEFAULT_SIZE/9

def moveUp(event):
	global lastv, vx, vy, pause

	if lastv[1] != DEFAULT_SIZE and not pause:
		vy = - DEFAULT_SIZE
		vx = 0

def moveDown(event):
	global lastv, vx, vy, pause

	if lastv[1] != -DEFAULT_SIZE and not pause:
		vy = DEFAULT_SIZE
		vx = 0

def moveRight(event):
	global lastv, vx, vy, pause

	if lastv[0] != -DEFAULT_SIZE and not pause:
		vx = DEFAULT_SIZE
		vy = 0

def moveLeft(event):
	global lastv, vx, vy, pause

	if lastv[0] != DEFAULT_SIZE and not pause:
		vx = -DEFAULT_SIZE
		vy = 0

def quitSnek(event):
	global quit
	quit = True

def generateSnack(canvas):
	global C_HEIGHT, C_WIDTH, DEFAULT_SIZE
	snacky = randint(1, (C_HEIGHT - DEFAULT_SIZE)//DEFAULT_SIZE)
	snackx = randint(1, (C_WIDTH - DEFAULT_SIZE)//DEFAULT_SIZE)
	#print("Snack's x: %d and y: %d", snackx, snacky)

	return canvas.create_rectangle(snackx*DEFAULT_SIZE, snacky*DEFAULT_SIZE, (snackx*DEFAULT_SIZE)+DEFAULT_SIZE, (snacky*DEFAULT_SIZE)+DEFAULT_SIZE, fill='blue')

def playAgain(event):
	global cont
	cont = True

C_HEIGHT -= (C_HEIGHT % DEFAULT_SIZE)
if C_HEIGHT % (2 * DEFAULT_SIZE) != 0:
	C_HEIGHT -= DEFAULT_SIZE		

C_WIDTH -= (C_WIDTH % DEFAULT_SIZE)
if C_WIDTH % (2 * DEFAULT_SIZE) != 0:
	C_WIDTH -= DEFAULT_SIZE		

def pauseGem(event):
	global pause

	if pause:
		pause = False
		print('Un-Paused')
	else:
		pause = True
		print('Paused')


app = Tk()

quit =  False
cont = True
pause = False

app.title('Snek V. 1A')
app.resizable(0, 0)

title_screen = Image.open("snek_title.jpg")
title_screen = title_screen.resize([C_WIDTH, C_HEIGHT])
title_screen = ImageTk.PhotoImage(title_screen)

can = Canvas(app, width=C_WIDTH, height=C_HEIGHT)

app.bind('w', moveUp)
app.bind('<Up>', moveUp)
app.bind('s', moveDown)
app.bind('<Down>', moveDown)
app.bind('d', moveRight)
app.bind('<Right>', moveRight)
app.bind('a', moveLeft)
app.bind('<Left>', moveLeft)
app.bind('q', quitSnek)
app.bind('y', playAgain)
app.bind('p', pauseGem)
can.pack()

while cont and not quit: # ----------------------------- outer loop

	lastv = [0, 0]
	cont = False
	x = C_WIDTH/2
	y = C_HEIGHT/2

	snek_size = 0
	vx = 0
	vy = 0

	hiscore = open('hi_score.txt', 'r')
	previous = hiscore.read()
	hiscore.close()

	can.create_image(C_WIDTH/2, C_HEIGHT/2, image=title_screen)
	can.create_text(C_WIDTH/2, C_HEIGHT/10, text="SNEK", font=("Comic Sans MS", 60, "bold"))
	can.create_text(C_WIDTH/2, C_HEIGHT/5, text="the gem", font=("Comic Sans MS", 30, "italic"))
	hi_skor = can.create_text(C_WIDTH/1.2, C_HEIGHT/8, text="hi-skor: " + str(previous), font=("Comic Sans MS", 45, "bold italic"))
	press = can.create_text(C_WIDTH/2, C_HEIGHT/3.8, text="pressss key 2 ply", font=("Comic Sans MS", 20, "italic"))

	flash = False
	while vx == 0 and vy == 0 and quit == False:
		if flash:
			can.itemconfigure(press, fill="white")
			flash = False
		else:
			can.itemconfigure(press, fill="black")
			flash = True

		time.sleep(0.3)
		app.update_idletasks()
		app.update()

	can.delete(ALL)

	sneks = [can.create_rectangle(300, 100, 350, 150, fill="LightGreen")]
	snekeyes = [can.create_oval(x + EYE_WIDTH * 2, y + EYE_WIDTH, x + EYE_WIDTH*3, y + EYE_WIDTH*2, fill="black"),
					can.create_oval(x + EYE_WIDTH * 4, y + EYE_WIDTH, x + EYE_WIDTH*5, y + EYE_WIDTH*2, fill="black")]
	tx = x + DEFAULT_SIZE ** ((1 + vx)//2)
	ty = y + DEFAULT_SIZE ** ((1 + vy)//2)
	snektongue = [can.create_line(tx, ty, tx + vx/2 + vy/5, ty + vy/2 + vx/5),
				can.create_line(tx + vx/2 + vy/5, ty + vy/2 + vx/5, tx - vx/2 - vy/5, ty - vy/2 - vx/5)]
	tongue_smack = 1

	sneck = generateSnack(can)
	score = can.create_text(C_WIDTH - 50, 30, text="u suck", font=("Comic Sans MS", 20, "bold"))

	pauseText = can.create_line(1, 1, 1, 1)
	# --------------------------------- start of gem ----------------------------------------------------
	while True:
		lastv = [vx, vy]

		can.delete(pauseText)

		if not pause:
			x = (x + vx) % C_WIDTH
			y = (y + vy) % C_HEIGHT

			#print(x, ":", y)

			can.delete(sneks.pop(0))
			can.delete(snekeyes[0])
			can.delete(snekeyes[1])

			sneks.append(can.create_rectangle(x, y, x + DEFAULT_SIZE, y + DEFAULT_SIZE, fill="LightGreen"))
			snekeyes = [can.create_oval(x + EYE_WIDTH * 2, y + EYE_WIDTH*2, x + EYE_WIDTH*3, y + EYE_WIDTH*3, fill="black"),
						can.create_oval(x + EYE_WIDTH * 6, y + EYE_WIDTH*3, x + EYE_WIDTH*7, y + EYE_WIDTH*4, fill="black")]

		else:
			pauseText = can.create_text(C_WIDTH/2, C_HEIGHT/10, text="pause", font=("Comic Sans MS", 50, "bold"))

		can.delete(snektongue[0])
		can.delete(snektongue[1])

		tx = x + DEFAULT_SIZE ** ((DEFAULT_SIZE + vx)//(2*DEFAULT_SIZE)) + (DEFAULT_SIZE/2)* abs(vy)/DEFAULT_SIZE
		ty = y + DEFAULT_SIZE ** ((DEFAULT_SIZE + vy)//(2*DEFAULT_SIZE)) + (DEFAULT_SIZE/2)* abs(vx)/DEFAULT_SIZE
		
		if tongue_smack > 0:
			snektongue = [can.create_line(tx, ty, tx + vx/1.5 - vy/10, ty + vy/1.5 - vx/10),
						can.create_line(tx + vx/4 - vy/18, ty + vy/4 - vx/18, tx + vx/2.5 + vy/4, ty + vy/2.5 + vx/4)]
			tongue_smack += 1
		elif tongue_smack < 0:
			snektongue = [can.create_line(tx, ty, tx + vx/4 + vy/6, ty + vy/4 + vx/6),
						can.create_line(tx + vx/4 + vy/6, ty + vy/4 + vx/6, tx + vx/2 - vy/4, ty + vy/2 - vx/4)]
			tongue_smack -= 1
		
		if tongue_smack > 3*(1.02**snek_size) or tongue_smack < -3*(1.02**snek_size):
			tongue_smack = tongue_smack - tongue_smack - tongue_smack/abs(tongue_smack)

		for i in range (0, len(sneks) - 1):
			if can.coords(sneks[i]) == can.coords(sneks[-1]):
				quit = True
				break

		app.update_idletasks()
		app.update()
		time.sleep(0.10*(0.97**snek_size))

		if can.coords(sneks[-1]) == can.coords(sneck):
			can.delete(sneck)
			snek_size += 1
			sneks.append(can.create_rectangle(x, y, x + DEFAULT_SIZE, y + DEFAULT_SIZE, fill="LightGreen"))
			sneck = generateSnack(can)
			can.delete(score)
			score = can.create_text(C_WIDTH - 50, 30, text=snek_size, font=("Comic Sans MS", 20, "bold"))

		
		if quit == True:
			print("snek has run away successfully")
			break

	hiscore = open('hi_score.txt', 'r')
	previous = hiscore.read()
	hiscore.close()

	if int(previous) < snek_size:
		hiscore = open('hi_score.txt', 'w')
		hiscore.write(str(snek_size))
		hiscore.close()
		can.delete(ALL)
		long_boi = Image.open("long_snek.jpg")
		long_boi = long_boi.resize([C_WIDTH, C_HEIGHT])
		long_boi = ImageTk.PhotoImage(long_boi)
		flash = True
		can.create_image(C_WIDTH/2, C_HEIGHT/2, image=long_boi)
		hi_skor = can.create_text(C_WIDTH/1.2, C_HEIGHT/8, text="hi-skor! " + str(snek_size), font=("Comic Sans MS", 45, "bold italic"))
	else:
		can.delete(ALL)
		ded_boi = Image.open("ded_snek.jpg")
		ded_boi = ded_boi.resize([C_WIDTH, C_HEIGHT])
		ded_boi = ImageTk.PhotoImage(ded_boi)
		can.create_image(C_WIDTH/2, C_HEIGHT/2, image=ded_boi)
		can.create_text(C_WIDTH/1.2, C_HEIGHT/8, text="skor " + str(snek_size), font=("Comic Sans MS", 45, "bold italic"))

	can.create_text(C_WIDTH/2, C_HEIGHT/5, text="agen?", font=("Comic Sans MS", 30, "italic"))
	can.create_text(C_WIDTH/2, C_HEIGHT/4, text="y or q", font=("Comic Sans MS", 10, "italic"))
	quit = False

	while not cont and not quit:
		if flash:
			can.itemconfigure(hi_skor, fill="white")
			flash = False
		else:
			can.itemconfigure(hi_skor, fill="black")
			flash = True
		time.sleep(0.2)
		app.update_idletasks()
		app.update()

	can.delete(ALL)