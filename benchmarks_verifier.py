import numpy as np
import time
import multiprocessing
from random import randint
import matplotlib.pyplot as plt
from verifier import Verifier
from chia.types.spend_bundle import SpendBundle
from chia.types.coin_spend import CoinSpend
from chia.types.blockchain_format.serialized_program import SerializedProgram
from chia.types.blockchain_format.coin import Coin
from blspy import (PrivateKey, AugSchemeMPL, PopSchemeMPL, G1Element, G2Element)
from pymerkle import MerkleTree


def generate_spend_bundle():
    return generate_coin_spend()


def generate_coin_spend():
    coin = bytes([randint(0, 255) for _ in range(320)])
    return coin


def sign_spend_bundle(spend_bundle):
    seed = bytes([randint(0, 255) for _ in range(0, 32)])
    sk: PrivateKey = AugSchemeMPL.key_gen(seed)
    pk: G1Element = sk.get_g1()
    sig: G2Element = AugSchemeMPL.sign(sk, spend_bundle)
    return pk, sk, sig


def generate_digest(spend_bundles):
    digest = MerkleTree()
    for bundle in spend_bundles:
        digest.append_entry(bundle)
    return digest


def sign_digest(digest):
    seed = bytes([randint(0, 255) for _ in range(0, 32)])
    sk: PrivateKey = PopSchemeMPL.key_gen(seed)
    pk: G1Element = sk.get_g1()
    sig: G2Element = PopSchemeMPL.sign(sk, digest.root)
    return pk, sk, sig


def aggregate_batch(digest_signatures):
    return PopSchemeMPL.aggregate(digest_signatures)


def aggregate_single(single_sigs):
    return AugSchemeMPL.aggregate(single_sigs)


def verify_batch(digest_signatures, digest, pks):
    start_time = time.time()
    # execute verification function for the batch
    verified = PopSchemeMPL.fast_aggregate_verify(pks, digest.root, digest_signatures)
    verification_time = time.time() - start_time
    return verified, verification_time


def verify_single(agg_single_sigs, spend_bundles, pks):
    start_time = time.time()
    # execute verification function for the batch
    verified = AugSchemeMPL.aggregate_verify(pks, spend_bundles, agg_single_sigs)
    verification_time = time.time() - start_time
    return verified, verification_time


def run_block(spend_bundles, sigs, pks):
    # run benchmarking
    times_sum = [0] * 624
    single_transactions = [0] * 624
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(0, 624):
            print('iteration', i)
            # generate the digest of all spend_bundles
            digest = generate_digest(spend_bundles[0:624-i])

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in spend_bundles[0:624-i]:
                pk, sk, sig = sign_digest(digest)
                sks_digest.append(sk)
                pks_digest.append(pk)
                sigs_digest.append(sig)

            # aggregate the digest signatures
            sig_agg_digest = aggregate_batch(sigs_digest)

            # aggregate single signatures
            sig_agg_single = aggregate_single(sigs[624-i:624])

            # verify the aggregate signatures
            verified, verification_time = verify_batch(sig_agg_digest, digest, pks_digest[0:624-i])

            # verify single signatures
            verified2, verification_time2 = verify_single(sig_agg_single, spend_bundles[624-i:624], pks[624-i:624])

            # add to plot
            single_transactions[i] = i
            times_sum[i] += verification_time + verification_time2

    times_sum = [elem/3 for elem in times_sum]
    plt.plot(single_transactions, times_sum)
    plt.xlabel('Number of straggler transactions')
    plt.ylabel('Verification time (seconds)')
    plt.title('Verification time for 625 transactions')
    plt.show()


def run_fully_aggregated(spend_bundles):
    # run benchmarking
    times_sum = [0] * 625
    num_transactions = [0] * 625
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(1, 625):
            print('iteration', i)
            # generate the digest of all spend_bundles
            digest = generate_digest(spend_bundles[0:i])

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in spend_bundles[0:i]:
                pk, sk, sig = sign_digest(digest)
                sks_digest.append(sk)
                pks_digest.append(pk)
                sigs_digest.append(sig)

            # aggregate the digest signatures
            sig_agg_digest = aggregate_batch(sigs_digest)

            # verify the aggregate signatures
            verified, verification_time = verify_batch(sig_agg_digest, digest, pks_digest[0:i])

            # add to plot
            num_transactions[i] = i
            times_sum[i] += verification_time

    times_sum = [elem / 3 for elem in times_sum]
    return times_sum, num_transactions


def run_fully_single(spend_bundles, sigs, pks):
    # run benchmarking
    times_sum = [0] * 625
    num_transactions = [0] * 625
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(1, 625):
            print('iteration', i)

            # aggregate single signatures
            sig_agg_single = aggregate_single(sigs[0:i])

            # verify single signatures
            verified2, verification_time2 = verify_single(sig_agg_single, spend_bundles[0:i], pks[0:i])

            # add to plot
            num_transactions[i] = i
            times_sum[i] += verification_time2

    times_sum = [elem / 3 for elem in times_sum]
    return times_sum, num_transactions


def run_compare_fully_vs_single(spend_bundles, sigs, pks):

    # Get the results from the subfunctions
    times1_sum, num1_transactions = run_fully_aggregated(spend_bundles)
    times2_sum, num2_transactions = run_fully_single(spend_bundles, sigs, pks)

    plt.plot(num1_transactions, times1_sum, color='g', label='fully aggregated')
    plt.plot(num1_transactions, times2_sum, color='r', label='fully single')
    plt.xlabel('Number of transactions')
    plt.ylabel('Verification time (seconds)')
    plt.title('Performance of fully aggregated SIGINT vs. one-by-one transaction verification')
    plt.legend()
    plt.show()


def run_fully_aggregated_with_digest_generation(spend_bundles):
    # run benchmarking
    times_sum = [0] * 625
    num_transactions = [0] * 625
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(1, 625):
            print('iteration', i)
            # generate the digest of all spend_bundles
            time_digest_start = time.time()
            digest = generate_digest(spend_bundles[0:i])
            time_digest = time.time() - time_digest_start

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in spend_bundles[0:i]:
                pk, sk, sig = sign_digest(digest)
                sks_digest.append(sk)
                pks_digest.append(pk)
                sigs_digest.append(sig)

            # aggregate the digest signatures
            sig_agg_digest = aggregate_batch(sigs_digest)

            # verify the aggregate signatures
            verified, verification_time = verify_batch(sig_agg_digest, digest, pks_digest[0:i])

            # add to plot
            num_transactions[i] = i
            times_sum[i] += verification_time + time_digest

    times_sum = [elem / 3 for elem in times_sum]

    plt.plot(num_transactions[1:], times_sum[1:])
    plt.xlabel('Number of transactions')
    plt.ylabel('Verification time (seconds)')
    plt.title('Verification time for fully aggregated transactions (including digest regeneration)')
    plt.show()


def run_optimal_block(spend_bundles, sigs, pks):
    # run benchmarking
    times_sum = [0] * 624
    num_transactions = [0] * 624
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(10, 624):
            print('iteration', i)
            # generate the digest of all spend_bundles
            digest = generate_digest(spend_bundles[0:i])

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in spend_bundles[0:i]:
                pk, sk, sig = sign_digest(digest)
                sks_digest.append(sk)
                pks_digest.append(pk)
                sigs_digest.append(sig)

            # aggregate the digest signatures
            sig_agg_digest = aggregate_batch(sigs_digest)

            # aggregate single signatures
            sig_agg_single = aggregate_single(sigs[i:(i+i/10)-1])

            # verify the aggregate signatures
            verified, verification_time = verify_batch(sig_agg_digest, digest, pks_digest[0:i])

            # verify single signatures
            verified2, verification_time2 = verify_single(sig_agg_single, spend_bundles[i:(i+i/10)-1], pks[i:(i+i/10)-1])

            # add to plot
            num_transactions[i] = i
            times_sum[i] += verification_time + verification_time2

    times_sum = [elem/3 for elem in times_sum]
    plt.plot(num_transactions[10:], times_sum[10:])
    plt.xlabel('Number of transactions in a block')
    plt.ylabel('Verification time (seconds)')
    plt.title('Verification time for different-sized blocks (assuming 10% stragglers)')
    plt.show()


def run_block_with_digest_regeneration(spend_bundles, sigs, pks):
    # run benchmarking
    times_sum = [0] * 624
    single_transactions = [0] * 624
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(0, 624):
            print('iteration', i)
            # generate the digest of all spend_bundles
            time_digest_start = time.time()
            digest = generate_digest(spend_bundles[0:624-i])
            time_digest = time.time() - time_digest_start

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in spend_bundles[0:624-i]:
                pk, sk, sig = sign_digest(digest)
                sks_digest.append(sk)
                pks_digest.append(pk)
                sigs_digest.append(sig)

            # aggregate the digest signatures
            sig_agg_digest = aggregate_batch(sigs_digest)

            # aggregate single signatures
            sig_agg_single = aggregate_single(sigs[624-i:624])

            # verify the aggregate signatures
            verified, verification_time = verify_batch(sig_agg_digest, digest, pks_digest[0:624-i])

            # verify single signatures
            verified2, verification_time2 = verify_single(sig_agg_single, spend_bundles[624-i:624], pks[624-i:624])

            # add to plot
            single_transactions[i] = i
            times_sum[i] += verification_time + verification_time2 + time_digest

    times_sum = [elem/3 for elem in times_sum]
    plt.plot(single_transactions, times_sum)
    plt.xlabel('Number of straggler transactions')
    plt.ylabel('Verification time (seconds)')
    plt.title('Verification time for 625 transactions (including digest regeneration)')
    plt.show()


if __name__ == '__main__':
    # create 625 spend bundles (assuming 10 coin spends per spend bundle) that will be in the block
    spend_bundles = []
    for i in range(0, 625):
        spend_bundles.append(generate_spend_bundle())

    # sign all generated 625 spend bundles
    sks = []
    pks = []
    sigs = []
    for spend_bundle in spend_bundles:
        pk, sk, sig = sign_spend_bundle(spend_bundle)
        sks.append(sk)
        pks.append(pk)
        sigs.append(sig)
    # test 1
    # run_block(spend_bundles, sigs, pks)

    # test 2
    # times_sum, num_transactions = run_fully_aggregated(spend_bundles)
    # plt.plot(num_transactions[1:], times_sum[1:])
    # plt.xlabel('Number of transactions')
    # plt.ylabel('Verification time (seconds)')
    # plt.title('Verification time for fully aggregated transactions')
    # plt.show()
    # test 3
    # run_fully_single(spend_bundles, sigs, pks)

    # test 4
    # run_compare_fully_vs_single(spend_bundles, sigs, pks)

    # test 5
    # run_fully_aggregated_with_digest_generation(spend_bundles)

    # test 6
    run_block_with_digest_regeneration(spend_bundles, sigs, pks)
