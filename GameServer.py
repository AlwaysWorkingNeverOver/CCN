import threading
import pygame
import socket
import sys
import random
import time

name = "test"
posx = 300
posy = 200
speed = 1
gameOver = False
numBalls = 1
score = 0
cupSpeed = 40
goal = 5
minOffset = 0
maxOffset = 0

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400 
FPS = 60

BACKGROUND = (204, 230, 255)
SHAPE_COLOR = (0, 51, 204)
DROP_COLOR = (255, 0, 0)

def GameThread():
    global posx, posy, gameOver, numBalls, score, speed, goal, cupSpeed, minOffset, maxOffset

    pygame.init()
    fps = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Test')

    background_image = pygame.image.load("templates/background.jpg")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    apple_image = pygame.image.load("templates/apple.png")
    apple_image = pygame.transform.scale(apple_image, (40, 40))
    basket_image = pygame.image.load("templates/basket.png")
    basket_image = pygame.transform.scale(basket_image, (60, 60))

    font = pygame.font.Font(None, 36)

    boarders = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    border_color = (0, 0, 3)
    cupRect = pygame.Rect(0, 0, 60, 60)
    balls = []
    ball_timers = []

    for ball in range(numBalls):
        ball_timers.append(pygame.time.get_ticks() + random.randint(500, 2000))

    while not gameOver:
        current_time = pygame.time.get_ticks()
        for i in range(len(ball_timers)):
            if ball_timers[i] <= current_time:
                ball = pygame.Rect(random.randint(0, SCREEN_WIDTH - 15), -20, 40, 40)
                balls.append(ball)
                ball_timers[i] = current_time + random.randint(1000, 5000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(background_image, (0, 0))
        cupRect.center = (posx, posy)
        screen.blit(basket_image, (cupRect.x, cupRect.y))
        pygame.draw.rect(screen, border_color, boarders, 6, 1)

        delta_time = fps.tick(FPS) / 1000.0
        for ball in balls:
            ball.y += speed * delta_time * 60
            collision = cupRect.colliderect(ball)
            if collision:
                score += 1
                balls.remove(ball)

            if ball.y > SCREEN_HEIGHT and not collision:
                gameOver = True
                balls.remove(ball)
            screen.blit(apple_image, (ball.x, ball.y))

        score_text = font.render(f"Score: {score}", True, (0,0,0))
        screen.blit(score_text, (10, 10))

        if score != 0 and score % goal == 0:
            goal += 10
            numBalls += 2
            minOffset += 1000
            maxOffset += 1500
            for _ in range(2):
                ball_timers.append(pygame.time.get_ticks() + random.randint(1000 + minOffset, 5000 + maxOffset))
        
        if score != 0 and score % goal == 0:
            speed += 0.05
            cupSpeed += 1

        pygame.display.update()


def ServerThread():
    global posy, posx, cupSpeed, gameOver, SCREEN_HEIGHT, SCREEN_WIDTH

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("localhost", 80))
    host = s.getsockname()[0]
    s.close()
    print(host)

    server_socket = socket.socket()
    port = 5000
    server_socket.bind((host, port))
    print("Server enabled...")
    server_socket.listen(2)

    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    while not gameOver:
        #data = conn.rect(1024).decode()
        data = conn.recv(1024).decode()
        if not data:
            break

        print("from connected user: " + str(data))

        if data == 'w':
            posy -= cupSpeed
        if data == 's':
            posy += cupSpeed
        if data == 'a':
            posx -= cupSpeed
        if data == 'd':
            posx += cupSpeed

        if posx < 15:
            posx = 15
        if posx > SCREEN_WIDTH - 15:
            posx = SCREEN_WIDTH = 15
        if posy > SCREEN_HEIGHT - 15:
            posy = SCREEN_HEIGHT = 15
        
    conn.close()

t1 = threading.Thread(target=GameThread, args=[])
t2 = threading.Thread(target=ServerThread, args=[])
t1.start()
t2.start()
