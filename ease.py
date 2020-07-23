import math


def linear(t):
    return t


# in: A tween function that begins slow and then accelerates.
# out: A tween function that begins fast and then decelerates.
# in_out: A tween function that accelerates, reaches the midpoint, and then decelerates.


class Ease:
    def __init__(self):
        self._p = 1

    def power(self, power):
        self._p = power
        return self.rate

    def rate(self, t):
        pass


class EaseIn(Ease):
    def rate(self, t):
        return t**self._p


class EaseOut(Ease):
    def rate(self, t):
        return 1 - (1 - t)**self._p


class EaseInOut(Ease):
    def rate(self, t):
        if t < 0.5:
            return (2 * t)**self._p / 2
        else:
            return 1 - ((2 - 2 * t)**self._p) / 2


ease_in = EaseIn()
ease_out = EaseOut()
ease_in_out = EaseInOut()


def ease_in_sine(t):
    return 1 - math.cos(t * math.pi / 2)


def ease_out_sine(t):
    return math.sin(t * math.pi / 2)


def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


def ease_in_expo(t):
    if t == 0:
        return 0
    else:
        return 2**(10 * (t - 1))


def ease_out_expo(t):
    if t == 1:
        return 1
    else:
        return 1 - (2**(-10 * t))


def ease_in_out_expo(t):
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        if t < 0.5:
            return (2**(10 * (2 * t - 1))) / 2
        else:
            return (2 - (2**(10 * (1 - 2 * t)))) / 2


def ease_in_circ(t):
    return 1 - math.sqrt(1 - t**2)


def ease_out_circ(t):
    return math.sqrt(1 - (1 - t)**2)


def ease_in_out_circ(t):
    if t < 0.5:
        return (1 - math.sqrt(1 - (2 * t)**2)) / 2
    else:
        return (math.sqrt(1 - (-2 * t + 2)**2) + 1) / 2


def ease_in_elastic(t):
    c4 = (2 * math.pi) / 3
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return -(2**(10 * (t - 1))) * math.sin((t * 10 - 10.75) * c4)


def ease_out_elastic(t):
    c4 = (2 * math.pi) / 3
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return (2**(-10 * t)) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_in_out_elastic(t, amplitude=1, period=0.5):
    c5 = (2 * math.pi) / 4.5
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        if t < 0.5:
            return -((2**(10 * (2 * t - 1))) * math.sin((20 * t - 11.125) * c5)) / 2
        else:
            return ((2**(10 * (-2 * t + 1))) * math.sin((20 * t - 11.125) * c5)) / 2 + 1


def ease_in_back(t):
    c1 = 1.70158
    c3 = (c1 + 1)
    return c3 * t**3 - c1 * t**2


def ease_out_back(t):
    c1 = 1.70158
    c3 = (c1 + 1)
    return 1 + c3 * (t - 1)**3 + c1 * (t - 1)**2


def ease_in_out_back(t, s=1.70158):
    c1 = 1.70158
    c2 = c1 * 1.525
    if t < 0.5:
        return (((2 * t)**2) * ((c2 + 1) * 2 * t - c2)) / 2
    else:
        return (((2 * t - 2)**2) * ((c2 + 1) * (2 * t - 2) + c2) + 2) / 2


def ease_in_bounce(t):
    return 1 - ease_out_bounce(1 - t)


def ease_out_bounce(t):
    n1 = 7.5625
    d1 = 2.75

    if t < (1 / d1):
        return n1 * t**2
    elif t < (2 / d1):
        t -= (1.5 / d1)
        return n1 * t**2 + 0.75
    elif t < (2.5 / d1):
        t -= (2.25 / d1)
        return n1 * t * t + 0.9375
    else:
        t -= (2.65 / d1)
        return n1 * t * t + 0.984375


def ease_in_out_bounce(t):
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    else:
        return (1 + ease_out_bounce(2 * t - 1)) / 2


class YoYo:
    def __init__(self):
        self._p = 1

    def power(self, power):
        self._p = power
        return self.rate

    def rate(self, t):
        return 1 - (4 * t * (t - 1) + 1)**self._p


yoyo = YoYo()
