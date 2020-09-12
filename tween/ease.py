import math


def linear(t):
    return t


def sigmoid(t):
    return 1 / (1 + math.exp(-t))


class _Bezier:
    def config(self, start=0, control1=0 + 0.5j, control2=1 + 0.5j, end=1 + 1j):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end

    def rate(self, t):
        return ((1 - t)**3 * self.start + 3 * (1 - t)**2 * t * self.control1 + 3 *
                (1 - t) * t**2 * self.control2 + t**3 * self.end).imag


class _Smooth:
    def __init__(self):
        self._inflection = 10

    def config(self, inflection=10):
        self._inflection = inflection
        self._error = sigmoid(-inflection / 2)
        return self

    def rate(self, t):
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return (sigmoid(self._inflection * (t - 0.5)) - self._error) / (1 - 2 * self._error)


smooth = _Smooth().config(10)


class _RushInto:
    def config(self, inflection=10):
        self.smooth = _Smooth().config(inflection).rate
        return self

    def rate(self, t):
        return 2 * self.smooth(t / 2.0)


rush_into = _RushInto().config()


class _RushFrom:
    def config(self, inflection=10):
        self.smooth = _Smooth().config(inflection).rate
        return self

    def rate(self, t):
        return 2 * self.smooth(t / 2.0 + 0.5) - 1


rush_from = _RushFrom().config()


class _DoubleSmooth:
    def config(self, inflection=10):
        self.smooth = _Smooth().config(inflection).rate
        return self

    def rate(self, t):
        if t < 0.5:
            return 0.5 * self.smooth(2 * t)
        else:
            return 0.5 * (1 + self.smooth(2 * t - 1))


double_smooth = _DoubleSmooth().config()


class _ThereAndBack:
    def config(self, inflection=10):
        self.smooth = _Smooth().config(inflection).rate
        return self

    def rate(self, t):
        new_t = 2 * t if t < 0.5 else 2 * (1 - t)
        return self.smooth(new_t)


there_and_back = _ThereAndBack().config()


class _ThereAndBackWithPause:
    def config(self, pause_ratio=1 / 3, inflection=10):
        self.pause_ratio = pause_ratio
        self.a = 1 / self.pause_ratio
        self.smooth = _Smooth().config(inflection).rate
        return self

    def rate(self, t):
        if t < 0.5 - self.pause_ratio / 2:
            return self.smooth(self.a * t)
        elif t < 0.5 + self.pause_ratio / 2:
            return 1
        else:
            return self.smooth(self.a - self.a * t)


there_and_back_with_pause = _ThereAndBackWithPause()


def slow_into(t):
    return math.sqrt(1 - (1 - t) * (1 - t))


# in: A tween function that begins slow and then accelerates.
# out: A tween function that begins fast and then decelerates.
# in_out: A tween function that accelerates, reaches the midpoint, and then decelerates.


class _Ease:
    def __init__(self):
        self._power = 1

    def config(self, power):
        self._power = power
        return self

    def rate(self, t):
        pass


class _EaseIn(_Ease):
    def rate(self, t):
        return t**self._power


class _EaseOut(_Ease):
    def rate(self, t):
        return 1 - (1 - t)**self._power


class _EaseInOut(_Ease):
    def rate(self, t):
        if t < 0.5:
            return (2 * t)**self._power / 2
        else:
            return 1 - ((2 - 2 * t)**self._power) / 2


ease_in = _EaseIn().config(2)
ease_out = _EaseOut().config(2)
ease_in_out = _EaseInOut().config(2)


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


class _YoYo:
    def __init__(self):
        self._power = 1

    def config(self, power):
        self._power = power
        return self

    def rate(self, t):
        return 1 - (4 * t * (t - 1) + 1)**self._power


yoyo = _YoYo().config(1)

# def running_start(t, pull_factor=-0.5):
#     return bezier([0, 0, pull_factor, pull_factor, 1, 1, 1])(t)

    # def not_quite_there(func=smooth, proportion=0.7):
    #     def result(t):
    #         return proportion * func(t)

    #     return result

    # def wiggle(t, wiggles=2):
    #     return there_and_back(t) * np.sin(wiggles * np.pi * t)

    # def squish_rate_func(func, a=0.4, b=0.6):
    #     def result(t):
    #         if a == b:
    #             return a

    #         if t < a:
    #             return func(0)
    #         elif t > b:
    #             return func(1)
    #         else:
    #             return func((t - a) / (b - a))

    #     return result

    # # Stylistically, should this take parameters (with default values)?
    # # Ultimately, the functionality is entirely subsumed by squish_rate_func,
    # # but it may be useful to have a nice name for with nice default params for
    # # "lingering", different from squish_rate_func's default params

    # def lingering(t):
    #     return squish_rate_func(lambda t: t, 0, 0.8)(t)

    # def exponential_decay(t, half_life=0.1):
    #     # The half-life should be rather small to minimize
    #     # the cut-off error at the end
    #     return 1 - np.exp(-t / half_life)
