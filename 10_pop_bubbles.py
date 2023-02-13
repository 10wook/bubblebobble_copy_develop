from email.mime import image
from tkinter.tix import CELL
import random
import pygame
import os
import math

#버블 클래스 만들기
class Bubble(pygame.sprite.Sprite):
    def __init__(self,image,color,position = (0,0), row_idx = -1, col_idx = -1):
        super().__init__()
        self.image = image
        self.color = color
        self.rect = image.get_rect(center = position)
        self.radius = 18  
        self.row_idx = row_idx
        self.col_idx = col_idx
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
            
    def set_map_index (self, row_idx,col_idx):
        self.row_idx = row_idx
        self.col_idx = col_idx
        
        
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

        #    list("RRYYBBGG"),
        #    list("RRYYBBG/"), #/는 버블이 위치 할 수 없는 곳 이라는 의미
        #    list("BBGGRRYY"),
        #    list("BGGRRYY/"),
        #    list("........"),
        #    list("......./"),
        #    list("........"),
        #    list("......./"),
        #    list("........"), 
        #    list("......./"),
        #    list("........")
        list("...R...."),
        list("......./"), #/는 버블이 위치 할 수 없는 곳 이라는 의미
        list("........"),
        list("......./"),
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
            bubble_group.add(Bubble(image,col,position,row_idx,col_idx))
            
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
    
def process_collision():
    global curr_bubble,fire
    hit_bubble = pygame.sprite.spritecollideany(curr_bubble,bubble_group,pygame.sprite.collide_mask)
    if hit_bubble or curr_bubble.rect.top <= 0:
        row_idx ,col_idx = get_map_index(*curr_bubble.rect.center)
        place_bubble(curr_bubble,row_idx,col_idx)
        remove_adjacent_bubbles(row_idx,col_idx,curr_bubble.color)
        curr_bubble = None
        fire = False
        
def  get_map_index(x,y):
    row_idx = y//CELL_SIZE
    col_idx = x//CELL_SIZE
    if row_idx %2 == 1:
        col_idx = (x - (CELL_SIZE//2))//CELL_SIZE
        if col_idx < 0:
            col_idx = 0
        elif col_idx > MAP_COL_COUNT -2:
            col_idx =  MAP_COL_COUNT -2
    return row_idx, col_idx

def place_bubble(bubble:Bubble,row_idx,col_idx):
    global map
    map[row_idx][col_idx] = bubble.color
    position = get_bubble_postion(row_idx,col_idx)
    bubble.set_rect(position)
    bubble.set_map_index(row_idx,col_idx)
    bubble_group.add(bubble)
    return
    
    
def remove_adjacent_bubbles (row_idx,col_idx, color):
    visited.clear()
    visit(row_idx,col_idx,color)
    if len(visited) >= 3:
        remove_visited_bubbles()
        
def visit(row_idx,col_idx,color):
    #범위 확인
    if row_idx < 0 or row_idx > MAP_ROW_COUNT or col_idx < 0 or col_idx > MAP_ROW_COUNT:
        return 
    #현재 버블을 색깔 찾기
    if map[row_idx][col_idx] != color:
        return
    if (row_idx,col_idx) in visit:#방문 여부 확인하기   
        return 
    visited.append((row_idx,col_idx))
    rows = [0, -1, -1, 0, 1, 1]
    cols = [-1, -1, 0, 1, 0, -1]
    if row_idx % 2 ==1:
        rows = [0, -1, -1, 0, 1, 1]
        cols = [-1, 0, 1, 1, 1, 0]
        
    for i in range (len(rows)):
        visit(row_idx + rows[i],col_idx + cols[i], color)        
def remove_visited_bubbles():
    bubbles_to_remove = [b for b in bubble_group if (b.row_idx,b.)]
    
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
MAP_ROW_COUNT = 11
MAP_COL_COUNT = 8


#화살표 관련 변수   
#to_angle = 0
to_angle_left = 0
to_angle_right = 0
angle_speed = 1.5

curr_bubble = None#이번에 쏠 버블
next_bubble = None
fire = False

map = []
visited = []

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
    
    if fire:
        process_collision()
    
        
    screen.blit(background,(0,0))
    bubble_group.draw(screen)
    pointer.rotate(to_angle_right+to_angle_left)# 이 부분은 전에 쏘던 부분에도 추가하면 좋을 것 으로 보인다. 
    pointer.draw(screen)
    if curr_bubble:
        if fire:
            curr_bubble.move()
        curr_bubble.draw(screen)
        

            
    if next_bubble:
        next_bubble.draw(screen)
    pygame.display.update()
    
    
    
pygame.quit()