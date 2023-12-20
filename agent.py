from mesa import Agent
import random
import numpy as np
from simulation_classes import Order, Trade, percent
from agent_role_config import roles, resource_finder
import sys
sys.path.append('logic/')
from agent_price_assumption_logic import price_assumption_logic  # noqa: E402
from agent_trade_logic import trade_logic  # noqa: E402


class EcoAgent(Agent):
    def __init__(self, unique_id, model, role, color="red"):
        super().__init__(unique_id, model)
        self.age = 0
        self.resources = {
            "food": 3,
        }
        self.desired_resources = {}

        self.price_assumptions = {
        }
        # print("Setting up price assumptions")
        for resource in resource_finder():
            if resource not in self.resources:
                self.resources[resource] = 0
            if resource in self.price_assumptions:
                continue
            self.price_assumptions[resource] = {}
            current_price = model.price_history[resource][-1]
            self.price_assumptions[resource]['top'] = random.uniform(
                current_price, current_price*1.1)
            self.price_assumptions[resource]['bottom'] = random.uniform(
                current_price, current_price*0.9)
        self.cycles_since_last_trade = 0
        # print("Setting up agent")
        self.update_role(role)
        self.money = 100  # Starting money
        self.production = random.uniform(0, 2)  # Starting production
        self.last_production = dict()
        self.last_trade = 0

        self.orders = []
        self.last_order_count = 0

    def update_role(self, role):
        self.role = role
        self.desired_resources = role.desired_resources
        for resource in resource_finder():
            if resource not in self.desired_resources:
                self.desired_resources[resource] = 0

    def clear_orders(self):
        self.last_order_count = len(self.orders)
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
        self.age += 1

    def agent_name(self):
        return f"Agent {self.unique_id}"

    def get_stat(self, attr):
        return getattr(self, attr)

    # resouce handlers
    def get_resource(self, resource):
        if resource not in self.resources:
            return 0
        return self.resources[resource]

    def add_resource(self, resource, quantity):
        self.resources[resource] += quantity

    def remove_resource(self, resource, quantity):
        self.resources[resource] -= quantity
        if self.resources[resource] < 0:
            self.resources[resource] = 0

    def consume_resources(self):
        # Agent resource consumption logic
        if self.money <= 0:
            self.money = 0
            self.starve()
        # rot food
        current = self.get_resource("food")
        if current > self.desired_resources["food"]:
            self.remove_resource("food", current*0.01)

    def produce_resources(self):
        self.last_production = self.role.make_recipe(self)
        for resource in resource_finder():
            if resource not in self.last_production:
                quantity = 0
            else:
                quantity = self.last_production[resource]
            self.model.production_history[resource][-1] += quantity

    def update_reports(self):
        row = {"agent_id": self.unique_id, "food": self.resources['food']}
        self.model.datacollector.add_table_row("Final_Values", row)

    def trade(self):
        trade_logic(self)

    def update_price_assumption(self, orders: list[Order], trades: list[Trade]):
        # dont base the assumptions directly on the market price
        # this is factored when choosing the sell price in the trade function
        # this should only use the orders that have been fulfilled
        # the ideal situation is to have a 50/50 split of fulfilled orders
        for order in orders:
            if order.initator != self:
                continue
            # for order in orders:

            price_assumption_logic(self, order, orders, trades)

            # exit()

    def change_role(self):
        new_role = self.model.find_role(self)
        print("Agent changing role", self.unique_id, "to", new_role.name)
        self.update_role(new_role)
        self.clear_orders()

    def starve(self):
        print("Agent starving", self.unique_id)
        if (random.random() < 0.2):
            return self.change_role()
        if (random.random() < 0.2):
            self.die()

    def die(self):
        self.model.kill_agent(self)
        # this is called when the agent is starving
