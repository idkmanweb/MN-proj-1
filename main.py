import pandas as pd
import matplotlib.pyplot as mpl
import numpy as np
from shapely.geometry import LineString

# analysis parameters
start_day = 0              # from 0 to 998
amount_to_check = 999      # from 1 to (999 - start_day)
start_stocks = 1000        # amount of stocks you buy on day 1


def calculate_ema(data, interval, startday):
    top_ema = 0
    bottom_ema = 0

    a = 2/(interval+1)

    for i in range(interval):
        index = startday - interval + i + 1
        if 0 <= index < len(data):
            top_ema += pow((1 - a), i) * data[index]
            bottom_ema += pow((1 - a), i)

    return top_ema/bottom_ema


def calculate_macd(data):
    macd = []

    for day in range(1, 1000):
        daily_macd = calculate_ema(data, 12, day) - calculate_ema(data, 26, day)
        macd.append(daily_macd[0])

    return macd


def calculate_signal(data):
    signal = []

    for day in range(1, 1000):
        daily_signal = calculate_ema(data, 9, day)
        signal.append(daily_signal)

    return signal


def buy_sell_algorithm(price_data, buy_dates, sell_dates, macd_line, amount_of_stocks, days_to_check, start_day):
    value_of_stocks = amount_of_stocks*price_data[start_day]
    start_stocks = amount_of_stocks
    money_earned = 0
    transactions = 1

    for i in range(len(buy_dates)):
        buy_dates[i] = int(np.ceil(buy_dates[i]))
    for i in range(len(sell_dates)):
        sell_dates[i] = int(np.ceil(sell_dates[i]))

    for i in range(start_day, start_day+amount_to_check):
        if i in sell_dates:
            selling_stocks = int((macd_line[i - start_day]+10)*(start_stocks/20))
            if selling_stocks > amount_of_stocks:
                selling_stocks = amount_of_stocks
            if selling_stocks < 0:
                selling_stocks = 0
                transactions -= 1
            value_of_stocks -= selling_stocks*price_data[i - start_day]
            amount_of_stocks -= selling_stocks
            money_earned += selling_stocks*price_data[i - start_day]
            transactions += 1
        if i in buy_dates:
            buying_stocks = int(macd_line[i - start_day]+10)*(start_stocks/20)
            if buying_stocks < 0:
                buying_stocks = 0
                transactions -= 1
            value_of_stocks += buying_stocks*price_data[i - start_day]
            amount_of_stocks += buying_stocks
            money_earned -= buying_stocks*price_data[i - start_day]
            transactions += 1

    money_earned += amount_of_stocks*data[start_day+days_to_check-1]
    money_earned -= start_stocks*price_data[start_day]

    return money_earned


data = pd.read_csv('oil_input.csv').values
# Crude oil prices in USD
# Data from 03.02.2011 - 23.02.2015

macd_array = calculate_macd(data)
signal_array = calculate_signal(macd_array)

# arrays for plotting
x_axis = np.arange(start_day, start_day+amount_to_check)
macd_plot = np.array(macd_array[start_day:start_day+amount_to_check])
signal_plot = np.array(signal_array[start_day:start_day+amount_to_check])

# plotting macd and signal lines
mpl.title("MACD + Signal")
mpl.xlabel("Kolejne Dni w których licznono wskaźniki")
mpl.ylabel("Wartości wskaźników")
mpl.plot(x_axis, macd_plot, 'y-', label="MACD")       # macd - yellow line
mpl.plot(x_axis, signal_plot, 'c-', label="Signal")     # signal - cyan line

# finding positions where lines cross
line1 = LineString(np.column_stack((macd_plot, x_axis)))
line2 = LineString(np.column_stack((signal_plot, x_axis)))
intersection = line1.intersection(line2)

# putting crossing points in an array
point_x = []
point_y = []
for point in intersection.geoms:
    point_y.append(point.x)
    point_x.append(point.y)

# dividing into buy and sell points
buy_x = []
buy_y = []
sell_x = []
sell_y = []
for i in range(len(point_x)):
    if macd_plot[int(point_x[i] - 0.001) - start_day] < signal_plot[int(point_x[i] - 0.001) - start_day] and \
            macd_plot[int(point_x[i]) - start_day + 1] > signal_plot[int(point_x[i]) - start_day + 1]:
        buy_x.append(point_x[i])
        buy_y.append(point_y[i])
    elif macd_plot[int(point_x[i] - 0.001) - start_day] > signal_plot[int(point_x[i] - 0.001) - start_day] and \
            macd_plot[int(point_x[i]) + 1 - start_day] < signal_plot[int(point_x[i]) + 1 - start_day]:
        sell_x.append(point_x[i])
        sell_y.append(point_y[i])

# plotting buy and sell points
mpl.plot(buy_x, buy_y, 'go', label="Punkty kupna")        # buy points - green
mpl.plot(sell_x, sell_y, 'ro', label="Punkty sprzedaży")      # sell points - red
mpl.legend()
mpl.show()

# plotting stock prices
mpl.title("Notowania ropy naftowej")
mpl.xlabel("Kolejne Dni w których sprawdzono ceny")
mpl.ylabel("Cena jednej beczki ropy naftowej w USD")
mpl.plot(x_axis, data[start_day:start_day+amount_to_check], "g-")

# all in buy/sell
earnings = 0
current_stocks = start_stocks
transactions = 1

transactions_buy = []
transactions_sell = []
for i in range(len(buy_x)):
    buy_x[i] = int(np.ceil(buy_x[i]))
    transactions_buy.append(data[buy_x[i]])
for i in range(len(sell_x)):
    sell_x[i] = int(np.ceil(sell_x[i]))
    transactions_sell.append(data[sell_x[i]])

for i in range(start_day, start_day + amount_to_check):
    if i in sell_x:
        if current_stocks > 0:
            earnings += current_stocks*data[i]
            current_stocks = 0
            transactions += 1
    if i in buy_x:
        earnings -= start_stocks*data[i]
        current_stocks += start_stocks
        transactions += 1

# adding buy/sell points to the price chart
mpl.plot(buy_x, transactions_buy, 'go', label="Punkty kupna")        # buy points - green
mpl.plot(sell_x, transactions_sell, 'ro', label="Punkty sprzedaży")      # sell points - red
mpl.legend()
mpl.show()

earnings += data[start_day+amount_to_check-1]*current_stocks
if current_stocks > 0:
    transactions += 1
earnings -= data[start_day]*start_stocks

# results
print("\n")
print("Zysk z MACD (Kupno i sprzedaż wszystkiego naraz): " + str(round(earnings[0], 2)) + "$")

earnings = data[start_day + amount_to_check - 1]*start_stocks - data[start_day]*start_stocks
print("Zyski z kupieniem ropy pierwszego dnia i sprzedaniem ostatniego: " + str(round(earnings[0], 2)) + "$")

earnings = buy_sell_algorithm(data, buy_x, sell_x, macd_plot, start_stocks, amount_to_check, start_day)
print("Zyski po kupowniu/sprzedawaniu zgodnie z algorytmem: " + str(round(earnings[0], 2)) + "$")

print("Liczba Transakcji MACD: " + str(transactions))


