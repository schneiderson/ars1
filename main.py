from bot import environment as env
from bot import genetic as gen


def num_of_weights(nr_of_input_nodes=13,
                   nr_of_hidden_layers=1,
                   nr_of_hidden_layer_nodes=6,
                   nr_of_output_nodes=2,
                   recurrence=True):
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


def load_weights_from_file(path):
    file = open(path, 'r')
    weights_string = file.read()
    weights_list = weights_string.split()
    weights_float = [None] * len(weights_list)
    for i in range(0, len(weights_list)):
        weight = weights_list[i]
        weight = weight.replace('[','')
        weight = weight.replace(']','')
        weight = weight.replace(',','')
        weights_float[i] = float(weight)
    return weights_float


if __name__ == "__main__":
    environment = env.Environment()

    # Some untrained manual runs:
    # Simulate a game with graphics enabled at speed 1 for 20 seconds
    # print("Simulation fitness result: " + str(environment.simulate(True, 1, 20)))

    # Simulate a 90 second game at x20 speed without graphics
    # print("Simulation fitness result: " + str(environment.simulate(True, 20, 90)))

    # Load weights from a previous simulation:
    # weights = load_weights_from_file('weights/saved/weights_20180308-235402/gen8_cost-4036_avg-4036')
    # print("Simulation fitness result: " + str(environment.simulate(True, 0, 0, weights=weights, static_delta_t=200)))

    recurrence = True

    # Start the genetic algorithm
    def costfunc(gene):
        return -environment.simulate(False, 0, 90, weights=gene, static_delta_t=200, recurrence=recurrence)  # Return minus to convert fitness to cost


    gene_length = num_of_weights(nr_of_input_nodes=13,
                                 nr_of_hidden_layers=1,
                                 nr_of_hidden_layer_nodes=6,
                                 nr_of_output_nodes=2,
                                 recurrence=recurrence)

    genetic_algorithm = gen.GenAlg(cost_function=costfunc, gene_length=gene_length, pop_size=30, value_range=[-20, 20])

