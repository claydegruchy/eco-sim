from mesa import Agent
import random
import numpy as np
from helper_classes import Recipe, Role, farmer, roles


def percent(part, whole):
    # normalize to either 0 or 1
    # remaining_quantity, inital_quantity
    if part == 0.0 or whole == 0.0:
        return 0.0
    return float(part)/float(whole)


# def scale_range(input, min, max):
#     input = input + -(np.min(input))
#     input = input / np.max(input) / (max - min)
#     input = input + min
#     return input.tolist()


# print(scale_range([0,5,10], 0, 1))
# exit()


class EcoAgent(Agent):
    def __init__(self, unique_id, model, role, color="red"):
        super().__init__(unique_id, model)

        self.resources = {
            "food": 20,
        }
        self.desired_resources = {}

        self.price_assumptions = {
            "food": {
                "top": 6,
                "bottom": 4,
            },
        }

        self.latest_market_prices = {
        }

        self.update_role(role)
        self.money = 100  # Starting money
        self.production = random.uniform(0, 2)  # Starting production
        # self.production = random.gauss(1, 0.1)  # Starting production

        self.orders = []

    def update_role(self, role):
        self.role = role
        self.desired_resources = role.desired_resources

    def clear_orders(self):
        self.orders = []

    def average_price_assumption(self, resource):
        # Average price assumption
        return self.price_assumptions[resource]['top'] + self.price_assumptions[resource]['bottom'] / 2

    def random_price_assumption(self, resource):
        # Average price assumption
        return random.uniform(self.price_assumptions[resource]['top'], self.price_assumptions[resource]['bottom'])

    def step(self):
        self.consume_resources()
        self.produce_resources()
        self.trade()

    def agent_name(self):
        return f"Agent {self.unique_id}"

    # resouce handlers
    def get_resource(self, resource):
        return self.resources[resource]

    def add_resource(self, resource, quantity):
        self.resources[resource] += quantity

    def remove_resource(self, resource, quantity):
        self.resources[resource] -= quantity
        if self.resources[resource] < 0:
            self.resources[resource] = 0

    def consume_resources(self):
        # Agent resource consumption logic
        self.remove_resource("food", 1)
        # print("Agent consuming resources", self.unique_id, self.resources)
        if self.get_resource("food") < 1:
            self.starve()

    def produce_resources(self):
        self.role.make_recipe(self)

    def trade(self):
        for resouce in self.desired_resources:
            self.trade_resource(resouce)

    def trade_resource(self, resource):
        '''
        Determine-Sale-Quantity(Commodity)
            1 mean←historical mean price of Commodity
            2 favorability←position of mean within observed trading range
            3 amount to sell ←favorability * excess resources of Commodity
            4 return amount to sell
        '''
        if (resource not in self.latest_market_prices):
            self.latest_market_prices[resource] = 5

        market_average = self.latest_market_prices[resource]
        favorability = percent(
            market_average, self.average_price_assumption(resource))
        quantity = favorability * \
            (self.resources[resource] - self.desired_resources[resource])
        quantity = round(quantity, 1)
        if quantity > -1 and quantity < 1:
            quantity = 0
        price = self.random_price_assumption(resource)
        # print("market_average", market_average)
        # print("average_price_assumption", self.average_price_assumption())
        # print("favorability", favorability)
        # print("quantity", quantity)
        if price > self.money:
            price = self.average_price_assumption(resource)
            if price > self.money:
                price = self.money

        if quantity < 0:
            # we want to buy from the market
            self.model.register_buy_order(
                resource,
                self,
                price,
                abs(quantity)
            )
        if quantity > 0:
            # we want to sell to the market
            self.model.register_sell_order(
                resource,
                self,
                price,
                abs(quantity)
            )

    def update_price_assumption(self, order):
        # dont base the assumptions directly on the market price
        # this is factored when choosing the sell price in the trade function
        # this should only use the orders that have been fulfilled
        # the ideal situation is to have a 50/50 split of fulfilled orders

        # for order in orders:
        resource = order.resource
        top = self.price_assumptions[resource]['top']
        bottom = self.price_assumptions[resource]['bottom']

        change = 0.05

        ppu = order.ppu

        if ppu > top:
            # print(
                # f"[{order.type}]Ripoff! i paid too much {ppu} but i thought it was {top}")
            top = (top * (1+change))

        elif ppu < bottom:
            # print(
                # f"[{order.type}]cheap! i paid {ppu} but i thought it was {top}")
            bottom = (bottom * (1-change))

        elif bottom <= ppu <= top:
            # print(
                # f"[{order.type}]we are in the sweet spot, i paid {ppu}, right in the middle of {bottom} and {top}")
            # narrow the range
            top = (top * (1-change))
            bottom = (bottom * (1+change))
        else:
            print("something went wrong")
        self.price_assumptions[resource]['top'] = top
        self.price_assumptions[resource]['bottom'] = bottom

    def starve(self):
        print("Agent starving", self.unique_id)
        if (random.random() < 0.2):
            self.die()

    def die(self):
        # this is called when the agent is starving
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)
        print("Agent died", self.unique_id)
