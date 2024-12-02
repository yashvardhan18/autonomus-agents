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


class MessageQueue:
    def __init__(self):
        self.messages = []
        self.lock = threading.Lock()

    def add_message(self, message):
        
        with self.lock:
            self.messages.append(message)

    def get_message(self):
        
        with self.lock:
            if self.messages:
                return self.messages.pop(0)
            else:
                return None


class AutonomousAgent:
    def __init__(self, inbox, outbox):
        self.inbox = inbox
        self.outbox = outbox
        self.handlers = {}
        self.behaviors = []

    def register_handler(self, message_type, handler):
        
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)

    def register_behavior(self, behavior):
        
        self.behaviors.append(behavior)

    def process_messages(self):
        
        while True:
            message = self.inbox.get_message()
            if message:
                message_type = message.get("type")
                if message_type in self.handlers:
                    for handler in self.handlers[message_type]:
                        threading.Thread(target=handler, args=(message,)).start()
            time.sleep(1)  

    def run_behaviors(self):
        
        while True:
            for behavior in self.behaviors:
                threading.Thread(target=behavior).start()
            time.sleep(1)

    def start(self):
        
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
        self.nonce_cache = {}  

       
        self.register_handler("random_message", self.handle_hello)
        self.register_handler("random_message", self.handle_crypto)
    def get_erc20_abi(self):
        
        try:
            with open("erc20_abi.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("The file 'erc20_abi.json' was not found in the project directory.")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in 'erc20_abi.json'.")
    def generate_random_message(self):
        
        message_content = random.choice(self.word_list)
        
     
        if random.choice([True, False]):
            message_content = "hello " + random.choice(self.word_list)
        else:
            message_content = "crypto " + random.choice(self.word_list)

        self.outbox.add_message({"type": "random_message", "content": message_content})
        print(f"Generated message: {message_content}")  
        time.sleep(2)
    def check_erc20_balance(self):
        
        balance = self.erc20_contract.functions.balanceOf(self.source_address).call()
        print(f"Balance: {balance}")
        time.sleep(10)        
    def handle_hello(self, message):
        
        if "hello" in message.get("content", ""):
            print(f"handle_hello invoked for message: {message['content']}")

    def handle_crypto(self, message):
        
        balance = self.erc20_contract.functions.balanceOf(self.source_address).call()
        if balance > 0:
            retry_count = 2  
            while retry_count > 0:
                try:
                    
                    nonce = self.get_nonce()

                    
                    gas_price = self.web3.eth.gas_price
                    higher_gas_price = int(gas_price * (1.2 + (3 - retry_count) * 0.1))  #

                    
                    txn = self.erc20_contract.functions.transfer(
                        self.target_address, 1
                    ).build_transaction({
                        "from": self.source_address,
                        "nonce": nonce,
                        "gas": 200000,
                        "gasPrice": higher_gas_price,
                    })

                    
                    signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.source_private_key)

                    
                    txn_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                    print(f"Transaction sent. Waiting for confirmation... Transaction hash: {txn_hash.hex()}")

                    
                    receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash, timeout=120)
                    if receipt.status == 1:
                        print(f"Transaction confirmed. Block number: {receipt.blockNumber}")
                        return  
                    else:
                        print(f"Transaction failed. Receipt: {receipt}")
                        break  
                except Exception as e:
                    
                    if "already known" in str(e):
                        print("Transaction already known, Skipping or retrying.")
                    if "replacement transaction underpriced" in str(e):
                        print("Transaction underpriced, retrying with higher gas price.")
                    retry_count -= 1
                    if retry_count == 0:
                        print("Transaction failed after retries.")
                        return  
        else:
            print("Insufficient balance to transfer tokens.")

    def get_nonce(self):
        
        
        if self.source_address in self.nonce_cache:
            self.nonce_cache[self.source_address] += 1
        else:
            
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
    
    
    agent1 = ConcreteAgent(inbox1, outbox1, web3, source_private_key, source_address, target_address, erc20_contract_address)
    agent2 = ConcreteAgent(inbox2, outbox2, web3, source_private_key, source_address, target_address, erc20_contract_address)

    
    agent1.register_behavior(agent1.generate_random_message)
    agent1.register_behavior(agent1.check_erc20_balance)
    agent1.start()

    
    agent2.register_behavior(agent2.generate_random_message)
    agent2.register_behavior(agent2.check_erc20_balance)
    agent2.start()

    
    while True:
        pass
