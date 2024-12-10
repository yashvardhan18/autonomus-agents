
This project implements autonomous agents capable of communicating with each other, processing messages, and interacting with the Ethereum blockchain. These agents exhibit reactive and proactive behaviors, such as handling specific message types and generating new ones. Additionally, the agents perform ERC-20 token transfers while managing common blockchain transaction errors.


##  Features 

1. Reactive Behavior :
   - Process messages of type `hello` and `crypto`.
   - `"hello"` messages trigger logging, and `"crypto"` messages initiate ERC-20 token transfers.

2.  Proactive Behavior :
   - Periodically generates random messages to the outbox.
   - Regularly checks the ERC-20 token balance of the source address.

3.  Self-Sufficient Design :
   - Agents operate independently, exchanging messages using an `inbox` and `outbox`.
   - They are designed to run autonomously without external intermediaries like message brokers.

4.  Blockchain Interaction :
   - Uses Web3.py to interact with the Ethereum blockchain.
   - Transfers ERC-20 tokens and manages nonces dynamically to handle transaction retries.



  ## Setup Instructions


1. Clone the Repository 

   Clone this repository to your local machine:

   ```git clone https://github.com/yourusername/autonomous-agents-assignment.git```
   ```cd autonomous-agents-assignment```

2. **Create a Virtual Environment**:
   It's recommended to use a virtual environment to manage dependencies:
   ```bash
   ```python3 -m venv venv```
   
   On Windows: ```venv\Scripts\activate```

   On macOS/Linux: ```source venv/bin/activate```

3. Install the required Python packages using pip:

   ```pip install -r requirements.txt```

4. Create a .env file in the root directory of the project, and add the following environment variables:

   WEB3_PROVIDER_URL=<Your_Tenderly_Fork_URL>
   
   PRIVATE_KEY_SOURCE=<Your_Private_Key>
   
   ADDRESS_SOURCE=<Your_Source_Address>
   
   ADDRESS_TARGET=<Your_Target_Address>
   
   ERC20_CONTRACT_ADDRESS=<Your_ERC20_Contract_Address>


5. Run the unit tests by running the command-
   ```python -m unittest discover -s tests -p "*.py"```
            OR to run specific test files
   ```python -m unittest tests/test_conccreteAgent.py```



6. Start the agents by executing the agent.py script:
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

Generated message: hello world

handle_hello invoked for message: hello world

Balance: 1000000000000000000

Transaction sent. Waiting for confirmation... Transaction hash: 0xabc123...

Transaction confirmed. Block number: 12345678

Generated message: crypto moon

handle_crypto invoked for message: crypto moon

Transaction sent. Waiting for confirmation... Transaction hash: 0xdef456...

Transaction confirmed. Block number: 12345679





## **Known Issues**

Nonce Conflicts: If multiple transactions are sent simultaneously, nonce conflicts might occur. The system handles these by retrying transactions with updated nonces.

Long Wait Times: Blockchain confirmations may take longer than expected depending on network congestion.


