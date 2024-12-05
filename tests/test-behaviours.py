# tests/test_behaviors.py
import unittest
from unittest.mock import MagicMock
from inbox_outbox import MessageQueue
from agent import ConcreteAgent

class TestBehaviors(unittest.TestCase):
    def setUp(self):
        # Mock Web3 and ERC20 contract
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

    def test_generate_random_message(self):
        
        self.agent.generate_random_message()

        
        message = self.agent.outbox.get_message()
        self.assertIsNotNone(message)
        self.assertIn("content", message)
        self.agent.logger.info.assert_called()

    def test_check_erc20_balance(self):
        
        self.mock_contract.functions.balanceOf.return_value.call.return_value = 12345

        
        self.agent.check_erc20_balance()

        
        self.agent.logger.info.assert_called_with("Balance: 12345")
