from ApiClient import ApiClient
import json

print("Script is running...")

# API authentication path (used for establishing connection with the API)
path = "MjXagM6/ZB1ggzw5kmjMm5DKaqw9pJbEF04vF/lNsog=,HX6/3h79HEH5UdWQH+PparWEQLT6wAZWxm0UMi2oZRE=,BBwPOa9OdyJOjR9ouASyq1yKcmId3O9+RraRjhyGJkMpEJsCOiTm/fQ2ye1b2A0o/TQRMIta0XGFGoElKKfQP3g=,MTExLjExMS4xMTEuMTEx,BK7zvNsPWQ70Kyrkdk/BL/Ht5Vv7sMF/U6a0sl4wcKQAZWcTkGAFOGuWv9do6RypNX5ub3+SA8aw/1ta+ioC5Hg=,BBwPOa9OdyJOjR9ouASyq1yKcmId3O9+RraRjhyGJkMpEJsCOiTm/fQ2ye1b2A0o/TQRMIta0XGFGoElKKfQP3g=,RGFubnkgQ29oZW4=,IJiQZg0W2mNAY7t5T0RDEzmWb3S25ikhFwIVf2BWsBGd13uMcHmBsvarkW2YTpab+eljPKp0Z0fDix1YCqZSou8=,4bHAVm4K8WpSTa0CZ/L0W/yG7dwEmjZm+8iMvzsVVF8=,SSM:true,BDxS3OoL/NFng5ybzWu4PKPYNL1ibl2GViLhYOHfbi8dSOFhmoJqmECNaxifNv3TI38EJTiueMnbjJm6ntXazpA=,iGmf4ZgIvfJsCBqTAAzSGra/0JTdkH335Qqkncm80CA=,6b36ec25"

# List of supported cryptocurrencies
all_coins = ['BTC', 'ETH', 'BCH', 'XRP', 'XLM', 'ADA', 'XTZ', 'NEAR', 'HBAR', 'SMR', 'ATOM', 'TRX', 'CSPR', 'STRK', 'SOL', "GK8_ETH"]

# Minimum required balance in the ATM faucet for each supported cryptocurrency
faucet_minimum_balances = {
    'BTC': 100000,
    'ETH': 10000000000000000,
    'BCH': 100000,
    'XRP': 10000000,
    'XLM': 100000000,
    'ADA': 10000000,
    'XTZ': 10000000,
    'NEAR': 10000000000000000000000000,
    'HBAR': 1000000000,
    'SMR': 10000000,
    'ATOM': 6000000,
    'TRX': 10000000,
    "CSPR": 500000000,
    "STRK": 1000000000000000000,
    "SOL": 100000000,
    'GK8_ETH': 10000000000000000
}

class Fees:
    """
    A class to fetch and store suggested transaction fees for various cryptocurrencies.

    This class retrieves the suggested fees from the `ApiClient`, applies a 1.5x multiplier,
    and stores the values for use in transactions.
    """
    def __init__(self, apiUser) -> None:
        """
        Initializes the Fees class and retrieves suggested transaction fees.

        :param apiUser: An instance of `ApiClient` used to fetch fee suggestions.
        """
        self.HBAR = None
        self.XTZ = None
        self.ADA = None
        self.XLM = None
        self.XRP = None
        self.BCH = None
        self.GK8_ETH = None
        self.ETH = None
        self.BTC = None
        self.apiUser = apiUser
        suggested_fees = self.apiUser.getSuggestedFee(True, all_coins)["FunctionData"]["CurrenciesSuggestedFee"]
        for coin in all_coins:
            coin_data = next((currency for currency in suggested_fees if currency["Currency"] == coin), None)
            if coin_data is None:
                setattr(self, coin, "Unsupported currency")
                continue
            suggested_fee = coin_data["SuggestedFee"]
            if suggested_fee.isdigit():
                fee = 1.5 * int(suggested_fee)
                setattr(self, coin, round(fee))
            else:
                setattr(self, coin, suggested_fee)


# Gas limits and transaction settings for specific cryptocurrencies
GAS_LIMIT_ETH = 21000
GAS_LIMIT_GK8_ETH = 100000
MAX_PRIORITY_FEE_ETH = 1000000000
GAS_LIMIT_TEZOS = 1451
STORAGE_LIMIT_TEZOS = 257
MAX_FEE_COSMOS = 100000
GAS_LIMIT_COSMOS = 250000
GAS_PRICE_CSPR = 1
PAYMENT_AMOUNT_CSPR = 100000000
MAX_FEE_STRK = 10000000000
GAS_LIMIT_STRK = 8000

class SendMoneyApp:
    """
    The main class that interacts with the ATM faucet to send fake funds.

    This class manages authentication, balance checks, fee retrieval, and executing transactions.
    """
    all_coins = all_coins  # Adding the class attribute

    def __init__(self):
        """
        Initializes the SendMoneyApp, authenticates the API user, and retrieves account info.
        """
        self.apiUser = ApiClient.fromQr(path, "34.255.204.94", request_timeout=10, debug_logs=False)
        self.apiUser.generateNewAccessToken()

        self.account_info = self.apiUser.getAccounts()['FunctionData']['Accounts'][0]['AccountDataSignedByCold']
        self.BTC_HOT_ADDRESS = self.account_info['Addresses'][0]['HotAddress']
        self.BCH_HOT_ADDRESS = self.account_info['Addresses'][2]['HotAddress']
        self.fees = Fees(self.apiUser)
        self.coins_decimals = self.fetch_coins_decimals()

    def fetch_coins_decimals(self):
        """
        Fetches and returns the decimal precision for each supported coin.

        :return: Dictionary with coin symbols as keys and their decimal precision as values.
        """
        coins_data = self.apiUser.getCoins()["FunctionData"]["Coins"]
        coins_decimals = {}
        for coin in coins_data:
            coin_symbol = coin.get("CoinSymbol")
            coin_data_signed_by_cold = coin.get("CoinDataSignedByCold", {})
            data_field = coin_data_signed_by_cold.get("Data")

            if data_field:
                try:
                    coin_details = json.loads(data_field)
                    coins_decimals[coin_symbol] = coin_details.get("Decimal")
                except json.JSONDecodeError:
                    continue
            else:
                continue

        return coins_decimals

    def get_faucet_status(self, convert_units: bool = False) -> dict:
        """
        Retrieves and returns the current balance status of the ATM faucet.

        :param convert_units: Whether to convert balance values using coin decimals.
        :return: Dictionary containing coin balances and their addresses.
        """
        account_info = self.apiUser.getAccounts()['FunctionData']['Accounts'][0]
        address_infos = {}
        for address in account_info['AccountDataSignedByCold']['Addresses']:
            symbol = address['CoinSymbol']
            balance = next((balance['HotFunds'] for balance in account_info['BalancesAndPriceForAccount'] if balance['CoinSymbol'] == symbol), "Balance not found")
            balance_above_minimum = int(balance) > faucet_minimum_balances[symbol]
            if convert_units:
                balance = float(balance) / 10 ** self.coins_decimals[symbol]
            else:
                balance = int(balance)
            address_infos[symbol] = {'balance': balance, 'address': address['HotAddress'],
                                     'balance_above_minimum': balance_above_minimum}
        return address_infos

    def send_transaction(self, request_data):
        """
        Sends a transaction for a given cryptocurrency.

        :param request_data: Dictionary containing transaction details (address, amount, coin type).
        :return: API response containing transaction details or an error message.
        """
        target_address = request_data.get("address")
        amount = request_data.get("amount")
        coin_type = request_data.get("coin_symbol")
        transaction_data = [(target_address, amount)]
        response = {"error": "Unsupported currency"}
        try:
            if coin_type == "BTC":
                response = self.apiUser.sendBitcoinTransaction(1, transaction_data, self.fees.BTC)
            elif coin_type == "ETH":
                response = self.apiUser.sendEthereumTransaction(1, transaction_data, self.fees.ETH, gas_limit=GAS_LIMIT_ETH,
                                                           max_priority_fee=MAX_PRIORITY_FEE_ETH)
            elif coin_type == "GK8_ETH":
                response = self.apiUser.sendErc20Transaction(1, "GK8_ETH", transaction_data, self.fees.GK8_ETH,
                                                        gas_limit=GAS_LIMIT_GK8_ETH,
                                                        max_priority_fee=MAX_PRIORITY_FEE_ETH)
            elif coin_type == "BCH":
                response = self.apiUser.sendBitcoinCashTransaction(1, transaction_data, self.fees.BCH)
            elif coin_type == "XRP":
                response = self.apiUser.sendRippleTransaction(1, transaction_data, self.fees.XRP, "sendRipple")
            elif coin_type == "XLM":
                response = self.apiUser.sendStellarTransaction(1, transaction_data, self.fees.XLM)
            elif coin_type == "ADA":
                response = self.apiUser.sendCardanoTransaction(1, transaction_data, self.fees.ADA)
            elif coin_type == "XTZ":
                response = self.apiUser.sendTezosTransaction(1, transaction_data, self.fees.XTZ, gas_limit=GAS_LIMIT_TEZOS,
                                                        storage_limit=STORAGE_LIMIT_TEZOS)
            elif coin_type == "NEAR":
                response = self.apiUser.sendNearTransaction(1, transaction_data)
            elif coin_type == "ATOM":
                response = self.apiUser.sendCosmosTransaction(1, transaction_data, max_fee=MAX_FEE_COSMOS,
                                                         gas_limit=GAS_LIMIT_COSMOS)
            elif coin_type == "HBAR":
                response = self.apiUser.sendHederaTransaction(1, transaction_data, self.fees.HBAR)
            elif coin_type == "SMR":
                response = self.apiUser.sendShimmerTransaction(1, transaction_data)
            elif coin_type == "TRX":
                response = self.apiUser.sendTronTransaction(1, transaction_data)
            elif coin_type == "CSPR":
                response = self.apiUser.sendCasperTransaction(1, transaction_data, gas_price=GAS_PRICE_CSPR,
                                                              payment_amount=PAYMENT_AMOUNT_CSPR)
            elif coin_type == "STRK":
                response = self.apiUser.sendStarknetTransaction(1, transaction_data, max_fee = MAX_FEE_STRK,
                                                                gas_limit = GAS_LIMIT_STRK)
            elif coin_type == "SOL":
                response = self.apiUser.sendSolanaTransaction(1, transaction_data)

        except Exception as e:
            print(f"An error occurred while processing the {coin_type} transaction: {e}")
            self.apiUser.generateNewAccessToken()

        return response
