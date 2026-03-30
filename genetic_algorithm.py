import math
import random

from config import MUTATE_PERCENT_CHANCE


def get_next_pop(candidates, size_of_next_pop):
    """
    Taken from PyWorld
    Creates DNA of next population
    """
    total_fitness = sum(float(candidate[1]) for candidate in candidates)
    if total_fitness == 0:
        total_fitness = float(len(candidates))
        candidate_probs = [(index, 100.0 / len(candidates)) for index in range(len(candidates))]
    else:
        candidate_probs = [
            (index, (candidate[1] / total_fitness) * 100)
            for index, candidate in enumerate(candidates)
        ]

    candidate_boundaries = []
    previous_boundary = 0.0
    for index, probability in candidate_probs:
        upper_boundary = previous_boundary + float(probability)
        candidate_boundaries.append((index, previous_boundary, upper_boundary))
        previous_boundary = upper_boundary

    next_pop = []
    for _ in range(int(math.ceil(size_of_next_pop / 2))):
        parent_a = None
        parent_b = None
        parent_a_temp = None

        while parent_a is None:
            next_mate = random.randrange(100.0, 10000.0) / 100.0
            for candidate in candidate_boundaries:
                if candidate[1] < next_mate < candidate[2]:
                    parent_a = candidates[candidate[0]][0]
                    parent_a_temp = candidate
                    candidate_boundaries.remove(candidate)
                    break

        while parent_b is None:
            if len(candidate_boundaries) == 1:
                candidate = candidate_boundaries.pop()
                parent_b = candidates[candidate[0]][0]
            else:
                next_mate = random.randrange(100.0, 10000.0) / 100.0
                for candidate in candidate_boundaries:
                    if candidate[1] < next_mate < candidate[2]:
                        parent_b = candidates[candidate[0]][0]
                        break

        candidate_boundaries.append(parent_a_temp)
        child_a_dna, child_b_dna = crossover(parent_a, parent_b, len(parent_a.genes.dna))
        next_pop.append(mutate(child_a_dna))
        next_pop.append(mutate(child_b_dna))

    return next_pop


def crossover(parent_a, parent_b, num_genes):
    """
    Taken from PyWorld
    Given two parent Organisms and the length of those parents DNA, generate two children
    """
    child_a_dna = ""
    child_b_dna = ""

    for this_gene in range(num_genes):
        if random.randint(0, 1) == 0:
            child_a_dna += parent_a.genes.getGene(this_gene)
            child_b_dna += parent_b.genes.getGene(this_gene)
        else:
            child_a_dna += parent_b.genes.getGene(this_gene)
            child_b_dna += parent_a.genes.getGene(this_gene)

    return child_a_dna, child_b_dna


def mutate(genes):
    """
    Taken from PyWorld
    Given a string containing a genotype, perform some mutations
    """
    new_genes = ""
    for gene in genes:
        if random.randrange(0, 100) < MUTATE_PERCENT_CHANCE:
            new_genes += "1" if gene == "0" else "0"
        else:
            new_genes += gene

    return new_genes
