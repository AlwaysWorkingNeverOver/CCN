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
gameOver = False
numBalls = 1
score = 0
cupSpeed = 40
goal = 5
minOffset = 0
maxOffset = 0


# Game settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Colors
BACKGROUND = (204, 230, 255)
SHAPE_COLOR = (0, 51, 204)
DROP_COLOR = (255, 0, 0)

def GameThread():
    global posx, posy,gameOver,numBalls,score,speed,goal,cupSpeed,minOffset,maxOffset

    # Initialize Pygame
    pygame.init()
    fps = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Test')

    # Create game objects
    boarders = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    border_color = (0, 0, 5) 
    cupRect = pygame.Rect(0, 0, 30, 30)
    balls = []
    ball_timers = []  

    # Ball timers
    for _ in range(numBalls):
        ball_timers.append(pygame.time.get_ticks() + random.randint(500, 2000))  # Random delay between 500ms and 2000ms

    while not gameOver:
        # Check if it's time to drop a ball
        current_time = pygame.time.get_ticks()
        for i in range(len(ball_timers)):
            if ball_timers[i] <= current_time:
                ball = pygame.Rect(random.randint(0, SCREEN_WIDTH - 15), -20, 20, 20)
                balls.append(ball)
                ball_timers[i] = current_time + random.randint(1000, 5000) 
            
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BACKGROUND)
        cupRect.center = (posx, posy)

        # prevent cup from going out of bounds
        if posx < 15:  
            posx = 15
        if posx > SCREEN_WIDTH - 15: 
            posx = SCREEN_WIDTH - 15
        if posy < 15:  
            posy = 15
        if posy > SCREEN_HEIGHT - 15: 
            posy = SCREEN_HEIGHT - 15

        # Draw cup and borders
        pygame.draw.rect(screen, SHAPE_COLOR, cupRect)
        pygame.draw.rect(screen, border_color, boarders, 6, 1)

        # Update and draw balls
        delta_time = fps.tick(FPS) / 1000.0
        for ball in balls:
            ball.y += speed * delta_time * 60
            collision = cupRect.colliderect(ball)  # checks collision with cup      
            if collision:
                score+=1
                balls.remove(ball)  # Remove ball on collision
          
            if ball.y > SCREEN_HEIGHT and not collision:  
                gameOver = True
                balls.remove(ball)  # Remove ball on collision
            pygame.draw.rect(screen, DROP_COLOR, ball)
        
        # Increase difficulty
        if score != 0 and score % goal == 0:
            goal += 10
            numBalls += 2  # Increase number of balls every 5 points
            minOffset += 1000  # changed min time for ball drop
            maxOffset += 1500  # changed max time for ball drop
            for _ in range(2):  # Add timers for new balls
                ball_timers.append(pygame.time.get_ticks() + random.randint(1000+minOffset, 5000+maxOffset))  

        # increase cup and ball speeds every benchmark
        if score != 0 and score % goal == 0:
            speed += 0.05
            cupSpeed += 1  
                
        pygame.display.update()


def ServerThread():
    global posy, posx,cupSpeed,gameOver

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
    while not gameOver:
        data = conn.recv(1024).decode()
        if not data:
            break
        
        print("from connected user: " + str(data))
        # Handle movement
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

    conn.close()

# Start threads
t1 = threading.Thread(target=GameThread, args=[])
t2 = threading.Thread(target=ServerThread, args=[])
t1.start()
t2.start()