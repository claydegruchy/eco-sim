from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random


class EcoAgent(Agent):
    def __init__(self, unique_id, model, color="red"):
        super().__init__(unique_id, model)
        self.food = 10  # Starting food
        self.desired_food = 20  # Desired food
        self.money = 100  # Starting money
        self.production = random.randrange(0, 2)  # Starting production

    def step(self):
        self.consume_resources()
        self.produce_resources()
        self.trade()

    def trade(self):
        # Attempt to trade with random neighbor
        neighbors = random.sample(self.model.schedule.agents, 1)

        self.model.register_trade(self, neighbors[0], 1, 1)

    def consume_resources(self):
        # Agent resource consumption logic
        self.food -= 1
        if self.food <= 0:
            self.food = 0
            self.model.kill_agents.append(self)

    def produce_resources(self):
        # Agent resource production logic
        self.food = self.food*self.production


class EcoModel(Model):
    def __init__(self, width, height, num_agents):
        super().__init__()
        self.current_id = 0

        self.num_agents = num_agents
        self.grid = SingleGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.kill_agents = []
        self.trades = []

        # Create agents
        for i in range(self.num_agents):
            # Use next_id() to generate unique agent id
            agent = EcoAgent(self.next_id(), self)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            while self.grid.is_cell_empty((x, y)) == False:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)

            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

        self.datacollector = DataCollector(
            agent_reporters={"Food": "food",
                             "Money": "money",
                             "Production": "production",
                             "Desired Food": "desired_food"},
        )

    # def get_price():
    #     # returns the current price
    #     for x in self.agents:

    def register_trade(self, seller, buyer, quantity, price):
        # registers a trade between two agents

        # register the trade
        self.trades.append((seller, buyer, quantity, price))

        buyer.food += quantity
        buyer.money -= price
        seller.food -= quantity
        seller.money += price

        print("Trade registered")

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        for x in self.kill_agents:
            if (random.random() < 0.5):
                print("Agent died", x.unique_id)
                self.grid.remove_agent(x)
                self.schedule.remove(x)
        self.kill_agents.clear()

        # if all agents are dead, stop the simulation
        if len(self.schedule.agents) == 0:
            self.running = False
