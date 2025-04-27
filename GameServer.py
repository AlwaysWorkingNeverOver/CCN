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
game_started = False

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

BACKGROUND = (204, 230, 255)
SHAPE_COLOR = (0, 51, 204)
DROP_COLOR = (255, 0, 0)

def Menu(screen):
    global game_started
    pygame.display.set_caption('Apple Picking Tycoon')
    font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)

    start_button = pygame.Rect(200, 150, 200, 50)
    quit_button = pygame.Rect(200, 250, 200, 50)
    button_color = (100, 100, 100)
    button_hover_color = (150, 150, 150)

    clock = pygame.time.Clock()
    while not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    print("Start button clicked")
                    game_started = True
                if quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        
        screen.fill(BACKGROUND)
        title_text = font.render("Apple Picker", True, (0, 0, 0))
        screen.blit(title_text, (150, 50))

        mouse_pos = pygame.mouse.get_pos()
        start_color = button_hover_color if start_button.collidepoint(mouse_pos) else button_color
        quit_color = button_hover_color if quit_button.collidepoint(mouse_pos) else button_color

        pygame.draw.rect(screen, start_color, start_button)
        pygame.draw.rect(screen, quit_color, quit_button)
        start_text = button_font.render("Start", True, (255, 255, 255))
        quit_text = button_font.render("Quit", True, (255, 255, 255))
        screen.blit(start_text, (start_button.x + 70, start_button.y + 10))
        screen.blit(quit_text, (quit_button.x + 70, quit_button.y + 10))

        pygame.display.flip()
        clock.tick(60)
    
    print("Menu exiting")

def GameThread(screen):
    global posx, posy, gameOver, numBalls, score, speed, goal, cupSpeed, minOffset, maxOffset
    print("GameThread started")
    pygame.display.set_caption('Test')

    try:
        screen.fill((0, 0, 255))
        print("Filled screen blue")
        pygame.display.flip()
        time.sleep(1)

        background_image = pygame.image.load("templates/background.jpg")
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("Loaded background image")

        apple_image = pygame.image.load("templates/apple.png")
        apple_image = pygame.transform.scale(apple_image, (40, 40))
        print("Loaded apple image")

        basket_image = pygame.image.load("templates/basket.png")
        basket_image = pygame.transform.scale(basket_image, (60, 60))
        print("Loaded basket image")

        font = pygame.font.Font(None, 36)
        boarders = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        border_color = (0, 0, 3)
        cupRect = pygame.Rect(0, 0, 60, 60)
        balls = []
        ball_timers = []

        for ball in range(numBalls):
            ball_timers.append(pygame.time.get_ticks() + random.randint(500, 2000))

        fps = pygame.time.Clock()
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
            print("Blitted background")
            cupRect.center = (posx, posy)
            screen.blit(basket_image, (cupRect.x, cupRect.y))
            print("Blitted basket")
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
            print("Blitted apples")

            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))
            print("Blitted score")

            pygame.event.pump()
            pygame.display.flip()
            print("Updated display")
    except Exception as e:
        print(f"Error in GameThread: {e}")
        pygame.quit()
        sys.exit()

def ServerThread():
    global posy, posx
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("localhost", 5000))
        host = s.getsockname()[0]
        s.close()
    except socket.error as e:
        print(f"Error getting host: {e}")
        host = "localhost"
    port = 5000
    print(f"Binding to {host}:{port}")

    server_socket = socket.socket()
    try:
        server_socket.bind((host, port))
        print("Server enabled...")
        server_socket.listen(2)
        conn, address = server_socket.accept()
        print("Connection from: " + str(address))
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print("from connected user: " + str(data))
            if data == 'w':
                posy -= 10
            if data == 's':
                posy += 10
            if data == 'a':
                posx -= 10
            if data == 'd':
                posx += 10
        conn.close()
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        server_socket.close()

if __name__ == '__main__':
    print("Starting program")
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    t2 = threading.Thread(target=ServerThread, args=[])
    t2.start()
    Menu(screen)  
    print(f"Menu finished, game_started: {game_started}")
    if game_started:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        GameThread(screen) 
    t2.join()
    pygame.quit()