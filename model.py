from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import random
import statistics
from agent import EcoAgent
import enum as Enum


def random_string(length=5):
    x = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(x) for _ in range(length))


class _Base_Order:
    def __init__(self, quantity, ppu, id=None):
        self.quantity = quantity
        self.ppu = round(ppu, 3)
        self.id = id
        if id == None:
            self.id = random_string()

    def __str__(self):
        return f"ID:{self.id} V:{type(self).__name__} QTY:{self.quantity} PPU:{self.ppu} "

    def __repr__(self):
        return self.__str__()


class Order(_Base_Order):
    def __init__(self, type, initator, quantity, ppu, fulfilled=0):
        _Base_Order.__init__(self,  quantity, ppu)
        self.initator = initator
        self.type = type
        self.fulfilled = fulfilled
        self.inital_quantity = quantity
        

        if type not in ["buy", "sell"]:
            raise Exception("Invalid order type, must be buy or sell")
        print("Order created", self)

    def __str__(self):
        return f"ID:{self.id} O:{self.type} V:{type(self).__name__} QTY:{self.fulfilled}/{self.quantity} PPI:{self.ppu} "

    def fulfill(self, quantity):
        print("Order fulfilled", self)
        self.fulfilled += quantity
        self.quantity -= quantity

    def is_fulfilled(self):
        return self.fulfilled >= self.quantity

    def resolve_order(self):
        print(self,"Order resolved" )

    def discard_order(self):
        print(self, "Order discarded")


class Trade(_Base_Order):
    def __init__(self, sell_order, buy_order, quantity, ppu, state):
        _Base_Order.__init__(self, quantity, ppu,
                             sell_order.id + "=>" + buy_order.id)
        self.sell_order = sell_order
        self.buy_order = buy_order
        self.state = state


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
        bo = Order('buy', agent, quantity, ppu)
        self.buy_orders.append(bo)

    def register_sell_order(self, agent, ppu, quantity):
        so = Order('sell', agent, quantity, ppu)
        self.sell_orders.append(so)

    def resolve_orders(self):
        print("Market opened")
        self.day_trades = 0

        # sort from highest to lowest price
        self.buy_orders.sort(key=lambda x: x.ppu, reverse=True)

        # sort from lowest to highest price
        self.sell_orders.sort(key=lambda x: x.ppu)

        print("Buy orders:", self.buy_orders)
        print("Sell orders:", self.sell_orders)

        orders = min(len(self.buy_orders), len(self.sell_orders))
        while orders > 0:

            #  self.sell_orders.append([
            #         agent,
            #         ppu,
            #         quantity,
            #         unique_transaction_id,
            #         0])

            # Order()
            # Trade()
            buy_order = self.buy_orders[0]
            sell_order = self.sell_orders[0]
            # resolve the first order
            # find an average between the two prices
            price = (buy_order.ppu + sell_order.ppu) / 2
            quantity = min(buy_order.quantity, sell_order.quantity)

            # sell_order.initiator
            # buy_order.initiator

            trade = Trade(sell_order, buy_order, quantity, price, "unresolved")

            # trade and fulfill the orders
            self.register_trade(trade)

            # remove the order if it is empty, and tell the agent to update their price assumption

            if sell_order.is_fulfilled():
 
                sell_order.initator.update_price_assumption(
                type='sell',
                successful=True,
                ppu=sell_order.ppu,
                remaining_quantity=sell_order.quantity,
                total_quantity=sell_order.inital_quantity,
                )
                
                sell_order.resolve_order()

                self.sell_orders.pop(0)

            if buy_order.is_fulfilled():
                # [FIXME]
                print(self.buy_orders[0][3]
                "Buy order resolved",)
                buy_order.initator.update_price_assumption(
                    type, successful, ppu, remaining_quantity, total_quantity
                    'buy', True,  self.buy_orders[0][1], self.buy_orders[0][2], self.buy_orders[0][4], )

                self.buy_orders.pop(0)

            orders -= 1

        # discard all other orders, tell the failed agents to update their price assumptions
        for order in self.buy_orders:
            order.update_price_assumption(
                type='buy', successful=False, ppu=order.ppu, remaining_quantity=order.quantity, total_quantity=order.inital_quantity)
            order.discard_order()
        for order in self.sell_orders:
            order.update_price_assumption(
                type='sell', successful=False, ppu=order.ppu, remaining_quantity=order.quantity, total_quantity=order.inital_quantity)

        self.buy_orders.clear()
        self.sell_orders.clear()

        print("Market closed")

    def register_trade(self, trade: Trade):
        # register the trade
        self.trades.append(trade)
        # print(unique_transaction_id, "Trade registered", seller.agent_name(), "to",
        #       buyer.agent_name(), "quantity:", quantity, " at ppu:", price, "total:", price*quantity)
        # sort out the money
        trade.sell_order.initator.money += trade.ppu*trade.quantity
        trade.buy_order.initator.money -= trade.ppu*trade.quantity
        # sort out the food
        trade.sell_order.initator.food -= trade.quantity
        trade.buy_order.initator.food += trade.quantity
        # fulfill the orders
        trade.sell_order.fulfill(trade.quantity)
        trade.buy_order.fulfill(trade.quantity)

        trade.state = "resolved"

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
