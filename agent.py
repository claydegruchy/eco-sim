from mesa import Agent
import random
import numpy as np


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
    def __init__(self, unique_id, model, color="red"):
        super().__init__(unique_id, model)
        self.food = 20  # Starting food
        self.desired_food = 20  # Desired food
        self.money = 100  # Starting money
        self.production = random.uniform(0, 2)  # Starting production

        self.orders = []
        # Starting price assumption
        self.price_assumption_top = 6 + random.uniform(-0.1, 0.1)
        self.price_assumption_bottom = 4 + random.uniform(-0.1, 0.1)
        self.latest_market_price = (
            self.price_assumption_top + self.price_assumption_bottom)/2

    def clear_orders(self):
        self.orders = []

    def average_price_assumption(self):
        # Average price assumption
        return self.price_assumption_top + self.price_assumption_bottom / 2

    def random_price_assumption(self):
        # Average price assumption
        return random.uniform(self.price_assumption_bottom, self.price_assumption_top)

    def step(self):
        self.consume_resources()
        self.produce_resources()
        self.trade()

    def agent_name(self):
        return f"Agent {self.unique_id}"

    def trade(self):
        '''
        Determine-Sale-Quantity(Commodity)
            1 mean←historical mean price of Commodity
            2 favorability←position of mean within observed trading range
            3 amount to sell ←favorability * excess inventory of Commodity
            4 return amount to sell

        '''

        market_average = self.latest_market_price
        favorability = percent(market_average, self.average_price_assumption())
        quantity = favorability * (self.food - self.desired_food)
        quantity = round(quantity, 1)
        if quantity > -1 and quantity < 1:
            quantity = 0
        price = self.random_price_assumption()
        # print("market_average", market_average)
        # print("average_price_assumption", self.average_price_assumption())
        # print("favorability", favorability)
        # print("quantity", quantity)
        if price > self.money:
            price = self.average_price_assumption()
            if price > self.money:
                price = self.money

        if quantity < 0:
            # we want to buy from the market
            self.model.register_buy_order(
                self,
                price,
                abs(quantity)
            )
        if quantity > 0:
            # we want to sell to the market
            self.model.register_sell_order(
                self,
                price,
                abs(quantity)
            )

    def consume_resources(self):
        # Agent resource consumption logic
        self.food -= 1
        if self.food <= 0:
            self.food = 0
            self.starve()

    def produce_resources(self):
        # Agent resource production logic
        produced = random.gauss(self.production, 0.5)  # *self.production
        self.food = self.food + produced
        self.model.total_food += produced

    def update_price_assumption(self, orders, today_price):

        # dont base the assumptions directly on the market price
        # this is factored when choosing the sell price in the trade function
        self.latest_market_price = today_price
        # this should only use the orders that have been fulfilled
        # the ideal situation is to have a 50/50 split of fulfilled orders

        for order in orders:

            change = 0.05

            ppu = order.ppu

            if ppu > self.price_assumption_top:
                print(
                    f"Ripoff! i paid {ppu} but i thought it was {self.price_assumption_top}")
                self.price_assumption_top = (
                    self.price_assumption_top * (1+change))
                continue

            if ppu < self.price_assumption_bottom:
                print(
                    f"cheap! i paid {ppu} but i thought it was {self.price_assumption_top}")
                self.price_assumption_bottom = (
                    self.price_assumption_bottom * (1-change))
                continue

            if self.price_assumption_bottom <= ppu <= self.price_assumption_top:
                print(
                    f"we are in the sweet spot, i paid {ppu}, right in the middle of {self.price_assumption_bottom} and {self.price_assumption_top}")
                # narrow the range
                self.price_assumption_top = (
                    self.price_assumption_top * (1-change))
                self.price_assumption_bottom = (
                    self.price_assumption_bottom * (1+change))
                continue

    def starve(self):
        print("Agent starving", self.unique_id)
        if (random.random() < 0.2):
            self.die()

    def die(self):
        # this is called when the agent is starving
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)
        print("Agent died", self.unique_id)
