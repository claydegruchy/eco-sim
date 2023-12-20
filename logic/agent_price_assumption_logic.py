import numpy as np
import sys
sys.path.append('../')
from simulation_classes import Order, Trade, percent  # noqa: E402


def price_assumption_logic(agent, order, orders: list[Order], trades: list[Trade]):
    self = agent
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