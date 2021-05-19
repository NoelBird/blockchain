import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transaction = []
        self.nodes = set()

        # genesis block
        self.new_block(previous_hash=1, proof=100)
    
    def new_block(self, proof, previous_hash=None):
        # Creates a new block and adds it to the chain
        block = {
            'index': len(self.chain)+1,
            'timestamp': time(), # timestamp from 1970
            'transactions': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transaction = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transactions
        self.current_transaction.append(
            {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            }
        )
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Hashes a Block
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last Blcok in the chain
        return self.chain[-1]

    def pow(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof
    
    def register_node(self, address):
        parsed_url = urlparse(address).netloc
        print(parsed_url)
        self.nodes.add(parsed_url)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print("%s " % last_block)
            print("%s " % block)
            print("\n----------\n")
            # check that the hash of the block is currect
            if block["previous_hash"] != self.hash(last_block):
                return False
            last_block = block
            current_index += 1
        return True
    
    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)
        for node in neighbors:
            tmp_url = 'http://' + str(node) + '/chain'
            response = requests.get(tmp_url)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
            if new_chain:
                self.chain = new_chain
                return True
            return False
            
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = str(last_proof + proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000" # nonce

