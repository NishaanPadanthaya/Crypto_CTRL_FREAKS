import streamlit as st
import hashlib
import json
import time
import requests


class Transaction:
    def __init__(self, sender, recipient, value):
        self.sender = sender
        self.recipient = recipient
        self.value = value

class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block([], "0")

    def get_last_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, miner_address):
        block = Block(self.pending_transactions, self.get_last_block().hash)
        while not block.hash.startswith('0' * self.difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        st.write("Block mined:", block.hash)
        self.chain.append(block)
        self.pending_transactions = []

    def create_transaction(self, sender, recipient, value):
        self.pending_transactions.append(Transaction(sender, recipient, value))

    def add_block_manually(self, transactions):
        block = Block(transactions, self.get_last_block().hash)
        self.chain.append(block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

def find_platform(transaction_id, input_address, output_address):
    # Replace 'YOUR_API_KEY', 'YOUR_API_SECRET', and 'EXCHANGE_API_ENDPOINT' with your actual API credentials and endpoint
    api_key = 'YOUR_API_KEY'
    api_secret = 'YOUR_API_SECRET'
    api_endpoint = 'EXCHANGE_API_ENDPOINT'
    
    # Construct the request payload
    payload = {
        'transaction_id': transaction_id,
        'input_address': input_address,
        'output_address': output_address,
        # Include any other required parameters for the API query
    }
    
    # Make a request to the exchange API
    response = requests.post(api_endpoint, json=payload, auth=(api_key, api_secret))
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON data
        data = response.json()
        
        # Extract relevant information from the response
        platform = data.get('platform')
        
        # Return the platform
        return platform
    else:
        st.error(f'Error: {response.status_code}')
        return None

def get_transaction_data(address):
    api_url = f"https://blockchain.info/rawtx/b6f6991d03df0e2e04dafffcd6bc418aac66049e2cd74b80f14ac86db1e3f0da"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Failed to fetch data: {response.status_code}")

def main():
    st.set_page_config(page_title='Blockchain Explorer', page_icon=':link:')
    st.title('Blockchain Explorer')
    st.write("Welcome to the Blockchain Explorer!")

    page = st.sidebar.radio("Navigation", ["Blockchain Explorer", "Platform Finder", "Transaction Analysis"])

    if page == "Blockchain Explorer":
        blockchain = Blockchain()
        st.write("Current Blockchain Status:")
        st.write("Chain Length:", len(blockchain.chain))
        st.write("Is Chain Valid?", blockchain.is_chain_valid())

        st.write("Create a Transaction:")
        sender = st.text_input("Sender")
        recipient = st.text_input("Recipient")
        value = st.number_input("Value", min_value=0)
        if st.button("Create Transaction"):
            blockchain.create_transaction(sender, recipient, value)
            st.write("Transaction created successfully!")

        if st.button("Mine Block"):
            miner_address = st.text_input("Miner Address")
            blockchain.mine_pending_transactions(miner_address)
            st.write("Block mined successfully!")

        st.write("Manually Add a Block:")
        transactions = st.text_area("Enter Transactions (JSON format)")
        if st.button("Add Block"):
            try:
                transactions = json.loads(transactions)
                blockchain.add_block_manually(transactions)
                st.write("Block added successfully!")
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please enter transactions in JSON format.")

        st.write("Updated Blockchain Status:")
        st.write("Chain Length:", len(blockchain.chain))
        st.write("Is Chain Valid?", blockchain.is_chain_valid())

    elif page == "Platform Finder":
        st.title('Platform Finder')
        st.write("Enter the transaction details below to find the cryptocurrency platform.")
        
        transaction_id = st.text_input('Transaction ID')
        input_address = st.text_input('Input Wallet Address')
        output_address = st.text_input('Output Wallet Address')
        
        if st.button('Find Platform'):
            with st.spinner('Searching...'):
                if transaction_id and input_address and output_address:
                    platform = find_platform(transaction_id, input_address, output_address)
                    if platform:
                        st.success(f'Platform: {platform}')
                    else:
                        st.error('Failed to determine platform. Please check your inputs and try again.')
                else:
                    st.warning('Please provide transaction ID, input address, and output address.')

    elif page == "Transaction Analysis":
        st.title('Blockchain Transaction Analysis')
        address = st.text_input("Enter Transaction ID")
        if st.button("Get Transaction Data"):
            if address:
                transaction_data = get_transaction_data(address)
                if transaction_data:
                    st.write("Transaction Data:")
                    st.write(transaction_data)
                    print(transaction_data)
                else:
                    st.warning("No data found for the provided address.")
            else:
                st.warning("Please enter a wallet address.")

if __name__ == "__main__":
    main()
