import numpy as np
import sys
sys.path.append('../')   # noqa: E402
from simulation_classes import Order, Trade, percent

min_price = 0.0000001


def trade_logic(agent):
    self = agent
    for resource in self.desired_resources:
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
