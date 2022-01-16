import json
import os
from dotenv import load_dotenv
# In the video, we forget to `install_solc`
# from solcx import compile_standard
from solcx import compile_standard, install_solc
from web3 import Web3

load_dotenv()


def get_transaction_params() -> dict:
    # Get the latest transaction
    nonce = w3.eth.getTransactionCount(my_address)
    return {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": my_address, "nonce": nonce}


def sign_and_send_transaction(transaction, wait_for_receipt: bool):
    # Sign the transaction
    print("Signing transaction...")
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key=private_key
    )
    # Send it!
    print("Sending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    if wait_for_receipt:
        # Wait for the transaction to be mined, and get the transaction receipt
        print("Waiting for transaction to finish...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    return None


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# We add these two lines that we forgot from the video!
print("Installing...")
install_solc("0.6.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

compiled_simple_storage = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]

# get bytecode
bytecode = compiled_simple_storage["evm"]["bytecode"]["object"]

# get abi
abi = json.loads(
    compiled_simple_storage["metadata"]
)["output"]["abi"]

# w3 = Web3(Web3.HTTPProvider(os.getenv("RINKEBY_RPC_URL")))
# chain_id = 4
#
# For connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://0.0.0.0:8545"))
chain_id = 1337
my_address = "0xdbB4A708755dfD59f9c4b100B2BE23a6d2EB7D57"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Submit the transaction that deploys the contract
transaction = SimpleStorage.constructor().buildTransaction(get_transaction_params())
print("Deploying Contract!")
tx_receipt = sign_and_send_transaction(transaction, True)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")


# Working with deployed Contracts
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
greeting_transaction = simple_storage.functions.store(15).buildTransaction(get_transaction_params())
tx_receipt = sign_and_send_transaction(greeting_transaction, True)
print("Updating stored Value...")

print(simple_storage.functions.retrieve().call())
