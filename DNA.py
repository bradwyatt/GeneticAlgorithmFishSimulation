import random

# A class to hold a binary string representing the DNA of an organism
class DNA():
    #Takes an int representing the number of genes, and possibly an existing genotype to use
    def __init__(self, numGenes, existingGenes):

        self.numGenes = numGenes
        #If a genotype is given, use this
        if existingGenes is not None:
            self.dna = existingGenes
        #Else, create a random genotype
        else:
            self.dna = ""
            #Randomly pick 1 or 0 for the required number of genes
            for i in range(0, numGenes):
                value = random.randint(0, 1)

                if value == 0:
                    self.dna += "0"
                else:
                    self.dna += "1"
    #Given a number, return the corresponding bit
    def getGene(self, num):
        return self.dna[num]

    #Return a string containing the genotype of this instance. Bits are grouped as they are expressed in an Organism
    def getGenotype(self):
        #Get a string for each gene that an Organism will express
        gene0to4   = self.getGene(0)  + self.getGene(1)  + self.getGene(2)  + self.getGene(3) + self.getGene(4)
        gene5to7   = self.getGene(5)  + self.getGene(6)  + self.getGene(7)
        gene8to11  = self.getGene(8)  + self.getGene(9) + self.getGene(10) + self.getGene(11)
        gene12to16 = self.getGene(12) + self.getGene(13) + self.getGene(14) + self.getGene(15) + self.getGene(16)
        gene17to21 = self.getGene(17) + self.getGene(18) + self.getGene(19) + self.getGene(20) + self.getGene(21)
        #Prints out each chunk
        genes = ""
        genes += str(gene0to4)+"   "
        genes += str(gene5to7)+"   "
        genes += str(gene8to11)+"   "
        genes += str(gene12to16)+"   "
        genes += str(gene17to21)+"   "
        genes += "   "
        #Genes past 40 are also unused, group these together too
        for i in range(22, self.numGenes):
            genes += self.dna[i]

        return genes
    #Returns the genotype as a single contiguous string
    def getGenotypeString(self):
        genes = ""
        for i in range(0, len(self.dna)):
            genes += self.dna[i]
        return genes