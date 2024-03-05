class XRate:

    def __init__(self, currency_a: str, currency_b: str, rate_ab: float):
        self.currency_a = currency_a
        self.currency_b = currency_b
        self.rate_ab = rate_ab

    def convert(self, currency, amount) -> float:
        if currency == self.currency_a:
            return amount * self.rate_ab
        elif currency == self.currency_b:
            return amount / self.rate_ab
        else:
            raise ValueError(currency)

    def rate(self, currency) -> float:
        if currency == self.currency_a:
            return self.rate_ab
        elif currency == self.currency_b:
            return 1 / self.rate_ab
        else:
            raise ValueError(currency)

    def other(self, currency) -> str:
        if currency == self.currency_a:
            return self.currency_b
        elif currency == self.currency_b:
            return self.currency_a
        else:
            raise ValueError(currency)
