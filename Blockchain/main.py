#Interacting with the Dexter's blockchain with multiple nodes using HTTP requests

from flask import Flask, jsonify, request

from blockchain import Blockchain

#Initialise our node with identifier and instantiate the Blockchain class
app = Flask(__name__)
blockchain = Blockchain()

#API endpoint to mine a block, its an HTTP GET request
@app.route('/mine', methods=['GET'])

#Method to mine a block 
def mine():

    #To ensure that only delegates elected by voting can mine a new block
    current_port = "localhost:"+ str(port)
    if(current_port in blockchain.delegates):

        # To ensure that a new block is mined only if there are atleast 2 transactions
        if len(blockchain.unverified_transactions) >= 2:
            last_block = blockchain.last_block
            previous_hash = blockchain.hash(last_block)
            block = blockchain.new_block(previous_hash)

            response = {
                'message': "New block mined!",
                'index': block['index'],
                'transactions': block['transactions'],
                'previous_hash': block['previous_hash']
            }
            print(len(blockchain.unverified_transactions))
            return jsonify(response), 200

        else:
            response = {
                'message' : 'Not enough transactions to mine a new block and add to chain!'
            }
            print(len(blockchain.unverified_transactions))
            return jsonify(response),400
    else:
        response = {
            'message': 'You are not authorised to mine block! Only delegates can mine.'
        }
        return jsonify(response),400


#Endpoint for a new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['Customer name','Item name', 'Total billing amount']
    if not all(k in values for k in required):
        return 'Missing values! Please enter customer name, item name and billing amount.', 400
    
    index = blockchain.new_transaction(values['Customer name'], values['Item name'], values['Total billing amount'])

    response = {
        'message': f'Transaction will be added to block {index}'
    }
    return jsonify(response), 201


#Endpoint for viewing the blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


#Endpoint for adding HTTP address of new nodes along with their stakes in the network.
@app.route('/nodes/add', methods=['POST'])
def add_nodes():
    values = request.get_json()
    required = ['nodes','stake']
    
    if not all(k in values for k in required):
        return 'Error',400

    blockchain.add_node(values['nodes'], values['stake'])
    
    response = {
        'message': 'New nodes are added!',
        'total_nodes': list(blockchain.nodes)
    }
    print(blockchain.nodes)
    return jsonify(response), 201


#Endpoint to start the voting process
@app.route('/voting',methods=['GET'])
def voting():

    if(port == 5000):
        show_votes = blockchain.add_vote()

        response ={
            'message': 'The voting results are as follows:',
            'nodes': blockchain.voteNodespool
            }
        
        return jsonify(response),200
        
    else:
        response={
            'message': 'You are not authorized to conduct the election process!'
        }
        return jsonify(response),400


#Endpoint to view the list of all three elected delegate nodes
@app.route('/delegates/show',methods=['GET'])
def delegates():
    show_delegates = blockchain.selection()

    response={
        'message': 'The 3 delegate nodes selected for block mining are:',
        'node_delegates': blockchain.delegates
    }
    return jsonify(response),200


#Endpoint to synchronise the list of elected delegates with all other nodes in the network 
@app.route('/delegates/sync',methods=['GET'])
def sync_delegates():
    sync_delegates = blockchain.sync()

    response ={
        'message': 'The delegate nodes are:',
        'node_delegates':blockchain.delegates
    }
    return jsonify(response),200


#Endpoint to resolve and replace current chain with the longest validated one,achieving consensus
@app.route('/chain/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_chain()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='Listening on port')
    args = parser.parse_args()
    port = args.port
    app.run(host = '0.0.0.0', port = port)
