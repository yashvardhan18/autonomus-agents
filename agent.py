import json
import time
import random
import threading
from web3 import Web3
from dotenv import load_dotenv
import os
from inbox_outbox import MessageQueue

load_dotenv()
web3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))
source_private_key = os.getenv("PRIVATE_KEY_SOURCE")
source_address = os.getenv("ADDRESS_SOURCE")
target_address = os.getenv("ADDRESS_TARGET")
erc20_contract_address = os.getenv("ERC20_CONTRACT_ADDRESS")

# MessageQueue Class for handling message exchange
class MessageQueue:
    def __init__(self):
        self.messages = []
        self.lock = threading.Lock()

    def add_message(self, message):
        """ Add message to the queue (OutBox) """
        with self.lock:
            self.messages.append(message)

    def get_message(self):
        """ Get and remove the first message from the queue (InBox) """
        with self.lock:
            if self.messages:
                return self.messages.pop(0)
            else:
                return None

# AutonomousAgent Base Class for common behavior
class AutonomousAgent:
    def __init__(self, inbox, outbox):
        self.inbox = inbox
        self.outbox = outbox
        self.handlers = {}
        self.behaviors = []

    def register_handler(self, message_type, handler):
        """ Register a handler function for a specific message type. """
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)

    def register_behavior(self, behavior):
        """ Register a proactive behavior for the agent. """
        self.behaviors.append(behavior)

    def process_messages(self):
        """ Process incoming messages concurrently. """
        while True:
            message = self.inbox.get_message()
            if message:
                message_type = message.get("type")
                if message_type in self.handlers:
                    for handler in self.handlers[message_type]:
                        threading.Thread(target=handler, args=(message,)).start()
            time.sleep(1)  # Optional: to avoid CPU spiking

    def run_behaviors(self):
        """ Run the agent's proactive behaviors concurrently. """
        while True:
            for behavior in self.behaviors:
                threading.Thread(target=behavior).start()
            time.sleep(1)

    def start(self):
        """ Start processing messages and behaviors in separate threads. """
        threading.Thread(target=self.process_messages, daemon=True).start()
        threading.Thread(target=self.run_behaviors, daemon=True).start()

class ConcreteAgent(AutonomousAgent):
    def __init__(self, inbox, outbox, web3, source_private_key, source_address, target_address, erc20_contract_address):
        super().__init__(inbox, outbox)
        self.web3 = web3
        self.source_private_key = source_private_key
        self.source_address = source_address
        self.target_address = target_address
        self.erc20_contract = self.web3.eth.contract(address=erc20_contract_address, abi=self.get_erc20_abi())
        self.lock = threading.Lock()
        self.word_list = ["hello", "sun", "world", "space", "moon", "crypto", "sky", "ocean", "universe", "human"]
        self.nonce_cache = {}  # Cache to track the latest nonce

        # Register handlers
        self.register_handler("random_message", self.handle_hello)
        self.register_handler("random_message", self.handle_crypto)
    def get_erc20_abi(self):
        """ Load the ERC-20 ABI from a file or hardcode it """
        try:
            with open("erc20_abi.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("The file 'erc20_abi.json' was not found in the project directory.")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in 'erc20_abi.json'.")
    def generate_random_message(self):
        """ Generate a random message and add it to the OutBox """
        message_content = random.choice(self.word_list)
        
        # Ensure that the message randomly contains either 'hello' or 'crypto'
        if random.choice([True, False]):
            message_content = "hello " + random.choice(self.word_list)
        else:
            message_content = "crypto " + random.choice(self.word_list)

        self.outbox.add_message({"type": "random_message", "content": message_content})
        print(f"Generated message: {message_content}")  # Debug: print generated message
        time.sleep(2)
    def check_erc20_balance(self):
        """ Check ERC-20 token balance """
        balance = self.erc20_contract.functions.balanceOf(self.source_address).call()
        print(f"Balance: {balance}")
        time.sleep(10)        
    def handle_hello(self, message):
        """ Handle messages containing 'hello'. """
        if "hello" in message.get("content", ""):
            print(f"handle_hello invoked for message: {message['content']}")

    def handle_crypto(self, message):
        """ Handle messages containing 'crypto'. """
        balance = self.erc20_contract.functions.balanceOf(self.source_address).call()
        if balance > 0:
            retry_count = 3  # Number of retries for failed transactions
            while retry_count > 0:
                try:
                    # Fetch the latest nonce
                    nonce = self.get_nonce()

                    # Fetch and dynamically increase the gas price
                    gas_price = self.web3.eth.gas_price
                    higher_gas_price = int(gas_price * (1.2 + (3 - retry_count) * 0.1))  # Increment gas price with retries

                    # Build the transaction
                    txn = self.erc20_contract.functions.transfer(
                        self.target_address, 1
                    ).build_transaction({
                        "from": self.source_address,
                        "nonce": nonce,
                        "gas": 200000,
                        "gasPrice": higher_gas_price,
                    })

                    # Sign the transaction
                    signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.source_private_key)

                    # Send the transaction
                    txn_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                    print(f"Transaction sent. Waiting for confirmation... Transaction hash: {txn_hash.hex()}")

                    # Wait for confirmation
                    receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash, timeout=120)
                    if receipt.status == 1:
                        print(f"Transaction confirmed. Block number: {receipt.blockNumber}")
                        return  # Exit the function upon successful confirmation
                    else:
                        print(f"Transaction failed. Receipt: {receipt}")
                        break  # Stop retries if the transaction is explicitly failed
                except Exception as e:
                    # print(f"Transaction error: {e}")
                    if "already known" in str(e):
                        print("Transaction already known, Skipping or retrying.")
                    if "replacement transaction underpriced" in str(e):
                        print("Transaction underpriced, retrying with higher gas price.")
                    retry_count -= 1
                    if retry_count == 0:
                        print("Transaction failed after retries.")
                        return  # Exit after exhausting retries
        else:
            print("Insufficient balance to transfer tokens.")

    def get_nonce(self):
        """ Get the latest nonce and increment it """
        # We can use the cached nonce if it's available or fetch it from the blockchain
        if self.source_address in self.nonce_cache:
            self.nonce_cache[self.source_address] += 1
        else:
            # Fetch the latest nonce from the blockchain
            latest_nonce = self.web3.eth.get_transaction_count(self.source_address, "pending")
            self.nonce_cache[self.source_address] = latest_nonce
        return self.nonce_cache[self.source_address]

if __name__ == "__main__":
    web3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))
    source_private_key = os.getenv("PRIVATE_KEY_SOURCE")
    source_address = os.getenv("ADDRESS_SOURCE")
    target_address = os.getenv("ADDRESS_TARGET")
    erc20_contract_address = os.getenv("ERC20_CONTRACT_ADDRESS")

    inbox1 = MessageQueue()
    outbox1 = MessageQueue()
    inbox2 = outbox1
    outbox2 = inbox1
    
    # Initialize Agent 1 and Agent 2
    agent1 = ConcreteAgent(inbox1, outbox1, web3, source_private_key, source_address, target_address, erc20_contract_address)
    agent2 = ConcreteAgent(inbox2, outbox2, web3, source_private_key, source_address, target_address, erc20_contract_address)

    # Register behaviors and handlers for Agent 1
    agent1.register_behavior(agent1.generate_random_message)
    agent1.register_behavior(agent1.check_erc20_balance)
    agent1.start()

    # Register behaviors and handlers for Agent 2
    agent2.register_behavior(agent2.generate_random_message)
    agent2.register_behavior(agent2.check_erc20_balance)
    agent2.start()

    # Run agents concurrently
    while True:
        pass
