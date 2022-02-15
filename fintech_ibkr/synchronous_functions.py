import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

def fetch_managed_accounts():

    class ibkr_app(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.error_messages = pd.DataFrame(columns = [
                'reqId', 'errorCode', 'errorString'
            ])
            self.managed_accounts = []

        def error(self, reqId, errorCode, errorString):
            print("Error: ", reqId, " ", errorCode, " ", errorString)

        def managedAccounts(self, accountsList):
            self.managed_accounts = [i for i in accountsList.split(",") if i]
            self.disconnect()

    app = ibkr_app()

    app.connect('127.0.0.1', 7497, 10645)
    while not app.isConnected():
        time.sleep(0.5)

    print('connected')

    def run_loop():
        app.run()

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while len(app.managed_accounts) == 0:
        time.sleep(0.5)

    print('handshake complete')

    return app.managed_accounts


def req_historical_data(tickerId, contract, endDateTime, durationStr,
                        barSizeSetting, whatToShow, useRTH):

    class ibkr_app(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.error_messages = pd.DataFrame(columns = [
                'reqId', 'errorCode', 'errorString'
            ])
            self.historical_data = pd.DataFrame()

        def error(self, reqId, errorCode, errorString):
            print("Error: ", reqId, " ", errorCode, " ", errorString)

        def historicalData(self, reqId, bar):
            # YOUR CODE GOES HERE: Turn "bar" into a pandas dataframe, formatted
            #   so that it's accepted by the plotly candlestick function.
            # Take a look at candlestick_plot.ipynb for some help!
            # assign the dataframe to self.historical_data.
            print(reqId, bar)

        def historicalDataEnd(self, reqId: int, start: str, end: str):
            self.disconnect()

        # EWrapper.nextValidID callback is commonly used to indicate that the connection is completed
        # and other messages can be sent from the API client to TWS.
        # There is the possibility that function calls (e.g. reqHistoricalData() ) made prior
        # to this time could be dropped by TWS
        def nextValidId(self, orderId: int):
            self.start()

        def start(self):
            print('Triggering historical data request...')
            self.reqHistoricalData(tickerId, contract, endDateTime, durationStr,
                                   barSizeSetting, whatToShow, useRTH,
                                   True, False, [])
            print('Finished triggering historical data request')

    app = ibkr_app()

    app.connect('127.0.0.1', 7497, 10645)
    while not app.isConnected():
        time.sleep(0.5)

    print('connected')

    def run_loop():
        app.run()

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    eurusd_contract = Contract()
    eurusd_contract.symbol = 'EUR'
    eurusd_contract.secType = 'CASH'
    eurusd_contract.exchange = 'IDEALPRO'
    eurusd_contract.currency = 'USD'

    # As long as the historical data instance variable has no rows, wait
    #  until you receive it from the socket:
    while app.historical_data.count == 0:
        time.sleep(0.5)

    # When you've got it, return it:
    return app.historical_data
