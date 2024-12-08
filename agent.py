import json
import time
import random
import threading
import logging
from web3 import Web3
from dotenv import load_dotenv
import os
from inbox_outbox import MessageQueue

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)



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
        
        for behavior in self.behaviors:
            threading.Thread(target=behavior, daemon=True).start()

    def start(self):
    
        threading.Thread(target=self.process_messages, daemon=True).start()
        self.run_behaviors()

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
 
        next_run = time.monotonic()  # Agent-specific timing
        while True:
            current_time = time.monotonic()
            if current_time >= next_run:
                message_content = random.choice(self.word_list)
                if random.choice([True, False]):
                    message_content = "hello " + random.choice(self.word_list)
                else:
                    message_content = "crypto " + random.choice(self.word_list)

                self.outbox.add_message({"type": "random_message", "content": message_content})
                self.logger.info(f"[{self.logger.name}] Generated message: {message_content}")
                next_run += 2  # Increment by 2 seconds
            else:
                time.sleep(0.1)  # Sleep briefly to reduce CPU usage

    def check_erc20_balance(self):

        next_run = time.monotonic()  # Agent-specific timing
        while True:
            current_time = time.monotonic()
            if current_time >= next_run:
                balance = self.erc20_contract.functions.balanceOf(self.source_address).call()
                self.logger.info(f"[{self.logger.name}] Balance: {balance}")
                next_run += 10  # Increment by 10 seconds
            else:
                time.sleep(0.1)  # Sleep briefly to reduce CPU usage
        
    def handle_hello(self, message):
        
        if "hello" in message.get("content", ""):
            self.logger.info(f"handle_hello invoked for message: {message['content']}")

    def handle_crypto(self, message):
        self.logger.info(f"Processing crypto message: {message['content']}")
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
                    self.logger.info(f"Transaction sent. Waiting for confirmation... Transaction hash: {txn_hash.hex()}")

                    
                    receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash, timeout=120)
                    if receipt.status == 1:
                        self.logger.info(f"Transaction confirmed. Block number: {receipt.blockNumber}")
                        return  
                    else:
                        self.logger.error(f"Transaction failed. Receipt: {receipt}")
                        break  
                except Exception as e:
                    
                    if "already known" in str(e):
                        self.logger.error("Transaction already known, Skipping or retrying.")
                    if "replacement transaction underpriced" in str(e):
                        self.logger.error("Transaction underpriced, retrying with higher gas price.")
                    retry_count -= 1
                    if retry_count == 0:
                        self.logger.error("Transaction failed after retries.")
                        return  
        else:
            self.logger.warning("Insufficient balance to transfer tokens.")

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
    agent1_logger = logging.getLogger("Agent1")
    agent2_logger = logging.getLogger("Agent2")
    inbox1 = MessageQueue()
    outbox1 = MessageQueue()
    inbox2 = outbox1
    outbox2 = inbox1
    
    
    agent1 = ConcreteAgent(inbox1, outbox1, web3, source_private_key, source_address, target_address, erc20_contract_address)
    agent1.logger = agent1_logger
    agent2 = ConcreteAgent(inbox2, outbox2, web3, source_private_key, source_address, target_address, erc20_contract_address)
    agent2.logger = agent2_logger

    
    agent1.register_behavior(agent1.generate_random_message)
    agent1.register_behavior(agent1.check_erc20_balance)
    agent1.start()

    
    agent2.register_behavior(agent2.generate_random_message)
    agent2.register_behavior(agent2.check_erc20_balance)
    # agent2.start()

    
    while True:
        pass








