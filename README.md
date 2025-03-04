# 🚀 ATM Faucet System – Automated Fake Money Distribution  

## 📌 Overview  
This project provides an **automated ATM faucet system** that allows developers to quickly and efficiently receive **test cryptocurrency** for their local development environments. Instead of manually searching for faucets and waiting for funds, developers can use this **script-based ATM** to request multiple fake cryptocurrencies instantly.  

## ⚙️ How It Works  
1️⃣ The **developer runs `SendMoney.py`** on their local machine to request test funds.  
2️⃣ The script **communicates with the cloud-based ATM (`SendMoneyApp.py`)**, which processes the request.  
3️⃣ The ATM **validates balances, selects the appropriate transaction method**, and sends the requested fake money to the developer’s wallet.  
4️⃣ The developer **receives the requested test funds within seconds.**  

---

## 🚀 Features  
✅ **Instant Fake Crypto Distribution** – No more waiting for testnet faucets.  
✅ **Supports Multiple Currencies** – Easily request BTC, ETH, XRP, and more.  
✅ **Automated Balance Validation** – Ensures funds are available before transactions.  
✅ **Scalable & Secure** – Can be extended to support more test currencies.  

---

## 🛠️ Setup & Installation  

### 1️⃣ Clone the Repository  
```bash
git https://github.com/Matanzor/Fake-money-ATM.git
cd Fake-money-ATM
```

---

💰 Usage
1️⃣ Check Available Faucet Balances
Run the following command to see available funds:
```bash
python3 SendMoney.py --get-status
```
2️⃣ Request Fake Money for a Specific Coin
```bash
python3 SendMoney.py --coin_type BTC
```
✅ Sends BTC test funds to the developer’s wallet.

3️⃣ Request Funds for Multiple Coins
```bash
python3 SendMoney.py --coin_type BTC ETH XRP
```
✅ Sends multiple cryptocurrencies in one request.

4️⃣ Request All Available Coins
```bash
python3 SendMoney.py --all-coins
```
✅ Automatically sends all supported currencies to the developer’s wallet.

---

⚙️ How It Works Internally
🔹 SendMoney.py → User-facing script that sends requests to the ATM.
🔹 SendMoneyApp.py → ATM backend that processes and executes transactions.
🔹 config.json → Stores default amounts for each currency (pre-configured, no modification needed).

---

📌 Supported Cryptocurrencies
The system currently supports:

BTC, ETH, BCH, XRP, XLM, ADA, XTZ, NEAR, HBAR, SMR, ATOM, TRX, CSPR, STRK, SOL
Easily extendable by adding new coins to SendMoneyApp.py.

---

## 🔄 Improvements & Lessons Learned  

Since originally writing this project **1.5 years ago**, I have **gained more experience** and identified several key areas for improvement:  

### **✅ 1. Modular Code Structure**  
- Move **hardcoded variables** (`path`, `all_coins`, `faucet_minimum_balances`, etc.) into **separate config files** for cleaner, more maintainable code.  

### **✅ 2. Automate Coin Management**  
- Dynamically fetch `all_coins` from `ApiClient.getCoins()` instead of manually defining them.  
- Exclude only **system-unsupported coins**, making the process of adding new cryptocurrencies fully automated.  

### **✅ 3. Automate Transaction Settings**  
- Fetch **gas limits, transaction fees, and other blockchain-specific settings** dynamically from `ApiClient.getCoins()`, reducing manual updates.  

### **✅ 4. Implement Smart Caching for Expensive API Calls**  
- **Reduce redundant API calls** by caching the following:  
  - `getSuggestedFee()` → Fetches transaction fees (changes rarely).  
  - `getAccounts()` → Account data doesn't change often (cache short-term).  
  - `getCoins()` → Coin metadata (cache short-term to minimize unnecessary calls).  
- **Balance between caching and real-time updates**: Cache data for **short durations** to reduce API load while still supporting new accounts/coins.  

### **✅ 5. Add a Logging System**  
- Introduce a **dedicated logging class** for tracking:  
  - API requests & responses  
  - Transaction success/failures  
  - Warnings and error handling  

📌 **These improvements will make the system more efficient, scalable, and maintainable for future expansion.**  
"""

