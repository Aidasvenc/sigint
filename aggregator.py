import concurrent.futures
import time
from typing import Dict, List, Optional, Tuple
from blspy import (PrivateKey, AugSchemeMPL, G1Element, G2Element)
from pymerkle import MerkleTree
from chia.types.spend_bundle import SpendBundle


class Aggregator:
    """
    Has to have an array of Transactions(SpendBundle + additional parameters) that it can possibly aggregate
    We have 2 choices:
    1. Fill the array from the mempool by calling create_bundle_from_mempool() that will also aggregate many
    SpendBundles into one SpendBundle with a multi-sig
    2. Fill the array gradually by receiving requests that contain transactions(or SpendBundles)
    """

    signed_transactions: List[Tuple[SpendBundle, G1Element]]  # use generate_signed_transaction() from wallet_tools
    batch_threshold: int  # number of transactions that are aggregated into a batch
    batch: List[Tuple[SpendBundle, G1Element]]  # batch of transactions to be aggregated
    digest: MerkleTree  # digest of a batch in a form of Merkle Tree
    signed_digest: List[G2Element]  # all signatures of digest
    single_transactions: List[SpendBundle]  # all transactions that could not complete digest signing
    agg_signed_digest: G2Element  # aggregated digest signatures

    def __init__(self, batch_threshold: int):
        self.signed_transactions = List[Tuple[SpendBundle, G1Element]]()
        self.batch_threshold = batch_threshold
        self.batch = List[Tuple[SpendBundle, G1Element]]()
        self.digest = MerkleTree()
        self.signed_digest = List[G2Element]()
        self.agg_signed_digest = G2Element()

    def receive_transaction(self) -> None:
        """
        TODO: to be implemented
        """

    def create_batch(self):
        """
        creates a batch from the SpendBundles that were accumulated
        """
        if len(self.signed_transactions) > self.batch_threshold:
            self.batch = self.signed_transactions[:]
            return self.generate_digest()

        return print('There is not enough transactions to put in a batch')

    def generate_digest(self):
        """
        generates a merkle tree from the batch
        """
        for (tx, signature) in self.batch:
            # TODO: are messages or signatures put into a merkle tree?
            self.digest.append_entry(bytes(tx.aggregated_signature))
        return self.request_to_sign_digest()

    def request_to_sign_digest(self):
        """
        requests all clients in a batch of transactions to sign the generated digest in parallel
        """
        # send requests in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_request = {executor.submit(self.send_request, receiver, self.digest): (receiver, self.digest)
                                 for receiver in self.batch}

        # Wait for some time for the requests to complete
        time.sleep(10)

        # Check the status of each request
        for future in future_to_request:
            (receiver, data) = future_to_request[future]
            if not future.done() or future.cancelled():
                future.cancel()
                self.single_transactions.append(receiver)

        return self.aggregate_batch()

    def send_request(self, receiver, data):
        """
        sends a single request to a receiver
        TODO: to be implemented
        """

    def aggregate_batch(self):
        """
        aggregates signatures of a digest in a batch
        """
        self.agg_signed_digest = AugSchemeMPL.aggregate(self.signed_digest)

    def send_to_verifier(self):
        """
        submits the aggregated signed batch and any unsuccessfully signed transactions
        to the verifier.
        TODO: To be defined
        """