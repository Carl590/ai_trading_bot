# Solana Auto Trading Bot Guide

Thanks for the clarification — we're now targeting:

---

### ✅ GOAL:

Build a **fully functional backend** in **Python** for a **Telegram bot** that:

* Receives webhook alerts from **TradingView** (already working on your end).
* Parses alerts that contain **`buy`** or **`sell`** and a **Solana token address**.
* **Automatically buys/sells** SPL tokens on Solana based on those alerts.

---

### ⚙️ TECH STACK OVERVIEW:

| Component         | Tool/Library                              |
| ----------------- | ----------------------------------------- |
| Blockchain        | Solana                                    |
| Python Solana API | `solana-py` + `anchorpy` (optional)       |
| Trading Interface | `jupiter-aggregator` via API or SDK       |
| Wallet            | `Keypair` from solana-py                  |
| Webhook Parsing   | `FastAPI` (to receive TradingView alerts) |
| Optional Telegram | `python-telegram-bot` or `aiogram`        |

---

## 🛠️ Step-by-Step Plan:

1. **Receive TradingView Webhook**
2. **Parse Message → Detect `buy`/`sell` + Token Address**
3. **Use Jupiter Aggregator** to swap (buy/sell) tokens:

   * BUY = Swap SOL → Token
   * SELL = Swap Token → SOL
4. **Sign & Send TX** from your wallet
5. **Log or report status**

---

## ✅ Deliverable: Fully Functional Python Backend for Auto Buy/Sell on Solana

I'll now write a complete working backend code (including `FastAPI` server + Jupiter swap handler).
We'll assume:

* You have a funded **Solana wallet (Keypair)**.
* Alerts look like this:

  ```json
  {
    "action": "buy",
    "address": "So11111111111111111111111111111111111111112"
  }
  ```

---

## 🧠 Dependencies to Install

```bash
pip install fastapi uvicorn solana requests
```

We'll use Jupiter Aggregator via API (not SDK) for simplicity.

---

## 🧾 `main.py` — Solana AutoTrader Backend

```python
from fastapi import FastAPI, Request
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
import requests
import base64
import json
import os

app = FastAPI()

# --- CONFIG ---
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6"
RPC_URL = "https://api.mainnet-beta.solana.com"
client = Client(RPC_URL)

# Load wallet from a local file
with open("id.json", "r") as f:
    secret_key = json.load(f)
    WALLET = Keypair.from_secret_key(bytes(secret_key))

OWNER = WALLET.public_key
INPUT_MINT = "So11111111111111111111111111111111111111112"  # SOL token address

# --- Swap Execution ---
def get_swap_route(input_mint, output_mint, amount, swap_mode):
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": str(amount),
        "slippageBps": 100,  # 1% slippage
        "swapMode": swap_mode
    }
    response = requests.get(f"{JUPITER_SWAP_API}/quote", params=params)
    routes = response.json().get("data", [])
    if not routes:
        raise Exception("No swap route found")
    return routes[0]

def execute_swap(route):
    swap_tx = requests.post(
        f"{JUPITER_SWAP_API}/swap",
        json={
            "route": route,
            "userPublicKey": str(OWNER),
            "wrapUnwrapSOL": True,
            "feeAccount": None,
            "asLegacyTransaction": True
        }
    ).json()

    tx_base64 = swap_tx["swapTransaction"]
    tx_bytes = base64.b64decode(tx_base64)
    tx = Transaction.deserialize(tx_bytes)
    tx.sign(WALLET)
    tx_sig = client.send_raw_transaction(tx.serialize(), opts=TxOpts(skip_preflight=True))
    return tx_sig["result"]

# --- FastAPI Route for TradingView Webhook ---
@app.post("/webhook")
async def tradingview_webhook(request: Request):
    data = await request.json()
    action = data.get("action")
    token_address = data.get("address")

    if not action or not token_address:
        return {"error": "Invalid payload"}

    try:
        if action.lower() == "buy":
            # Buy token: SOL → token
            # For testing: Buy 0.01 SOL (1e7 lamports)
            amount = 10_000_000
            route = get_swap_route(INPUT_MINT, token_address, amount, "ExactIn")
        elif action.lower() == "sell":
            # Sell token: token → SOL
            # For testing: Sell 1 unit (adjust decimals accordingly)
            amount = 1_000_000  # Assume 6 decimals
            route = get_swap_route(token_address, INPUT_MINT, amount, "ExactIn")
        else:
            return {"error": "Unknown action"}

        tx_sig = execute_swap(route)
        return {"status": "success", "tx": tx_sig}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
```

---

## 📁 Wallet File: `id.json`

Export your Solana wallet's keypair into a JSON array and save it as `id.json`.

Example (for testing only!):

```json
[12, 34, 56, ..., 89]
```

Use `solana-keygen` to export yours:

```bash
solana-keygen new --outfile id.json
```

---

## 🚀 Run the Bot

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Your webhook endpoint will be:

```
POST http://<your-ip>:8000/webhook
```

TradingView alert message:

```json
{
  "action": "buy",
  "address": "TARGET_TOKEN_ADDRESS"
}
```

---

## 🔐 Important Notes

* **Never expose your private key.**
* Test on **devnet** first if possible.
* Jupiter supports `asLegacyTransaction` which is signed like a normal TX.
* You must handle **token account creation** for selling if it's your first time receiving a token.