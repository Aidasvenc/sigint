from chia.wallet.transaction_record import TransactionRecord
from flask import Flask, request, jsonify
from wallet import get_wallet
from aggregator import Aggregator
import asyncio

server = Flask(__name__)
aggregator = Aggregator(3)
wallet = asyncio.run(get_wallet())


# route
# route function
@server.route('/queue_transaction', methods=["POST"])
def api_queue_transaction():
    print("AGGREGATION REQUEST RECEIVED")
    data = request.get_json()
    print(data)
    tx = TransactionRecord(**data)
    print(tx)
    
    asyncio.run(aggregator.receive_transaction("pk placeholder", tx))
    
    return jsonify({'status': 'success'}), 200

@server.route('/sign_digest', methods=["POST"])
def api_sign_digest():
    return jsonify({'status': 'success'}), 200

# listen
if __name__ == "__main__":
  server.run(port=3000, debug=True, use_reloader=False)

