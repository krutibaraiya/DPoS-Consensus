#Implementation of a simple decentralized blockchain class with multiple nodes and DPoS consensus in the network

import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse
import requests
from random import randint

# Blockchain class
class Blockchain(object):
    
    # Constructor which creates lists to store the blockchain and the transactions
    def __init__(self):

        #List to store the blockchain
        self.chain = []

        #List to store the unverified transactions
        self.unverified_transactions = []  

        #List to store verified transactions
        self.verified_transactions = []

        #Genesis block        
        self.new_block(previous_hash = 1)

        #Set containing the nodes in the network. Used set here to prevent the same node getting added again.
        self.nodes = set()

        #List containing all the nodes along with their stake in the network
        self.all_nodes = []

        #List of all the voting nodes in the network
        self.voteNodespool = []

        #List which stores all the nodes in descending order of votes received
        self.starNodespool = []

        #List to store the top 3 nodes with the highest (stake * votes_received)
        self.superNodespool = []

        #List to store the address of the delegate nodes selected for mining process
        self.delegates = []


    # Method to create a new block in the Blockchain
    def new_block(self,previous_hash = None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'transactions': self.unverified_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.verified_transactions += self.unverified_transactions
        print(self.verified_transactions)
        self.unverified_transactions = []

        #appending the block at the end of the blockchain
        self.chain.append(block)
        return block


    #Method to add a new transaction in the next block
    def new_transaction(self, sender, item_name, bill_amount):
        self.unverified_transactions.append({
            'Customer name': sender,
            'Recipient': "Dexter's Coffee Shop",
            'Item name': item_name,
            'Total billing amount': bill_amount,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return self.last_block['index'] + 1


    @property
    def last_block(self):
        return self.chain[-1]


    #Static method to create a SHA-256 Hash of a given block
    @staticmethod
    def hash(block):       
        block_string = json.dumps(block, sort_keys = True).encode()
        hash_val = hashlib.sha256(block_string).hexdigest()
        return hash_val


    #Method to add node using its IP address to our Blockchain network. 
    def add_node(self, address, stake):
        parsed_url = urlparse(address)
        authority = stake
        self.nodes.add((parsed_url.netloc,authority))


    #Method to simulate the voting process
    def add_vote(self):
        self.all_nodes = list(self.nodes)

        for x in self.all_nodes:
            y=list(x)
            y.append(x[1] * randint(0,100))
            self.voteNodespool.append(y)

        print(self.voteNodespool)
    

    #Method to select top three nodes based on voting results
    def selection(self):
        self.starNodespool = sorted(self.voteNodespool, key = lambda vote: vote[2],reverse = True)
        print(self.starNodespool)

        for x in range(3):
            self.superNodespool.append(self.starNodespool[x])
        print(self.superNodespool)

        for y in self.superNodespool:
            self.delegates.append(y[0])
        print(self.delegates)


    #Method to sync the list
    def sync(self):
        r = requests.get('http://localhost:5000/delegates/show')
        print(r)

        if(r.status_code == 200):
            delegates = r.json()['node_delegates']
            self.delegates = delegates[0:3]
            print(self.delegates)


    #Method to check if the chain is validated.
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            #If the hash value of the current block isn't correct then return false
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            last_block = block
            current_index += 1

        return True
    

    #Method to replace the blockchain with the longest validated chain in the network.
    def resolve_chain(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours: 
            response = requests.get(f'http://{node}/chain')
        
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
        
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True

        return False    
   
