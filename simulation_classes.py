import random


def random_string(length=5):
    x = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(x) for _ in range(length))


def percent(part, whole):
    # normalize to either 0 or 1
    # remaining_quantity, inital_quantity
    if part == 0.0 or whole == 0.0:
        return 0.0
    return float(part)/float(whole)


class _Base_Order:
    def __init__(self, resource, quantity, ppu, id=None, closed=False):
        self.resource = resource
        self.quantity = quantity
        self.ppu = ppu
        # self.ppu = round(ppu, 3)
        self.id = id
        if id == None:
            self.id = random_string()

    def __str__(self):
        return f"R:{self.resource} V:{type(self).__name__} QTY:{self.quantity} PPU:{self.ppu} ID:{self.id} "

    def __repr__(self):
        return self.__str__()


class Order(_Base_Order):
    def __init__(self, resource, type, initator, quantity, ppu, fulfilled=0):
        _Base_Order.__init__(self, resource,  quantity, ppu)
        self.initator = initator
        self.type = type
        self.fulfilled = fulfilled
        self.inital_quantity = quantity
        self.trades = []

        if type not in ["buy", "sell"]:
            raise Exception("Invalid order type, must be buy or sell")
        print("Order created", self)

    def __str__(self):
        return f"R:{self.resource} A:{self.initator.unique_id} O:{self.type} V:{type(self).__name__} QTY:{self.fulfilled}/{self.inital_quantity}({round(self.fulfilled/self.inital_quantity*100,2)}) PPU:{round(self.ppu,2)} ID:{self.id} "

    def fulfill(self, quantity):
        self.fulfilled += quantity
        self.quantity -= quantity
        print("[Order]Order fulfilled", quantity, self)

    def is_fulfilled(self):
        return self.fulfilled >= self.quantity

    def resolve_order(self):
        print("[Order]Order resolved", self)
        self.closed = True

    def discard_order(self):
        print("[Order]Order discarded", self)
        self.closed = True


class Trade(_Base_Order):
    def __init__(self, resource, sell_order, buy_order, quantity, ppu):
        _Base_Order.__init__(self, resource, quantity, ppu,
                             sell_order.id + "=>" + buy_order.id)
        self.sell_order = sell_order
        self.buy_order = buy_order
        self.sell_order.trades.append(self)
        self.buy_order.trades.append(self)

        print("[Trade]Trade created", self)


class Recipe:
    def __init__(self, name, requires: dict, produces: dict):
        self.name = name
        self.requires = requires
        self.produces = produces

    def pr(self, x: list):
        return ','.join([f"{k}={v}" for k, v in x.items()])

    def __str__(self) -> str:
        return f"[Recipe]{self.name} IN:{self.pr(self.requires)} OUT:{self.pr(self.produces)}"

    def can_make(self, agent):
        for resource, quantity in self.requires.items():
            if resource not in agent.resources:
                return False
            if agent.resources[resource] < quantity:
                return False
        return True

    def make_recipe(self, agent):
        # print("Making recipe", self.name)
        # old_inventory = agent.resources.copy()
        if not self.can_make(agent):
            return 0
        produced = dict()

        for resource, quantity in self.requires.items():
            agent.remove_resource(resource, (quantity))
        for resource, quantity in self.produces.items():
            # here is a gaussian distribution where lower numbers produce smaller outputs
            # quantity = quantity * random.gauss(agent.production, 0.1)
            produced[resource] = quantity

            agent.add_resource(resource, quantity)
        return produced

    def get_profitability(self, agent):
        profitability = 0
        for resource, quantity in self.produces.items():
            profitability += agent.average_price_assumption(
                resource) * quantity
        for resource, quantity in self.requires.items():
            profitability -= agent.average_price_assumption(
                resource) * quantity
        return profitability


class Role:
    def __init__(self, name, recipes: list[Recipe], desired_resources: dict):
        self.name = name
        self.recipes = recipes
        self.desired_resources = desired_resources
        if "food" not in self.desired_resources:
            self.desired_resources["food"] = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def get_profitability(self, agent):
        profitability = 0
        for recipe in self.recipes:
            profitability += recipe.get_profitability(agent)
        return profitability

    def make_recipe(self, agent):
        for recipe in self.recipes:
            if recipe.can_make(agent):
                if recipe.get_profitability(agent) > 0:
                    return recipe.make_recipe(agent)
                else:
                    print("[Role]Recipe not profitable",
                          agent.unique_id, recipe.name)
            else:
                print("[Role]Recipe cannot be made", recipe)
        print("[Role]No recipes can be made", agent.unique_id, self.name)
        return {}
        # idle tax
        agent.money -= 2

    def get_created_resources(self):
        resources = {}
        for recipe in self.recipes:
            for resource, quantity in recipe.produces.items():
                if resource not in resources:
                    resources[resource] = 0
                resources[resource] += quantity
        return resources
