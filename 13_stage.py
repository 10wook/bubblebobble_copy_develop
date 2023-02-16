# 게임종료 처리
# 성공 : 화면내에 버블 사라지면 성공 => 다음 스테이지로 넘어가기
# 실패 다 내려오면 실패 ㅇㅇ => 바로 게임 종료

#게임 오버 함수랑 스테이지 오버 함수를 따로 만드는게 좋을 듯 하다



#from email.mime import image
# from pickle import TRUE
# from tkinter.tix import CELL
import random
import pygame
import os
import math
from map import MAP

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
        
    def draw(self,screen, to_x = None):
        if to_x :
            screen.blit(self.image,(self.rect.x + to_x, self.rect.y))
            
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
        
    def drop_downward(self, height):
        self.rect  = self.image.get_rect(center = (self.rect.centerx, self.rect.centery + height ))

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
    global map, stage_level
    #여기서 스테이지에 따라서 다른 맵을 임포트 해주면 될거 같은 생각이 드네용
    
    map = MAP[stage_level-1]
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
    pos_y = row_idx * CELL_SIZE + BUBBLE_HEIGHT//2 + wall_hieght
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
    global curr_bubble,fire, curr_fire_count
    hit_bubble = pygame.sprite.spritecollideany(curr_bubble,bubble_group,pygame.sprite.collide_mask)
    if hit_bubble or curr_bubble.rect.top <= wall_hieght:
        row_idx ,col_idx = get_map_index(*curr_bubble.rect.center)
        place_bubble(curr_bubble,row_idx,col_idx)
        remove_adjacent_bubbles(row_idx,col_idx,curr_bubble.color)
        curr_bubble = None
        fire = False
        curr_fire_count = curr_fire_count -1
               
def  get_map_index(x,y):
    row_idx = (y - wall_hieght) //CELL_SIZE
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
        remove_hanging_bubbles()
        
def visit(row_idx,col_idx, color = None):
    #범위 확인
    if (row_idx < 0) or (row_idx >= MAP_ROW_COUNT) or (col_idx < 0) or (col_idx >= MAP_COL_COUNT):
        return 
    #현재 버블을 색깔 찾기
    #print(row_idx,col_idx)
    if color and map[row_idx][col_idx] != color:
        return
    #버블이 빈공간이나 존재할 수 없는 곳이면 넘어간다.
    if map[row_idx][col_idx] in [".", "/"]:
        return
    
    if (row_idx,col_idx) in visited:#방문 여부 확인하기   
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
    bubbles_to_remove = [b for b in bubble_group if (b.row_idx,b.col_idx) in visited]
    for bubble in bubbles_to_remove:
        map[bubble.row_idx][bubble.col_idx] = "."
        bubble_group.remove(bubble)
        
def remove_not_visited_bubbles():
    bubbles_to_remove = [b for b in bubble_group if (b.row_idx,b.col_idx) not in visited]
    for bubble in bubbles_to_remove:
        map[bubble.row_idx][bubble.col_idx] = "."
        bubble_group.remove(bubble) 
        
def remove_hanging_bubbles():
    visited.clear()
    for col_idx in range(MAP_COL_COUNT):
        if map[0][col_idx] != ".":
            visit(0,col_idx,)
    remove_not_visited_bubbles()
    
def  draw_bubbles():
    to_x = None
    if curr_fire_count ==2 :
        to_x = random.randint(0,2) - 1
    elif curr_fire_count == 1 : 
        to_x = random. randint(0,8) - 4 
        
    for bubble in bubble_group:
        bubble.draw(screen, to_x)
        
    return

def get_lowest_bubble_bottom():
    bubble_bottoms = [bubble.rect.bottom for bubble in bubble_group]
    return max(bubble_bottoms)

def drop_wall():
    global wall_hieght, curr_fire_count
    wall_hieght += CELL_SIZE
    for bubble in bubble_group:
        bubble.drop_downward(CELL_SIZE)
    curr_fire_count = FIRE_COUNT

def change_bubble_image(image):
    for bubble in bubble_group:
        bubble.image = image
        
def display_gameover():
    global game_result
    txt_game_over = game_font.render(game_result,True , WHITE)
    rect_gameover = txt_game_over.get_rect(center = (screen_width//2, screen_height//2 ))
    screen.blit(txt_game_over, rect_gameover)

def display_stage_title(stage_title):
    screen.fill(BLACK)
    txt_stage_title = game_font.render(stage_title, True , WHITE)
    rect_stage_title = txt_stage_title.get_rect(center = (screen_width//2, screen_height//2 ))
    screen.blit(txt_stage_title, rect_stage_title)
    
def next_stage():
    global stage_level, curr_bubble, next_bubble, fire, curr_fire_count, wall_hieght, is_stage_over
    stage_level += 1
    display_gameover()
    bubble_group.draw(screen)
    draw_bubbles()
    pygame.display.update()
    pygame.time.delay(2000)
    ##여기 부분에 다름 스테이지를 표기해준다!
    stage_title = "STAGE " + str(stage_level)
    display_stage_title(stage_title)
    pygame.display.update()
    pygame.time.delay(2000)
    initailize()
    setup()
    
def initailize():
    global stage_level, curr_bubble, next_bubble, fire, curr_fire_count, wall_hieght, is_stage_over
    curr_bubble = None#이번에 쏠 버블
    next_bubble = None
    fire = False
    curr_fire_count = FIRE_COUNT
    wall_hieght = 0
    is_stage_over = False
    return
    
def display_start_page():
    start_font = pygame.font.SysFont("arialrounded",20)
    screen.fill(BLACK)
    txt_start = start_font.render("PRESS SPACE TO START!",True , WHITE)
    rect_start = txt_start.get_rect(center = (screen_width//2, screen_height//2 ))
    screen.blit(txt_start, rect_start)
    return
pygame.init()
screen_width = 448
screen_height = 720
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Puzzle Bobble")
clock = pygame.time.Clock()


current_path = os.path.dirname(__file__)
#배경
background = pygame.image.load(os.path.join(current_path,"background.png"))
wall = pygame.image.load(os.path.join(current_path,"wall.png"))
#거품의 그림
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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAP_ROW_COUNT = 11
MAP_COL_COUNT = 8
FIRE_COUNT = 7
FINAL_STAGE = len(MAP)


#화살표 관련 변수   
#to_angle = 0
to_angle_left = 0
to_angle_right = 0
angle_speed = 1.5

curr_bubble = None#이번에 쏠 버블
next_bubble = None
fire = False
curr_fire_count = FIRE_COUNT
wall_hieght = 0
stage_level = 1

is_game_over = False
is_stage_over = False
game_font = pygame.font.SysFont("arialrounded",38)
game_result = None
start = True
map = []
visited = []
stage1 = True
bubble_group = pygame.sprite.Group()
setup()
# stage_title = "STAGE " + str(stage_level)
# display_stage_title(stage_title)
# pygame.display.update()
# pygame.time.delay(2000)

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
                start = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                to_angle_left = 0
            elif event.key == pygame.K_RIGHT:
                to_angle_right = 0
                
    if start == True:
        display_start_page()
        pygame.display.update()
        #pygame.time.delay(2000)
        # start = False
        continue
        
        
    if stage1 == True:
        stage_title = "STAGE " + str(stage_level)
        display_stage_title(stage_title)
        pygame.display.update()
        pygame.time.delay(2000)
        stage1 = False
        continue
        
    if not curr_bubble:
        prepare_bubbles()
    
    if fire:
        process_collision()
    
    if curr_fire_count == 0:
        drop_wall()
        
    if not bubble_group :
        if stage_level >= FINAL_STAGE:
            game_result = "ALL CLEAR"
            is_game_over = True
        else:
            game_result = "STAGE CLEAR"
            #next_stage()
            is_stage_over = True
            
    elif get_lowest_bubble_bottom() > len(map)*CELL_SIZE:
        game_result = "GAME OVER"
        is_game_over = True
        change_bubble_image(bubble_images[-1])
        
    screen.blit(background,(0,0))
    screen.blit(wall, (0, wall_hieght - screen_height))
    
    bubble_group.draw(screen)
    
    draw_bubbles()
    pointer.rotate(to_angle_right+to_angle_left)# 이 부분은 전에 쏘던 부분에도 추가하면 좋을 것 으로 보인다. 
    pointer.draw(screen)
    if curr_bubble:
        if fire:
            curr_bubble.move()
        curr_bubble.draw(screen)
 
            
    if next_bubble:
        next_bubble.draw(screen)
        
        
    if is_game_over:
        display_gameover()
        
        running = False 
        
    if is_stage_over:
        
        pygame.display.update()
        
        next_stage()
        
        
    pygame.display.update()
    
    
pygame.time.delay(2000)
pygame.quit()