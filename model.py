from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random
import statistics
from agent import EcoAgent
from helper_classes import Order, Trade


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
        self.grid = SingleGrid(width, height, True)
        self.schedule = RandomActivation(self)

        self.current_id = 0

        self.num_agents = num_agents

        # trade variables
        self.trades = []
        self.buy_orders = []
        self.sell_orders = []
        self.orders = []
        self.price_history = [5]

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
                           #    "Average Price Assumption": "average_price_assumption",
                           "avg_price_assumption_bottom": "avg_price_assumption_bottom",
                           "avg_price_assumption_top": "avg_price_assumption_top",
                           }

        self.datacollector = DataCollector(
            agent_reporters={"Food": "food",
                             "Money": "money",
                             "Production": "production",


                             },
            model_reporters=model_reporters

        )

    def register_buy_order(self, agent, ppu, quantity):
        bo = Order('buy', agent, quantity, ppu)
        self.buy_orders.append(bo)

    def register_sell_order(self, agent, ppu, quantity):
        so = Order('sell', agent, quantity, ppu)
        self.sell_orders.append(so)

    def resolve_orders(self):
        print("Market opened")
        self.day_trades = 0
        self.orders = sorted(self.buy_orders + self.sell_orders,
                             key=lambda x: x.fulfilled, reverse=True)

        # sort from highest to lowest price
        self.buy_orders.sort(key=lambda x: x.ppu, reverse=True)

        # sort from lowest to highest price
        self.sell_orders.sort(key=lambda x: x.ppu)

        print("Buy orders:", len(self.buy_orders))
        print("Sell orders:", len(self.sell_orders))

        orders = min(len(self.buy_orders), len(self.sell_orders))
        while orders > 0:
            buy_order = self.buy_orders[0]
            sell_order = self.sell_orders[0]
            # resolve the first order
            # find an average between the two prices
            price = (buy_order.ppu + sell_order.ppu) / 2
            quantity = min(buy_order.quantity, sell_order.quantity)
            trade = Trade(sell_order, buy_order, quantity, price)
            # trade and fulfill the orders
            self.register_trade(trade)
            # remove the order if it is empty, and tell the agent to update their price assumption
            if sell_order.is_fulfilled():
                sell_order.resolve_order()
                self.sell_orders.pop(0)

            if buy_order.is_fulfilled():
                buy_order.resolve_order()
                self.buy_orders.pop(0)

            orders -= 1
        self.buy_orders.clear()
        self.sell_orders.clear()
        print("Market closed")

    def register_trade(self, trade: Trade):
        # register the trade
        self.trades.append(trade)
        # sort out the money
        trade.sell_order.initator.money += trade.ppu*trade.quantity
        trade.buy_order.initator.money -= trade.ppu*trade.quantity
        # sort out the food
        trade.sell_order.initator.food -= trade.quantity
        trade.buy_order.initator.food += trade.quantity
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
        trades_ppus = [t.ppu for t in self.trades]
        average_price = sum(trades_ppus) / len(trades_ppus)
        self.price_history.append(average_price)

    def update_price_assumptions(self):
        avg_price_assumption_bottom = []
        avg_price_assumption_top = []
        for agent in self.schedule.agents:
            agent_orders = [
                order for order in self.orders if order.initator == agent]

            agent.update_price_assumption(agent_orders, self.price_history[-1])
            avg_price_assumption_bottom.append(agent.price_assumption_bottom)
            avg_price_assumption_top.append(agent.price_assumption_top)

        self.avg_price_assumption_bottom = statistics.mean(
            avg_price_assumption_bottom)*10
        self.avg_price_assumption_top = statistics.mean(
            avg_price_assumption_top)*10

        # exit()

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
