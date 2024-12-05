# tests/test_concrete_agent.py
import unittest
from unittest.mock import MagicMock
from inbox_outbox import MessageQueue
from agent import ConcreteAgent
from web3 import Web3

class TestConcreteAgent(unittest.TestCase):
    def setUp(self):
        # Mock Web3
        self.mock_web3 = MagicMock()
        self.mock_contract = MagicMock()
        self.mock_web3.eth.contract.return_value = self.mock_contract

        # Initialize ConcreteAgent
        self.agent = ConcreteAgent(
            inbox=MessageQueue(),
            outbox=MessageQueue(),
            web3=self.mock_web3,
            source_private_key="0xmockprivatekey",
            source_address="0xMockSourceAddress",
            target_address="0xMockTargetAddress",
            erc20_contract_address="0xMockERC20Contract"
        )
        self.agent.logger = MagicMock()

    def test_handle_hello(self):
        
        message = {"type": "random_message", "content": "hello world"}
        self.agent.handle_hello(message)

        
        self.agent.logger.info.assert_called_with("handle_hello invoked for message: hello world")

    def test_handle_crypto_with_sufficient_balance(self):
        
        self.mock_contract.functions.balanceOf.return_value.call.return_value = 100

        
        message = {"type": "random_message", "content": "crypto world"}
        self.agent.handle_crypto(message)

        
        self.agent.logger.info.assert_any_call("Processing crypto message: crypto world")
        self.mock_web3.eth.send_raw_transaction.assert_called_once()

    def test_handle_crypto_with_insufficient_balance(self):
        
        self.mock_contract.functions.balanceOf.return_value.call.return_value = 0

        
        message = {"type": "random_message", "content": "crypto world"}
        self.agent.handle_crypto(message)

        
        self.agent.logger.warning.assert_called_with("Insufficient balance to transfer tokens.")
