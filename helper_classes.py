import random


def random_string(length=5):
    x = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(x) for _ in range(length))


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
        return f"ID:{self.id} R:{self.resource} V:{type(self).__name__} QTY:{self.quantity} PPU:{self.ppu} "

    def __repr__(self):
        return self.__str__()


class Order(_Base_Order):
    def __init__(self, resource, type, initator, quantity, ppu, fulfilled=0):
        _Base_Order.__init__(self, resource,  quantity, ppu)
        self.initator = initator
        self.type = type
        self.fulfilled = fulfilled
        self.inital_quantity = quantity

        if type not in ["buy", "sell"]:
            raise Exception("Invalid order type, must be buy or sell")
        print("Order created", self)

    def __str__(self):
        return f"ID:{self.id} A:{self.initator.unique_id} O:{self.type} V:{type(self).__name__} QTY:{self.fulfilled}/{self.inital_quantity}({round(self.fulfilled/self.inital_quantity*100,2)}) PPU:{round(self.ppu,2)} "

    def fulfill(self, quantity):
        self.fulfilled += quantity
        self.quantity -= quantity
        print("Order fulfilled", quantity, self)

    def is_fulfilled(self):
        return self.fulfilled >= self.quantity

    def resolve_order(self):
        print("Order resolved", self)
        self.closed = True

    def discard_order(self):
        print("Order discarded", self)
        self.closed = True


class Trade(_Base_Order):
    def __init__(self, resource, sell_order, buy_order, quantity, ppu):
        _Base_Order.__init__(self, resource, quantity, ppu,
                             sell_order.id + "=>" + buy_order.id)
        self.sell_order = sell_order
        self.buy_order = buy_order
        print("Trade created", self)


class Recipe:
    def __init__(self, name, requires: dict, produces: dict):
        self.name = name
        self.requires = requires
        self.produces = produces

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

        for resource, quantity in self.requires.items():
            agent.remove_resource(resource, (quantity))
        for resource, quantity in self.produces.items():
            # using gaussian distribution to simulate randomness and highlight changes
            # this can go into negatives!

            # here is a gaussian distribution where lower numbers produce smaller outputs
            # quantity = quantity * random.gauss(agent.production, 0.1)

            agent.add_resource(resource, quantity*agent.production)
            return quantity
        # print("Inventory:", old_inventory, "->", agent.resources)

    def get_profitability(self, agent):
        profitability = 0
        for resource, quantity in self.produces.items():
            profitability += agent.price_assumptions[resource] * quantity
        for resource, quantity in self.requires.items():
            profitability -= agent.price_assumptions[resource] * quantity
        return profitability


class Role:
    def __init__(self, name, recipes: list[Recipe], desired_resources: dict):
        self.name = name
        self.recipes = recipes
        self.desired_resources = desired_resources
        if "food" not in self.desired_resources:
            self.desired_resources["food"] = 20

    def get_profitability(self, agent):
        profitability = 0
        for recipe in self.recipes:
            profitability += recipe.get_profitability(agent)
        return profitability

    def make_recipe(self, agent):
        for recipe in self.recipes:
            if recipe.can_make(agent):
                return recipe.make_recipe(agent)
        print("No recipes can be made", agent.unique_id, self.name)

    def get_created_resources(self):
        resources = {}
        for recipe in self.recipes:
            for resource, quantity in recipe.produces.items():
                if resource not in resources:
                    resources[resource] = 0
                resources[resource] += quantity
        return resources


chop_wood_strong = Recipe("Strong Chop Wood", {"tools": 1}, {"wood": 3})
chop_wood_weak = Recipe("Weak Chop Wood", {}, {"wood": 1})
craft_tools = Recipe("Craft Tools", {"wood": 1}, {"tools": 1})
farm_strong = Recipe("Strong Farm", {"tools": 0.5}, {"food": 3, "tools": 0.4})
farm_weak = Recipe("Weak Farm", {}, {"food": 1})


lumberjack = Role("Lumberjack",
                  [chop_wood_strong, chop_wood_weak],
                  {"wood": 0, "tools": 5})
farmer = Role("Farmer", [farm_strong, farm_weak], {"food": 10, "tools": 5})
smith = Role("Smith", [craft_tools], {"tools": 0, "wood": 20})


roles = [farmer, lumberjack, smith]


def resource_finder():
    potential_resources = set()
    for role in roles:
        creates = role.get_created_resources()
        potential_resources.update(creates.keys())
    return potential_resources
