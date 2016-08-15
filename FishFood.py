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
POPSIZE=20
NUMGENES = 22
scoreBlit = 0
highScore = 0
bestGeneration = 0
fps = 60
screen = None
walls = []
eliteCloneList = []
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
    pygame.display.set_caption("Genetic Algorithm Fish Simulation")

def quit():
    print 'Thanks for playing'
    sys.exit()

def startplaceholder(screen):
    global menuOn, keys
    Rooms = []
    Rooms.append(Room())
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
            self.clock.tick(fps)
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
            if(highScore == get_high_score()):
                highScoreText = oceanFontGameOver.render("High Score!", 1, (0,0,0))
                self.screen.blit(highScoreText, (50, 260))
            else:
                highScoreText = oceanFontGameOver.render("Try Again!", 1, (0,0,0))
                self.screen.blit(highScoreText, (50, 270))
            highScoreText = arialFont.render("Personal Best: "+str(get_high_score()), 1, (0,0,0))
            self.screen.blit(highScoreText, (50, 220))
            bestGenText = arialFont.render("Best Generation For This Population Breeding: "+str(bestGeneration), 1, (0,0,0))
            self.screen.blit(bestGenText, (50, 360))
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

def getNextPop(candidates, sizeOfNextPop):

    sumFitness = 0
    #Initialize an array that will hold the probabilities of each candidate being chosen
    candidateProbs = ['' for i in range(len(candidates))]
    #Loop through all the candidates and compute the sum of all of their fitness scores
    for c in range(len(candidates)):
        sumFitness += float(candidates[c][1])
        #Store the fitness of each candidate in the probability array for now
        candidateProbs[c] = (c, candidates[c][1])

    for i in range(len(candidateProbs)):
        #Divide each candidates fitness by the sum of all the fitnesses to determine its proportion
        candidateProbs[i] = (i, (candidateProbs[i][1]/sumFitness)*100)

    prevBoundry = 0.0
    #Set up an array to hold the "boundrys" for each candidate,
    # which are proportionate based on the individuals fitness
    candidateBoundrys = [(0, 0, 0) for i in range(len(candidateProbs))]
    b = 0
    for p in candidateProbs:
        #Give each candidate a range, based on its proportion, and the end of the last boundry
        candidateBoundrys[b] = (p[0], prevBoundry, float(prevBoundry+p[1]))
        prevBoundry = candidateBoundrys[b][2]
        b += 1

    #Create an empty array to hold the next population
    nextPop = []
    #We will need n/2 sets of parents, where n is the size of the population we want
    for counter in range((int(math.ceil(sizeOfNextPop/2)))):
        parentA = None
        parentB = None
        #While we still need to select a parent A

        #Will be used to store parent A to be reintroduced after parentB is chosen
        parentATemp = None
        while parentA is None:

            #Pick a random number (1-100, scaled up by 100)
            nextMate = random.randrange(100.0, 10000.0)/100.0
            #Look through all of the boundries
            for a in candidateBoundrys:
                #Select the candidate whose boundry contains the selected random value
                if a[1] < nextMate < a[2]:
                    #Set that candidate to be Parent A
                    parentA = candidates[a[0]][0]
                    #Remove that candidate from the list
                    parentATemp = a
                    candidateBoundrys.remove(a)
        #While we still need to select a parent B
        while parentB is None:
            #If there's only one candidate left, just use that one, no need to randomly select
            if len(candidateBoundrys) == 1:
                b = candidateBoundrys.pop()
                #Set that candidate to be Parent B
                parentB = candidates[b[0]][0]
            else:
                #Pick a random number (1-100, scaled up by 100)
                nextMate = random.randrange(100.0, 10000.0)/100.0
                #Look through all of the boundries
                for b in candidateBoundrys:
                    #Select the candidate whose boundry contains the selected random value
                    if b[1] < nextMate < b[2]:
                        #Set that candidate to be Parent B, and remove the candidate from the list
                        parentB = candidates[b[0]][0]
                        #candidateBoundrys.remove(b)
        candidateBoundrys.append(parentATemp)
        #Using the two parents , create two children DNA using crossover
        childADNA, childBDNA = crossover(parentA, parentB, len(parentA.genes.dna))
        #Mutate the DNA of each child
        childADNA = mutate(childADNA)
        childBDNA = mutate(childBDNA)
        #Add the children DNA to the next population
        nextPop.append(childADNA)
        nextPop.append(childBDNA)
    #Return the population
    return nextPop

#Given two parent Organisms and the length of those parents DNA, generate two children
def crossover(parentA, parentB, numGenes):
    #Initialize two empty strings for the children
    childADNA = ""
    childBDNA = ""
    #For the length of the genotype
    for thisGene in range(numGenes):
        #Randomly pick to use either Parent A or Parent B
        if random.randint(0, 1) == 0:
            #If child A gets gene from Parent A, child B gets gene from Parent B
            childADNA += parentA.genes.getGene(thisGene)
            childBDNA += parentB.genes.getGene(thisGene)
        else:
            #If child A gets gene from Parent B, child B gets gene from Parent A
            childADNA += parentB.genes.getGene(thisGene)
            childBDNA += parentA.genes.getGene(thisGene)
    #Return the created DNA strings
    return childADNA, childBDNA

#Given a string containing a genotype, perform some mutations
def mutate(genes):

    newGenes = ""
    #For each gene in the genotype
    for g in range(len(genes)):
        gene = genes[g]
        #Use a 5% chance of mutating. If we decide to mutate this gene, reverse it's value
        if random.randrange(0, 100) < 5:
            if gene == "0":
                newGenes += "1"
            else:
                newGenes += "0"
        #Otherwise, leave it unchanged
        else:
            newGenes += gene
    #Return the new genotype
    return newGenes

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
        self.direction = random.uniform(0, math.pi*2)
        self.speed = 0
        self.size = 0
        self.genes = newDNA
        self.eliteclone = 0
        for i in eliteCloneList:
            if(self.genes.getGenotypeString() == i):
                self.eliteclone = 1
        self.freqTurns = 0
        self.radiusArc = 0
        self.intelligence = 0
        self.change_dir_timer = 0
        self.expressGenes()
        self.image = pygame.transform.smoothscale(images["spr_redfish"], (self.size+5, self.size))
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.health = 1
        self.arcIndex = 0
        self.sharkList = []
    def update(self):
        global arcsList
        if(self.health == 1):
            self.rect.x -= math.sin(self.direction) * self.speed
            self.rect.y -= math.cos(self.direction) * self.speed
            self.change_dir_timer += 1
            if(self.direction < math.pi): #fish facing left
                if(self.eliteclone == 0):
                    self.image = pygame.transform.smoothscale(images["spr_redfishleft"], (self.size+5, self.size))
                else:
                    self.image = pygame.transform.smoothscale(images["spr_elitecloneleft"], (self.size+5, self.size))
                arcsList[self.arcIndex].image = pygame.transform.scale(images["spr_arcleft"], (self.radiusArc*3, self.radiusArc*3))
                arcsList[self.arcIndex].rect = arcsList[self.arcIndex].image.get_rect()
                arcsList[self.arcIndex].rect.right = self.rect.left
                arcsList[self.arcIndex].rect.centery = self.rect.center[1]
            else: #fish facing right
                if(self.eliteclone == 0):
                    self.image = pygame.transform.smoothscale(images["spr_redfish"], (self.size+5, self.size))
                else:
                    self.image = pygame.transform.smoothscale(images["spr_eliteclone"], (self.size+5, self.size))
                arcsList[self.arcIndex].image = pygame.transform.scale(images["spr_arc"], (self.radiusArc*3, self.radiusArc*3))
                arcsList[self.arcIndex].rect = arcsList[self.arcIndex].image.get_rect()
                arcsList[self.arcIndex].rect.left = self.rect.right
                arcsList[self.arcIndex].rect.centery = self.rect.centery
            shark_collisions = 0
            for shark in sharks:
                if pygame.sprite.collide_mask(arcsList[self.arcIndex], shark):
                    if shark not in self.sharkList:
                        self.sharkList.append(shark)
                        temp = random.randrange(0,32)
                        if (temp < self.intelligence):
                            self.direction = self.direction*-1
                            self.change_dir_timer = 0
                            break
                else:
                    if shark in self.sharkList:
                        self.sharkList.remove(shark)
            if(self.change_dir_timer > 20*self.freqTurns):
                self.direction = random.uniform(0, math.pi*2)
                self.change_dir_timer = 0
        else:
            self.kill()
            
    def collision_with_wall(self, wall):
        self.change_dir_timer = 0
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32+self.size: #left walls
                self.rect.left = 32+self.size
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top > screenHeight-64-self.size: #bottom walls,
                self.rect.top = screenHeight-64-self.size
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.right > screenWidth-32-self.size: #right walls
                self.rect.right = screenWidth-32-self.size
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top < 32+self.size: #top walls
                self.rect.top = 32+self.size
                self.direction = random.uniform(0, math.pi*2)
    def expressGenes(self):
        self.expressSize()
        self.expressSpeed()
        self.expressFreqTurns()
        self.expressRadiusArc()
        self.expressIntelligence()
    def expressSize(self):
        gene0to4 = self.genes.getGene(0) + self.genes.getGene(1) + self.genes.getGene(2) + self.genes.getGene(3) + self.genes.getGene(4)
        self.size = 6 + int(gene0to4, 2)
    def expressSpeed(self):
        gene5to8 = self.genes.getGene(5) + self.genes.getGene(6) + self.genes.getGene(7)
        self.speed = 2 + int(gene5to8, 2)
    def expressFreqTurns(self):
        gene9to12 = self.genes.getGene(8) + self.genes.getGene(9) + self.genes.getGene(10) + self.genes.getGene(11)
        self.freqTurns = 1+int(gene9to12, 2)
    def expressRadiusArc(self):
        gene13to16 = self.genes.getGene(12) + self.genes.getGene(13) + self.genes.getGene(14)+self.genes.getGene(15) + self.genes.getGene(16)
        self.radiusArc = 1 + int(gene13to16, 2)
    def expressIntelligence(self):
        gene17to21 = self.genes.getGene(17) + self.genes.getGene(18) + self.genes.getGene(19)+self.genes.getGene(20) + self.genes.getGene(21)
        self.intelligence = 1 + int(gene17to21, 2)
    def stillAlive(self):
        #If the Organisms health is 0 or lower, then it is dead
        if self.health == 0:
            return False
        else:
            return True
        
class Arc(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_arc"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.destroy = 0
    def update(self):
        if self.destroy == 1:
            self.kill()

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
            elif self.rect.top < 20: #top walls
                self.rect.top = 32
                self.direction = random.uniform(0, math.pi*2)

class Room():
    def __init__(self):
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

def reset():
    for i in range(0,len(redfishes)):
        redfishes.sprites()[i].rect.topleft = (random.randrange(300, screenWidth-300), random.randrange(100, screenHeight-100))
    for i in range(0,len(sharks)):
        if i<=len(sharks)/2:
            sharks[i].rect.topleft = (100, random.randrange(100, screenHeight-100))
        else:
            sharks[i].rect.topleft = (screenWidth-100, random.randrange(100, screenHeight-100))

    
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

nextPopDNA = []
score = 0
generation=0
#Init
pygame.init()


def degreesToRadians(deg):
    return deg/180.0 * math.pi


    
    
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Fish Food")
spr_wall = load_image("sprites/wall.bmp", "spr_wall", True, False)
#player sprites
player_left = load_image("sprites/Player_left.png", "player_left", True, True)
player_downright = load_image("sprites/Player_downright.png", "player_downright", True, True)
player_down = load_image("sprites/Player_down.png", "player_down", True, True)
#other fish sprites
spr_redfish = load_image("sprites/redfish.png", "spr_redfish", True, True)
spr_redfishleft = load_image("sprites/redfishleft.png", "spr_redfishleft", True, True)
spr_eliteclone = load_image("sprites/eliteclone.png", "spr_eliteclone", True, True)
spr_elitecloneleft = load_image("sprites/elitecloneleft.png", "spr_elitecloneleft", True, True)
spr_arc = load_image("sprites/arc.png", "spr_arc", True, True)
spr_arcleft = load_image("sprites/arcleft.png", "spr_arcleft", True, True)
spr_shark = load_image("sprites/shark.png", "spr_shark", True, True)
sharks = [ Shark() for i in range(8)]
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
#pygame.mixer.music.load("sounds/gamemusic.mp3")
#pygame.mixer.music.set_volume(.2)
#pygame.mixer.music.play(-1)
#Main

deadList = []
redfishes = pygame.sprite.Group()
arcsList = []
#Create a list of POPSIZE Organisms, all with random DNA, and at random locations
for countOrganism in range(POPSIZE):
    d = DNA.DNA(NUMGENES, None)
    o = RedFish(d)
    #Sets the Organisms Sprite location to match its decided location

    redfishes.add(o)
    arcsList.append(Arc())
#Subsequent generations will be created using crossover and mutation
for i in range(0,len(arcsList)):
    redfishes.sprites()[i].arcIndex = i

while running:
    if(firstMessage == 1):
        print "Please ignore the errors."
        firstMessage = 0
    clock.tick(60)
    displayCaption()
    if menuOn == 1: #Menu Screen
        Menu(screen)
    elif menuOn == 2: #Gameover Screen
        high_score = get_high_score()
        if highScore > high_score:
            save_high_score(highScore)
        GameOver(screen)
        nextPopDNA = []
        score = 0
        generation=0
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
            elif event.key==K_TAB:
                menuOn = 2
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
    allsprites.draw(screen)
    screen.blit(blackbg, (0,0))
    #Seaweed
    for i in range(5,screenWidth-15,60):
        screen.blit(images["spr_seaweed"], (i, screenHeight-130)) #top seaweed
    for i in range(5,screenWidth-15,60):
        screen.blit(images["spr_seaweed"], (i, screenHeight-80))
    
    #Font On Top
    scoreText = oceanFont.render("Fitness: "+str(score), 1, (255,255,255))
    screen.blit(scoreText, ((screenWidth/2)+300, 5))
    generationText = oceanFont.render("Generation: "+str(generation), 1, (255,255,255))
    screen.blit(generationText, ((screenWidth/2)+100, 5))
    highScoreText = oceanFont.render("Highest Avg Score: "+str(highScore), 1, (255,255,255))
    screen.blit(highScoreText, ((screenWidth/2)-200, 5))
    bestGenerationText = oceanFont.render("Best Generation: "+str(bestGeneration), 1, (255,255,255))
    screen.blit(bestGenerationText, ((screenWidth/2)-400, 5))
    for redFish in redfishes:
        for shark in sharks:
            if pygame.sprite.collide_mask(redFish, shark):
                redFish.health = 0
        for wall in walls:
            if redFish.rect.colliderect(wall.rect):
                redFish.collision_with_wall(wall)
    for shark in sharks:
        for wall in walls:
            if shark.rect.colliderect(wall.rect):
                shark.collision_with_wall(wall)
                break
            
        #Compute game logic
        #If there are no more living Organisms, the generation is over
        #Compute statistics and generate DNA for next generation
        if len(redfishes) == 0:
            #Sort the list of dead organisms by their score
            deadList.sort(key=lambda item: item[1])
            #Pass the list of dead organisms to be used for deciding the next generation
            nextPopDNA = getNextPop(deadList, (POPSIZE-2))
            #Print some helpful information for watching the DNA change each generation
            print "Top 50% for generation " + str(generation+1)
            print "Size | Speed | FreqTurns | RadiusArc | Intelligence | Score"
            sumScores = 0
            #Print the genotypes of the top 50% of this generation and their scores
            for n in range(int(len(deadList)*0.5)):
                temp = deadList[-(n+1)]
                sumScores += temp[1]

                print temp[0].genes.getGenotype() + " " + str(temp[1])

            #Print the average score for this generation
            print "Avg score: " + str(sumScores/float(len(deadList)))
            print ""
            avgScore = sumScores/float(len(deadList))
            if avgScore > highScore:
                highScore = int(avgScore)
                bestGeneration = generation

            #Take the top 2 performing Organisms from this generation and add them to the next population
            eliteCloneList = [deadList[-1][0].genes.getGenotypeString(), deadList[-2][0].genes.getGenotypeString()]
            nextPopDNA.append(deadList[-1][0].genes.getGenotypeString())
            nextPopDNA.append(deadList[-2][0].genes.getGenotypeString())
            #Set flag to end game loop
            #Create a new list of Organisms, using the generated DNA, all at random locations
            arcsList = []
            redfishes = pygame.sprite.Group()
            for genes in nextPopDNA:
                d = DNA.DNA(NUMGENES, genes)
                o = RedFish(d)
                redfishes.add(o)
                arcsList.append(Arc())
            for i in range(0,POPSIZE):
                redfishes.sprites()[i].arcIndex = i
            #Clear the list for the next generation
            nextPopDNA = []

            generation += 1
            reset()
            deadList = []
            score = 0
        #Increase score by 1
        score += 1
        #For each Organism that's still alive
        for redFish in redfishes:
            #Check if it is still alive
            if not redFish.stillAlive():
                #If not, remove it from the list, and add it to the list of dead Organisms
                redfishes.remove(redFish)
                deadList.append((redFish, score))
                arcsList[redFish.arcIndex].destroy = 1
                
    #Test Print Code: FOR DEBUGGING PURPOSES BELOW:
    
    
    pygame.display.flip()
    pygame.display.update()