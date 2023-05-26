from typing import Dict, List, Optional, Tuple
from blspy import (PrivateKey, AugSchemeMPL, PopSchemeMPL, G1Element, G2Element)
from pymerkle import MerkleTree
from chia.types.spend_bundle import SpendBundle


class Verifier:
    """
    Receives an array of signed transactions with public keys and an aggregated signature that can then be verified
    in constant time. Also, possibly receives single transactions that could not be aggregated.
    """

    batch: List[SpendBundle]  # batch of transactions to be aggregated
    batch_pks: List[G1Element]  # list of public keys
    digest: MerkleTree  # digest of a batch in a form of Merkle Tree
    single_transactions: List[Tuple[SpendBundle, G1Element]]  # all transactions that could not complete digest signing
    agg_signed_digest: G2Element  # aggregated digest signatures

    def __init__(self):
        self.batch = []
        self.batch_pks = list[G1Element]()
        self.digest = MerkleTree()
        self.single_transactions = list[Tuple[SpendBundle, G1Element]]()
        self.agg_signed_digest = G2Element()

    def receive_transactions(self) -> None:
        """
        TODO: to be implemented
        """

    def regenerate_digest(self):
        """
        generates a merkle tree from the batch
        """
        for (tx, signature) in self.batch:
            # TODO: need to put SpendBundles and not signatures into a digest
            # However, spend bundles have aggregate signatures field, which takes additional space, so we should get rid
            # of it when SIGINT is used to maximize space and time efficiency
            self.digest.append_entry(bytes(tx.aggregated_signature))
        return

    def verify(self):
        """
        verifies the transactions of the batch in constant time and any separate transactions if there are any
        """
        # verify batch
        ok = PopSchemeMPL.aggregate_verify(self.batch_pks, self.digest, self.agg_signed_digest)

        # verify any separate signatures
        for bundle, pk in self.single_transactions:
            ok = AugSchemeMPL.verify(pk, bundle.coin_spends, bundle.aggregated_signature)
            if not ok:
                return False
        return ok

    def push_to_blockchain(self):
        """
        pushes all verified transactions to blockchain
        """
        # TODO: to be implemented

