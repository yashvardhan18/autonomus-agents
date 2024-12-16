# Autonomous Agents for Ethereum Interaction

This project implements autonomous agents capable of inter-agent communication, message processing, and Ethereum blockchain interaction. These agents exhibit both reactive and proactive behaviors, such as processing specific message types, generating messages, and performing ERC-20 token transfers while managing blockchain transaction errors.

---

## Features

1. **Reactive Behavior**
   - Handles messages of types `hello` and `crypto`.
   - `"hello"` messages trigger logging via `handle_hello`.
   - `"crypto"` messages initiate ERC-20 token transfers using `handle_crypto`.

2. **Proactive Behavior**
   - Periodically generates random messages to the outbox.
   - Regularly checks the ERC-20 token balance of the source address.

3. **Self-Sufficient Design**
   - Agents operate independently, using `inbox` and `outbox` queues for communication.
   - Designed to function autonomously without external intermediaries.

4. **Blockchain Interaction**
   - Uses Web3.py to interact with the Ethereum blockchain.
   - Transfers ERC-20 tokens and dynamically manages nonces for transaction retries.

---



  ## Setup Instructions


### 1. Clone the Repository 

   Clone this repository to your local machine:

   ```git clone https://github.com/yourusername/autonomous-agents-assignment.git```
   ```cd autonomous-agents-assignment```

### 2. Create a Virtual Environment:
   It's recommended to use a virtual environment to manage dependencies:
   ```bash
   ```python3 -m venv venv```
   
   On Windows: ```venv\Scripts\activate```

   On macOS/Linux: ```source venv/bin/activate```

###3. Install the required Python packages using pip:

   ```pip install -r requirements.txt```

###4. Create a .env file in the root directory of the project, and add the following environment variables:

   WEB3_PROVIDER_URL=<Your_Tenderly_Fork_URL>
   
   PRIVATE_KEY_SOURCE=<Your_Private_Key>
   
   ADDRESS_SOURCE=<Your_Source_Address>
   
   ADDRESS_TARGET=<Your_Target_Address>
   
   ERC20_CONTRACT_ADDRESS=<Your_ERC20_Contract_Address>


###5. Run the unit tests by running the command-
   ```python -m unittest discover -s tests -p "*.py"```
            OR to run specific test files
   ```python -m unittest tests/test_concreteAgent.py```



###6. Start the agents by executing the agent.py script:
   ```python agent.py```





## **How It Works**
**Message Handling:**

Agents listen to their inboxes for messages and process them using registered handlers.
"hello" messages are logged by handle_hello.
"crypto" messages trigger ERC-20 token transfers via handle_crypto.


**Message Generation:**

Agents proactively generate random messages periodically and add them to the outbox.


**Error Handling:**

Handles common Ethereum transaction errors, including:
-nonce too low

-already known

-replacement transaction underpriced

Implements retries with increasing gas prices for failed transactions






## **Example Logs**

When you run the script, you should see logs similar to the following:

```2024-12-10 17:38:47,864 - agent1 - INFO - Generated message: hello world

2024-12-10 17:38:47,964 - agent2 - INFO - handle_hello invoked for message: hello world

2024-12-10 17:38:48,746 - agent1 - INFO - Balance: 98897999594

2024-12-10 17:38:49,865 - agent2 - INFO - Generated message: crypto hello

2024-12-10 17:38:49,870 - agent1 - INFO - handle_hello invoked for message: crypto hello

2024-12-10 17:38:51,865 - agent1 - INFO - Generated message: crypto ocean

2024-12-10 17:38:51,877 - agent2 - INFO - Processing crypto message: crypto ocean

2024-12-10 17:38:53,866 - agent2 - INFO - Generated message: hello ocean

2024-12-10 17:38:53,882 - agent1 - INFO - handle_hello invoked for message: hello ocean

2024-12-10 17:38:55,865 - agent1 - INFO - Generated message: crypto sun

2024-12-10 17:38:55,964 - agent2 - INFO - Processing crypto message: crypto sun

2024-12-10 17:38:57,866 - agent2 - INFO - Generated message: hello ocean

2024-12-10 17:38:57,895 - agent1 - INFO - handle_hello invoked for message: hello ocean

2024-12-10 17:38:58,695 - agent2 - INFO - Balance: 98897999594```





## **Known Issues**

Nonce Conflicts: If multiple transactions are sent simultaneously, nonce conflicts might occur. The system handles these by retrying transactions with updated nonces.

Long Wait Times: Blockchain confirmations may take longer than expected depending on network congestion.

Transaction Retries: Due to sepolia congestion the transaction might fail.


