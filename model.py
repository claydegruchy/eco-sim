from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random
import statistics
from agent import EcoAgent
from helper_classes import Order, Trade, farmer, roles, resource_finder
from numpy import mean, median


# BO = Order('buy', "man1", 1, 1)
# SO = Order('sell', "man2", 1, 1)

# T = Trade(SO, BO, 1, 1, "a")
# print(BO)
# print(SO)
# print(T)


# exit()


class EcoModel(Model):
    def __init__(self, width, height, num_agents):
        super().__init__()
        print("Model created, proforming setup...")
        self.grid = SingleGrid(width, height, True)
        self.schedule = RandomActivation(self)

        self.current_id = 0
        self.num_agents = num_agents

        print("Setting up resources")
        potential_resources = resource_finder()

        # trade variables
        self.trades = []
        # self.buy_orders = []
        # self.sell_orders = []
        self.orders = []
        self.price_history = dict(
            zip(potential_resources, [[5] for x in range(len(potential_resources))]))

        # report variables
        self.total_trades = 0
        self.day_trades = 0
        self.total_food = 0
        self.total_money = 0
        self.average_money = 0
        self.median_money = 0
        self.current_agents = num_agents
        self.dead_agents = []

        # Create agents
        for i in range(self.num_agents):
            # generate a distribution of efficiency
            # normalised = i / self.num_agents+0.5
            # self.create_agent(random.choice(roles), normalised)
            self.create_agent(random.choice(roles))

        model_reporters = {"Total Food": "total_food",
                           "Agents": lambda m: m.schedule.get_agent_count(),
                           "Total Money": "total_money",
                           "Average Money": "average_money",
                           "Median Money": "median_money",
                           "Total Trades": "total_trades",
                           "Day Trades": "day_trades",
                           "Dead Agents": lambda m: len(m.dead_agents),
                           }
    # list of resources rpices
        for resource in potential_resources:
            model_reporters[resource +
                            "_price"] = lambda m, resource=resource: m.price_history[resource][-1]
            model_reporters[resource +
                            "_avg_assummed"] = lambda m, resource=resource: mean([a.average_price_assumption(resource) for a in m.schedule.agents])
            model_reporters[resource +
                            "_median_assummed"] = lambda m, resource=resource: median([a.average_price_assumption(resource) for a in m.schedule.agents])

        # role counts
        for role in roles:
            model_reporters[role.name+"_count"] = lambda m, role=role: len(
                [a for a in m.schedule.agents if a.role.name == role.name])

        self.datacollector = DataCollector(
            agent_reporters={"Food": "food",
                             "Money": "money",
                             "Production": "production",
                             },
            model_reporters=model_reporters,
            tables={
                "Final_Values": ["agent_id", "food"]
            }
        )
        print("Model setup complete, starting...")

    def create_agent(self, role, production=0):

        agent = EcoAgent(self.next_id(), self, role)
        agent.production = production
        if production == 0:
            agent.production = random.gauss(1, 0.2)
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        while self.grid.is_cell_empty((x, y)) == False:
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)

        self.grid.place_agent(agent, (x, y))
        self.schedule.add(agent)
        print("Agent created", agent.unique_id, agent.role.name)

    def register_buy_order(self, resource, agent, ppu, quantity):
        bo = Order(resource, 'buy', agent, quantity, ppu)
        self.orders.append(bo)
        return bo

    def register_sell_order(self, resource, agent, ppu, quantity):
        so = Order(resource, 'sell', agent, quantity, ppu)
        self.orders.append(so)
        return so

    def resolve_orders(self):
        print("Market opened")
        self.day_trades = 0
        total_orders = len(self.orders)

        for resource in set([order.resource for order in self.orders]):
            print("Resolving orders for", resource)
            buy_orders = [
                order for order in self.orders if order.resource == resource and order.type == 'buy']
            sell_orders = [
                order for order in self.orders if order.resource == resource and order.type == 'sell']

            buy_orders.sort(key=lambda x: x.ppu, reverse=True)
            sell_orders.sort(key=lambda x: x.ppu)

            orders = min(len(buy_orders), len(sell_orders))

            print("Buy orders:", len(buy_orders))
            print("Sell orders:", len(sell_orders))

            while orders > 0:
                buy_order = buy_orders[0]
                sell_order = sell_orders[0]
                # resolve the first order
                # find an average between the two prices
                price = (buy_order.ppu + sell_order.ppu) / 2
                quantity = min(buy_order.quantity, sell_order.quantity)
                if quantity*price > buy_order.initator.money:
                    print("Not enough money to buy", quantity,
                          "of", resource, "at", price)
                    quantity = buy_order.initator.money / price
                    print("Buying", quantity, "instead")
                trade = Trade(resource, sell_order, buy_order, quantity, price)
                # trade and fulfill the orders
                self.register_trade(trade)
                # remove the order if it is empty, and tell the agent to update their price assumption
                if sell_order.is_fulfilled():
                    sell_order.resolve_order()
                    sell_orders.pop(0)

                if buy_order.is_fulfilled():
                    buy_order.resolve_order()
                    buy_orders.pop(0)

                orders -= 1
        # print("Resources:", resources)
        print("Market closed",
              f"{self.day_trades} trades and {total_orders} orders")
        return

    def register_trade(self, trade: Trade):
        # register the trade
        self.trades.append(trade)
        # sort out the money
        trade.sell_order.initator.money += trade.ppu*trade.quantity
        trade.buy_order.initator.money -= trade.ppu*trade.quantity
        # transfer resources
        trade.sell_order.initator.remove_resource(
            trade.resource, trade.quantity)
        trade.buy_order.initator.add_resource(trade.resource, trade.quantity)
        # fulfill the orders
        trade.sell_order.fulfill(trade.quantity)
        trade.buy_order.fulfill(trade.quantity)

        self.total_trades += 1
        self.day_trades += 1

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def generate_stats(self):
        money_temp = 0
        for x in self.schedule.agents:
            money_temp += x.money
        self.average_money = money_temp / self.current_agents
        self.median_money = statistics.median(
            [x.money for x in self.schedule.agents])
        self.total_money = money_temp/10

    def update_trade_history(self):
        if len(self.trades) < 1:
            return
        resources = set([trade.resource for trade in self.trades])
        for resource in resources:
            trades_ppus = [
                t.ppu for t in self.trades if t.resource == resource]
            average_price = sum(trades_ppus) / len(trades_ppus)
            self.price_history[resource].append(average_price)

    def update_price_assumptions(self):

        # this needs reversal as we now have more orders than agents
        for order in self.orders:
            order.initator.update_price_assumption(order)
            # for agent in self.schedule.agents:
        #     orders = [order for order in self.orders if order.initator == agent]
        #     for order in orders:
        #         agent.update_price_assumptions(order)

    def find_role(self, agent):
        profitability = [
            [role, role.get_profitability(agent)] for role in roles]

        # select the role with the highest profitability
        profitability.sort(key=lambda x: x[1], reverse=True)

        print("Agent", agent.unique_id, "role updated to most profitable role:",
              profitability[0][0].name, profitability[0][1])
        return profitability[0][0]

    def kill_agent(self, agent):
        print("Agent died", agent.unique_id)
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)
        self.dead_agents.append(agent)
        self.create_agent(random.choice(roles))

    def step(self):
        self.schedule.step()

        self.resolve_orders()

        self.current_agents = self.schedule.get_agent_count()
        self.update_trade_history()
        self.update_price_assumptions()

        # if all agents are dead, stop the simulation
        if len(self.schedule.agents) == 0:
            self.running = False
        self.generate_stats()
        self.datacollector.collect(self)
        self.trades.clear()
        self.orders.clear()
