from datetime import datetime
import hashlib

# Blockchain Data
chain = []
pending_transactions = []


def create_genesis_block():
    block = {
        "index": 0,
        "timestamp": str(datetime.now()),
        "transactions": [],
        "previous_hash": "0",
        "nonce": 0,
        "hash": "",
    }
    block["hash"] = calculate_hash(block)
    chain.append(block)


def calculate_hash(block):
    block_string = f'{block["index"]}{block["timestamp"]}{block["transactions"]}{block["previous_hash"]}{block["nonce"]}'
    return hashlib.sha256(block_string.encode()).hexdigest()


def mine_block(miner_id):
    if len(pending_transactions) == 0:
        return None

    last_block = chain[-1]
    block = {
        "index": len(chain),
        "timestamp": str(datetime.now()),
        "transactions": pending_transactions.copy(),
        "previous_hash": last_block["hash"],
        "nonce": 0,
        "hash": "",
    }

    while not block["hash"].startswith("0000"):
        block["nonce"] += 1
        block["hash"] = calculate_hash(block)

    chain.append(block)
    pending_transactions.clear()


def create_transaction(sender, recipient, amount):
    transaction = {"sender": sender, "recipient": recipient, "amount": amount}
    pending_transactions.append(transaction)
    return {"status": "success", "transaction": transaction}


def get_chain():
    return chain


def get_balance(user_id):
    balance = 0
    for block in chain:
        for tx in block["transactions"]:
            if tx["sender"] == user_id:
                balance -= tx["amount"]
            if tx["recipient"] == user_id:
                balance += tx["amount"]
    return balance


create_genesis_block()
