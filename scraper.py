import yfinance as yf
import time


def recordForLength(length, stock, checkLength=60) -> list:
    """
    :param length: How many times should the program repeat?
    :param stock: Abbreviation of the stock.
    :param checkLength: The wait time in seconds. Defaults to 60s.
    :return: Returns a list of the stock's history.
    """

    history = []
    ticker = yf.Ticker(stock)

    for i in range(length):
        history.append(ticker.history(period="1d")["Close"].iloc[-1])
        time.sleep(checkLength)

    return history
