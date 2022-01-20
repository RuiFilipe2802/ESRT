import socket
from _thread import *
import pickle
import time
import random
import math

# setup sockets
tcp_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_peer.connect(("127.0.0.1", 5009))
tcp_peer.send(str.encode("c"))
# Set constants
PORT = 5555

BALL_RADIUS = 5
START_RADIUS = 7

ROUND_TIME = 60 * 5

MASS_LOSS_TIME = 7

W, H = 1000, 500

HOST_NAME = socket.gethostname()
SERVER_IP = '127.0.0.1'

# try to ipect to server
'''try:
    S.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

S.listen()  # listen for ipections

print(f"[SERVER] Server Started with local ip {SERVER_IP}")'''

pacote_jogo = []

# dynamic variables
players = {}
balls = []
ipections = 0
_id = 0
colors = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]
start = False
stat_time = 0
game_time = "Starting Soon"
nxt = 1

def cria_pacote(ip,data):
    pacote = bytearray(0)
    array = ip.split(".")
    for a in range(len(array)):
        pacote.append(int(array[a]))
    ip = socket.inet_ntoa(pacote[0:4])
    print(ip)
    pacote[4:] = data
    return pacote
# FUNCTIONS

def release_mass(players):
	for player in players:
		p = players[player]
		if p["score"] > 8:
			p["score"] = math.floor(p["score"]*0.95)


def check_collision(players, balls):
	to_delete = []
	for player in players:
		p = players[player]
		x = p["x"]
		y = p["y"]
		for ball in balls:
			bx = ball[0]
			by = ball[1]

			dis = math.sqrt((x - bx)**2 + (y-by)**2)
			if dis <= START_RADIUS + p["score"]:
				p["score"] = p["score"] + 0.5
				balls.remove(ball)


def player_collision(players):
	sort_players = sorted(players, key=lambda x: players[x]["score"])
	for x, player1 in enumerate(sort_players):
		for player2 in sort_players[x+1:]:
			p1x = players[player1]["x"]
			p1y = players[player1]["y"]

			p2x = players[player2]["x"]
			p2y = players[player2]["y"]

			dis = math.sqrt((p1x - p2x)**2 + (p1y-p2y)**2)
			if dis < players[player2]["score"] - players[player1]["score"]*0.85:
				players[player2]["score"] = math.sqrt(players[player2]["score"]**2 + players[player1]["score"]**2) # adding areas instead of radii
				players[player1]["score"] = 0
				players[player1]["x"], players[player1]["y"] = get_start_location(players)
				print(f"[GAME] " + players[player2]["name"] + " ATE " + players[player1]["name"])


def create_balls(balls, n):
	for i in range(n):
		while True:
			stop = True
			x = random.randrange(0,W)
			y = random.randrange(0,H)
			for player in players:
				p = players[player]
				dis = math.sqrt((x - p["x"])**2 + (y-p["y"])**2)
				if dis <= START_RADIUS + p["score"]:
					stop = False
			if stop:
				break

		balls.append((x,y, random.choice(colors)))


def get_start_location(players):
	while True:
		stop = True
		x = random.randrange(0,W)
		y = random.randrange(0,H)
		for player in players:
			p = players[player]
			dis = math.sqrt((x - p["x"])**2 + (y-p["y"])**2)
			if dis <= START_RADIUS + p["score"]:
				stop = False
				break
		if stop:
			break
	return (x,y)
	

def threaded_client(ip, _id, name):
	global ipections, players, balls, game_time, nxt, start

	current_id = _id

	# recieve a name from the client
	data = name
	name = data.decode("utf-8")
	print("[LOG]", name, "connected to the server.")

	# Setup properties for each new player
	color = colors[current_id]
	x, y = get_start_location(players)
	players[current_id] = {"x":x, "y":y,"color":color,"score":0,"name":name}  # x, y color, score, name

	# pickle data and send initial info to clients
	pacote_enviar = cria_pacote(ip,str(current_id).encode("utf-8"))
	tcp_peer.send(pacote_enviar)
	#ip.send(str.encode(str(current_id)))

	# server will recieve basic commands from client
	# it will send back all of the other clients info

	while True:

		if start:
			game_time = round(time.time()-start_time)
			# if the game time passes the round time the game will stop
			if game_time >= ROUND_TIME:
				start = False
			else:
				if game_time // MASS_LOSS_TIME == nxt:
					nxt += 1
					release_mass(players)
					print(f"[GAME] {name}'s Mass depleting")
		try:
			# Recieve data from client
			data = tcp_peer.recv(32)

			if not data:
				break

			data = data.decode("utf-8")
			#print("[DATA] Recieved", data, "from client id:", current_id)

			# look for specific commands from recieved data
			if data.split(" ")[0] == "move":
				split_data = data.split(" ")
				x = int(split_data[1])
				y = int(split_data[2])
				players[current_id]["x"] = x
				players[current_id]["y"] = y

				# only check for collison if the game has started
				if start:
					check_collision(players, balls)
					player_collision(players)

				# if the amount of balls is less than 150 create more
				if len(balls) < 150:
					create_balls(balls, random.randrange(100,150))
					print("[GAME] Generating more orbs")

				send_data = pickle.dumps((balls,players, game_time))

			elif data.split(" ")[0] == "id":
				send_data = str.encode(str(current_id))  # if user requests id then send it

			elif data.split(" ")[0] == "jump":
				send_data = pickle.dumps((balls,players, game_time))
			else:
				# any other command just send back list of players
				send_data = pickle.dumps((balls,players, game_time))

			# send data back to clients
			pacote_envia =cria_pacote(ip,send_data)
			tcp_peer.send(pacote_envia)

		except Exception as e:
			print(e)
			break  # if an exception has been reached disipect client

		time.sleep(0.001)

	# When user disipects	
	print("[DISipECT] Name:", name, ", Client Id:", current_id, "disipected")

	ipections -= 1 
	del players[current_id]  # remove client information from players list
	#tcp.close()  # close ipection

# MAINLOOP

# setup level with balls
create_balls(balls, random.randrange(200,250))

print("[GAME] Setting up level")
print("[SERVER] Waiting for ipections")
# Keep looping to accept new ipections
while True:
	#host, addr = S.accept()
	#print("[ipECTION] ipected to:", addr)
	# start game when a client on the server computer ipects
	if ipections >= 1 and not(start):
		start = True
		start_time = time.time()
		print("[STARTED] Game Started")
	# increment ipections start new thread then increment ids
	ipections += 1
	print("esperar Nome")
	try:
		pacote_jogo_rec = tcp_peer.recv(4096)
	finally:
		print(pacote_jogo_rec)
		if(len(pacote_jogo_rec)>5):
			ip = socket.inet_ntoa(pacote_jogo_rec[0:4])
			print(ip)
			name = pacote_jogo_rec[4:]
			if(len(pacote_jogo_rec)<15):
				start_new_thread(threaded_client,(ip,_id,name))
				_id += 1

# when program ends
print("[SERVER] Server offline")
