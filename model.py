from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random
import statistics
from agent import EcoAgent
from helper_classes import Order, Trade, farmer, roles, resource_finder


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
        # self.average_price_assumption = 5
        self.avg_price_assumption_bottom = 0
        self.avg_price_assumption_top = 0

        # Create agents
        for i in range(self.num_agents):
            normalised = i / self.num_agents+0.5
            # Use next_id() to generate unique agent id
            agent = EcoAgent(self.next_id(), self, farmer)
            agent.production = normalised

            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            while self.grid.is_cell_empty((x, y)) == False:
                x = random.randrange(self.grid.width)
                y = random.randrange(self.grid.height)

            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

        model_reporters = {"Total Food": "total_food",
                           "Agents": lambda m: m.schedule.get_agent_count(),
                           "Total Money": "total_money",
                           "Average Money": "average_money",
                           "Median Money": "median_money",
                           "Total Trades": "total_trades",
                           "Day Trades": "day_trades",
                           }
    # list of resources rpices
        for resource in potential_resources:
            model_reporters[resource +
                            "_price"] = lambda m, resource=resource: m.price_history[resource][-1]*10
            model_reporters[resource +
                            "_avg_assummed"] = lambda m, resource=resource: [a.average_price_assumption(resource) for a in m.schedule.agents]

        self.datacollector = DataCollector(
            agent_reporters={"Food": "food",
                             "Money": "money",
                             "Production": "production",


                             },
            model_reporters=model_reporters,
        )
        print("Model setup complete, starting...")

    def test(a):
        print(a, type(a))
        return 1

    def register_buy_order(self, resource, agent, ppu, quantity):
        bo = Order(resource, 'buy', agent, quantity, ppu)
        self.orders.append(bo)

    def register_sell_order(self, resource, agent, ppu, quantity):
        so = Order(resource, 'sell', agent, quantity, ppu)
        self.orders.append(so)

    def resolve_orders(self):
        print("Market opened")
        self.day_trades = 0

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
        print("Market closed")
        return

        self.buy_orders.clear()
        self.sell_orders.clear()

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
        self.day_trades += 10

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def generate_stats(self):
        money_temp = 0
        ass_temp = 0
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
        for order in self.orders:
            order.initator.update_price_assumption(order)

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
