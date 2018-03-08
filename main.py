from bot import environment as env
import gen
from bot import ann


def num_of_weights(nr_of_input_nodes=12,
                   nr_of_hidden_layers=1,
                   nr_of_hidden_layer_nodes=6,
                   nr_of_output_nodes=2,
                   recurrence=False):
    nr_of_edges = 0
    if recurrence:
        nr_of_input_nodes += nr_of_output_nodes
    if nr_of_hidden_layers > 0:
        nr_of_edges += nr_of_input_nodes * nr_of_hidden_layer_nodes
        for i in range(1, nr_of_hidden_layers):
            nr_of_edges += nr_of_hidden_layer_nodes ** 2
        nr_of_edges += nr_of_hidden_layer_nodes * nr_of_output_nodes
    else:
        nr_of_edges += nr_of_input_nodes * nr_of_output_nodes

    return nr_of_edges


if __name__ == "__main__":
    environment = env.Environment()

    # Simulate a game with graphics enabled at speed 1 for 20 seconds
    # print("Simulation fitness result: " + str(environment.simulate(True, 1, 20)))


    def costfunc(gene):
        return environment.simulate(True, 5, 5, weights=gene)


    # Simulate a 90 second game at x1000 speed without graphics
    # print("Simulation fitness result: " + str(environment.simulate(False, 1000, 90)))

    # Start the genetic algorithm

    # Determine the length of the gene
    gene_length = num_of_weights(nr_of_input_nodes=12,
                                 nr_of_hidden_layers=1,
                                 nr_of_hidden_layer_nodes=6,
                                 nr_of_output_nodes=2,
                                 recurrence=False)

    genetic_algorithm = gen.GenAlg(cost_function=costfunc, gene_length=gene_length)
