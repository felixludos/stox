

# from ibapi.client import EClient
# from ibapi.wrapper import EWrapper
# from ibapi.contract import Contract, ContractDetails
#
# import pandas
# import threading
# import time
#
#
# class IBapi(EWrapper, EClient):
# 	def __init__(self):
# 		EClient.__init__(self, self)
# 		self.data = []  # Initialize variable to store candle
#
# 	def historicalData(self, reqId, bar):
# 		print(f'Time: {bar.date} Close: {bar.close}')
# 		self.data.append([bar.date, bar.close])
#
# 	def contractDetails(self, reqId: int, contractDetails: ContractDetails):
# 		print("Contract Details:")
# 		print("Symbol:", contractDetails.contract.symbol)
# 		print("Security Type:", contractDetails.contract.secType)
# 		print("Primary Exchange:", contractDetails.contract.primaryExchange)
# 		print("Currency:", contractDetails.contract.currency)
# 		# ... and any other details you're interested in
#
#
# def run_loop():
# 	app.run()
#
#
# app = IBapi()
# app.connect('127.0.0.1', 4001, 1024)
# # app.clientVersion(163)  # Explicitly set the client version.
#
# # Start the socket in a thread
# api_thread = threading.Thread(target=run_loop, daemon=True)
# api_thread.start()
#
# time.sleep(1)  # Sleep interval to allow time for connection to server
#
# contract = Contract()
# contract.secType = "STK"
# contract.symbol = "MC"
# # contract.exchange = "SMART"  # Using SMART will auto-route to the best exchange
# # contract.currency = "USD"
#
# req_id = 1
# app.reqContractDetails(req_id, contract)
#
# # # Create contract object
# # eurusd_contract = Contract()
# # eurusd_contract.symbol = 'EUR'
# # eurusd_contract.secType = 'CASH'
# # eurusd_contract.exchange = 'IDEALPRO'
# # eurusd_contract.currency = 'USD'
# #
# # # Request historical candles
# # app.reqHistoricalData(1, eurusd_contract, '', '2 D', '1 hour', 'BID', 0, 2, False, [])
#
# time.sleep(5)  # sleep to allow enough time for data to be returned
#
# # df = pandas.DataFrame(app.data, columns=['DateTime', 'Close'])
# # df['DateTime'] = pandas.to_datetime(df['DateTime'], unit='s')
# # df.to_csv('EURUSD_Hourly.csv')
# #
# # print(df)
#
# app.disconnect()

from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook
#%%

ib = IB()
ib.connect('127.0.0.1', 4001, clientId=1)

# contract = Forex('EURUSD')
# bars = ib.reqHistoricalData(
#     contract, endDateTime='', durationStr='30 D',
#     barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)




pos = ib.positions()


print(pos)





