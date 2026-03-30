"""
PyWorld code includes: get_next_pop, crossover, mutate functions and DNA module
1) Having issue with redfish in 0 sprite groups
It may have to do with collision in redfish class
"""
import math
import os
import random
import sys

import pygame

import DNA
from app_setup import adjust_to_correct_appdir
from config import (
    NUMGENES,
    NUM_OF_ELITECLONES,
    POPSIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from genetic_algorithm import get_next_pop
from resources import find_asset_path, load_images

IMAGES = {}

adjust_to_correct_appdir()

def display_caption():
    pygame.display.set_caption("Genetic Algorithm Simulation")

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


def load_assets():
    global IMAGES

    IMAGES = load_images()
    font_ocean = pygame.font.Font(find_asset_path("Fonts/Oceanfont.ttf"), 16)

    ground = pygame.image.load(find_asset_path("Sprites/ground.bmp")).convert()
    ground = pygame.transform.scale(ground, (SCREEN_WIDTH, 100))

    bg_water = pygame.image.load(find_asset_path("Sprites/background.bmp")).convert()
    bg_water = pygame.transform.scale(bg_water, (SCREEN_WIDTH, SCREEN_HEIGHT))

    bg_black = pygame.image.load(find_asset_path("Sprites/blackbg.jpg")).convert()
    bg_black = pygame.transform.scale(bg_black, (SCREEN_WIDTH, 30))

    game_icon = pygame.image.load(find_asset_path("Sprites/redfishico.png"))
    pygame.display.set_icon(game_icon)

    return font_ocean, ground, bg_water, bg_black


def create_room(all_sprites):
    for x_top in range(38):
        Wall(all_sprites, (x_top * 32, 0))
    for x_bottom in range(38):
        Wall(all_sprites, (x_bottom * 32, SCREEN_HEIGHT - 32))
    for y_left in range(23):
        Wall(all_sprites, (0, (y_left * 32) + 32))
    for y_right in range(23):
        Wall(all_sprites, (SCREEN_WIDTH - 32, (y_right * 32) + 32))


def create_population(all_sprites, population_dna=None):
    dna_sequences = population_dna or [None] * POPSIZE

    for index, genes in enumerate(dna_sequences):
        dna = DNA.DNA(NUMGENES, genes)
        RedFish(dna, all_sprites, index < NUM_OF_ELITECLONES and genes is not None)
        Arc(all_sprites)


def render_scene(screen, all_sprites, backgrounds, hud, ui_state):
    font_ocean, ground, bg_water, bg_black = backgrounds
    x_first, y_first, x_second, y_second = ui_state["background_offsets"]
    score, generation, highscore, best_generation = hud

    screen.blit(bg_water, (x_first, y_first))
    screen.blit(bg_water, (x_second, y_second))
    screen.blit(ground, (0, SCREEN_HEIGHT - 100))
    all_sprites.draw(screen)
    screen.blit(bg_black, (0, 0))

    for i in range(5, SCREEN_WIDTH - 15, 60):
        screen.blit(IMAGES["spr_seaweed"], (i, SCREEN_HEIGHT - 130))
    for i in range(5, SCREEN_WIDTH - 15, 60):
        screen.blit(IMAGES["spr_seaweed"], (i, SCREEN_HEIGHT - 80))

    score_text = font_ocean.render("Fitness: " + str(score), 1, (255, 255, 255))
    screen.blit(score_text, ((SCREEN_WIDTH / 2) + 300, 5))
    generation_text = font_ocean.render("Generation: " + str(generation), 1, (255, 255, 255))
    screen.blit(generation_text, ((SCREEN_WIDTH / 2) + 100, 5))
    highscore_text = font_ocean.render("Highest Avg Score: " + str(highscore), 1, (255, 255, 255))
    screen.blit(highscore_text, ((SCREEN_WIDTH / 2) - 200, 5))
    best_generation_text = font_ocean.render("Best Generation: " + str(best_generation), 1, (255, 255, 255))
    screen.blit(best_generation_text, ((SCREEN_WIDTH / 2) - 400, 5))


def update_background_offsets(ui_state):
    x_first, y_first, x_second, y_second = ui_state["background_offsets"]
    y_first += 10
    y_second += 10

    if y_second > SCREEN_HEIGHT:
        y_second = -SCREEN_HEIGHT
    if y_first > SCREEN_HEIGHT:
        y_first = -SCREEN_HEIGHT

    ui_state["background_offsets"] = (x_first, y_first, x_second, y_second)


def handle_collisions(dead_list, score):
    for redfish in RedFish.redfishes[:]:
        for wall in Wall.wall_list:
            if redfish.rect.colliderect(wall.rect):
                redfish.collision_with_wall(wall)

        for shark in Shark.sharks:
            if pygame.sprite.collide_mask(redfish, shark):
                redfish_pos = RedFish.redfishes.index(redfish)
                dead_list = redfish.destroy(dead_list, score)
                Arc.arc_list[redfish_pos].destroy()
                break

    for shark in Shark.sharks:
        for wall in Wall.wall_list:
            if shark.rect.colliderect(wall.rect):
                shark.collision_with_wall(wall)

    return dead_list


def build_next_generation(all_sprites, dead_list, generation, highscore, best_generation):
    dead_list.sort(key=lambda item: item[1])
    next_pop_dna = get_next_pop(dead_list, POPSIZE - NUM_OF_ELITECLONES)

    print("Top 50% for generation " + str(generation + 1))
    print("Size | Speed | FreqTurns | RadiusArc | Intelligence | Score")

    sum_scores = 0
    for n in range(int(len(dead_list) * 0.5)):
        temp = dead_list[-(n + 1)]
        sum_scores += temp[1]
        print(temp[0].genes.getGenotype() + " " + str(temp[1]))

    avg_score = sum_scores / float(len(dead_list))
    print("Avg score: " + str(avg_score))
    print("")

    screenshot_path = "Generation " + str(generation) + " screenshot.jpeg"
    if avg_score > highscore:
        highscore = int(avg_score)
        best_generation = generation
    elif os.path.exists(screenshot_path):
        os.remove(screenshot_path)

    for i in range(NUM_OF_ELITECLONES * -1, 0):
        next_pop_dna.append(dead_list[i][0].genes.getGenotypeString())

    create_population(all_sprites, next_pop_dna[::-1])
    reset()
    return highscore, best_generation

def main():
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

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Fish Food")
    backgrounds = load_assets()
    pygame.display.set_caption('Genetic Algorithm Simulation')
    pygame.mouse.set_visible(0)

    create_room(all_sprites)

    [Shark(all_sprites) for i in range(8)]

    create_population(all_sprites)
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
            ui_state = {"background_offsets": (x_first, y_first, x_second, y_second)}
            update_background_offsets(ui_state)
            x_first, y_first, x_second, y_second = ui_state["background_offsets"]
            render_scene(
                screen,
                all_sprites,
                backgrounds,
                (score, generation, highscore, best_generation),
                ui_state,
            )

            dead_list = handle_collisions(dead_list, score)

            # Initially creates screenshot (deletes this later if it's not high score)
            if score == 10:
                pygame.image.save(screen, "Generation " + str(generation) + " screenshot.jpeg")

            #If there are no more living Organisms, the generation is over
            #Compute statistics and generate DNA for next generation
            if not RedFish.redfishes:
                highscore, best_generation = build_next_generation(
                    all_sprites,
                    dead_list,
                    generation,
                    highscore,
                    best_generation,
                )
                generation += 1
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
