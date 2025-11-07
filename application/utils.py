import math


async def round_m(x, m=4):
    if x == 0:
        return 0
    return round(x, m - int(math.floor(math.log10(abs(x)))) - 1)


# async def detect_series(quantities: dict):
#     quantities_list = [quantity for quantity in quantities]
#
#     for quantity in quantities:
#         if quantities_list.count(quantity.split("-")[0]) > 1:










data = {"x": [3, 4, 5, 2, 4, 2, 4], "time-1": [1, 2, 1, 2, 1, 2], "time-2": [4, 3, 4, 5, 4, 4], "time-3": [10, 9, 10, 11, 9, 10, 10],
        "length-1": [1, 2, 1, 2, 1, 2], "length-2": [4, 3, 4, 5, 4, 4], "length-3": [10, 9, 10, 11, 9, 10, 10]}
