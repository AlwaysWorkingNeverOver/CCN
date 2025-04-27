import threading
import pygame
import socket
import sys
import random
import time

# Global variables
name = "test"
posx = 300
posy = 200
speed = 1
gameOver = True
numBalls = 1
score = 0
cupSpeed = 40
goal = 5
minOffset = 0
maxOffset = 0
in_menu = True
x,y = 200,100

# Game settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Colors
BACKGROUND = (204, 230, 255)
SHAPE_COLOR = (0, 51, 204)
DROP_COLOR = (255, 0, 0)

def GameThread():
    global posx, posy, gameOver, numBalls, score, speed, goal, cupSpeed, minOffset, maxOffset,in_menu,x,y

    # Initialize Pygame
    pygame.init()
    fps = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Test')

    # Background image
    background_image = pygame.image.load("templates/background.jpg")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_image = pygame.image.load("templates/menu.png")
    menu_image = pygame.transform.scale(menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Pre-game objects
    grey_square = pygame.Rect(100, 100, 10, 10)
    red_square = pygame.Rect(250, 200, 60, 60)

    # Game objects
    apple_image = pygame.image.load("templates/apple.png")
    apple_image = pygame.transform.scale(apple_image, (40, 40))
    basket_image = pygame.image.load("templates/basket.png")
    basket_image = pygame.transform.scale(basket_image, (60, 60))
    font = pygame.font.Font(None, 36)

    # Game state
    boarders = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    border_color = (0, 0, 5)
    cupRect = pygame.Rect(0, 0, 60, 60)
    balls = []
    ball_timers = []

    # Ball timers
    for _ in range(numBalls):
        ball_timers.append(pygame.time.get_ticks() + random.randint(500, 2000))



    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if in_menu:
            # Check proximity to the red square
            if grey_square.colliderect(red_square):
                red_square_color = (255, 255, 255)  # Highlight red square in white
                if pygame.key.get_pressed()[pygame.K_e]:  # Start the game when 'E' is pressed
                    in_menu = False
                    gameOver = False
            else:
                red_square_color = (255, 0, 0)  # Default red color

            screen.blit(menu_image, (0, 0))
            pygame.draw.rect(screen, (255, 0, 0), red_square)  # the play  button
            grey_square.topleft = (x, y)
            pygame.draw.rect(screen, (128, 128, 128), grey_square)  # the cursor square
            fps.tick(FPS)
            pygame.display.update()
            continue

    
        if not gameOver:
            # Game logic (apple catcher)
            current_time = pygame.time.get_ticks()
            for i in range(len(ball_timers)):
                if ball_timers[i] <= current_time:
                    ball = pygame.Rect(random.randint(0, SCREEN_WIDTH - 15), -20, 40, 40)
                    balls.append(ball)
                    ball_timers[i] = current_time + random.randint(1000, 5000)

            screen.blit(background_image, (0, 0))
            cupRect.center = (posx, posy)
            screen.blit(basket_image, (cupRect.x, cupRect.y))
            pygame.draw.rect(screen, border_color, boarders, 6, 1)

            # Update and draw balls
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

            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))

            # Increase difficulty
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
    global posy, posx,cupSpeed,gameOver,x,y

    # Set up server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("localhost", 80))
    host = s.getsockname()[0]
    s.close()
    print(host)

    # Initialize server socket
    server_socket = socket.socket()
    port = 5000
    server_socket.bind((host, port))
    print("Server enabled...")
    server_socket.listen(2)

    # Accept connection
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    # Handle client communication
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        
        print("from connected user: " + str(data))
        # Handle movement
        if not in_menu:
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
                posx = SCREEN_WIDTH - 15
            if posy < 15:  
                posy = 15
            if posy > SCREEN_HEIGHT - 15: 
                posy = SCREEN_HEIGHT - 15
        else:
            # Handle movement of the grey square in the menu
            if data == 'w':
                y -= 15
            if data == 's':
                y += 15
            if data == 'a':
                x -= 15
            if data == 'd':
                x += 15

    conn.close()

# Start threads
t1 = threading.Thread(target=GameThread, args=[])
t2 = threading.Thread(target=ServerThread, args=[])
t1.start()
t2.start()