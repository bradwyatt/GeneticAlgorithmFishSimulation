"""
Created by Brad Wyatt
"""
import pygame, random, sys, math, DNA
from pygame.locals import *
from genmenu import *
running = True #Flags game as on
menuOn = 1
firstMessage = 1
Rooms = []
(screenWidth, screenHeight) = 1200, 800
SCORE, scoreBlit, scoreDisappearTimer = 0, 0, 0
screen = None
keys = [False, False, False, False]
walls = []
images = {}
sounds = {}
lastPressed = 0
(x1, y1) = (0, 0)
(x2, y2) = (0, -screenHeight)
allsprites = pygame.sprite.Group()
clock = pygame.time.Clock()

def adjust_to_correct_appdir():
    try:
        appdir = sys.argv[0] #feel free to use __file__
        if not appdir:
            raise ValueError
        appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(appdir)
        if not appdir in sys.path:
            sys.path.insert(0,appdir)
    except:
        #placeholder for feedback, adjust to your app.
        #remember to use only python and python standard libraries
        #not any resource or module into the appdir 
        #a window in Tkinter can be adequate for apps without console
        #a simple print with a timeout can be enough for console apps
        print 'Please run from an OS console.'
        import time
        time.sleep(10)
        sys.exit(1)
adjust_to_correct_appdir()

def load_sound(file, name):
    sound = pygame.mixer.Sound(file)
    sounds[name] = sound
    
def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha == True:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0,0))
        new_image.set_colorkey(colorkey, RLEACCEL)
    images[name] = new_image
    
def displayCaption():
    pygame.display.set_caption("Fish Food")

def quit():
    print 'Thanks for playing'
    sys.exit()

def startplaceholder(screen):
    global menuOn, keys
    Rooms = []
    Rooms.append(Room())
    SCORE = 0
    menuOn = 0
    keys = [False, False, False, False]
    pass

def infoplaceholder(screen):
    global menuOn
    menuOn = 4
    pass

class Menu(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = startMenu
        self.menu = genmenu(['START', lambda: startplaceholder(screen)],['INFO', lambda: infoplaceholder(screen)], ['QUIT', lambda: quit()])
        self.menu.changeFont('oceanfont.ttf',28)
        self.menu.position(430,190)
        self.menu.defaultColor((0,0,0))
        self.menu.choiceColor((255,255,255))
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.menu.create(self.screen)
        self.menu.choose(event)
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 1:
            self.clock.tick(60)
            events = pygame.event.get()
            self.menu.choose(events)
            self.screen.blit(self.title, (0, 0))
            highScoreText = oceanFontMain.render("High Score: "+str(get_high_score()), 1, (243,189,0))
            self.screen.blit(highScoreText, (550, 240))
            self.menu.create(self.screen)
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                    
class InfoScreen(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = infoScreen
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 4:
            self.clock.tick(60)
            self.screen.blit(self.title, (0, 0))
            events = pygame.event.get()
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        menuOn = 1

class GameOver(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = gameOver
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 2:
            self.clock.tick(60)
            events = pygame.event.get()
            self.screen.blit(self.title, (0, 0))
            scoreGameOverText = arialFont.render("Score: "+str(SCORE), 1, (0,0,0))
            self.screen.blit(scoreGameOverText, (50, 175))
            if(SCORE == get_high_score()):
                highScoreText = oceanFontGameOver.render("High Score!", 1, (0,0,0))
                self.screen.blit(highScoreText, (50, 260))
            else:
                highScoreText = oceanFontGameOver.render("Try Again!", 1, (0,0,0))
                self.screen.blit(highScoreText, (50, 270))
            highScoreText = arialFont.render("Personal Best: "+str(get_high_score()), 1, (0,0,0))
            self.screen.blit(highScoreText, (50, 220))
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        reset()
                        menuOn = 1

def resumeplaceholder(screen):
    global menuOn, keys
    menuOn = 0
    keys = [False, False, False, False]

def mainmenuplaceholder(screen):
    global menuOn
    menuOn = 1
    pass

class PauseScreen(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = bgwater
        self.menu = genmenu(['Resume', lambda: resumeplaceholder(screen)],['End Game', lambda: mainmenuplaceholder(screen)])
        self.menu.changeFont('oceanfont.ttf',28)
        self.menu.position(430,190)
        self.menu.defaultColor((0,0,0))
        self.menu.choiceColor((255,255,255))
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.menu.create(self.screen)
        self.menu.choose(event)
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 3:
            self.clock.tick(60)
            events = pygame.event.get()
            self.menu.choose(events)
            self.screen.blit(self.title, (0, 0))
            self.menu.create(self.screen)
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()

class Wall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_wall"]
        self.rect = self.image.get_rect()
        allsprites.add(self)

class RedFish(pygame.sprite.Sprite):
    def __init__(self, newDNA):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_redfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = random.uniform(0, math.pi*2)
        self.speed = 0
        self.size = 0
        self.image = pygame.transform.smoothscale(self.image, (self.size, self.size))
        self.genes = newDNA
        self.freqTurns = 0
        self.radiusArc = 0
        self.intelligence = 0
        self.change_dir_timer = 0
        self.expressGenes()
    def update(self):
        self.rect.x -= math.sin(self.direction) * self.speed
        self.rect.y -= math.cos(self.direction) * self.speed
        self.change_dir_timer += 1
        self.sharktimer += 1
        if(self.direction < math.pi):
            self.image = pygame.transform.flip(images["spr_redfish"], 1, 0)
        else:
            self.image = images["spr_redfish"]
        if(self.change_dir_timer > random.randrange(2000,3000)):
            self.direction = random.uniform(0, math.pi*2)
            self.change_dir_timer = 0
            
    def collision_with_wall(self, wall):
        self.change_dir_timer = 0
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32: #left walls
                self.rect.left = 32
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top > screenHeight-64: #bottom walls,
                self.rect.top = screenHeight-64
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.right > screenWidth-32: #right walls
                self.rect.right = screenWidth-32
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top < 32: #top walls
                self.rect.top = 32
                self.direction = random.uniform(0, math.pi*2)
    def drawCircleArc(self,screen,center,radius,startDeg,endDeg):
        (x,y) = center
        rect = (x-radius,y-radius,radius*2,radius*2)
        startRad = degreesToRadians(startDeg)
        endRad = degreesToRadians(endDeg)
        color = (255, 0, 0)
   
        arcPos = pygame.draw.arc(screen,color,rect,startRad,endRad, 20)
        linePos = pygame.draw.line(screen, color, (center[0],center[1]-radius), (center[0],center[1]+radius))
        for shark in sharks:
            if (arcPos.colliderect(shark) or linePos.colliderect(shark)):
                self.change_dir_timer = 0
                self.direction = shark.direction-math.pi/2
    def expressGenes(self):
        self.expressSize()
        self.expressSpeed()
        self.expressFreqTurns()
        self.expressRadiusArc()
        self.expressIntelligence()
    def expressSize(self):
        gene0to4 = self.genes.getGene(0) + self.genes.getGene(1) + self.genes.getGene(2) + self.genes.getGene(3) + self.genes.getGene(4)
        self.size = int(gene0to4, 2)
    def expressSpeed(self):
        gene5to7 = self.genes.getGene(5) + self.genes.getGene(6) + self.genes.getGene(7)
        self.speed = int(gene5to8, 2)
    def expressFreqTurns(self):
        gene8to11 = self.genes.getGene(8) + self.genes.getGene(9) + self.genes.getGene(10) + self.genes.getGene(11)
        self.freqTurns = int(gene9to12, 2)
    def expressRadiusArc(self):
        gene12to16 = self.genes.getGene(12) + self.genes.getGene(13) + self.genes.getGene(14)+self.genes.getGene(15) + self.genes.getGene(16)
        self.radiusArc = 1 + int(gene13to17, 2)
    def expressIntelligence(self):
        gene17to21 = self.genes.getGene(17) + self.genes.getGene(18) + self.genes.getGene(19)+self.genes.getGene(20) + self.genes.getGene(21)
        self.intelligence = 1 + int(gene17to21, 2)
        
class Shark(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_shark"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = random.uniform(0, math.pi*2)
        self.speed = 3
    def update(self):
        if(self.rect.topleft[1] < 0):
                self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1]+3)
        else:
            self.rect.x -= math.sin(self.direction) * self.speed
            self.rect.y -= math.cos(self.direction) * self.speed
    def collision_with_wall(self, wall):
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32: #left walls
                self.rect.left = 32
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top > screenHeight-64: #bottom walls,
                self.rect.top = screenHeight-64
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.right > screenWidth-32: #right walls
                self.rect.right = screenWidth-32
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top < 32: #top walls
                self.rect.top = 32
                self.direction = random.uniform(0, math.pi*2)

class Room():
    def __init__(self):
        generation = -1
        #Adjust the range depending on the size of the screen!
        for x in range(38):
            wall = Wall()
            wall.rect.topleft = (x*32,0) #top walls
            walls.append(wall)
        for x in range(38):
            wall = Wall()
            wall.rect.topleft = (x*32,screenHeight-32) #bottom walls
            walls.append(wall)
        for y in range(23):
            wall = Wall()
            wall.rect.topleft = (0, (y*32)+32) #left walls
            walls.append(wall)
        for y in range(23):
            wall = Wall()
            wall.rect.topleft = (screenWidth-32, (y*32)+32) #right walls
            walls.append(wall)
        reset()
        powerUpReset()

def powerUpReset():
    global SCORE
    SCORE = 0

def reset():
    global SCORE, scoreBlit, scoreDisappearTimer
    SCORE, scoreBlit, scoreDisappearTimer = 0, 0, 0
    keys = [False, False, False, False]
    for redFish in redfishes:
        redFish.rect.topleft = (random.randrange(100, screenWidth-100), screenHeight-100)
    sharks[0].rect.topleft = (random.randrange(100, screenWidth-100), 100)
    sharks[1].rect.topleft = (random.randrange(100, screenWidth-100), 100)
    sharks[2].rect.topleft = (random.randrange(100, screenWidth-100), 100)
    sharks[3].rect.topleft = (random.randrange(100, screenWidth-100), 100)
    generation += 1
    
def get_high_score():
    #Default high score
    high_score = 0
    #Try to read the high score from a file
    try:
        high_score_file = open("high_score.txt", "r")
        high_score = int(high_score_file.read())
        high_score_file.close()
    except IOError:
        #Error reading file, no high score
        pass
    except ValueError:
        #There's a file there, but we don't understand the number.
        print("Error Reading High Score. Please delete high_score.txt in the game folder.")
    return high_score
    
def save_high_score(new_high_score):
    try:
        # Write the file to disk
        high_score_file = open("high_score.txt", "w")
        high_score_file.write(str(new_high_score))
        high_score_file.close()
    except IOError:
        pass
    #Try to read the high score from a file
    try:
        high_score_file = open("high_score.txt", "r")
        high_score = int(high_score_file.read())
        high_score_file.close()
    except IOError:
        #No high score yet
        print("There is no high score yet.")
    except ValueError:
        #Bad number formatting in file
        print("Error Reading High Score. Please delete high_score.txt in the game folder.")
    return high_score

#Init
pygame.init()

def degreesToRadians(deg):
    return deg/180.0 * math.pi


    
    
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Fish Food")
spr_wall = load_image("sprites/wall.bmp", "spr_wall", True, True)
#player sprites
player_left = load_image("sprites/Player_left.png", "player_left", True, True)
player_downright = load_image("sprites/Player_downright.png", "player_downright", True, True)
player_down = load_image("sprites/Player_down.png", "player_down", True, True)
#other fish sprites
spr_redfish = load_image("sprites/redfish.png", "spr_redfish", True, True)
redfishes = [ RedFish() for i in range(10)]
spr_shark = load_image("sprites/shark.png", "spr_shark", True, True)
sharks = [ Shark() for i in range(4)]
arrow_warning_red = load_image("sprites/arrowwarningred.png", "arrow_warning_red", True, True)
arrow_warning_silver = load_image("sprites/arrowwarningsilver.png", "arrow_warning_silver", True, True)
arrow_warning_blue = load_image("sprites/arrowwarningblue.png", "arrow_warning_blue", True, True)
spr_seaweed = load_image("sprites/seaweed.png", "spr_seaweed", True, True)
#font and texts
oceanFont = pygame.font.Font("fonts/oceanfont.ttf", 16)
oceanFontMain = pygame.font.Font("fonts/oceanfont.ttf", 48)
oceanFontGameOver = pygame.font.Font("fonts/oceanfont.ttf", 76)
arialFont = pygame.font.SysFont('Arial', 32)
#backgrounds
startMenu = pygame.image.load("sprites/startmenu.png").convert()
startMenu = pygame.transform.scale(startMenu, (screenWidth, screenHeight))
infoScreen = pygame.image.load("sprites/infoscreen.bmp").convert()
infoScreen = pygame.transform.scale(infoScreen, (screenWidth, screenHeight))
gameOver = pygame.image.load("sprites/gameover.png").convert()
gameOver = pygame.transform.scale(gameOver, (screenWidth, screenHeight))
ground = pygame.image.load("sprites/ground.bmp").convert()
ground = pygame.transform.scale(ground, (screenWidth, 100))
bgwater = pygame.image.load("sprites/background.bmp").convert()
bgwater = pygame.transform.scale(bgwater, (screenWidth, screenHeight))
blackbg = pygame.image.load("sprites/blackbg.jpg").convert()
blackbg = pygame.transform.scale(blackbg, (screenWidth, 30))
#window
gameicon = pygame.image.load("sprites/redfishico.png")
pygame.display.set_icon(gameicon)
pygame.display.set_caption('Fish Food')
pygame.mouse.set_visible(0)
#sounds
snd_eat = load_sound("sounds/snd_eat.wav", "snd_eat")
sounds["snd_eat"].set_volume(.2)
snd_eatshark = load_sound("sounds/eatshark.wav", "snd_eatshark")
sounds["snd_eatshark"].set_volume(.2)
snd_sizedown = load_sound("sounds/sizedown.wav", "snd_sizedown")
snd_playerdie = load_sound("sounds/playerdie.wav", "snd_playerdie")
sounds["snd_playerdie"].set_volume(.3)
snd_siren = load_sound("sounds/siren.wav", "snd_siren")
sounds["snd_siren"].set_volume(.15)
snd_sharkincoming = load_sound("sounds/sharkincoming.wav", "snd_sharkincoming")
sounds["snd_sharkincoming"].set_volume(.05)
#music loop
pygame.mixer.music.load("sounds/gamemusic.mp3")
pygame.mixer.music.set_volume(.2)
pygame.mixer.music.play(-1)
#Main
while running:
    if(firstMessage == 1):
        print "Please ignore the errors."
        firstMessage = 0
    clock.tick(60)
    displayCaption()
    if menuOn == 1: #Menu Screen
        Menu(screen)
        SCORE = 0     
    elif menuOn == 2: #Gameover Screen
        high_score = get_high_score()
        if SCORE > high_score:
            save_high_score(SCORE)
        sounds["snd_playerdie"].play()
        GameOver(screen)
    elif menuOn == 3:
        PauseScreen(screen)
    elif menuOn == 4:
        InfoScreen(screen)
    if(scoreBlit > 0): #Score Timer above player sprite
        scoreDisappearTimer += 1
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                for i in range(0, len(sounds)):
                    soundslist = sounds.keys() #returns list of keys in sounds
                    sounds[soundslist[i]].stop() #stops all sounds when go to menu
                menuOn = 3
    allsprites.update()
    #water background movement
    y1 += 10
    y2 += 10
    screen.blit(bgwater, (x1,y1))
    screen.blit(bgwater, (x2,y2))
    if y2 > screenHeight:
        y2 = -screenHeight
    if y1 > screenHeight:
        y1 = -screenHeight
    screen.blit(ground, (0,screenHeight-100))
    #Arrow Warnings
    if (SCORE >= 20 and SCORE < 25) or (SCORE >= 25 and sharks[1].rect.topleft[1] < 0):
        screen.blit(images["arrow_warning_silver"], (sharks[1].rect.topleft[0], 40))
    if (SCORE >= 45 and SCORE < 50) or (SCORE >= 50 and sharks[2].rect.topleft[1] < 0):
        screen.blit(images["arrow_warning_silver"], (sharks[2].rect.topleft[0], 40))
    if (SCORE >= 70 and SCORE < 75) or (SCORE >= 75 and sharks[3].rect.topleft[1] < 0):
        screen.blit(images["arrow_warning_silver"], (sharks[3].rect.topleft[0], 40))
    allsprites.draw(screen)
    screen.blit(blackbg, (0,0))
    #Seaweed
    for i in range(5,screenWidth-15,60):
        screen.blit(images["spr_seaweed"], (i, screenHeight-130)) #top seaweed
    for i in range(5,screenWidth-15,60):
        screen.blit(images["spr_seaweed"], (i, screenHeight-80))
    
    #Menu Design
    menuText = oceanFont.render("Menu:", 1, (255,255,255))
    screen.blit(menuText, (10, 5))
    screen.blit(images["spr_redfish"], (65, 11))
    screen.blit(oceanFont.render("", 1, (0,0,0)), (220,7))
    #Font On Top
    scoreText = oceanFont.render("Score: "+str(SCORE), 1, (255,255,255))
    screen.blit(scoreText, ((screenWidth/2)-32, 5))
    for redFish in redfishes:
        for shark in sharks:
            if pygame.sprite.collide_mask(redFish, shark):
                redFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
                #sounds["snd_eat"].play()
                scoreBlit = 1
                SCORE += 1
            if redFish.direction > math.pi:
                redFish.drawCircleArc(screen,(redFish.rect.centerx, redFish.rect.centery),50,-90,90)
            else:
                redFish.drawCircleArc(screen,(redFish.rect.centerx, redFish.rect.centery),50,90,270)
        for wall in walls:
            if redFish.rect.colliderect(wall.rect):
                redFish.collision_with_wall(wall)
    for shark in sharks:
        for wall in walls:
            if shark.rect.colliderect(wall.rect):
                shark.collision_with_wall(wall)
                break
    #Test Print Code: FOR DEBUGGING PURPOSES BELOW:
    
    #Top Screen Design
    if(scoreBlit == 0):
        scoreBlitText = oceanFont.render("", 1, (255,255,255))
    else:
        scoreBlitText = oceanFont.render("+" + str(scoreBlit), 1, (255,255,255))
        if(scoreDisappearTimer > 10):
            scoreBlit = 0
            scoreDisappearTimer = 0
    
    pygame.display.flip()
    pygame.display.update()