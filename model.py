from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random
import statistics


class EcoAgent(Agent):
    def __init__(self, unique_id, model, color="red"):
        super().__init__(unique_id, model)
        self.food = 10  # Starting food
        self.desired_food = 20  # Desired food
        self.money = 100  # Starting money
        self.production = random.uniform(0, 2)  # Starting production

    def step(self):
        self.consume_resources()
        self.produce_resources()
        self.trade()

    def trade(self):
        # Attempt to trade with random neighbor

        if self.food > self.desired_food:
            neighbors = random.sample(self.model.schedule.agents, 1)
            self.model.register_trade(self, neighbors[0], 5, 5)

    def consume_resources(self):
        # Agent resource consumption logic
        self.food -= 1
        if self.food <= 0:
            self.food = 0
            self.model.kill_agents.append(self)

    def produce_resources(self):
        # Agent resource production logic
        produced = 1*self.production
        self.food = self.food + produced
        self.model.total_food += produced


class EcoModel(Model):
    def __init__(self, width, height, num_agents):
        super().__init__()
        self.current_id = 0

        self.num_agents = num_agents
        self.current_agents = num_agents
        self.grid = SingleGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.kill_agents = []
        self.trades = []

        self.buy_orders = []
        self.sell_orders = []

        self.total_trades = 0
        self.total_food = 0
        self.total_money = 0
        self.average_money = 0
        self.median_money = 0

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
                             "Desired Food": "desired_food",
                             },
            model_reporters={"Total Food": "total_food",
                             "Agents": "current_agents",
                             "Total Money": "total_money",
                             "Average Money": "average_money",
                             "Median Money": "median_money",
                             }
        )

    # def get_price():
    #     # returns the current price
    #     for x in self.agents:

    def register_buy_order(self, agent, ppu, quantity):
        self.buy_orders.append((agent, ppu))

    def register_sell_order(self, agent, ppu, quantity):
        self.sell_orders.append((agent, ppu))

    def resolve_orders(self):
        # resolve buy orders
        for x in self.buy_orders:
            for y in self.sell_orders:
                if x[1] >= y[1]:
                    # trade
                    self.register_trade(x[0], y[0], x[1], y[1])
                    self.buy_orders.remove(x)
                    self.sell_orders.remove(y)
                    break

    def register_trade(self, seller, buyer, quantity, price):
        # registers a trade between two agents

        # register the trade
        self.trades.append((seller, buyer, quantity, price))

        buyer.food += quantity
        buyer.money -= price
        seller.food -= quantity
        seller.money += price

        # print("Trade registered")

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
        self.current_agents = self.schedule.get_agent_count()

        # if all agents are dead, stop the simulation
        if len(self.schedule.agents) == 0:
            self.running = False
        money_temp = 0
        for x in self.schedule.agents:
            money_temp += x.money
        self.average_money = money_temp / self.current_agents
        self.median_money = statistics.median(
            [x.money for x in self.schedule.agents])
        self.total_money = money_temp/10
