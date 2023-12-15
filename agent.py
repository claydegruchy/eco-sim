from mesa import Agent
import random
import numpy as np
from helper_classes import Role, Order, resource_finder


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
min_price = 0.0000001


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
        # print("Setting up price assumptions")
        for resource in resource_finder():
            if resource in self.price_assumptions:
                continue
            self.price_assumptions[resource] = {}
            self.price_assumptions[resource]['top'] = random.uniform(
                6, 10)
            self.price_assumptions[resource]['bottom'] = random.uniform(
                1, 5)

        print("Setting up agent")
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

        market_average = self.model.price_history[resource][-1]
        favorability = percent(
            market_average, self.average_price_assumption(resource))
        quantity = favorability * \
            (self.resources[resource] - self.desired_resources[resource])
        quantity = round(quantity, 1)
        if quantity > -1 and quantity < 1:
            quantity = 0
        price = self.random_price_assumption(resource)
        # print("market_average", market_average)
        # print("average_price_assumption", price)
        # print("favorability", favorability)
        # print("quantity", quantity)

        if quantity < 0:
            if self.money < 0:
                return
            if price > self.money:
                price = self.average_price_assumption(resource)
                if price > self.money:
                    price = self.money

            # we want to buy from the market
            self.model.register_buy_order(
                resource,
                self,
                max(price, min_price),
                abs(quantity)
            )
        if quantity > 0:
            # we want to sell to the market
            self.model.register_sell_order(
                resource,
                self,
                max(price, min_price),
                abs(quantity)
            )

    def update_price_assumption(self, order: Order):
        # dont base the assumptions directly on the market price
        # this is factored when choosing the sell price in the trade function
        # this should only use the orders that have been fulfilled
        # the ideal situation is to have a 50/50 split of fulfilled orders

        # for order in orders:
        resource = order.resource
        top = self.price_assumptions[resource]['top']
        bottom = self.price_assumptions[resource]['bottom']

        ht = top
        hb = bottom

        change = 0.1
        ppu = order.ppu

        # this is somehow creating a runaway effect where the price assumptions are rising constantly
        # becuase the success of the order is not being used to factor the price assumption
        failure_degree = round(order.fulfilled / order.inital_quantity, 2)

        # people are raising their prices in response to not selling, which is counter logic
        

        if ppu > top:
            top = (top * (1+change))
        elif ppu < bottom:
            bottom = (bottom * (1-change))
        elif bottom <= ppu <= top:
            # narrow the range
            top = (top * (1-change))
            bottom = (bottom * (1+change))
            # print("something went wrong")

        self.price_assumptions[resource]['top'] = max(top, 0)
        self.price_assumptions[resource]['bottom'] = max(bottom, 0)

        ht = round(ht, 2)
        top = round(top, 2)
        hb = round(hb, 2)
        bottom = round(bottom, 2)
        t_percent = round((top-ht)/ht*100, 2)
        b_percent = round((bottom-hb)/hb*100, 2)

        print("PA:", self.unique_id, order.type, resource, f"T:{ht}=>{top}({t_percent}%)",
              f"B:{hb}=>{bottom}({b_percent}%), based on {failure_degree}")

    def change_role(self):
        # find a suitable role
        new_role = self.model.find_role(self)
        # check if the agent has the resources to change roles
        self.update_role(new_role)
        self.clear_orders()

    def starve(self):
        print("Agent starving", self.unique_id)
        if (random.random() < 0.2):
            self.die()

    def die(self):
        # this is called when the agent is starving
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)
        print("Agent died", self.unique_id)
