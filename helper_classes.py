import random


def random_string(length=5):
    x = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(x) for _ in range(length))


class _Base_Order:
    def __init__(self, quantity, ppu, id=None, closed=False):
        self.quantity = quantity
        self.ppu = ppu
        # self.ppu = round(ppu, 3)
        self.id = id
        if id == None:
            self.id = random_string()

    def __str__(self):
        return f"ID:{self.id} V:{type(self).__name__} QTY:{self.quantity} PPU:{self.ppu} "

    def __repr__(self):
        return self.__str__()


class Order(_Base_Order):
    def __init__(self, type, initator, quantity, ppu, fulfilled=0):
        _Base_Order.__init__(self,  quantity, ppu)
        self.initator = initator
        self.type = type
        self.fulfilled = fulfilled
        self.inital_quantity = quantity

        if type not in ["buy", "sell"]:
            raise Exception("Invalid order type, must be buy or sell")
        print("Order created", self)

    def __str__(self):
        return f"ID:{self.id} O:{self.type} V:{type(self).__name__} QTY:{self.fulfilled}/{self.inital_quantity}({round(self.fulfilled/self.inital_quantity*100,2)}) PPU:{round(self.ppu,2)} "

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
    def __init__(self, sell_order, buy_order, quantity, ppu):
        _Base_Order.__init__(self, quantity, ppu,
                             sell_order.id + "=>" + buy_order.id)
        self.sell_order = sell_order
        self.buy_order = buy_order
