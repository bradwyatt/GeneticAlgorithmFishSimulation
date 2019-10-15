"""
PyWorld code includes: get_next_pop, crossover, mutate functions and DNA module
"""
import random
import sys
import math
import os
import pygame
import DNA

RUNNING = True #Flags game as on
(SCREEN_WIDTH, SCREEN_HEIGHT) = 1200, 800
POPSIZE = 20
NUMGENES = 22
HIGHSCORE = 0
BEST_GENERATION = 0
SCREEN = None
WALLS = []
ELITECLONE_LIST = []
IMAGES = {}
(X_FIRST, Y_FIRST) = (0, 0)
(X_SECOND, Y_SECOND) = (0, -SCREEN_HEIGHT)
ALL_SPRITES = pygame.sprite.Group()
CLOCK = pygame.time.Clock()

def adjust_to_correct_appdir():
    try:
        appdir = sys.argv[0] #feel free to use __file__
        if not appdir:
            raise ValueError
        appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(appdir)
        if not appdir in sys.path:
            sys.path.insert(0, appdir)
    except:
        #placeholder for feedback, adjust to your app.
        #remember to use only python and python standard libraries
        #not any resource or module into the appdir 
        #a window in Tkinter can be adequate for apps without console
        #a simple print with a timeout can be enough for console apps
        print('Please run from an OS console.')
        import time
        time.sleep(10)
        sys.exit(1)
adjust_to_correct_appdir()

def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0, 0))
        new_image.set_colorkey(colorkey, pygame.RLEACCEL)
    IMAGES[name] = new_image

def display_caption():
    pygame.display.set_caption("Genetic Algorithm Simulation")

def get_next_pop(candidates, size_of_next_pop):
    sum_fitness = 0
    #Initialize an array that will hold the probabilities of each candidate being chosen
    candidate_probs = ['' for i in range(len(candidates))]
    #Loop through all the candidates and compute the sum of all of their fitness SCOREs
    for c in range(len(candidates)):
        sum_fitness += float(candidates[c][1])
        #Store the fitness of each candidate in the probability array for now
        candidate_probs[c] = (c, candidates[c][1])

    for i in range(len(candidate_probs)):
        #Divide each candidates fitness by the sum of all the fitnesses to determine its proportion
        candidate_probs[i] = (i, (candidate_probs[i][1]/sum_fitness)*100)

    prev_boundry = 0.0
    #Set up an array to hold the "boundrys" for each candidate,
    # which are proportionate based on the individuals fitness
    candidate_boundaries = [(0, 0, 0) for i in range(len(candidate_probs))]
    b = 0
    for p in candidate_probs:
        #Give each candidate a range, based on its proportion, and the end of the last boundry
        candidate_boundaries[b] = (p[0], prev_boundry, float(prev_boundry+p[1]))
        prev_boundry = candidate_boundaries[b][2]
        b += 1

    #Create an empty array to hold the next population
    next_pop = []
    #We will need n/2 sets of parents, where n is the size of the population we want
    for _ in range((int(math.ceil(size_of_next_pop/2)))):
        parent_a = None
        parent_b = None

        #Will be used to store parent A to be reintroduced after parent_b is chosen
        parent_a_temp = None
        while parent_a is None:

            #Pick a random number (1-100, scaled up by 100)
            next_mate = random.randrange(100.0, 10000.0)/100.0
            #Look through all of the boundries
            for a in candidate_boundaries:
                #Select the candidate whose boundry contains the selected random value
                if a[1] < next_mate < a[2]:
                    #Set that candidate to be Parent A
                    parent_a = candidates[a[0]][0]
                    #Remove that candidate from the list
                    parent_a_temp = a
                    candidate_boundaries.remove(a)
        #While we still need to select a parent B
        while parent_b is None:
            #If there's only one candidate left, just use that one, no need to randomly select
            if len(candidate_boundaries) == 1:
                b = candidate_boundaries.pop()
                #Set that candidate to be Parent B
                parent_b = candidates[b[0]][0]
            else:
                #Pick a random number (1-100, scaled up by 100)
                next_mate = random.randrange(100.0, 10000.0)/100.0
                #Look through all of the boundries
                for b in candidate_boundaries:
                    #Select the candidate whose boundry contains the selected random value
                    if b[1] < next_mate < b[2]:
                        #Set that candidate to be Parent B, and remove the candidate from the list
                        parent_b = candidates[b[0]][0]
                        #candidate_boundaries.remove(b)
        candidate_boundaries.append(parent_a_temp)
        #Using the two parents , create two children DNA using crossover
        child_a_dna, child_b_dna = crossover(parent_a, parent_b, len(parent_a.genes.dna))
        #Mutate the DNA of each child
        child_a_dna = mutate(child_a_dna)
        child_b_dna = mutate(child_b_dna)
        #Add the children DNA to the next population
        next_pop.append(child_a_dna)
        next_pop.append(child_b_dna)
    #Return the population
    return next_pop

#Given two parent Organisms and the length of those parents DNA, generate two children
def crossover(parent_a, parent_b, num_genes):
    #Initialize two empty strings for the children
    child_a_dna = ""
    child_b_dna = ""
    #For the length of the genotype
    for this_gene in range(num_genes):
        #Randomly pick to use either Parent A or Parent B
        if random.randint(0, 1) == 0:
            #If child A gets gene from Parent A, child B gets gene from Parent B
            child_a_dna += parent_a.genes.getGene(this_gene)
            child_b_dna += parent_b.genes.getGene(this_gene)
        else:
            #If child A gets gene from Parent B, child B gets gene from Parent A
            child_a_dna += parent_b.genes.getGene(this_gene)
            child_b_dna += parent_a.genes.getGene(this_gene)
    #Return the created DNA strings
    return child_a_dna, child_b_dna

#Given a string containing a genotype, perform some mutations
def mutate(genes):
    new_genes = ""
    #For each gene in the genotype
    for g in range(len(genes)):
        gene = genes[g]
        #Use a 5% chance of mutating. If we decide to mutate this gene, reverse it's value
        if random.randrange(0, 100) < 5:
            if gene == "0":
                new_genes += "1"
            else:
                new_genes += "0"
        #Otherwise, leave it unchanged
        else:
            new_genes += gene
    #Return the new genotype
    return new_genes

class Wall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_wall"]
        self.rect = self.image.get_rect()
        ALL_SPRITES.add(self)

class RedFish(pygame.sprite.Sprite):
    def __init__(self, new_dna):
        pygame.sprite.Sprite.__init__(self)
        self.direction = random.uniform(0, math.pi*2)
        self.speed = 0
        self.size = 0
        self.genes = new_dna
        self.eliteclone = 0
        for ec in ELITECLONE_LIST:
            if self.genes.getGenotypeString() == ec:
                self.eliteclone = 1
        self.freq_turns = 0
        self.radius_arc = 0
        self.intelligence = 0
        self.change_dir_timer = 0
        self.express_genes()
        self.image = pygame.transform.smoothscale(IMAGES["spr_redfish"], (self.size+5, self.size))
        self.rect = self.image.get_rect()
        ALL_SPRITES.add(self)
        self.health = 1
        self.arc_index = 0
        self.shark_list = []
    def update(self):
        #global ARCS_LIST
        if self.health == 1:
            self.rect.x -= math.sin(self.direction) * self.speed
            self.rect.y -= math.cos(self.direction) * self.speed
            self.change_dir_timer += 1
            if self.direction < math.pi: #fish facing left
                if self.eliteclone == 0:
                    self.image = pygame.transform.smoothscale(IMAGES["spr_redfishleft"], (self.size+5, self.size))
                else:
                    self.image = pygame.transform.smoothscale(IMAGES["spr_elitecloneleft"], (self.size+5, self.size))
                ARCS_LIST[self.arc_index].image = pygame.transform.scale(IMAGES["spr_arcleft"], (self.radius_arc*3, self.radius_arc*3))
                ARCS_LIST[self.arc_index].rect = ARCS_LIST[self.arc_index].image.get_rect()
                ARCS_LIST[self.arc_index].rect.right = self.rect.left
                ARCS_LIST[self.arc_index].rect.centery = self.rect.center[1]
            else: #fish facing right
                if self.eliteclone == 0:
                    self.image = pygame.transform.smoothscale(IMAGES["spr_redfish"], (self.size+5, self.size))
                else:
                    self.image = pygame.transform.smoothscale(IMAGES["spr_eliteclone"], (self.size+5, self.size))
                ARCS_LIST[self.arc_index].image = pygame.transform.scale(IMAGES["spr_arc"], (self.radius_arc*3, self.radius_arc*3))
                ARCS_LIST[self.arc_index].rect = ARCS_LIST[self.arc_index].image.get_rect()
                ARCS_LIST[self.arc_index].rect.left = self.rect.right
                ARCS_LIST[self.arc_index].rect.centery = self.rect.centery
            for shark in SHARKS:
                if pygame.sprite.collide_mask(ARCS_LIST[self.arc_index], shark):
                    if shark not in self.shark_list:
                        self.shark_list.append(shark)
                        temp = random.randrange(0, 32)
                        if temp < self.intelligence:
                            self.direction = self.direction*-1
                            self.change_dir_timer = 0
                            break
                else:
                    if shark in self.shark_list:
                        self.shark_list.remove(shark)
            if self.change_dir_timer > 20*self.freq_turns:
                self.direction = random.uniform(0, math.pi*2)
                self.change_dir_timer = 0
        else:
            self.kill()
            
    def collision_with_wall(self, wall):
        self.change_dir_timer = 0
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32+self.size: #left WALLS
                self.rect.left = 32+self.size
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top > SCREEN_HEIGHT-64-self.size: #bottom WALLS,
                self.rect.top = SCREEN_HEIGHT-64-self.size
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.right > SCREEN_WIDTH-32-self.size: #right WALLS
                self.rect.right = SCREEN_WIDTH-32-self.size
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top < 32+self.size: #top WALLS
                self.rect.top = 32+self.size
                self.direction = random.uniform(0, math.pi*2)
    def express_genes(self):
        self.express_size()
        self.express_speed()
        self.express_freq_turns()
        self.express_radius_arc()
        self.express_intelligence()
    def express_size(self):
        gene0to4 = self.genes.getGene(0) + self.genes.getGene(1) + self.genes.getGene(2) + self.genes.getGene(3) + self.genes.getGene(4)
        self.size = 6 + int(gene0to4, 2)
    def express_speed(self):
        gene5to8 = self.genes.getGene(5) + self.genes.getGene(6) + self.genes.getGene(7)
        self.speed = 2 + int(gene5to8, 2)
    def express_freq_turns(self):
        gene9to12 = self.genes.getGene(8) + self.genes.getGene(9) + self.genes.getGene(10) + self.genes.getGene(11)
        self.freq_turns = 1+int(gene9to12, 2)
    def express_radius_arc(self):
        gene13to16 = self.genes.getGene(12) + self.genes.getGene(13) + self.genes.getGene(14)+self.genes.getGene(15) + self.genes.getGene(16)
        self.radius_arc = 1 + int(gene13to16, 2)
    def express_intelligence(self):
        gene17to21 = self.genes.getGene(17) + self.genes.getGene(18) + self.genes.getGene(19)+self.genes.getGene(20) + self.genes.getGene(21)
        self.intelligence = 1 + int(gene17to21, 2)
    def still_alive(self):
        # If the Organisms health is 0 or lower, then it is dead
        if self.health == 0:
            return False
        return True
        
class Arc(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_arc"]
        self.rect = self.image.get_rect()
        ALL_SPRITES.add(self)
        self.destroy = 0
    def update(self):
        if self.destroy == 1:
            self.kill()

class Shark(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_shark"]
        self.rect = self.image.get_rect()
        ALL_SPRITES.add(self)
        self.direction = random.uniform(0, math.pi*2)
        self.speed = 3
    def update(self):
        if self.rect.topleft[1] < 0:
            self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1]+3)
        else:
            self.rect.x -= math.sin(self.direction) * self.speed
            self.rect.y -= math.cos(self.direction) * self.speed
    def collision_with_wall(self, wall):
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32: #left WALLS
                self.rect.left = 32
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top > SCREEN_HEIGHT-64: #bottom WALLS,
                self.rect.top = SCREEN_HEIGHT-64
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.right > SCREEN_WIDTH-32: #right WALLS
                self.rect.right = SCREEN_WIDTH-32
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top < 20: #top WALLS
                self.rect.top = 32
                self.direction = random.uniform(0, math.pi*2)

class Room():
    def __init__(self):
        #Adjust the range depending on the size of the SCREEN!
        for x_top in range(38):
            wall = Wall()
            wall.rect.topleft = (x_top*32, 0) #top WALLS
            WALLS.append(wall)
        for x_bottom in range(38):
            wall = Wall()
            wall.rect.topleft = (x_bottom*32, SCREEN_HEIGHT-32) #bottom WALLS
            WALLS.append(wall)
        for y_left in range(23):
            wall = Wall()
            wall.rect.topleft = (0, (y_left*32)+32) #left WALLS
            WALLS.append(wall)
        for y_right in range(23):
            wall = Wall()
            wall.rect.topleft = (SCREEN_WIDTH-32, (y_right*32)+32) #right WALLS
            WALLS.append(wall)
        reset()

def reset():
    for i in range(0, len(REDFISHES)):
        REDFISHES.sprites()[i].rect.topleft = (random.randrange(300, SCREEN_WIDTH-300),
                                               random.randrange(100, SCREEN_HEIGHT-100))
    for i in range(0, len(SHARKS)):
        if i <= len(SHARKS)/2:
            SHARKS[i].rect.topleft = (100, random.randrange(100, SCREEN_HEIGHT-100))
        else:
            SHARKS[i].rect.topleft = (SCREEN_WIDTH-100, random.randrange(100, SCREEN_HEIGHT-100))

NEXT_POP_DNA = []
SCORE = 0
GENERATION = 0
DEAD_LIST = []
REDFISHES = pygame.sprite.Group()
ARCS_LIST = []

#Init
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Fish Food")
load_image("sprites/wall.bmp", "spr_wall", True, False)
load_image("sprites/redfish.png", "spr_redfish", True, True)
load_image("sprites/redfishleft.png", "spr_redfishleft", True, True)
load_image("sprites/eliteclone.png", "spr_eliteclone", True, True)
load_image("sprites/elitecloneleft.png", "spr_elitecloneleft", True, True)
load_image("sprites/arc.png", "spr_arc", True, True)
load_image("sprites/arcleft.png", "spr_arcleft", True, True)
load_image("sprites/shark.png", "spr_shark", True, True)
load_image("sprites/seaweed.png", "spr_seaweed", True, True)
#font and texts
FONT_OCEAN = pygame.font.Font("fonts/oceanfont.ttf", 16)
FONT_ARIAL = pygame.font.SysFont('Arial', 32)
#backgrounds
GROUND = pygame.image.load("sprites/ground.bmp").convert()
GROUND = pygame.transform.scale(GROUND, (SCREEN_WIDTH, 100))
BG_WATER = pygame.image.load("sprites/background.bmp").convert()
BG_WATER = pygame.transform.scale(BG_WATER, (SCREEN_WIDTH, SCREEN_HEIGHT))
BG_BLACK = pygame.image.load("sprites/blackbg.jpg").convert()
BG_BLACK = pygame.transform.scale(BG_BLACK, (SCREEN_WIDTH, 30))
#window
GAME_ICON = pygame.image.load("sprites/redfishico.png")
pygame.display.set_icon(GAME_ICON)
pygame.display.set_caption('Genetic Algorithm Simulation')
pygame.mouse.set_visible(0)

SHARKS = [Shark() for i in range(8)]

#Create a list of POPSIZE Organisms, all with random DNA
#Subsequent generations will be created using crossover and mutation
for count_organism in range(POPSIZE):
    d = DNA.DNA(NUMGENES, None)
    o = RedFish(d)
    #Sets the Organisms Sprite location to match its decided location

    REDFISHES.add(o)
    ARCS_LIST.append(Arc())
for arc in range(0, len(ARCS_LIST)):
    REDFISHES.sprites()[arc].arc_index = arc

ROOMS = Room()

while RUNNING:
    CLOCK.tick(60)
    display_caption()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False
            pygame.quit()
            sys.exit()
    ALL_SPRITES.update()
    # Water background movement
    Y_FIRST += 10
    Y_SECOND += 10
    SCREEN.blit(BG_WATER, (X_FIRST, Y_FIRST))
    SCREEN.blit(BG_WATER, (X_SECOND, Y_SECOND))
    if Y_SECOND > SCREEN_HEIGHT:
        Y_SECOND = -SCREEN_HEIGHT
    if Y_FIRST > SCREEN_HEIGHT:
        Y_FIRST = -SCREEN_HEIGHT
    SCREEN.blit(GROUND, (0, SCREEN_HEIGHT-100))
    ALL_SPRITES.draw(SCREEN)
    SCREEN.blit(BG_BLACK, (0, 0))
    #Seaweed
    for i in range(5, SCREEN_WIDTH-15, 60):
        SCREEN.blit(IMAGES["spr_seaweed"], (i, SCREEN_HEIGHT-130)) #top seaweed
    for i in range(5, SCREEN_WIDTH-15, 60):
        SCREEN.blit(IMAGES["spr_seaweed"], (i, SCREEN_HEIGHT-80))
    
    #Font On Top
    SCORE_TEXT = FONT_OCEAN.render("Fitness: " + str(SCORE), 1, (255, 255, 255))
    SCREEN.blit(SCORE_TEXT, ((SCREEN_WIDTH/2)+300, 5))
    GENERATION_TEXT = FONT_OCEAN.render("Generation: "+str(GENERATION), 1, (255, 255, 255))
    SCREEN.blit(GENERATION_TEXT, ((SCREEN_WIDTH/2)+100, 5))
    HIGHSCORE_TEXT = FONT_OCEAN.render("Highest Avg Score: " + str(HIGHSCORE), 1, (255, 255, 255))
    SCREEN.blit(HIGHSCORE_TEXT, ((SCREEN_WIDTH/2)-200, 5))
    BEST_GENERATION_TEXT = FONT_OCEAN.render("Best Generation: " + str(BEST_GENERATION), 1, (255, 255, 255))
    SCREEN.blit(BEST_GENERATION_TEXT, ((SCREEN_WIDTH/2)-400, 5))
    for redfish in REDFISHES:
        for shark in SHARKS:
            if pygame.sprite.collide_mask(redfish, shark):
                redfish.health = 0
        for wall in WALLS:
            if redfish.rect.colliderect(wall.rect):
                redfish.collision_with_wall(wall)
    for shark in SHARKS:
        for wall in WALLS:
            if shark.rect.colliderect(wall.rect):
                shark.collision_with_wall(wall)
    if SCORE == 10:
        pygame.image.save(SCREEN, "Generation " + str(GENERATION) + " screenshot.jpeg")
    #Compute game logic
    #If there are no more living Organisms, the generation is over
    #Compute statistics and generate DNA for next generation
    if not REDFISHES:
        for z in ARCS_LIST:
            print(z.rect.topleft)
        #Sort the list of dead organisms by their SCORE
        DEAD_LIST.sort(key=lambda item: item[1])
        #Pass the list of dead organisms to be used for deciding the next generation
        NEXT_POP_DNA = get_next_pop(DEAD_LIST, (POPSIZE-2))
        #Print some helpful information for watching the DNA change each generation
        print("Top 50% for generation " + str(GENERATION+1))
        print("Size | Speed | FreqTurns | RadiusArc | Intelligence | Score")
        SUM_SCORES = 0
        #Print the genotypes of the top 50% of this generation and their SCOREs
        for n in range(int(len(DEAD_LIST)*0.5)):
            temp = DEAD_LIST[-(n+1)]
            SUM_SCORES += temp[1]

            print(temp[0].genes.getGenotype() + " " + str(temp[1]))

        #Print the average SCORE for this generation
        print("Avg SCORE: " + str(SUM_SCORES/float(len(DEAD_LIST))))
        print("")
        AVG_SCORE = SUM_SCORES/float(len(DEAD_LIST))
        if AVG_SCORE > HIGHSCORE:
            HIGHSCORE = int(AVG_SCORE)
            BEST_GENERATION = GENERATION
        else:
            os.remove("Generation " + str(GENERATION) + " screenshot.jpeg")

        #Take the top 2 performing Organisms from this generation and add them to the next population
        ELITECLONE_LIST = [DEAD_LIST[-1][0].genes.getGenotypeString(), DEAD_LIST[-2][0].genes.getGenotypeString()]
        NEXT_POP_DNA.append(DEAD_LIST[-1][0].genes.getGenotypeString())
        NEXT_POP_DNA.append(DEAD_LIST[-2][0].genes.getGenotypeString())
        #Set flag to end game loop
        #Create a new list of Organisms, using the generated DNA, all at random locations
        ARCS_LIST = []
        REDFISHES = pygame.sprite.Group()
        for genes in NEXT_POP_DNA:
            d = DNA.DNA(NUMGENES, genes)
            o = RedFish(d)
            REDFISHES.add(o)
            ARCS_LIST.append(Arc())
        for i in range(0, POPSIZE):
            REDFISHES.sprites()[i].arc_index = i
        #Clear the list for the next generation
        NEXT_POP_DNA = []
        GENERATION += 1
        reset()
        DEAD_LIST = []
        SCORE = 0
    #Increase SCORE by 1
    SCORE += 1

    #For each Organism that's still alive
    for redfish in REDFISHES:
        #Check if it is still alive
        if not redfish.still_alive():
            #If not, remove it from the list, and add it to the list of dead Organisms
            REDFISHES.remove(redfish)
            DEAD_LIST.append((redfish, SCORE))
            ARCS_LIST[redfish.arc_index].destroy = 1
    
    pygame.display.flip()
    pygame.display.update()
    