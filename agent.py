from mesa import Agent
import random


def percent(part, whole):
    # normalize to either 0 or 1
    # remaining_quantity, inital_quantity
    if part == 0.0 or whole == 0.0:
        return 0.0
    return float(part)/float(whole)


class EcoAgent(Agent):
    def __init__(self, unique_id, model, color="red"):
        super().__init__(unique_id, model)
        self.food = 10  # Starting food
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

        # [todo: add this logic]
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
        price = self.random_price_assumption()
        print("market_average", market_average)
        print("average_price_assumption", self.average_price_assumption())
        print("favorability", favorability)
        print("quantity", quantity)
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
        return

        # Attempt to place a trade in the local market

        if self.food > self.desired_food:
            # attempt to sell
            quantity = round(self.food - self.desired_food, 3)
            # quantity = self.food - self.desired_food
            if quantity > 0:
                self.model.register_sell_order(
                    self,
                    self.average_price_assumption(),
                    quantity
                )
        elif self.food < self.desired_food:
            # attempt to buy
            if self.money < 0:
                return
            quantity = round(self.desired_food - self.food, 3)
            # quantity = self.desired_food - self.food
            if quantity > 0:
                self.model.register_buy_order(
                    self,
                    self.average_price_assumption(),
                    quantity
                )

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

    def update_price_assumption(self, orders, today_price):

        print("update_price_assumption", len(orders))
        self.latest_market_price = today_price
        capture_current_assumptions = (
            self.price_assumption_top, self.price_assumption_bottom)

        for order in orders:
            inital_quantity = order.inital_quantity
            fulfilled = order.fulfilled
            ppu = order.ppu

            # was this order successful?
            successful = fulfilled > 0

            # if we sold none
            if fulfilled == 0:
                # did we charge too much?
                # if order.ppu > self.price_assumption_top:
                # lower our top assumption
                self.price_assumption_top *= 0.95
                # maybe our minimum price is too high?
                # if order.ppu < self.price_assumption_bottom:
                # lower our bottom assumption
                self.price_assumption_bottom *= 0.95
                continue

            # if we sold all
            if fulfilled == inital_quantity:
                # this is worth more than we thought
                self.price_assumption_top *= 1.05
                self.price_assumption_bottom *= 1.05
                continue

            # if we sold some
            if fulfilled > 0:
                if self.latest_market_price < self.average_price_assumption():
                    self.price_assumption_top *= 0.95
                else:
                    self.price_assumption_bottom *= 1.05
                continue
        # print("Changed assumptions", capture_current_assumptions,
        #       (self.price_assumption_top, self.price_assumption_bottom))

        # if fulfilled > 0:
        #     if order.ppu > self.price_assumption_top:
        #         self.price_assumption *= 1.05
        #     if order.ppu < self.price_assumption_bottom:
        #         self.price_assumption *= 0.95
        # else:
        #     if order.ppu > self.price_assumption_top:
        #         self.price_assumption *= 0.95
        #     if order.ppu < self.price_assumption_bottom:
        #         self.price_assumption *= 1.05

        # # Update price assumption based on recent trades
        # # do this in 5% increments of the average price based on if the previous trade was successful or not

        # # if we were very unsuccessful, change the assumption by a larger amount
        # sale_percent = percent(remaining_quantity, inital_quantity)

        # print("sale_percent", sale_percent)

        # #  this speeds up the assumption change if the agent is very far from their desired price
        # assumption_change = (self.price_assumption *
        #                      (0.05+(sale_percent*0.15)))

        # # if theres a big difference between desired food and actual food, change the assumption faster by some proportion
        # # assumption_change *= abs_assumption_change / 10

        # def lower_assumption():
        #     print(self.agent_name(), "lowering assumption by", assumption_change)
        #     self.price_assumption -= assumption_change
        #     if self.price_assumption < 0.001:
        #         self.price_assumption = 0.001

        # def raise_assumption():
        #     print(self.agent_name(), "raising assumption by", assumption_change)
        #     self.price_assumption += assumption_change

        # def pick_type():
        #     if type == "buy":
        #         return raise_assumption
        #     elif type == "sell":
        #         return lower_assumption

        # if successful:
        #     if ppu > self.price_assumption:
        #         pick_type()()
        #     elif ppu < self.price_assumption:
        #         pick_type()()
        # else:
        #     pick_type()()
        return
