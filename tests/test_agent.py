def test_handle_hello():
    inbox = MessageQueue()
    outbox = MessageQueue()
    web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
    agent = ConcreteAgent(inbox, outbox, web3, ..., ..., ...)
    inbox.add_message({"type": "random_message", "content": "hello world"})
    agent.process_messages()
    # Check if message was processed correctly

def test_integration():
    inbox1 = MessageQueue()
    outbox1 = MessageQueue()
    inbox2 = outbox1
    outbox2 = inbox1
    web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
    agent1 = ConcreteAgent(inbox1, outbox1, web3, ..., ..., ...)
    agent2 = ConcreteAgent(inbox2, outbox2, web3, ..., ..., ...)
    agent1.start()
    agent2.start()
    # Simulate message passing and verify results
