from mesa import Agent

import random


class EcoAgent(Agent):
    def __init__(self, unique_id, model, color="red"):
        super().__init__(unique_id, model)
        self.food = 20  # Starting food
        self.desired_food = 20  # Desired food
        self.money = 100  # Starting money
        self.production = random.uniform(0, 2)  # Starting production
        # Starting price assumption
        self.price_assumption = 5 + random.uniform(-0.1, 0.1)

    def step(self):
        self.consume_resources()
        self.produce_resources()
        self.trade()

    def agent_name(self):
        return f"Agent {self.unique_id}"

    def trade(self):
        # Attempt to place a trade in the local market

        if self.food > self.desired_food:
            # attempt to sell
            quantity = round(self.food - self.desired_food, 0)
            if quantity > 0:
                self.model.register_sell_order(
                    self,
                    self.price_assumption,
                    quantity
                )
        elif self.food < self.desired_food:
            # attempt to buy
            if self.money < 0:
                return
            quantity = round(self.desired_food - self.food, 0)
            if quantity > 0:
                self.model.register_buy_order(
                    self,
                    self.price_assumption,
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

    def update_price_assumption(self, type, successful, ppu, remaining_quantity, total_quantity):
        # Update price assumption based on recent trades
        # do this in 5% increments of the average price based on if the previous trade was successful or not

        assumption_change = (self.price_assumption * (0.05))
        assumption_change = round(assumption_change, 3)
        abs_assumption_change = abs(self.desired_food - self.food)
        # if theres a big difference between desired food and actual food, change the assumption faster by some proportion
        # assumption_change *= abs_assumption_change / 10

        def lower_assumption():
            print(self.agent_name(), "lowering assumption by", assumption_change)
            self.price_assumption -= assumption_change

        def raise_assumption():
            print(self.agent_name(), "raising assumption by", assumption_change)
            self.price_assumption += assumption_change

        def pick_type():
            if type == "buy":
                return raise_assumption
            elif type == "sell":
                return lower_assumption

        if successful:
            if ppu > self.price_assumption:
                pick_type()()
            elif ppu < self.price_assumption:
                pick_type()()
        else:
            pick_type()()
