import asyncio
from chia.wallet.transaction_record import TransactionRecord
from flask import Flask, request, jsonify
import logging
from aggregator import Aggregator
from wallet import get_wallet
import asyncio

log = logging.getLogger()

class AggregatorServer():
    app = Flask(__name__)

    async def __init__(self, aggregator: Aggregator):
        self.aggregator = aggregator
        loop = asyncio.get_event_loop()
        loop.run_until_complete(aggregator.wait_for_txs())
        self.app.run(port=3000, debug=True, use_reloader=False)

    @app.route('/queue_transaction', methods=["POST"])
    def api_queue_transaction(self):
        log.info("Aggregation request received")
        data = request.get_json()
        print(data)
        tx = TransactionRecord(**data)
        print(tx)
        
        self.aggregator.receive_transaction(tx)
        
        return jsonify({'status': 'success'}), 200

    @app.route('/sign_digest', methods=["POST"])
    def api_sign_digest():
        return jsonify({'status': 'success'}), 200

async def main():
    wallet = await get_wallet()
    agg = Aggregator(2, wallet)
    AggregatorServer(agg)

if __name__ == "__main__":
    asyncio.run(main())
    
