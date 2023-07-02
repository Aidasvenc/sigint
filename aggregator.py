import time
from typing import List, Tuple
from blspy import (PopSchemeMPL, G1Element, G2Element)
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.wallet.transaction_record import TransactionRecord
from pymerkle import MerkleTree
from chia.types.spend_bundle import SpendBundle
from threading import Lock
import logging 
import asyncio
from wallet import get_wallet
from server import AggregatorServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger()


class Aggregator:
    """
    Has to have an array of Transactions(SpendBundle + additional parameters) that it can possibly aggregate
    We have 2 choices:
    1. Fill the array from the mempool by calling create_bundle_from_mempool() that will also aggregate many
    SpendBundles into one SpendBundle with a multi-sig
    2. Fill the array gradually by receiving requests that contain transactions(or SpendBundles)
    """

    signed_transactions: List[TransactionRecord]  # use generate_signed_transaction() from wallet_tools
    batch_threshold: int  # number of transactions that are aggregated into a batch
    batch: List[SpendBundle]  # batch of transactions to be aggregated
    digest: MerkleTree  # digest of a batch in a form of Merkle Tree
    signed_digest: List[G2Element]  # all signatures of digest
    single_transactions: List[Tuple[SpendBundle, G1Element]]  # all transactions that could not complete digest signing
    lock : Lock
    wallet: WalletRpcClient

    def __init__(self, batch_threshold: int, wallet: WalletRpcClient):
        self.signed_transactions = list()
        self.batch_threshold = batch_threshold
        self.batch = list()
        self.digest = MerkleTree()
        self.signed_digest = list()
        self.wallet = wallet

    async def wait_for_txs(self):
        log.info("Started aggregator main loop")
        while True:
            await asyncio.sleep(2)
            log.info("Attempting aggregation")
            self.create_batch()
        
    def receive_transaction(self, tx: TransactionRecord) -> None:
            self.signed_transactions.append(tx)


    def create_batch(self):
        """
        Attemps to creates a batch from the SpendBundles that were accumulated
        """
    
        if len(self.signed_transactions) > self.batch_threshold:
            for tx in self.signed_transactions:
                spend_bundle = tx.spend_bundle
                assert spend_bundle is not None
                if spend_bundle is None:
                    log.error("Received transaction doesn't contain a spend bundle")
                else:
                    self.batch.append(spend_bundle)
            self.signed_transactions = []
            self.generate_digest()
        else:
            log.info(f"Aggregation not possible, waiting for {self.batch_threshold - len(self.signed_transactions)} tx(s)")

    def generate_digest(self):
        """
        generates a merkle tree from the batch
        """
        for sb in self.batch:
            self.digest.append_entry(str(hash(sb))) 
        return self.request_to_sign_digest()

    def request_to_sign_digest(self):
        """
        requests all clients in a batch of transactions to sign the generated digest in parallel
        """
        for tx in self.batch:
            print(tx)
            target = self.digest.root_node
            proof = self.digest.prove_inclusion(0)
            self.wallet.sign_digest(target, proof)
        
    def aggregate_batch(self):
        """
        aggregates signatures of a digest in a batch
        """
        self.agg_signed_digest = PopSchemeMPL.aggregate(self.signed_digest)
        # TODO: consider aggregating the public keys to make verification faster

    async def send_to_verifier(self):
        """
        submits the aggregated signed batch and any unsuccessfully signed transactions
        to the verifier.
        """
        await self.wallet.send_aggregated_transactions([], "signature placeholder")
        

async def start_server(server):
    print("server", flush=True)
    server.app.run(port=3000, debug=True, use_reloader=False)

async def run_parallel():
    wallet = await get_wallet()
    agg = Aggregator(2, wallet)
    server = AggregatorServer(agg)
    task2 = loop.create_task(start_server(server))
    task1 = loop.create_task(start_aggregator(agg))
    await asyncio.wait([task1, task2])
    
    wallet.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_parallel())
    loop.close()
