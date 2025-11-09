import math

async def round_m(x, m=4):
    if x == 0:
        return 0
    return round(x, m - int(math.floor(math.log10(abs(x)))) - 1)

