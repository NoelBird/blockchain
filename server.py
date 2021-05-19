# /chain: 현재 블록체인 보여줌
# /transaction/new: 새 트랜잭션 생성
# /mine: server에게 새 블록 채굴 요청
from flask import Flask, jsonify, request
from blockchain import Blockchain
from uuid import uuid4

app = Flask(__name__)
# Universial Unique Identifier
node_identifider = str(uuid4()).replace("-", "")

blockchain = Blockchain()

@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route("/mine", methods=["GET"])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block["proof"]

    proof = blockchain.pow(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=node_identifider,
        amount=1 # coinbase transaction
    )
    # forge the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "new block found",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }

    return response, 200

@app.route("/transactions/new", methods=["POST"])
def new_transactions():
    values = request.get_json()

    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return "missing values", 400
    
    # Create a new Transaction
    index = blockchain.new_transaction(values["sender"], values["recipient"], values["amount"])
    response = {"message": "Transaction will be added to Block {%s}" % index}

    return jsonify(response), 201

@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    values = request.get_json()

    nodes = values.get("nodes")
    if nodes is None:
        return "Error: please supply a valid list of nodes", 400
    
    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        "message": "New nodes have been added",
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts() # True False return

    if replaced:
        response = {
            "message": "Our chain was replaced",
            "new_chain": blockchain.chain
        }
    else:
        response = {
            "message": "Our chain is authoritative",
            "chain": blockchain.chain
        }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)