import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from client import Network
import random
import os
import time
pygame.font.init()
import sys

# Constants
PLAYER_RADIUS = 10
START_VEL = 9
BALL_RADIUS = 5

decision = int(sys.argv[1])

W, H = 1000, 500

NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

COLORS = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255),
          (0, 128, 255), (0, 0, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128), (128, 128, 128), (0, 0, 0)]

# Dynamic Variables
players = {}
balls = []
game_time = 0
data1 = ""

# FUNCTIONS


def convert_time(t):
    if type(t) == str:
        return t

    if int(t) < 60:
        return str(t) + "s"
    else:
        minutes = str(t // 60)
        seconds = str(t % 60)

        if int(seconds) < 10:
            seconds = "0" + seconds

        return minutes + ":" + seconds


def redraw_window(players, balls, game_time, score):
    WIN.fill((255, 255, 255))  # fill screen white, to clear old frames

    # draw all the orbs/balls
    for ball in balls:
        pygame.draw.circle(WIN, ball[2], (ball[0], ball[1]), BALL_RADIUS)

    # draw each player in the list
    for player in sorted(players, key=lambda x: players[x]["score"]):
        p = players[player]
        pygame.draw.circle(WIN, p["color"], (p["x"], p["y"]),
                           PLAYER_RADIUS + round(p["score"]))
        # render and draw name for each player
        text = NAME_FONT.render(p["name"], 1, (0, 0, 0))
        WIN.blit(text, (p["x"] - text.get_width() /
                 2, p["y"] - text.get_height()/2))

    # draw scoreboard
    sort_players = list(
        reversed(sorted(players, key=lambda x: players[x]["score"])))
    title = TIME_FONT.render("Scoreboard", 1, (0, 0, 0))
    start_y = 25
    x = W - title.get_width() - 10
    WIN.blit(title, (x, 5))

    ran = min(len(players), 3)
    for count, i in enumerate(sort_players[:ran]):
        text = SCORE_FONT.render(
            str(count+1) + ". " + str(players[i]["name"]), 1, (0, 0, 0))
        WIN.blit(text, (x, start_y + count * 20))

    # draw time
    text = TIME_FONT.render("Time: " + convert_time(game_time), 1, (0, 0, 0))
    WIN.blit(text, (10, 10))
    # draw score
    text = TIME_FONT.render("Score: " + str(round(score)), 1, (0, 0, 0))
    WIN.blit(text, (10, 15 + text.get_height()))

#troca de dados com server 
def set_p_b_gt(r_data):
    global players, game_time, balls
    balls, players, game_time = r_data

def set_data():
    return data1

def set_start(st):
    global start
    start = 1

def get_start():
    global start
    return start

def get_enviar():
    global enviar_game
    return enviar_game

def set_recebida(r):
    global recebida 
    recebida = r

recebida = 0
enviar_game = 0



    

def main(name):
    global players,decision, data1, start, enviar_game, recebida
    #so para testes vou definir aqui
    decision = 1
    # start by connecting to the network
    if decision == 0:
        server = Network()
        current_id = server.connect(name)
        balls, players, game_time = server.send("get")
        start = 1


    # setup the clock, limit to 30fps
    clock = pygame.time.Clock()

    run = True
    if start == 1:
        while run:
            clock.tick(30)  # 30 fps max
            player = players[current_id]
            vel = START_VEL - round(player["score"]/14)
            if vel <= 1:
                vel = 1

            # get key presses
            keys = pygame.key.get_pressed()

            data1 = ""
            # movement based on key presses
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if player["x"] - vel - PLAYER_RADIUS - player["score"] >= 0:
                    player["x"] = player["x"] - vel

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if player["x"] + vel + PLAYER_RADIUS + player["score"] <= W:
                    player["x"] = player["x"] + vel

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                if player["y"] - vel - PLAYER_RADIUS - player["score"] >= 0:
                    player["y"] = player["y"] - vel

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if player["y"] + vel + PLAYER_RADIUS + player["score"] <= H:
                    player["y"] = player["y"] + vel

            data1 = "move " + str(player["x"]) + " " + str(player["y"])
            #print('--------------------')
            #print(data)
            # send data to server and recieve back all players information
            if decision == 0:
                balls, players, game_time = server.send(data1)
            else:
                enviar_game = 1 
                loop = 0
                while  loop == 0:
                    if recebida == 1:
                        enviar_game = 0
                        recebida = 0
                        loop = 1

            #time.sleep(1)
            #print(balls)
            #print(players)
            #print(game_time)

            for event in pygame.event.get():
                # if user hits red x button close window
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    # if user hits a escape key close program
                    if event.key == pygame.K_ESCAPE:
                        run = False

            # redraw window then update the frame
            redraw_window(players, balls, game_time, player["score"])
            pygame.display.update()
    if decision == 0:
        server.disconnect()
    else: 
        start = 0
    pygame.quit()
    quit()


# get users name

WIN = None

def start_gaming(name):# make window start in top left hand corner
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)

    # setup pygame window
    WIN = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Game")

    # start game
    main(name)