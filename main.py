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
    # Simulate a game with graphics enabled at speed 1 for 20 seconds, without movement model
    # print("Simulation fitness result: " + str(environment.simulate(True, 1, 20)))

    # Simulate a 90 second game at x20 speed without graphics, without movement model
    # print("Simulation fitness result: " + str(environment.simulate(True, 20, 90)))

    recurrence = True

    # Load weights from a previous simulation:
    weights = load_weights_from_file('weights/saved/dt200_180sec_slidescostfunc/gen5_cost-1_avg0')
    print("Simulation fitness result: " + str(environment.simulate(True, 5, 0, weights=weights, static_delta_t=200, recurrence=recurrence)))

    # Start the genetic algorithm
    def costfunc(gene):
        cost = 0
        graphics = False
        time_dilation = 0
        simulation_time = 180
        delta_t = 200
        cost -= environment.simulate(graphics, time_dilation, simulation_time, weights=gene, static_delta_t=delta_t, recurrence=recurrence, start_x=400, start_y=175, start_angle=0) # Start in the middle
        cost -= environment.simulate(graphics, time_dilation, simulation_time, weights=gene, static_delta_t=delta_t, recurrence=recurrence, start_x=80, start_y=80, start_angle=45)  # Start in corner
        cost -= environment.simulate(graphics, time_dilation, simulation_time, weights=gene, static_delta_t=delta_t, recurrence=recurrence, start_x=400, start_y=550, start_angle=270)  # Start next to a wall
        return cost

    gene_length = num_of_weights(nr_of_input_nodes=13,
                                 nr_of_hidden_layers=1,
                                 nr_of_hidden_layer_nodes=6,
                                 nr_of_output_nodes=2,
                                 recurrence=recurrence)

    # genetic_algorithm = gen.GenAlg(cost_function=costfunc, gene_length=gene_length, verbose=True, plot=True)

