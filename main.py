"""
PyWorld code includes: get_next_pop, crossover, mutate functions and DNA module
1) Having issue with redfish in 0 sprite groups
It may have to do with collision in redfish class
"""
import random
import sys
import math
import os
import pygame
import DNA

(SCREEN_WIDTH, SCREEN_HEIGHT) = 1200, 800
POPSIZE = 20
NUMGENES = 22
NUM_OF_ELITECLONES = 2
MUTATE_PERCENT_CHANCE = 5
IMAGES = {}

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
    """
    Taken from PyWorld
    Creates DNA of next population
    """
    sum_fitness = 0
    # Initialize an array that will hold the probabilities of each candidate being chosen
    candidate_probs = ['' for i in range(len(candidates))]
    # Loop through all the candidates and compute the sum of all of their fitness scores
    for c in range(len(candidates)):
        sum_fitness += float(candidates[c][1])
        # Store the fitness of each candidate in the probability array for now
        candidate_probs[c] = (c, candidates[c][1])

    for i in range(len(candidate_probs)):
        # Divide each candidates fitness by the sum of all the fitnesses to determine its proportion
        candidate_probs[i] = (i, (candidate_probs[i][1]/sum_fitness)*100)

    prev_boundry = 0.0
    # Set up an array to hold the "boundaries" for each candidate,
    # which are proportionate based on the individuals fitness
    candidate_boundaries = [(0, 0, 0) for i in range(len(candidate_probs))]
    b = 0
    for p in candidate_probs:
        # Give each candidate a range, based on its proportion, and the end of the last boundry
        candidate_boundaries[b] = (p[0], prev_boundry, float(prev_boundry+p[1]))
        prev_boundry = candidate_boundaries[b][2]
        b += 1

    # Create an empty array to hold the next population
    next_pop = []
    # We will need n/2 sets of parents, where n is the size of the population we want
    for _ in range((int(math.ceil(size_of_next_pop/2)))):
        parent_a = None
        parent_b = None

        # Will be used to store parent A to be reintroduced after parent_b is chosen
        parent_a_temp = None
        while parent_a is None:

            # Pick a random number (1-100, scaled up by 100)
            next_mate = random.randrange(100.0, 10000.0)/100.0
            # Look through all of the boundries
            for a in candidate_boundaries:
                # Select the candidate whose boundry contains the selected random value
                if a[1] < next_mate < a[2]:
                    # Set that candidate to be Parent A
                    parent_a = candidates[a[0]][0]
                    # Remove that candidate from the list
                    parent_a_temp = a
                    candidate_boundaries.remove(a)
        # While we still need to select a parent B
        while parent_b is None:
            # If there's only one candidate left, just use that one, no need to randomly select
            if len(candidate_boundaries) == 1:
                b = candidate_boundaries.pop()
                # Set that candidate to be Parent B
                parent_b = candidates[b[0]][0]
            else:
                # Pick a random number (1-100, scaled up by 100)
                next_mate = random.randrange(100.0, 10000.0)/100.0
                # Look through all of the boundries
                for b in candidate_boundaries:
                    # Select the candidate whose boundry contains the selected random value
                    if b[1] < next_mate < b[2]:
                        # Set that candidate to be Parent B, and remove the candidate from the list
                        parent_b = candidates[b[0]][0]
                        # candidate_boundaries.remove(b)
        candidate_boundaries.append(parent_a_temp)
        # Using the two parents , create two children DNA using crossover
        child_a_dna, child_b_dna = crossover(parent_a, parent_b, len(parent_a.genes.dna))
        # Mutate the DNA of each child
        child_a_dna = mutate(child_a_dna)
        child_b_dna = mutate(child_b_dna)
        # Add the children DNA to the next population
        next_pop.append(child_a_dna)
        next_pop.append(child_b_dna)
    # Return the population
    return next_pop


def crossover(parent_a, parent_b, num_genes):
    """
    Taken from PyWorld
    Given two parent Organisms and the length of those parents DNA, generate two children
    """
    # Initialize two empty strings for the children
    child_a_dna = ""
    child_b_dna = ""
    # For the length of the genotype
    for this_gene in range(num_genes):
        # Randomly pick to use either Parent A or Parent B
        if random.randint(0, 1) == 0:
            # If child A gets gene from Parent A, child B gets gene from Parent B
            child_a_dna += parent_a.genes.getGene(this_gene)
            child_b_dna += parent_b.genes.getGene(this_gene)
        else:
            # If child A gets gene from Parent B, child B gets gene from Parent A
            child_a_dna += parent_b.genes.getGene(this_gene)
            child_b_dna += parent_a.genes.getGene(this_gene)
    # Return the created DNA strings
    return child_a_dna, child_b_dna

def mutate(genes):
    """
    Taken from PyWorld
    Given a string containing a genotype, perform some mutations
    """
    new_genes = ""
    # For each gene in the genotype
    for g in range(len(genes)):
        gene = genes[g]
        # Use a X% chance of mutating. If we decide to mutate this gene, reverse it's value
        if random.randrange(0, 100) < MUTATE_PERCENT_CHANCE:
            if gene == "0":
                new_genes += "1"
            else:
                new_genes += "0"
        # Otherwise, leave it unchanged
        else:
            new_genes += gene
    # Return the new genotype
    return new_genes

class Wall(pygame.sprite.Sprite):
    wall_list = []
    def __init__(self, all_sprites, new_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_wall"]
        self.rect = self.image.get_rect()
        self.rect.topleft = new_pos
        Wall.wall_list.append(self)
        all_sprites.add(self)

class RedFish(pygame.sprite.Sprite):
    redfishes = []
    def __init__(self, new_dna, all_sprites, elite_clone=False):
        pygame.sprite.Sprite.__init__(self)
        RedFish.redfishes.append(self)
        self.direction = random.uniform(0, math.pi*2)
        self.speed = 0
        self.size = 0
        self.genes = new_dna
        self.freq_turns = 0
        self.radius_arc = 0
        self.intelligence = 0
        self.change_dir_timer = 0
        self.elite_clone = elite_clone
        self.express_genes()
        self.image = pygame.transform.smoothscale(IMAGES["spr_redfish"], (self.size+5, self.size))
        self.rect = self.image.get_rect()
        all_sprites.add(self)
        self.shark_list = []
    def update(self):
        self.rect.x -= math.sin(self.direction) * self.speed
        self.rect.y -= math.cos(self.direction) * self.speed
        self.change_dir_timer += 1
        if self.direction < math.pi: # facing left
            if not self.elite_clone:
                self.image = pygame.transform.smoothscale(IMAGES["spr_redfishleft"], (self.size+5, self.size))
            else:
                self.image = pygame.transform.smoothscale(IMAGES["spr_elitecloneleft"], (self.size+5, self.size))

        else: # facing right
            if not self.elite_clone:
                self.image = pygame.transform.smoothscale(IMAGES["spr_redfish"], (self.size+5, self.size))
            else:
                self.image = pygame.transform.smoothscale(IMAGES["spr_eliteclone"], (self.size+5, self.size))
        for shark in Shark.sharks:
            if pygame.sprite.collide_mask(Arc.arc_list[RedFish.redfishes.index(self)], shark):
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
    def collision_with_wall(self, wall):
        self.change_dir_timer = 0
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32+self.size: #left WALLS
                self.rect.left = 32+self.size
                self.direction = random.uniform(0, math.pi*2)
            elif self.rect.top > SCREEN_HEIGHT-64-self.size: #bottom WALLS
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
        gene13to16 = self.genes.getGene(12) + self.genes.getGene(13) + self.genes.getGene(14) + self.genes.getGene(15) + self.genes.getGene(16)
        self.radius_arc = 1 + int(gene13to16, 2)
    def express_intelligence(self):
        gene17to21 = self.genes.getGene(17) + self.genes.getGene(18) + self.genes.getGene(19) + self.genes.getGene(20) + self.genes.getGene(21)
        self.intelligence = 1 + int(gene17to21, 2)
    def destroy(self, dead_list, score):
        dead_list.append((self, score))
        RedFish.redfishes.remove(self)
        self.kill()
        return dead_list

class Arc(pygame.sprite.Sprite):
    """
    Arc for fish eyesight
    Moves in front of fish's direction
    """
    arc_list = []
    def __init__(self, all_sprites):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_arc"]
        self.rect = self.image.get_rect()
        Arc.arc_list.append(self)
        all_sprites.add(self)
    def update(self):
        if RedFish.redfishes[Arc.arc_list.index(self)].direction < math.pi:
            self.image = pygame.transform.scale(IMAGES["spr_arcleft"],
                                                (RedFish.redfishes[Arc.arc_list.index(self)].radius_arc*3, RedFish.redfishes[Arc.arc_list.index(self)].radius_arc*3))
            self.rect = self.image.get_rect()
            self.rect.right = RedFish.redfishes[Arc.arc_list.index(self)].rect.left
            self.rect.centery = RedFish.redfishes[Arc.arc_list.index(self)].rect.center[1]
        else:
            self.image = pygame.transform.scale(IMAGES["spr_arc"], 
                                                (RedFish.redfishes[Arc.arc_list.index(self)].radius_arc*3, RedFish.redfishes[Arc.arc_list.index(self)].radius_arc*3))
            self.rect = self.image.get_rect()
            self.rect.left = RedFish.redfishes[Arc.arc_list.index(self)].rect.right
            self.rect.centery = RedFish.redfishes[Arc.arc_list.index(self)].rect.centery
    def destroy(self):
        Arc.arc_list.remove(self)
        self.kill()

class Shark(pygame.sprite.Sprite):
    """
    Predator of fish
    """
    sharks = []
    def __init__(self, all_sprites):
        pygame.sprite.Sprite.__init__(self)
        Shark.sharks.append(self)
        self.image = IMAGES["spr_shark"]
        self.rect = self.image.get_rect()
        all_sprites.add(self)
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

def reset():
    for redfish in RedFish.redfishes:
        redfish.rect.topleft = (random.randrange(300, SCREEN_WIDTH-300),
                                random.randrange(100, SCREEN_HEIGHT-100))
    # Spawns sharks on both sides of room
    for item, shark in enumerate(Shark.sharks):
        if item <= len(Shark.sharks)/2:
            shark.rect.topleft = (100, random.randrange(100, SCREEN_HEIGHT-100))
        else:
            shark.rect.topleft = (SCREEN_WIDTH-100, random.randrange(100, SCREEN_HEIGHT-100))

def main():
    screen = None
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    RUNNING, DEBUG = 0, 1
    state = RUNNING
    debug_message = 0

    (x_first, y_first) = (0, 0)
    (x_second, y_second) = (0, -SCREEN_HEIGHT)
    score = 0
    highscore = 0
    generation = 0
    best_generation = 0
    dead_list = []
    next_pop_dna = []

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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
    font_ocean = pygame.font.Font("fonts/oceanfont.ttf", 16)
    #FONT_ARIAL = pygame.font.SysFont('Arial', 32)
    #backgrounds
    ground = pygame.image.load("sprites/ground.bmp").convert()
    ground = pygame.transform.scale(ground, (SCREEN_WIDTH, 100))
    bg_water = pygame.image.load("sprites/background.bmp").convert()
    bg_water = pygame.transform.scale(bg_water, (SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_black = pygame.image.load("sprites/blackbg.jpg").convert()
    bg_black = pygame.transform.scale(bg_black, (SCREEN_WIDTH, 30))
    #window
    game_icon = pygame.image.load("sprites/redfishico.png")
    pygame.display.set_icon(game_icon)
    pygame.display.set_caption('Genetic Algorithm Simulation')
    pygame.mouse.set_visible(0)

    # Initiate Room
    for x_top in range(38):
        Wall(all_sprites, (x_top*32, 0)) #top
    for x_bottom in range(38):
        Wall(all_sprites, (x_bottom*32, SCREEN_HEIGHT-32)) #bottom
    for y_left in range(23):
        Wall(all_sprites, (0, (y_left*32)+32)) #left
    for y_right in range(23):
        Wall(all_sprites, (SCREEN_WIDTH-32, (y_right*32)+32)) #right

    [Shark(all_sprites) for i in range(8)]

    # Create a list of POPSIZE Organisms, all with random DNA
    # Subsequent generations will be created using crossover and mutation
    for count_organism in range(POPSIZE):
        d = DNA.DNA(NUMGENES, None)
        RedFish(d, all_sprites, False)
        Arc(all_sprites)
    reset()

    while True:
        clock.tick(60)
        display_caption()
        if state == RUNNING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        debug_message = 1
                        state = DEBUG
            all_sprites.update()

            # Water background movement
            y_first += 10
            y_second += 10
            screen.blit(bg_water, (x_first, y_first))
            screen.blit(bg_water, (x_second, y_second))
            if y_second > SCREEN_HEIGHT:
                y_second = -SCREEN_HEIGHT
            if y_first > SCREEN_HEIGHT:
                y_first = -SCREEN_HEIGHT
            screen.blit(ground, (0, SCREEN_HEIGHT-100))
            all_sprites.draw(screen)
            screen.blit(bg_black, (0, 0))
            # Seaweed
            for i in range(5, SCREEN_WIDTH-15, 60):
                screen.blit(IMAGES["spr_seaweed"], (i, SCREEN_HEIGHT-130)) # top
            for i in range(5, SCREEN_WIDTH-15, 60):
                screen.blit(IMAGES["spr_seaweed"], (i, SCREEN_HEIGHT-80)) # bottom

            # Font On Top
            score_text = font_ocean.render("Fitness: " + str(score), 1, (255, 255, 255))
            screen.blit(score_text, ((SCREEN_WIDTH/2)+300, 5))
            generation_text = font_ocean.render("Generation: " + str(generation), 1, (255, 255, 255))
            screen.blit(generation_text, ((SCREEN_WIDTH/2)+100, 5))
            highscore_text = font_ocean.render("Highest Avg Score: " + str(highscore), 1, (255, 255, 255))
            screen.blit(highscore_text, ((SCREEN_WIDTH/2)-200, 5))
            best_generation_text = font_ocean.render("Best Generation: " + str(best_generation), 1, (255, 255, 255))
            screen.blit(best_generation_text, ((SCREEN_WIDTH/2)-400, 5))

            # Collisions
            for redfish in RedFish.redfishes[:]:
                for wall in Wall.wall_list:
                    if redfish.rect.colliderect(wall.rect):
                        redfish.collision_with_wall(wall)
                for shark in Shark.sharks:
                    if pygame.sprite.collide_mask(redfish, shark):
                        redfish_pos = RedFish.redfishes.index(redfish) # THIS SOMETIMES GIVES ERROR OF 0 sprites in group
                        dead_list = redfish.destroy(dead_list, score)
                        Arc.arc_list[redfish_pos].destroy()
                        break
            for shark in Shark.sharks:
                for wall in Wall.wall_list:
                    if shark.rect.colliderect(wall.rect):
                        shark.collision_with_wall(wall)

            # Initially creates screenshot (deletes this later if it's not high score)
            if score == 10:
                pygame.image.save(screen, "Generation " + str(generation) + " screenshot.jpeg")

            #If there are no more living Organisms, the generation is over
            #Compute statistics and generate DNA for next generation
            if not RedFish.redfishes:
                #Sort the list of dead organisms by their score
                dead_list.sort(key=lambda item: item[1])
                #Pass the list of dead organisms to be used for deciding the next generation
                next_pop_dna = get_next_pop(dead_list, (POPSIZE-NUM_OF_ELITECLONES))
                #Print some helpful information for watching the DNA change each generation
                print("Top 50% for generation " + str(generation+1))
                print("Size | Speed | FreqTurns | RadiusArc | Intelligence | Score")
                sum_scores = 0
                #Print the genotypes of the top 50% of this generation and their scoreS
                for n in range(int(len(dead_list)*0.5)):
                    temp = dead_list[-(n+1)]
                    sum_scores += temp[1]

                    print(temp[0].genes.getGenotype() + " " + str(temp[1]))

                #Print the average score for this generation
                print("Avg score: " + str(sum_scores/float(len(dead_list))))
                print("")
                avg_score = sum_scores/float(len(dead_list))
                if avg_score > highscore:
                    highscore = int(avg_score)
                    best_generation = generation
                else:
                    os.remove("Generation " + str(generation) + " screenshot.jpeg")

                # Take the top X performing Organisms ("Elite Clones") from this generation and add them to the next population
                # Create a new list of Organisms, using the generated DNA, all at random locations
                # Last number of items are elite clones since they were sorted by score
                for i in range(NUM_OF_ELITECLONES*-1, 0):
                    next_pop_dna.append(dead_list[i][0].genes.getGenotypeString())

                for i, genes in enumerate(next_pop_dna[::-1]):
                    d = DNA.DNA(NUMGENES, genes)
                    if i < NUM_OF_ELITECLONES:
                        # Elite Clone
                        RedFish(d, all_sprites, True)
                    else:
                        RedFish(d, all_sprites, False)
                    Arc(all_sprites)
                # Clear the list for the next generation
                next_pop_dna = []
                generation += 1
                reset()
                dead_list = []
                score = 0
            # Increase score by 1 during the round of generation
            score += 1

            pygame.display.flip()
    if state == DEBUG:
        if debug_message == 1:
            print("Entering debug mode")
            debug_message = 0
            # USE BREAKPOINT HERE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    state = RUNNING

if __name__ == '__main__':
    main()
