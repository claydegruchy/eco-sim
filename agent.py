from mesa import Agent
import random
import numpy as np
from simulation_classes import Order, Trade
from agent_role_config import roles, resource_finder


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

        print("Setting up agent")
        self.update_role(role)
        self.money = 100  # Starting money
        self.production = random.uniform(0, 2)  # Starting production
        self.last_production = 0
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
        self.remove_resource("food", current*0.01)

    def produce_resources(self):
        self.last_production = self.role.make_recipe(self)

    def update_reports(self):
        row = {"agent_id": self.unique_id, "food": self.resources['food']}
        self.model.datacollector.add_table_row("Final_Values", row)

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
        # stop the dickhead agents from selling more than they have
        if quantity > self.resources[resource]:
            quantity = self.resources[resource]
        price = self.random_price_assumption(resource)

        if quantity < 0:
            if self.money <= 0:
                return
            if price > self.money:
                price = self.average_price_assumption(resource)
                if price > self.money:
                    price = self.money

            # we want to buy from the market
            order = self.model.register_buy_order(
                resource,
                self,
                max(price, min_price),
                abs(quantity)
            )
            self.orders.append(order)
        if quantity > 0:
            # we want to sell to the market
            order = self.model.register_sell_order(
                resource,
                self,
                max(price, min_price),
                abs(quantity)
            )
            self.orders.append(order)

    def update_price_assumption(self, orders: list[Order], trades: list[Trade]):
        # dont base the assumptions directly on the market price
        # this is factored when choosing the sell price in the trade function
        # this should only use the orders that have been fulfilled
        # the ideal situation is to have a 50/50 split of fulfilled orders
        for order in orders:
            if order.initator != self:
                continue
            # for order in orders:
            resource = order.resource
            top = self.price_assumptions[resource]['top']
            bottom = self.price_assumptions[resource]['bottom']
            ht = self.price_assumptions[resource]['top']
            hb = self.price_assumptions[resource]['bottom']
            last_trade_price = self.model.price_history[resource][-1]
            hisorical_average = np.mean(self.model.price_history[resource])
            # to determine market share, we need to know how many orders were placed for that resource
            # then check if that is the same as the number of orders that we placed

            total_supply = sum(
                [o.inital_quantity for o in orders if o.resource == resource and o.type == 'sell'])
            total_demand = sum(
                [o.inital_quantity for o in orders if o.resource == resource and o.type == 'buy'])
            market_share = percent(
                len(self.orders), len([o for o in orders if o.resource == resource and o.type == order.type]))
            ppu = order.ppu

            # this is somehow creating a runaway effect where the price assumptions are rising constantly
            # becuase the success of the order is not being used to factor the price assumption
            failure_degree = order.fulfilled / order.inital_quantity

            change = 0.05
            # change_factor = (failure_degree-0.5)
            # change *= change_factor
            # print("change_factor", change, change_factor, failure_degree)
            # exit()

            # if i am attempting to sell, and i am not finding buyers, then i should lower my prices
            if order.type == "sell" and failure_degree < 1/3:
                top = (top * (1-change))
                bottom = (bottom * (1-(change*2)))
            # if i am attempting to sell, and i am finding buyers, then i should raise my prices
            if order.type == "sell" and failure_degree > 2/3:
                top = (top * (1+change))
                bottom = (bottom * (1+change))
            # if i am attempting to buy, but i am not finding sellers, then i should raise my prices
            if order.type == "buy" and failure_degree < 1/3:
                top = (top * (1+(change*2)))
                bottom = (bottom * (1+change))
            # if i am attempting to buy, and i am easily finding sellers, then i should lower my prices
            if order.type == "buy" and failure_degree > 2/3:
                top = (top * (1-change))
                bottom = (bottom * (1-change))

            # if the order is being fulfilled at the desired rate, then the price assumption should contract
            if 1/3 < failure_degree < 2/3:
                top = (top * (1-change*2))
                bottom = (bottom * (1+change*2))
            if top < bottom:
                top = bottom + 0.0000001

            self.price_assumptions[resource]['top'] = max(top, 0.0000001)
            self.price_assumptions[resource]['bottom'] = max(bottom, 0.0000001)

            # max(top, 0.0000001)
            self.price_assumptions[resource]['top'] = top
            # max(bottom, 0.0000001)
            self.price_assumptions[resource]['bottom'] = bottom

            ht = round(ht, 2)
            top = round(top, 2)
            hb = round(hb, 2)
            bottom = round(bottom, 2)
            success_degree = round(order.fulfilled / order.inital_quantity, 2)

            if 0 not in [ht, top, hb, bottom]:
                # print(ht, top, hb, bottom)
                t_percent = round((top-ht)/ht*100, 2)
                b_percent = round((bottom-hb)/hb*100, 2)
            else:
                t_percent = 0
                b_percent = 0

            print("PA:", self.unique_id, order.type, resource, f"T:{ht}=>{top}({t_percent}%)",
                  f"B:{hb}=>{bottom}({b_percent}%), based on {success_degree}")

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
