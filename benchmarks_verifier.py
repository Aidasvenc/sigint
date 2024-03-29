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

def generate_coin_spend():
    coin_spend = bytes([randint(0, 255) for _ in range(320)])
    return coin_spend


def sign_coin_spend(coin_spend):
    seed = bytes([randint(0, 255) for _ in range(0, 32)])
    sk: PrivateKey = AugSchemeMPL.key_gen(seed)
    pk: G1Element = sk.get_g1()
    sig: G2Element = AugSchemeMPL.sign(sk, coin_spend)
    return pk, sk, sig


def generate_digest(coin_spends):
    digest = MerkleTree()
    for spend in coin_spends:
        digest.append_entry(spend)
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


def verify_single(agg_single_sigs, coin_spends, pks):
    start_time = time.time()
    # execute verification function for the batch
    verified = AugSchemeMPL.aggregate_verify(pks, coin_spends, agg_single_sigs)
    verification_time = time.time() - start_time
    return verified, verification_time


def run_block(coin_spends, sigs, pks):
    # run benchmarking
    times_sum = [0] * 891
    single_transactions = [0] * 891
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(1, 891):
            print('iteration', i)
            # generate the digest of all spend_bundles
            digest = generate_digest(coin_spends[0:891-i])

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in coin_spends[0:891-i]:
                pk, sk, sig = sign_digest(digest)
                sks_digest.append(sk)
                pks_digest.append(pk)
                sigs_digest.append(sig)

            # aggregate the digest signatures
            sig_agg_digest = aggregate_batch(sigs_digest)

            # aggregate single signatures
            sig_agg_single = aggregate_single(sigs[891-i:891])

            # verify the aggregate signatures
            verified, verification_time = verify_batch(sig_agg_digest, digest, pks_digest[0:891-i])

            # verify single signatures
            verified2, verification_time2 = verify_single(sig_agg_single, coin_spends[891-i:891], pks[891-i:891])

            # add to plot
            single_transactions[i] = i
            times_sum[i] += verification_time + verification_time2

    times_sum = [elem / 3 for elem in times_sum]

    # Convert arrays to strings
    single_transactions_str = np.array2string(np.array(single_transactions[:]), separator=',')
    times_sum_str = np.array2string(np.array(times_sum[:]), separator=',')

    # Prepare the data to be written
    data1 = f"Number of coin spends: {single_transactions_str}\nVerification time: {times_sum_str}"

    # Write the data to the file
    with open("data/block.txt", 'w') as file:
        file.write(data1)

    plt.figure(figsize=(8, 6))
    plt.plot(single_transactions, times_sum)
    plt.xlabel('Number of stragglers')
    plt.ylabel('Verification time, s')
    plt.title('Verification time for a block of 890 coin spends')
    plt.tight_layout()  # Ensures that all elements are properly displayed
    plt.show()


def run_fully_aggregated(coin_spends):
    # run benchmarking
    times_sum = [0] * 891
    num_transactions = [0] * 891
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(1, 891):
            print('iteration', i)
            # generate the digest of all spend_bundles
            digest = generate_digest(coin_spends[0:i])

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for coin_spend in coin_spends[0:i]:
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
    times_sum = [0] * 891
    num_transactions = [0] * 891
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(1, 891):
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


def run_compare_fully_vs_single(coin_spends, sigs, pks):

    # Get the results from the subfunctions
    times1_sum, num1_transactions = run_fully_aggregated(coin_spends)
    times2_sum, num2_transactions = run_fully_single(coin_spends, sigs, pks)

    # Convert arrays to strings
    num1_transactions_str = np.array2string(np.array(num1_transactions[:]), separator=',')
    times1_sum_str = np.array2string(np.array(times1_sum[:]), separator=',')

    # Convert arrays to strings
    num2_transactions_str = np.array2string(np.array(num2_transactions[:]), separator=',')
    times2_sum_str = np.array2string(np.array(times2_sum[:]), separator=',')

    # Prepare the data to be written
    data1 = f"Number of coin spends: {num1_transactions_str}\nVerification time: {times1_sum_str}"

    # Prepare the data to be written
    data2 = f"Number of coin spends: {num2_transactions_str}\nVerification time: {times2_sum_str}"

    # Write the data to the file
    with open("data/fully.txt", 'w') as file:
        file.write(data1)

    # Write the data to the file
    with open("data/single.txt", 'w') as file:
        file.write(data2)

    plt.plot(num1_transactions[1:], times1_sum[1:], color='g', label='fully aggregated')
    plt.plot(num1_transactions[1:], times2_sum[1:], color='r', label='fully single')
    plt.xlabel('Number of coin spends')
    plt.ylabel('Verification time (seconds)')
    plt.title('Performance of fully aggregated SIGINT vs. one-by-one signature verification')
    plt.legend()
    plt.show()


def run_fully_aggregated_with_digest_generation(coin_spends):
    # run benchmarking
    times_sum = [0] * 891
    num_transactions = [0] * 891
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(1, 891):
            print('iteration', i)
            # generate the digest of all spend_bundles
            digest_time_start = time.time()
            digest = generate_digest(coin_spends[0:i])
            digest_time_end = time.time()

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for coin_spend in coin_spends[0:i]:
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
            times_sum[i] += verification_time + (digest_time_end - digest_time_start)

    times_sum = [elem / 3 for elem in times_sum]

    # Convert arrays to strings
    num_transactions_str = np.array2string(np.array(num_transactions[:]), separator=',')
    times_sum_str = np.array2string(np.array(times_sum[:]), separator=',')

    # Prepare the data to be written
    data1 = f"Number of coin spends: {num_transactions_str}\nVerification time: {times_sum_str}"

    # Write the data to the file
    with open("data/fully_with_digest_generation.txt", 'w') as file:
        file.write(data1)

    plt.plot(num_transactions[1:], times_sum[1:])
    plt.xlabel('Number of transactions')
    plt.ylabel('Verification time (seconds)')
    plt.title('Verification time for fully aggregated transactions (including digest regeneration)')
    plt.show()


def run_optimal_block(coin_spends, sigs, pks):
    # run benchmarking
    times_sum = [0] * 891
    num_transactions = [0] * 891
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(10, 891):
            print('iteration', i)
            # generate the digest of all spend_bundles
            time_digest_start = time.time()
            digest = generate_digest(coin_spends[0:i])
            time_digest = time.time() - time_digest_start

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in coin_spends[0:i]:
                pk, sk, sig = sign_digest(digest)
                sks_digest.append(sk)
                pks_digest.append(pk)
                sigs_digest.append(sig)

            # aggregate the digest signatures
            sig_agg_digest = aggregate_batch(sigs_digest)

            # aggregate single signatures
            sig_agg_single = aggregate_single(sigs[0:int(i/10)])

            # verify the aggregate signatures
            verified, verification_time = verify_batch(sig_agg_digest, digest, pks_digest[0:i])

            # verify single signatures
            verified2, verification_time2 = verify_single(sig_agg_single, coin_spends[0:int(i/10)], pks[0:int(i/10)])

            # add to plot
            num_transactions[i] = i
            times_sum[i] += verification_time + verification_time2 + time_digest

    times_sum = [elem/3 for elem in times_sum]
    plt.plot(num_transactions[10:], times_sum[10:])
    plt.xlabel('Number of coin spends in a block')
    plt.ylabel('Verification time, s')
    plt.title('Verification time for different-sized blocks (assuming 10% stragglers)')
    plt.show()

    # Convert arrays to strings
    num_transactions_str = np.array2string(np.array(num_transactions[10:]), separator=',')
    times_sum_str = np.array2string(np.array(times_sum[10:]), separator=',')

    # Prepare the data to be written
    data = f"Number of transactions: {num_transactions_str}\nVerification time: {times_sum_str}"

    # Write the data to the file
    with open("data/optimal_block_final.txt", 'w') as file:
        file.write(data)


def run_block_with_digest_regeneration(coin_spends, sigs, pks):
    # run benchmarking
    times_sum = [0] * 891
    single_transactions = [0] * 891
    for epoch in range(0, 3):
        print('epoch', epoch)
        for i in range(0, 891):
            print('iteration', i)
            # generate the digest of all spend_bundles
            time_digest_start = time.time()
            digest = generate_digest(coin_spends[0:891-i])
            time_digest = time.time() - time_digest_start

            # all clients sign the digest
            sks_digest = []
            pks_digest = []
            sigs_digest = []
            for spend_bundle in coin_spends[0:624-i]:
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
            verified2, verification_time2 = verify_single(sig_agg_single, coin_spends[624-i:624], pks[624-i:624])

            # add to plot
            single_transactions[i] = i
            times_sum[i] += verification_time + verification_time2 + time_digest

    times_sum = [elem/3 for elem in times_sum]
    plt.plot(single_transactions, times_sum)
    plt.xlabel('Number of straggler transactions')
    plt.ylabel('Verification time (seconds)')
    plt.title('Verification time for 625 transactions (including digest regeneration)')
    plt.show()

    # Convert arrays to strings
    num_transactions_str = np.array2string(np.array(single_transactions), separator=',')
    times_sum_str = np.array2string(np.array(times_sum), separator=',')

    # Prepare the data to be written
    data = f"Number of transactions: {num_transactions_str}\nVerification time: {times_sum_str}"

    # Write the data to the file
    with open("data/block_with_digest.txt", 'w') as file:
        file.write(data)


if __name__ == '__main__':
    # create 890 coin spends that will be in the block
    coin_spends = []
    for i in range(0, 890):
        coin_spends.append(generate_coin_spend())

    # sign all generated 890 coin spends
    sks = []
    pks = []
    sigs = []
    for coin_spend in coin_spends:
        pk, sk, sig = sign_coin_spend(coin_spend)
        sks.append(sk)
        pks.append(pk)
        sigs.append(sig)
    # test 1
    run_block(coin_spends, sigs, pks)

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
    # run_compare_fully_vs_single(coin_spends, sigs, pks)

    # test 5
    # run_fully_aggregated_with_digest_generation(coin_spends)

    # test 6
    # run_block_with_digest_regeneration(spend_bundles, sigs, pks)

    # test 7
    run_optimal_block(coin_spends, sigs, pks)
