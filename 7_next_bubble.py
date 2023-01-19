from email.mime import image
from tkinter.tix import CELL
import random
import pygame
import os
import math

#버블 클래스 만들기
class Bubble(pygame.sprite.Sprite):
    def __init__(self,image,color,position = (0,0)):
        super().__init__()
        self.image = image
        self.color = color
        self.rect = image.get_rect(center = position)
        self.radius = 18
    def set_rect(self,position):
        self.rect = self.image.get_rect(center = position)
        
    def draw(self,screen):
        screen.blit(self.image,self.rect)
        
    def set_angle(self, angle):
        self.angle= angle
        self.rad_angle = math.radians(self.angle)
        
    def move(self):
        to_x = self.radius * math.cos(self.rad_angle)
        to_y = self.radius * math.sin(self.rad_angle) * -1
        
        self.rect.x += to_x
        self.rect.y += to_y
        
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.set_angle(180-self.angle)
class Pointer (pygame.sprite.Sprite):
    def __init__(self, image, position, angle):
        super().__init__()
        self.image = image
        self.rect = image.get_rect(center = position)
        self.original_image = image 
        self.angle = angle
        self.position = position
    def rotate(self,angle):
        self.angle += angle
        #각도 조정
        if self.angle + angle > 170:
            self.angle = 170
        if self.angle + angle < 10:
            self.angle = 10
        
        self.image = pygame.transform.rotozoom(self.original_image,self.angle,1)
        self.rect = self.image.get_rect(center = self.position)
        
        
    def draw(self,screen):
        screen.blit(self.image,self.rect)
        pygame.draw.circle(screen,RED,self.position,9)
#스테이지 별로 맵 만들기
def setup():
    global map
    map = [
           #["R","R","Y","Y","B"...]
           list("RRYYBBGG"),
           list("RRYYBBG/"), #/는 버블이 위치 할 수 없는 곳 이라는 의미
           list("BBGGRRYY"),
           list("BGGRRYY/"),
           list("........"),
           list("......./"),
           list("........"),
           list("......./"),
           list("........"), 
           list("......./"),
           list("........")
           ]
    for row_idx,row in enumerate(map):
        for col_idx, col in enumerate(row):
            if col == "." or col == "/":
                continue
            position = get_bubble_postion(row_idx,col_idx)
            image = get_bubble_image(col)
            bubble_group.add(Bubble(image,col,position))
            
def get_bubble_postion(row_idx,col_idx):
    #x좌표는 col_idx * cell_size + bubble_width//2
    #y좌표는 row_idx * cell_size + bubble_height//2
    # + 홀수 인덱스면 x += cell_size//2
    pos_x = col_idx * CELL_SIZE + BUBBLE_WIDTH//2
    pos_y = row_idx * CELL_SIZE + BUBBLE_HEIGHT//2
    if row_idx % 2 == 1:
        pos_x += CELL_SIZE//2
    return pos_x, pos_y
    
def get_bubble_image(color):
    if color == "R":
        return bubble_images[0]
    elif color == "B":
        return bubble_images[1]
    elif color == "Y":
        return bubble_images[2]
    elif color == "G":
        return bubble_images[3]
    elif color == "P":
        return bubble_images[4]
    else:
        return bubble_images[-1]
    
def prepare_bubbles():
    global curr_bubble, next_bubble
    if next_bubble:
        curr_bubble = next_bubble
    else:
        curr_bubble = create_bubble()
    curr_bubble.set_rect((screen_width/2,624))
    next_bubble = create_bubble()
    next_bubble.set_rect((screen_width/4,688))
def create_bubble():
    color = get_random_bubble_color()
    image = get_bubble_image(color)
    return Bubble(image, color)
    
    
def get_random_bubble_color():
        colors = []
        for row in map:
            for col in row:
                if col not in colors and col not in [".", "/"] :
                    colors.append(col)
                    
        return random.choice(colors)
    
pygame.init()
screen_width = 448
screen_height = 720
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Puzzle Bobble")
clock = pygame.time.Clock()


current_path = os.path.dirname(__file__)
#배경
background = pygame.image.load(os.path.join(current_path,"background.png"))

bubble_images = [
    pygame.image.load(os.path.join(current_path,"red.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path,"blue.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path,"yellow.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path,"green.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path,"purple.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path,"black.png")).convert_alpha()
]
pointer_image = pygame.image.load(os.path.join(current_path,"pointer.png"))
pointer = Pointer(pointer_image, (screen_width//2,624),90)
#게임 관련 변수
CELL_SIZE = 56
BUBBLE_WIDTH = 56
BUBBLE_HEIGHT = 62
RED = (255, 0, 0)

#화살표 관련 변수   
#to_angle = 0
to_angle_left = 0
to_angle_right = 0
angle_speed = 1.5

curr_bubble = None#이번에 쏠 버블
next_bubble = None
fire = False

map = []

bubble_group = pygame.sprite.Group()
setup()

running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                to_angle_left += angle_speed
            elif event.key == pygame.K_RIGHT:
                to_angle_right -= angle_speed
            elif event.key == pygame.K_SPACE:
                if curr_bubble and not fire:
                    fire = True
                    curr_bubble.set_angle(pointer.angle)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                to_angle_left = 0
            elif event.key == pygame.K_RIGHT:
                to_angle_right = 0
        
        
        
    if not curr_bubble:
        prepare_bubbles()
        
    screen.blit(background,(0,0))
    bubble_group.draw(screen)
    pointer.rotate(to_angle_right+to_angle_left)# 이 부분은 전에 쏘던 부분에도 추가하면 좋을 것 으로 보인다. 
    pointer.draw(screen)
    if curr_bubble:
        if fire:
            curr_bubble.move()
        curr_bubble.draw(screen)
        
        if curr_bubble.rect.top <= 0:
            curr_bubble = None
            fire = False
            
    if next_bubble:
        next_bubble.draw(screen)
    pygame.display.update()
    
    
    
pygame.quit()