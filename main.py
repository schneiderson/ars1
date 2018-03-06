from bot import environment as env

if __name__ == "__main__":
    environment = env.Environment()

    # Simulate a game with graphics enabled at speed 1 for 20 seconds
    print("Simulation fitness result: " + str(environment.simulate(True, 1, 20)))

    # Simulate a 90 second game at x1000 speed without graphics
    #print("Simulation fitness result: " + str(environment.simulate(False, 1000, 90)))

    # TODO: Start the genetic algorithm
