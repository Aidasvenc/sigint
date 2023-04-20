import sys
from typing import Dict, List, Optional, Tuple
from blspy import (PrivateKey, AugSchemeMPL, G1Element, G2Element)
import pymerkle
from chia.types.spend_bundle import SpendBundle
from chia.wallet.transaction_record import TransactionRecord

sys.path.append('../chia_blockchain')


class Aggregator:
    """
    Has to have an array of Transactions(SpendBundle + additional parameters) that it can possibly aggregate
    We have 2 choices:
    1. Fill the array from the mempool by calling create_bundle_from_mempool() that will also aggregate many
    SpendBundles into one SpendBundle with a multi-sig
    2. Fill the array gradually by receiving requests that contain transactions(or SpendBundles)
    """

    signed_transactions: List[SpendBundle]  # use generate_signed_transaction() from wallet_tools
    batch_threshold: int  # number of transactions that are aggregated into a batch
    batch: List[SpendBundle]  # batch of transactions to be aggregated
    digest: bytearray  # digest of a batch in a form of Merkle Tree
    signed_digest: List[G2Element]  # all signatures of digest
    agg_digest: G2Element  # aggregated digest signatures

    def __init__(self, batch_threshold: int):
        self.signed_transactions = List[SpendBundle]()
        self.batch_threshold = batch_threshold
        self.batch = List[SpendBundle]()
        self.digest = bytearray()
        self.signed_digest = List[G2Element]()
        self.agg_digest = G2Element()

    def receive_transaction(self) -> None:
        """
        TODO: beginning to be defined by Alberto
        """

    def create_batch(self):
        """
        creates a batch from the SpendBundles that were accumulated
        """
        if len(self.signed_transactions) > self.batch_threshold:
            self.batch = self.signed_transactions[:]

        return generate_digest()

    def generate_digest(self):
        """
        generates a merkle tree from the
        """
