from flask import Flask, request, jsonify
from wallet import get_wallet
from aggregator import Aggregator
import asyncio

server = Flask(__name__)
aggregator = Aggregator(3)
wallet = asyncio.run(get_wallet())


# route
# route function
@server.route('/send_transaction', methods=["POST"])
def api_send_transaction():
    try:
        data = request.get_json()
        # print(data)
        public_key = data['pk']
        amount = data["send_dict"]['amount']
        receiver_address = data["send_dict"]['address']
        
        print("AGGREGATION REQUEST RECEIVED")
        asyncio.run(aggregator.receive_transaction(public_key, amount, receiver_address))
        # aggregator.receive_transaction(public_key, amount, receiver_address, receiver, )
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# listen
if __name__ == "__main__":
  server.run(port=3000, debug=True, use_reloader=False)

