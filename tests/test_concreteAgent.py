import unittest
from unittest.mock import MagicMock, patch
from queue import Queue
from agent import ConcreteAgent, AutonomousAgent, MessageQueue

class TestAgents(unittest.TestCase):
    def setUp(self):
        # Mock web3 and contract setup
        self.web3_mock = MagicMock()
        self.contract_mock = MagicMock()
        self.web3_mock.eth.contract.return_value = self.contract_mock

        # Mock ERC20 methods
        self.contract_mock.functions.balanceOf.return_value.call.return_value = 100  # Mock balance
        self.contract_mock.functions.transfer.return_value.build_transaction.return_value = {
            "from": "mock_address",
            "nonce": 1,
            "gas": 200000,
            "gasPrice": 1,
        }

        # Mock accounts
        self.source_address = "0xSourceAddress"
        self.target_address = "0xTargetAddress"
        self.source_private_key = "0xMockPrivateKey"

        # Initialize MessageQueue mocks
        self.inbox = MessageQueue()
        self.outbox = MessageQueue()

        # Initialize ConcreteAgent
        self.agent = ConcreteAgent(
            inbox=self.inbox,
            outbox=self.outbox,
            web3=self.web3_mock,
            source_address=self.source_address,
            target_address=self.target_address,
            erc20_contract=self.contract_mock,
            source_private_key=self.source_private_key,
            agent_name="agent1",
        )

    def test_generate_message(self):
        with self.assertLogs(self.agent.logger, level="INFO") as log:
            self.agent.generate_message()
            self.assertTrue(
                any("Generated message:" in record for record in log.output),
                "Message generation log not found"
            )

    def test_check_balance(self):
        with self.assertLogs(self.agent.logger, level="INFO") as log:
            self.agent.check_balance()
            # Verify that the balance log contains the mocked balance
            self.assertTrue(
                any("Balance: 100" in record for record in log.output),
                "Balance log not found"
            )

    def test_handle_hello(self):
        message = {"type": "random_message", "content": "hello world"}
        with self.assertLogs(self.agent.logger, level="INFO") as log:
            self.agent.handle_hello(message)
            self.assertTrue(
                any("handle_hello invoked" in record for record in log.output),
                "handle_hello log not found"
            )


    def test_handle_crypto_insufficient_balance(self):
        # Mock balance to be zero
        self.contract_mock.functions.balanceOf.return_value.call.return_value = 0
        message = {"type": "random_message", "content": "crypto hello"}
        with self.assertLogs(self.agent.logger, level="WARNING") as log:
            self.agent.handle_crypto(message)
            self.assertTrue(
                any("Insufficient balance" in record for record in log.output),
                "Insufficient balance log not found"
            )




if __name__ == "__main__":
    unittest.main()
