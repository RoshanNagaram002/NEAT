import os
import sys
import pygame
import random
from pygame import * # type: ignore
from Neat import *
from Neat.Info import Network

pygame.init()

screen_size_display = (width_screen, height_screen) = (600, 150)
FPS = 60
gravity = 0.6

black_color = (0,0,0)
white_color = (255,255,255)
bg_color = (235, 235, 235)

highest_scores = 0

screen_layout_display = pygame.display.set_mode(screen_size_display)
time_clock = pygame.time.Clock()
pygame.display.set_caption("Dino Run ")

jump_sound = pygame.mixer.Sound('resources/jump.wav')
die_sound = pygame.mixer.Sound('resources/die.wav')
checkPoint_sound = pygame.mixer.Sound('resources/checkPoint.wav')


obstacle_count = 0 
old_count = obstacle_count

def load_image(
    name,
    sx=-1,
    sy=-1,
    colorkey=None,
    ):

    fullname = os.path.join('resources', name)
    img = pygame.image.load(fullname)
    img = img.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey, RLEACCEL)

    if sx != -1 or sy != -1:
        img = pygame.transform.scale(img, (sx, sy))

    return (img, img.get_rect())

def load_sprite_sheet(
        s_name,
        namex,
        namey,
        scx = -1,
        scy = -1,
        c_key = None,
        ):
    fullname = os.path.join('resources', s_name)
    sh = pygame.image.load(fullname)
    sh = sh.convert()

    sh_rect = sh.get_rect()

    sprites = []

    sx = sh_rect.width/ namex
    sy = sh_rect.height/ namey

    for i in range(0, namey):
        for j in range(0, namex):
            rect = pygame.Rect((j*sx,i*sy,sx,sy))
            img = pygame.Surface(rect.size)
            img = img.convert()
            img.blit(sh,(0,0),rect)

            if c_key is not None:
                if c_key == -1:
                    c_key = img.get_at((0, 0))
                img.set_colorkey(c_key, RLEACCEL)

            if scx != -1 or scy != -1:
                img = pygame.transform.scale(img, (scx, scy))

            sprites.append(img)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect

def extractDigits(num):
    if num > -1:
        d = []
        i = 0
        while(num / 10 != 0):
            d.append(num % 10)
            num = int(num / 10)

        d.append(num % 10)
        for i in range(len(d),5):
            d.append(0)
        d.reverse()
        return d

class Dino():
    def __init__(self, sx=-1, sy=-1):
        self.imgs, self.rect = load_sprite_sheet('dino.png', 5, 1, sx, sy, -1)
        self.imgs1, self.rect1 = load_sprite_sheet('dino_ducking.png', 2, 1, 59, sy, -1)
        self.rect.bottom = int(0.98 * height_screen)
        self.rect.left = width_screen / 15
        self.image = self.imgs[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.jumping = False
        self.dead = False
        self.ducking = False
        self.blinking = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5

        self.stand_position_width = self.rect.width
        self.duck_position_width = self.rect1.width

    def draw(self):
        screen_layout_display.blit(self.image, self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98 * height_screen):
            self.rect.bottom = int(0.98 * height_screen)
            self.jumping = False

    def update(self):
        if self.jumping:
            self.movement[1] = self.movement[1] + gravity # type: ignore

        if self.jumping:
            self.index = 0
        elif self.blinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.ducking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.dead:
           self.index = 4

        if not self.ducking:
            self.image = self.imgs[self.index]
            self.rect.width = self.stand_position_width
        else:
            self.image = self.imgs1[(self.index) % 2]
            self.rect.width = self.duck_position_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.dead and self.counter % 7 == 6 and self.blinking == False:
            self.score += 1
            # if self.score % 100 == 0 and self.score != 0:
            #     # if pygame.mixer.get_init() != None:
            #     #     checkPoint_sound.play()

        self.counter = (self.counter + 1)

class Cactus(pygame.sprite.Sprite):
    def __init__(self, speed=5, sx=-1, sy=-1):
        pygame.sprite.Sprite.__init__(self,self.containers) # type: ignore
        self.imgs, self.rect = load_sprite_sheet('cactus-small.png', 3, 1, sx, sy, -1)
        self.rect.bottom = int(0.98 * height_screen)
        self.rect.left = width_screen + self.rect.width
        self.image = self.imgs[random.randrange(0, 3)]
        self.movement = [-1*speed,0]

    def draw(self):
        screen_layout_display.blit(self.image, self.rect) # type: ignore

    def update(self):
        self.rect = self.rect.move(self.movement) # type: ignore

        if self.rect.right < 0:
            global obstacle_count
            obstacle_count += 1 
            self.kill()

class birds(pygame.sprite.Sprite):
    def __init__(self, speed=5, sx=-1, sy=-1):
        pygame.sprite.Sprite.__init__(self,self.containers) # type: ignore
        self.imgs, self.rect = load_sprite_sheet('birds.png', 2, 1, sx, sy, -1)
        self.birds_height = [height_screen * 0.82, height_screen * 0.75, height_screen * 0.60]
        self.rect.centery = self.birds_height[random.randrange(0, 3)]
        self.rect.left = width_screen + self.rect.width
        self.image = self.imgs[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen_layout_display.blit(self.image, self.rect) # type: ignore

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.imgs[self.index]
        self.rect = self.rect.move(self.movement) # type: ignore
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            global obstacle_count
            obstacle_count += 1
            self.kill()


class Ground():
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height_screen
        self.rect1.bottom = height_screen
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen_layout_display.blit(self.image, self.rect)
        screen_layout_display.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

class Scoreboard():
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.scre_img, self.screrect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width_screen * 0.89 # type: ignore
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height_screen * 0.1 # type: ignore
        else:
            self.rect.top = y

    def draw(self):
        screen_layout_display.blit(self.image, self.rect)

    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(bg_color)
        for s in score_digits: # type: ignore
            self.image.blit(self.scre_img[s], self.screrect)
            self.screrect.left += self.screrect.width
        self.screrect.left = 0



def gameplay(net: Network, view = True):
    global highest_scores
    gp = 4
    s_Menu = False
    g_Over = False
    g_exit = False
    gamer_Dino = Dino(44,47)
    new_grnd = Ground(-1*gp)
    score_boards = Scoreboard()
    highScore = Scoreboard(width_screen * 0.78)
    counter = 0


    cactusan = pygame.sprite.Group()
    smallBird = pygame.sprite.Group()

    last_end_obs = pygame.sprite.Group()

    Cactus.containers = cactusan # type: ignore
    birds.containers = smallBird # type: ignore


    rbtn_image,rbtn_rect = load_image('replay_button.png',35,31,-1)
    gmo_image,gmo_rect = load_image('game_over.png',190,11,-1)

    t_images,t_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
    ado_image = pygame.Surface((22,int(11*6/5)))
    ado_rect = ado_image.get_rect()
    ado_image.fill(bg_color)
    ado_image.blit(t_images[10],t_rect)
    t_rect.left += t_rect.width
    ado_image.blit(t_images[11],t_rect)
    ado_rect.top = height_screen * 0.1 # type: ignore
    ado_rect.left = width_screen * 0.73 # type: ignore

    while not g_exit:
        
        while s_Menu:
            pass
        while not g_Over:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                g_exit = True
                g_Over = True
            # Change this else to to allow for output
            else:
                # Game Speed, 3 bounding boxes of closest obstacles and in front
                inputs = [gp]
                cactus_boxes = [(c.rect.left, c.rect.bottom, c.rect.right, c.rect.top) for c in cactusan if c.rect.right >= 0] # type: ignore
                bird_boxes = [(c.rect.left, c.rect.bottom, c.rect.right, c.rect.top) for c in smallBird if c.rect.right >= 0] # type: ignore

                total_obstacle_boxes = cactus_boxes + bird_boxes
                
                # Sort to make the obstacles near you come first (ascending_order)
                total_obstacle_boxes.sort(key = lambda x: x[0], reverse = False)

                # make it really "far" left so it does not have to "worry" about it?
                # Make it have no height and be below me? 
                temp_tup = (10**5, 0, 10**6, 0)
                
                # model will only take into account the 3 nearest obstacles
                while len(total_obstacle_boxes) < 3:
                    total_obstacle_boxes.append(temp_tup)
                
                for obst in total_obstacle_boxes:
                    left, bottom, right, top = obst
                    inputs.append(left)
                    inputs.append(bottom)
                    inputs.append(right)
                    inputs.append(top)

                raw_jump, raw_duck = net.get_output(inputs)
                is_jump = True if raw_jump > .5 else False
                is_duck = True if raw_duck > .5 else False

                if is_jump:
                    if gamer_Dino.rect.bottom == int(0.98 * height_screen):
                        gamer_Dino.jumping = True
                        gamer_Dino.movement[1] = -1*gamer_Dino.jumpSpeed # type: ignore
                
                if is_duck:
                    if not (gamer_Dino.jumping and gamer_Dino.dead):
                        gamer_Dino.ducking = True
                
                else:
                    gamer_Dino.ducking = False


                # for event in pygame.event.get():
                #     if event.type == pygame.QUIT:
                #         g_exit = True
                #         g_Over = True
                #     if event.type == pygame.KEYDOWN:
                #         if event.key == pygame.K_SPACE:
                #             if gamer_Dino.rect.bottom == int(0.98 * height_screen):
                #                 gamer_Dino.jumping = True
                #                 gamer_Dino.movement[1] = -1*gamer_Dino.jumpSpeed

                #         if event.key == pygame.K_DOWN:
                #             if not (gamer_Dino.jumping and gamer_Dino.dead):
                #                 gamer_Dino.ducking = True

                #     if event.type == pygame.KEYUP:
                #         if event.key == pygame.K_DOWN:
                #             gamer_Dino.ducking = False

            global obstacle_count
            global old_count

            # if obstacle_count != old_count:
            #     print(obstacle_count)
            #     old_count = obstacle_count
            
            for c in cactusan:        
                c.movement[0] = -1*gp # type: ignore
                if pygame.sprite.collide_mask(gamer_Dino,c): # type: ignore
                    gamer_Dino.dead = True

            for p in smallBird:
                p.movement[0] = -1*gp # type: ignore
                if pygame.sprite.collide_mask(gamer_Dino,p): # type: ignore
                    gamer_Dino.dead = True

            if len(cactusan) < 2:
                if len(cactusan) == 0:
                    last_end_obs.empty()
                    last_end_obs.add(Cactus(gp,40,40))
                else:
                    for l in last_end_obs:
                        if l.rect.right < width_screen*0.7 and random.randrange(0, 50) == 10: # type: ignore
                            last_end_obs.empty()
                            last_end_obs.add(Cactus(gp, 40, 40))

            if len(smallBird) == 0 and random.randrange(0,200) == 10 and counter > 500:
                for l in last_end_obs:
                    if l.rect.right < width_screen*0.8: # type: ignore
                        last_end_obs.empty()
                        last_end_obs.add(birds(gp, 46, 40))

            gamer_Dino.update()
            cactusan.update()
            smallBird.update()
            new_grnd.update()
            score_boards.update(gamer_Dino.score)
            highScore.update(highest_scores)

            if view and pygame.display.get_surface() != None:
                screen_layout_display.fill(bg_color)
                new_grnd.draw()
                score_boards.draw()
                if highest_scores != 0:
                    highScore.draw()
                    screen_layout_display.blit(ado_image, ado_rect)
                cactusan.draw(screen_layout_display)
                smallBird.draw(screen_layout_display)
                gamer_Dino.draw()

                pygame.display.update()
            time_clock.tick(FPS)

            if gamer_Dino.dead:
                g_exit = True
                break

            if counter%700 == 699:
                new_grnd.speed -= 1
                gp += 1

            counter = (counter + 1)

        if g_exit:
            break

    pygame.quit()
    return obstacle_count

# def main():
#     gameplay(view = True)

# main()
