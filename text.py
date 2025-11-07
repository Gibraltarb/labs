from scipy import stats

a = {"x": 10}
b = {"y": 15}
print(a | b)

string = "¤"
for symbol in string:
    print(ord(symbol).bit_length())