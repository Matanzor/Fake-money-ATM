#!/usr/bin/env python3

import json
import sys
import argparse
import threading
import time

import requests

from LoadingSpinner import LoadingSpinner

sys.path.append("./scripts/apiclient")
sys.path.append("../scripts/apiclient")
from SendMoneyApp import SendMoneyApp

GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
CLEAR = '\033[0m'

faucet = None


def send_to_address(address, coin_symbol, address_type):
    """
    Initiates a transaction by calling the `send()` function if the address exists.

    This function is responsible for directing funds to a specific address type
    (hot or cold). If the provided address is valid, it forwards the request to
    `send()` to execute the transaction.

    Called by:
    - `send_coin()` when distributing funds to hot/cold wallets.

    :param address: The destination wallet address (hot or cold).
    :param coin_symbol: The symbol of the cryptocurrency (e.g., BTC, ETH).
    :param address_type: The type of address ("hot" or "cold").
    """
    if address is None:
        print(f"No {address_type} address found for {coin_symbol}")
    else:
        send(address, coin_symbol)


def send_coin(coin_type, machine, users_addresses):
    """
    Determines which coins need to be sent and directs transactions accordingly.

    This function decides whether to send funds to an MPC machine, a Cold wallet,
    or both. It then calls `send_to_address()` for each coin and address type.

    Called by:
    - `main()` when executing transactions based on user input.

    Calls:
    - `send_to_address()` to process each transaction.

    :param coin_type: The type of cryptocurrency to send (e.g., BTC, ETH).
    :param machine: The type of machine ('Cold', 'MPC', or 'both').
    :param users_addresses: A dictionary containing users' hot and cold addresses for each coin.
    """
    if coin_type != 'ALL_COINS' and coin_type not in faucet.all_coins:
        print(f'Invalid coin type: {coin_type}')
        return

    if machine not in ["Cold", "MPC", "both"]:
        print(f'Invalid machine type: {machine}')
        return

    if coin_type == 'ALL_COINS':
        coins = faucet.all_coins
    else:
        coins = [coin_type]

    if machine == 'MPC' or machine == 'both':
        print("\nStarting to fund MPC...\n")
        for coin_symbol in coins:
            address = users_addresses.get(coin_symbol, {}).get('HotAddress')
            print(f'Sending {coin_symbol} to MPC HotAddress: {address}')
            send_to_address(address, coin_symbol, 'hot')

    if machine == 'Cold' or machine == 'both':
        print("\nStarting to fund COLD...\n")
        for coin_symbol in coins:
            address = users_addresses.get(coin_symbol, {}).get('ColdAddress')
            print(f'Sending {coin_symbol} to ColdAddress: {address}')
            send_to_address(address, coin_symbol, 'cold')



def send(address, coin_type):
    """
    Reads transaction details from `config.json` and executes a transaction.

    This function retrieves the predefined amount for the specified coin from `config.json`
    and calls the `send_transaction()` method of `SendMoneyApp` to execute the transaction.

    Called by:
    - `send_to_address()` when an address is validated.

    Calls:
    - `faucet.send_transaction()` to execute the transaction.

    :param address: The recipient's wallet address.
    :param coin_type: The type of cryptocurrency to send.
    """
    endpoint = ''

    # Load transaction amounts from configuration file
    with open('config.json', 'r') as file:
        amounts_data = json.load(file)
    function_name_and_amount = {}
    for coin_symbol, amount in amounts_data.items():
        function_name_and_amount[coin_symbol] = [faucet.send_transaction, amount]
    if coin_type in function_name_and_amount:
        function_with_args = function_name_and_amount[coin_type]
        function = function_with_args[0]
        amount = function_with_args[1]
        data = {
            "account_id": 1,
            "address": address,
            "coin_symbol": coin_type,
            "amount": amount
        }
        endpoint = function(data) # Calls faucet.send_transaction(data)
    else:
        print(f"Invalid coin type: {coin_type}")
        return

    try:
        if "Transactions" in endpoint["FunctionData"]:
            print(f'{coin_type} transaction sent successfully!')
        else:
            print(f'Error sending {coin_type} transaction.')
    except KeyError:
        print("Invalid response format: 'FunctionData' key not found.")


class CommaSeparatedListAction(argparse.Action):
    """
    Custom argparse action to allow parsing comma-separated values into lists.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Processes the argument values, splitting them by commas.

        :param parser: The argument parser instance.
        :param namespace: The namespace for storing parsed arguments.
        :param values: The values provided for the argument.
        :param option_string: The option string triggering this action.
        """
        if isinstance(values, list):
            values = ','.join(values)
        assert isinstance(values, str), "values must be a string, not %s" % type(values)
        values = values.strip().split(',')
        values = [v.strip() for v in values if v.strip()]  # Remove empty strings
        print("Values:", values)
        setattr(namespace, self.dest, values)


def main():
    """
    Main function to handle argument parsing, API requests, and transaction execution.
    """
    parser = argparse.ArgumentParser(description='Send coin transaction')
    parser.add_argument('--coin_type', nargs='+',
                        default=['ETH', 'XRP', 'XLM', 'ADA', 'XTZ', 'NEAR', 'HBAR', 'SMR', 'ATOM', 'TRX', 'CSPR', 'STRK', 'SOL'],
                        help='Coin types (default: ETH, XRP, XLM, ADA, XTZ, NEAR, HBAR, SMR, ATOM, TRX, CSPR, STRK, SOL)', action=CommaSeparatedListAction)
    parser.add_argument('--machine', type=str, default='MPC', help='Machine type (default: Cold)')
    parser.add_argument('--all-coins', action='store_true', help='Send transactions for all available coins')
    parser.add_argument('--account', type=int, default=1, help='Account ID (default: 1)')
    parser.add_argument('--get-status', action='store_true', help='Get faucet status')
    parser.add_argument('--base-units', action='store_true', help='Show balances in base units')
    args = parser.parse_args()
    with LoadingSpinner('Connecting to faucet...'):
        global faucet
        faucet = SendMoneyApp()
    if args.get_status:
        with LoadingSpinner('Getting faucet status...'):
            balances = faucet.get_faucet_status(not args.base_units)
        print("{:<9} {:<19} {:<10}".format("Coin", "Balance", "Address"))
        for symbol, address_info in balances.items():
            balance_color = GREEN if address_info['balance_above_minimum'] else RED
            format_str = "{:<9} " + balance_color + "{:<19}" + CLEAR + " {:<10}"
            print(format_str.format(symbol, address_info['balance'], address_info['address']))
        sys.exit()

    account_id = args.account

    response = requests.post("http://127.0.0.1:8090/getAccounts")
    data = json.loads(response.text)
    account = None
    for acc in data["Accounts"]:
        if "AccountDataSignedByCold" in acc and "Id" in acc["AccountDataSignedByCold"]:
            if acc["AccountDataSignedByCold"]["Id"] == account_id:
                account = acc
                break
    if account is None:
        print(f"Account with ID {account_id} not found.")
        sys.exit()

    # Extract user addresses
    addresses = account["AccountDataSignedByCold"]["Addresses"]
    users_addresses = {}
    for currency in addresses:
        currency_symbol = currency["CoinSymbol"]
        currency_addresses = {
            "HotAddress": currency["HotAddress"],
            "ColdAddress": currency["ColdAddress"]
        }
        users_addresses[currency_symbol] = currency_addresses
    coin_types = args.coin_type
    print(coin_types)
    all_coins = args.all_coins

    if all_coins:
        coin_types = faucet.all_coins
    for coin_type in coin_types:
        send_coin(coin_type, args.machine, users_addresses)

    for coin_type in coin_types:
        if coin_type == 'BTC':
            print("Please remember to send BTC funds back to the BTC ATM Address: ", faucet.BTC_HOT_ADDRESS)
        elif coin_type == 'BCH':
            print("Please remember to send BCH funds back to the BCH ATM Address: ", faucet.BCH_HOT_ADDRESS)


if __name__ == '__main__':
    main()
