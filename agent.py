import os
import json
import time
import random
import threading
import logging
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
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
            return None


class AutonomousAgent:
    def __init__(self, inbox, outbox, agent_name):
        self.inbox = inbox
        self.outbox = outbox
        self.agent_name = agent_name
        self.logger = logging.getLogger(agent_name)

    def handle_hello(self, message):
        if "hello" in message.get("content", ""):
            self.logger.info(f"handle_hello invoked for message: {message['content']}")

    def handle_crypto(self, message):
        if "crypto" in message.get("content", ""):
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

    def process_messages(self):
        while True:
            message = self.inbox.get_message()
            if message:
                if "hello" in message["content"]:
                    self.handle_hello(message)
                elif "crypto" in message["content"]:
                    self.handle_crypto(message)
            time.sleep(0.1)


class ConcreteAgent(AutonomousAgent):
    def __init__(self, inbox, outbox, web3, source_address, target_address, erc20_contract, agent_name):
        super().__init__(inbox, outbox, agent_name)
        self.web3 = web3
        self.source_address = source_address
        self.target_address = target_address
        self.erc20_contract = erc20_contract
        self.word_list = ["hello", "sun", "world", "space", "moon", "crypto", "sky", "ocean", "universe", "human"]

    def generate_message(self):
        message_content = random.choice(self.word_list)
        if random.choice([True, False]):
            message_content = "hello " + random.choice(self.word_list)
        else:
            message_content = "crypto " + random.choice(self.word_list)

        self.outbox.add_message({"type": "random_message", "content": message_content})
        self.logger.info(f"Generated message: {message_content}")

    def check_balance(self):
        balance = self.erc20_contract.functions.balanceOf(self.source_address).call()
        self.logger.info(f"Balance: {balance}")


# Synchronization events
agent1_done_event = threading.Event()


def agent1_cycle(agent1):
    while True:
        agent1.generate_message()
        agent1_done_event.set()  # Notify Agent 2
        time.sleep(4)  # Agent 1 generates messages every 2 seconds


def agent2_cycle(agent2):
    while True:
        agent1_done_event.wait()  # Wait for Agent 1 to finish
        time.sleep(2)  # Ensure a 2-second delay after Agent 1
        agent2.generate_message()
        agent1_done_event.clear()  # Reset for the next round


def balance_cycle(agent1, agent2):
    while True:
        # Agent 1 checks balance
        agent1.check_balance()
        time.sleep(9)
        # Agent 2 checks balance
        agent2.check_balance()
        time.sleep(9)


def main():
    web3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))
    source_address = os.getenv("ADDRESS_SOURCE")
    target_address = os.getenv("ADDRESS_TARGET")
    erc20_contract_address = os.getenv("ERC20_CONTRACT_ADDRESS")

    # Load ERC20 ABI
    with open("erc20_abi.json", "r") as f:
        erc20_abi = json.load(f)

    erc20_contract = web3.eth.contract(address=erc20_contract_address, abi=erc20_abi)

    # Message queues
    inbox1 = MessageQueue()
    outbox1 = MessageQueue()
    inbox2 = outbox1
    outbox2 = inbox1

    # Agents
    agent1 = ConcreteAgent(inbox1, outbox1, web3, source_address, target_address, erc20_contract, "agent1")
    agent2 = ConcreteAgent(inbox2, outbox2, web3, source_address, target_address, erc20_contract, "agent2")

    # Threads
    threading.Thread(target=agent1.process_messages, daemon=True).start()
    threading.Thread(target=agent2.process_messages, daemon=True).start()
    threading.Thread(target=agent1_cycle, args=(agent1,), daemon=True).start()
    threading.Thread(target=agent2_cycle, args=(agent2,), daemon=True).start()
    threading.Thread(target=balance_cycle, args=(agent1, agent2), daemon=True).start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
