from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random
import statistics
from agent import EcoAgent


def random_string(length=5):
    x = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(x) for _ in range(length))


class EcoModel(Model):
    def __init__(self, width, height, num_agents):
        super().__init__()
        self.grid = SingleGrid(width, height, True)
        self.schedule = RandomActivation(self)

        self.current_id = 0

        self.num_agents = num_agents
        # utility variables
        self.kill_agents = []

        # trade variables
        self.trades = []
        self.buy_orders = []
        self.sell_orders = []

        self.historical_average = 0

        # report variables
        self.total_trades = 0
        self.day_trades = 0
        self.total_food = 0
        self.total_money = 0
        self.average_money = 0
        self.median_money = 0
        self.current_agents = num_agents
        self.average_price_assumption = 5

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

        model_reporters = {"Total Food": "total_food",
                           "Agents": "current_agents",
                           "Total Money": "total_money",
                           "Average Money": "average_money",
                           "Median Money": "median_money",
                           "Total Trades": "total_trades",
                           "Day Trades": "day_trades",
                           "Average Price Assumption": "average_price_assumption",
                           }

        self.datacollector = DataCollector(
            agent_reporters={"Food": "food",
                             "Money": "money",
                             "Production": "production",
                             "Desired Food": "desired_food",
                             },
            model_reporters=model_reporters

        )

    def register_buy_order(self, agent, ppu, quantity):
        unique_transaction_id = "["+random_string()+"]"
        print(unique_transaction_id, "Buy order registered", agent.unique_id,
              "price:", ppu, "quantity:", quantity)
        self.buy_orders.append([
            agent,
            ppu,
            quantity,
            unique_transaction_id,
            0])

    def register_sell_order(self, agent, ppu, quantity):
        unique_transaction_id = "["+random_string()+"]"
        print(unique_transaction_id, "Sell order registered", agent.unique_id,
              "price:", ppu, "quantity:", quantity)
        self.sell_orders.append([
            agent,
            ppu,
            quantity,
            unique_transaction_id,
            0])

    def resolve_orders(self):
        print("Market opened")
        self.day_trades = 0

        # sort from highest to lowest price
        self.buy_orders.sort(key=lambda x: x[1], reverse=True)

        # sort from lowest to highest price
        self.sell_orders.sort(key=lambda x: x[1])

        orders = min(len(self.buy_orders), len(self.sell_orders))
        while orders > 0:
            # resolve the first order
            # find an average between the two prices
            price = (self.buy_orders[0][1] + self.sell_orders[0][1]) / 2
            quantity = min(self.buy_orders[0][2], self.sell_orders[0][2])

            seller = self.sell_orders[0][0]
            buyer = self.buy_orders[0][0]

            # trade
            self.register_trade(
                seller, buyer, quantity, price, self.buy_orders[0][3] + "=>" + self.sell_orders[0][3])

            self.sell_orders[0][2] -= quantity
            self.sell_orders[0][4] += quantity
            self.buy_orders[0][2] -= quantity
            self.buy_orders[0][4] += quantity

            # remove the order if it is empty, and tell the agent to update their price assumption

            if self.sell_orders[0][2] <= 0:
                print(self.sell_orders[0][3], "Sell order resolved",)
                seller.update_price_assumption(
                    'sell', True,  self.sell_orders[0][1], self.sell_orders[0][2], self.sell_orders[0][4], )

                self.sell_orders.pop(0)

            if self.buy_orders[0][2] <= 0:
                print(self.buy_orders[0][3], "Buy order resolved",)
                buyer.update_price_assumption(
                    'buy', True,  self.buy_orders[0][1], self.buy_orders[0][2], self.buy_orders[0][4], )

                self.buy_orders.pop(0)

            orders -= 1

        # discard all other orders, tell the failed agents to update their price assumptions
        for order in self.buy_orders:
            print(order[3], order[0].agent_name(), "Buy order discarded, remaining:",
                  order[2], "satisfied:", order[4])
            order[0].update_price_assumption(
                'buy', False, order[1], order[2], order[4], )
        for order in self.sell_orders:
            print(order[3], order[0].agent_name(), "sell order discarded, remaining:",
                  order[2], "satisfied:", order[4])
            order[0].update_price_assumption(
                'sell', False, order[1], order[2], order[4], )

        self.buy_orders.clear()
        self.sell_orders.clear()

        print("Market closed")

    def register_trade(self, seller, buyer, quantity, price, unique_transaction_id):
        # register the trade
        self.trades.append((seller, buyer, quantity, price))
        print(unique_transaction_id, "Trade registered", seller.agent_name(), "to",
              buyer.agent_name(), "quantity:", quantity, " at ppu:", price, "total:", price*quantity)

        buyer.food += quantity
        buyer.money -= price*quantity
        seller.food -= quantity
        seller.money += price*quantity

        self.total_trades += 1
        self.day_trades += 10

        # print("Trade registered")

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def generate_stats(self):
        money_temp = 0
        ass_temp = 0
        for x in self.schedule.agents:
            money_temp += x.money
            ass_temp += x.price_assumption
        self.average_price_assumption = (ass_temp/self.current_agents) * 10
        self.average_money = money_temp / self.current_agents
        self.median_money = statistics.median(
            [x.money for x in self.schedule.agents])
        self.total_money = money_temp/10

    def step(self):
        self.schedule.step()

        self.resolve_orders()

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
        self.generate_stats()
        self.datacollector.collect(self)
