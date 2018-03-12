import datetime
import random
import math
import numpy as np
import os
from graphing import visualize_cost as vc

__author__ = "Olve Drageset"

WEIGHTS_DIRECTORY = 'weights/weights_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def getcost(individual):
    return individual.cost


def single_point_crossover(parent1, parent2):
    point = random.randrange(1, len(parent1.gene) - 1)
    gene1 = parent1.gene[0:point] + parent2.gene[point:]
    gene2 = parent2.gene[0:point] + parent1.gene[point:]
    return [Individual(gene1), Individual(gene2)]


def two_point_crossover(parent1, parent2):
    length = min(len(parent1.gene), len(parent2.gene))
    point1 = random.randrange(0, int(length - 1*0.66))  # Put the first point somewhere in the first two thirds
    point2 = random.randrange(point1, length - 1)
    p1s1 = parent1.gene[0:point1]
    p1s2 = parent1.gene[point1:point2]
    p1s3 = parent1.gene[point2:]
    p2s1 = parent1.gene[0:point1]
    p2s2 = parent1.gene[point1:point2]
    p2s3 = parent1.gene[point2:]

    # ABA / BAB
    gene1 = p1s1 + p2s2 + p1s3
    gene2 = p2s1 + p1s2 + p2s3

    # AAB / BBA
    gene3 = p2s1 + p2s2 + p1s3
    gene4 = p1s1 + p1s2 + p2s3

    # ABB / BAA
    gene5 = p2s1 + p1s2 + p1s3
    gene6 = p1s1 + p2s2 + p2s3

    return [Individual(gene1),
            Individual(gene2),
            Individual(gene3),
            Individual(gene4),
            Individual(gene5),
            Individual(gene6)]


class Individual:
    def __init__(self, gene, cost=0):
        self.gene = gene
        self.cost = cost

    def mutate(self, mutation_rate, mutation_size, value_range):
        self.hard_mutate(mutation_rate,value_range)
        # value_range_size = abs(value_range[1] - value_range[0])
        # for nucleotide in self.gene:
        #     if random.random() < mutation_rate:
        #         nucleotide += max(
        #             min(
        #                 random.randrange(-1, 2, 2) * mutation_size * value_range_size,
        #                 value_range[1]),
        #             value_range[0])

    def hard_mutate(self, mutation_rate, value_range):
        for i in range(0, len(self.gene)):
            if random.random() < mutation_rate:
                self.gene[i] = random.uniform(value_range[0], value_range[1])

    def mutant_clone(self, mutation_rate, mutation_size, value_range):
        clone = Individual(self.gene, self.cost)
        clone.mutate(mutation_rate, mutation_size, value_range)
        return clone

    def clones(self, number_of_clones):
        offspring = []
        for i in range(0, number_of_clones-1):
            child = Individual(self.gene, self.cost)
            offspring.append(child)
        return offspring

    def get_output_params(self, number_of_params):
        out = []
        for i in range(0, number_of_params):
            section_length = int(len(self.gene)/number_of_params)
            out.append(sum(self.gene[i*section_length:(i+1)*section_length]))
        return out

    def update_cost(self, cost_function):
        self.cost = cost_function(self.gene)
        return self.cost


class Population:
    def __init__(self,
                 pop_size=20,
                 gene_length=5,
                 value_range=[-5, 5],
                 init_near_zero=False):
        self.pop_size = pop_size
        self.gene_length = gene_length
        self.pop = []
        self.value_range = value_range
        self.init_near_zero = init_near_zero  # Whether we want the gene values to be initialized close to zero
        # As opposed to being initialized anywhere within the value_range

        if init_near_zero:
            value_range = [-0.05, 0.05]

        # Initialize genes randomly
        for pop_index in range(0, pop_size):
            gene = []
            for gene_index in range(0, gene_length):
                gene.append(random.uniform(value_range[0], value_range[1]))
            self.pop.append(Individual(gene=gene))


class GenAlg:
    generation_counter = 0
    gen_progress = 0
    best_cost = 0
    avg_cost = 0
    pop_size = 0
    pop_size_current = 0

    def __init__(self,
                 cost_function=None,
                 crossover_function=single_point_crossover,
                 pop_size=20,
                 gene_length=5,
                 mutation_rate=0.1,  # What is the probability of a gene mutating, [0,1]
                 mutation_size=0.5,  # How large is the change in a value upon mutation [0,1]
                 elite_rate=0.05,  # How large a piece of the population is kept as elitism [0,1]
                 max_generations=20,
                 value_range=[-5, 5],
                 init_near_zero=False,
                 verbose=True,
                 plot=False):
        self.cost_function = cost_function
        GenAlg.pop_size = pop_size
        GenAlg.pop_size_current = pop_size
        self.value_range = value_range
        self.mutation_rate = mutation_rate
        self.mutation_size = mutation_size
        self.pop = Population(pop_size=pop_size, gene_length=gene_length, value_range=value_range, init_near_zero=init_near_zero)
        self.verbose = verbose
        if self.verbose: print("GEN 0 IS BORN, SIZE: ", len(self.pop.pop))
        self.plot = plot
        self.graph = None
        if self.plot: 
            self.graph = vc.Graph()
            self.graph.start_animated_plotting()

        # Calculate the starting cost of the population
        GenAlg.gen_progress = 0
        for agent in self.pop.pop:
            GenAlg.gen_progress += 1
            agent.update_cost(self.cost_function)

        # Sort population from lowest to highest cost
        self.pop.pop = sorted(self.pop.pop, key=getcost)

        # Print relevant information about Generation 0: [x,y], cost, and the gene with nums rounded to nearest int
        for agent in self.pop.pop:
            if self.verbose: print(f"COST: {agent.cost} GENE(rounded):{[int(i) for i in agent.gene]}")
        if self.verbose: print("-----------------------------------------------")

        # Run max_generations generations
        for gen_index in range(0, max_generations):
            GenAlg.generation_counter += 1
            GenAlg.gen_progress = 0
            # Reproduce, creating a new generation
            self.reproduce(crossover_function, elite_rate)

    def reproduce(self, crossover_function, elite_rate):

        # Make offspring with some of the population. Save top individuals as elitism
        parent_rate = 0.50
        parent_individuals = int(GenAlg.pop_size * parent_rate)
        elite_individuals = max(int(elite_rate * GenAlg.pop_size), 1)  # max(min(int(GenAlg.pop_size * 0.1), 1), 3)  # Min 1, max 3, depending on pop size

        # Sort by cost, ascending
        self.pop.pop = sorted(self.pop.pop, key=getcost)

        # Create a new generation by crossing over and mutating the previous
        new_generation = []
        for i in range(0, parent_individuals-1):
            mut_rate = np.tanh(self.mutation_rate * math.log(i+2, 2))  # Less fit -> mutate more
            mut_size = np.tanh(self.mutation_size + (1-self.mutation_size)/parent_individuals * i)  # Less fit -> mutate more
            # nr_of_children = 3 - max(int(round(i/(parent_individuals*0.333))), 2)  # Less fit -> less children
            nr_of_children = math.ceil(1/parent_rate)
            # Generate a fitness-appropriate amount of offspring
            for j in range(0, nr_of_children):
                # Create children with a crossover function
                children = crossover_function(self.pop.pop[i], self.pop.pop[random.randrange(0, parent_individuals-1)])
                child = children[random.randrange(0, len(children))]  # Pick one of the children randomly
                child.mutate(mut_rate, mut_size, self.value_range)  # Mutate it
                new_generation.append(child)   # Add it to next generation

        GenAlg.pop_size_current = len(new_generation)
        if self.verbose: print(f"GEN {GenAlg.generation_counter} IS BORN, SIZE: {len(new_generation)}")

        # Elitism: Keep the top individuals.
        for i in range(0, elite_individuals):
            # If new_generation does not contain an individual with same gene as self.pop.pop[i]
            # Add self.pop.pop[i] to new generation
            copy = False
            for individual in new_generation:
                if individual.gene == self.pop.pop[i].gene:
                    copy = True
            if not copy:
                new_generation.append(self.pop.pop[i])

        self.pop.pop = new_generation

        # Calculate the cost of individuals in the new generation
        for individual in self.pop.pop:
            individual.update_cost(self.cost_function)

        # Sort by cost, ascending
        self.pop.pop = sorted(self.pop.pop, key=getcost)

        for individual in self.pop.pop:
            if self.verbose: print(f"COST: {individual.cost} GENE(rounded):{[int(i) for i in individual.gene]}")

        # Calculate average cost of the generation
        sumcost = 0
        for individual in self.pop.pop:
            sumcost += individual.cost
        
        min_cost = self.pop.pop[0].cost
        avg_cost = sumcost/len(self.pop.pop)
        if (min_cost) < self.best_cost:
            GenAlg.best_cost = min_cost
        GenAlg.avg_cost = avg_cost
        if self.verbose:
            print(f"MIN COST:{min_cost} AVG COST: {avg_cost}")
            print(f"BEST GENE: {self.pop.pop[0].gene}")
            print(f"END GEN {GenAlg.generation_counter}-----------------------------------------------")

        if self.plot:
            self.graph.add_costs(avg_cost, min_cost, True)

        # Save weights to file:
        ensure_weights_directory()
        file = open(WEIGHTS_DIRECTORY + '/gen' + str(GenAlg.generation_counter) + '_cost' + str(int(min_cost)) + '_avg' + str(int(avg_cost)), 'w')
        file.write(str(self.pop.pop[0].gene))
        file.close()

        return self.pop.pop

    # Rank-based reproduction through random mutations only
    def reproduce_mutate_only(self, elite_rate):

        # Make offspring with some of the population. Save top 1-3 as elitism
        parent_individuals = GenAlg.pop_size  #
        elite_individuals = GenAlg.pop_size * elite_rate

        # Sort by cost, ascending
        self.pop.pop = sorted(self.pop.pop, key=getcost)

        # Create a new generation by crossing over and mutating the previous
        new_generation = []
        for i in range(0, parent_individuals):
            mut_rate = self.mutation_rate * math.log(i + 2, 2)  # Less fit -> mutate more
            mut_size = self.mutation_size + (1 - self.mutation_size) / parent_individuals * i  # Less fit -> mutate more
            nr_of_children = 3 - max(int(round(i / (parent_individuals * 0.333))), 2)  # Less fit -> less children
            for j in range(0, nr_of_children):
                new_generation.append(self.pop.pop[i].mutate(mutation_rate=mut_rate, mutation_size=mut_size, value_range=self.value_range))  # Pick one of the children randomly #

        # Elitism
        for i in range(0, elite_individuals):
            new_generation.append(self.pop.pop[i])

        if self.verbose: print(f"GEN {GenAlg.generation_counter} IS BORN, SIZE: {len(new_generation)}")

        # Calculate the cost of individuals the new generation
        for individual in new_generation:
            individual.update_cost(self.cost_function)
            if self.verbose: print(f"COST: {individual.cost} GENE(rounded):{[int(i) for i in individual.gene]}")

        # Sort by cost, ascending
        self.pop.pop = sorted(self.pop.pop, key=getcost)

        # Calculate average cost of the generation
        sumcost = 0
        for individual in self.pop.pop:
            sumcost += individual.cost
        if self.verbose:
            print("MIN COST:", self.pop.pop[0].cost, "AVG COST:", sumcost / len(self.pop.pop))
            print("BEST GENE: ", self.pop.pop[0].gene)

            print(f"END GEN {GenAlg.generation_counter}-----------------------------------------------")
        return new_generation


#GenAlg(crossover_function=single_point_crossover, gene_length=20, max_generations=20, init_near_zero=False)


def ensure_weights_directory():
    directory = os.path.dirname(WEIGHTS_DIRECTORY + '/temp.txt')
    if not os.path.exists(directory):
        print('Created new weights directory: ' + directory)
        os.makedirs(directory)