import random
import math
import costfuncs


def getcost(agent):
    return agent.cost


def single_point_crossover(parent1, parent2):
    point = random.randrange(1, len(parent1.gene) - 1)
    gene1 = parent1.gene[0:point] + parent2.gene[point:]
    child1 = Agent(gene1)
    gene2 = parent1.gene[0:point] + parent1.gene[point:]
    child2 = Agent(gene2)
    return [child1, child2]


def two_point_crossover(parent1, parent2):
    length = max(len(parent1.gene), len(parent2.gene))
    point1 = random.randrange(0, int(length-1*0.66))  # Put the first point somewhere in the first two thirds
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

    return [gene1, gene2, gene3, gene4, gene5, gene6]


class Agent:
    def __init__(self, gene, cost=0):
        self.gene = gene
        self.cost = cost

    def mutate(self, mutation_rate, mutation_size, output_range):
        output_range_size = abs(output_range[1] - output_range[0])
        for nucleotide in self.gene:
            if random.random() < mutation_rate:
                nucleotide += max(
                    min(
                        random.randrange(-1, 2, 2) * mutation_size * output_range_size,
                        output_range[1]),
                    output_range[0])

    def mutant_clone(self, mutation_rate, mutation_size, output_range):
        clone = Agent(self.gene, self.cost)
        clone.mutate(mutation_rate, mutation_size, output_range)
        return clone

    def clones(self, number_of_clones):
        offspring = []
        for i in range(0, number_of_clones-1):
            child = Agent(self.gene, self.cost)
            offspring.append(child)
        return offspring

    def get_output_params(self, number_of_params):
        out = []
        for i in range(0, number_of_params):
            section_length = int(len(self.gene)/number_of_params)
            out.append(sum(self.gene[i*section_length:(i+1)*section_length]))
        return out

    def update_cost(self, cost_function):
        out = self.get_output_params(2)
        self.cost = cost_function(out[0], out[1])
        return self.cost


class Population:
    def __init__(self,
                 pop_size=20,
                 gene_length=5,
                 mutation_rate=0.05,
                 mutation_size=0.5,
                 elite_rate=0.1,
                 max_generations=500,
                 output_range=[-5, 5]):
        self.pop_size = pop_size
        self.gene_length = gene_length
        self.mutation_rate = mutation_rate
        self.mutation_size = mutation_size
        self.elite_rate = elite_rate
        self.pop = []
        self.output_range = output_range
        self.elite_units = self.pop_size * self.elite_rate
        self.max_generations = max_generations

        # Initialize genes randomly
        for pop_index in range(0, pop_size):
            gene = []
            for gene_index in range(0, gene_length):
                gene.append(random.uniform(output_range[0], output_range[1]))
            self.pop.append(Agent(gene))


class GenAlg:
    def __init__(self,
                 cost_function=costfuncs.rosenbrock,
                 crossover_function=single_point_crossover,
                 pop_size=20,
                 gene_length=5,
                 mutation_rate=0.1,
                 mutation_size=0.5,
                 elite_rate=0.05,
                 max_generations=20,
                 output_range=[-5, 5]):
        self.cost_function = cost_function
        self.pop_size = pop_size
        self.output_range = output_range
        self.mutation_rate = mutation_rate
        self.mutation_size = mutation_size
        self.generation_counter = 1
        self.pop = Population(pop_size,gene_length,mutation_rate,mutation_size,elite_rate,max_generations,output_range)

        print("GEN 0 IS BORN, SIZE: ", len(self.pop.pop))
        for agent in self.pop.pop:
            agent.update_cost(self.cost_function)
        self.pop.pop = sorted(self.pop.pop, key=getcost)
        for agent in self.pop.pop:
            out = agent.get_output_params(2)
            print(f"OUT:[%.2f,%.2f] COST: {agent.cost} GENE(rounded):{[int(i) for i in agent.gene]}" % (out[0], out[1]))
        print("-----------------------------------------------")

        # Run X generations
        for gen_index in range(0, max_generations):
            # Reproduce, creating a new generation
            self.pop.pop = self.reproduce(crossover_function)
            self.generation_counter += 1

            # Calculate fitness/cost of every individual in the current generation
            for agent in self.pop.pop:
                out = agent.get_output_params(2)
                agent.cost = cost_function(out[0], out[1])

        # Sort by cost, ascending, and print minimal and average cost
        self.pop.pop = sorted(self.pop.pop, key=getcost)
        sumcost = 0
        for agent in self.pop.pop:
            sumcost += agent.cost
        print("MIN COST: ", self.pop.pop[0].cost, ", AVG COST:", sumcost/len(self.pop.pop))
        print("[x,y] of min cost individual: ", self.pop.pop[0].get_output_params(2))

    def single_point_crossover(self, parent1, parent2):
        point = random.randrange(1, len(parent1.gene) - 1)
        gene1 = parent1.gene[0:point] + parent2.gene[point:]
        child1 = Agent(gene1)
        gene2 = parent1.gene[0:point] + parent1.gene[point:]
        child2 = Agent(gene2)
        return [child1, child2]

    def two_point_crossover(self, parent1, parent2):
        length = max(len(parent1.gene), len(parent2.gene))
        point1 = random.randrange(0, length - 2)
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

        return [gene1, gene2, gene3, gene4, gene5, gene6]

    def reproduce(self, crossover_function):
        # Make offspring with some of the population. Save top 1-3 as elitism
        parent_individuals = self.pop_size  # int(self.pop_size * 0.75)
        elite_individuals = max(min(int(self.pop_size * 0.1), 1), 3)  # Min 1, max 3, depending on pop size

        # Sort by cost, ascending
        self.pop.pop = sorted(self.pop.pop, key=getcost)

        new_generation = []
        for i in range(0, parent_individuals-1):
            mut_rate = self.mutation_rate * math.log(i+2, 2)  # Less fit -> mutate more
            mut_size = self.mutation_size + (1-self.mutation_size)/parent_individuals * i  # Less fit -> mutate more
            nr_of_children = 3 - max(int(round(i/(parent_individuals*0.333))), 2)  # Less fit -> less children
            for j in range(0, nr_of_children):
                # Create two children with single point crossover
                children = crossover_function(self.pop.pop[i], self.pop.pop[random.randrange(0, parent_individuals)])
                for child in children:
                    child.mutate(mut_rate, mut_size, self.output_range)
                new_generation.append(children[random.randrange(0, len(children))])  # Pick one of the children randomly

        # Elitism
        for i in range(0, elite_individuals):
            new_generation.append(self.pop.pop[i])

        print(f"GEN {self.generation_counter} IS BORN, SIZE: {len(new_generation)}")
        for agent in self.pop.pop:
            agent.update_cost(self.cost_function)
            out = agent.get_output_params(2)
            print(f"OUT:[%.2f,%.2f] COST: {agent.cost} GENE(rounded):{[int(i) for i in agent.gene]}" % (out[0], out[1]))

        # Sort by cost, ascending
        self.pop.pop = sorted(self.pop.pop, key=getcost)

        sumcost = 0
        for agent in self.pop.pop:
            sumcost += agent.cost
        print("MIN COST:", self.pop.pop[0].cost, "AVG COST:", sumcost/len(self.pop.pop))
        out = self.pop.pop[0].get_output_params(2)
        print("[x,y] BEST: [%.2f,%.2f]" % (out[0], out[1]))
        print("BEST GENE: ", self.pop.pop[0].gene)

        print(f"END GEN {self.generation_counter}-----------------------------------------------")
        return new_generation

    # Rank-based reproduction through random mutations only
    def reproduce_mutate_only(self):
        parent_individuals = int(round(self.pop_size * 0.75))
        elite_individuals = max(min(int(parent_individuals * 0.1), 1), 3)  # Min 1, max 3, depending on pop size
        self.pop.pop = sorted(self.pop.pop, key=getcost)
        sumcost = 0
        for agent in self.pop.pop:
            sumcost += agent.cost
        print("MIN COST:", self.pop.pop[0].cost, ", AVG COST:", sumcost/len(self.pop.pop))
        print("[x,y] of min cost individual: ", self.pop.pop[0].get_output_params(2))

        new_generation = []
        for i in range(0, parent_individuals):
            # Mutate genes further into the list more than those in the beginning
            mut_rate = self.mutation_rate * math.log(i+2, 2)
            mut_size = self.mutation_size + (1-self.mutation_size)/parent_individuals * i
            nr_of_children = 2 - max(int(round(i/(parent_individuals*0.5))), 1)
            for j in range(0, nr_of_children):
                child = self.pop.pop[i].mutant_clone(mut_rate, mut_size, self.output_range)
                new_generation.append(child)

        # Add best agents from last generation
        for i in range(0, elite_individuals):
            new_generation.append(self.pop.pop[i])

        for child in new_generation:
            out = child.get_output_params(2)
            child.cost = self.cost_function(out[0], out[1])

        print("GEN ", self.generation_counter, "IS BORN, SIZE: ", len(new_generation))
        return new_generation


GenAlg()

