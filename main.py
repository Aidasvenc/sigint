from blspy import (PrivateKey, AugSchemeMPL, PopSchemeMPL, G1Element, G2Element)
import time

if __name__ == '__main__':
    # Seed for private key generation (has to be random and 32 bytes or more)
    seed: bytes = bytes([0, 50, 6, 244, 24, 199, 1, 25, 52, 88, 192,
                         19, 18, 12, 89, 6, 220, 18, 102, 58, 209, 82,
                         12, 62, 89, 110, 182, 9, 44, 20, 254, 22])

    # generate some private keys and messages
    message: bytes = bytes([1, 2, 3, 4, 5])
    seed = bytes([1]) + seed[1:]
    sk1: PrivateKey = AugSchemeMPL.key_gen(seed)
    seed = bytes([2]) + seed[1:]
    sk2: PrivateKey = AugSchemeMPL.key_gen(seed)
    message2: bytes = bytes([1, 2, 3, 4, 5, 6, 7])

    # Generate first sig
    pk1: G1Element = sk1.get_g1()
    sig1: G2Element = AugSchemeMPL.sign(sk1, message)

    # Generate second sig
    pk2: G1Element = sk2.get_g1()
    sig2: G2Element = AugSchemeMPL.sign(sk2, message2)

    # Signatures can be non-interactively combined by anyone
    agg_sig: G2Element = AugSchemeMPL.aggregate([sig1, sig2])

    # verify
    start_time = time.time()
    ok = AugSchemeMPL.aggregate_verify([pk1, pk2], [message, message2], agg_sig)
    end_time = time.time()
    total_time = end_time - start_time
    print("simple aggregate verify:", ok)
    print("total time: ", total_time)

    # Multi-signatures

    # generate some private keys
    seed = bytes([1]) + seed[1:]
    sk1: PrivateKey = PopSchemeMPL.key_gen(seed)
    pk1: G1Element = sk1.get_g1()
    seed = bytes([2]) + seed[1:]
    sk2: PrivateKey = PopSchemeMPL.key_gen(seed)
    pk2: G1Element = sk2.get_g1()

    # generate multi-signatures
    sig1: G2Element = PopSchemeMPL.sign(sk1, message)
    sig2: G2Element = PopSchemeMPL.sign(sk2, message)

    # aggregate signatures
    sig_agg: G2Element = PopSchemeMPL.aggregate([sig1, sig2])

    # verify
    start_time = time.time()
    ok = PopSchemeMPL.fast_aggregate_verify([pk1, pk2], message, sig_agg)
    end_time = time.time()
    total_time = end_time - start_time
    print("Multi-signatures aggregate verify: ", ok)
    print("total time: ", total_time)

    # aggregate public keys and then verify
    agg_pk: G1Element = pk1 + pk2

    start_time = time.time()
    ok = PopSchemeMPL.verify(agg_pk, message, sig_agg)
    end_time = time.time()
    total_time = end_time - start_time
    print("Multi-signatures aggregate verify with aggregate public keys: ", ok)
    print("total time: ", total_time)

    # scaled versions

    # Simple aggregate signatures
    sigs = []
    pks = []
    msgs = []
    for i in range(0, 100):
        m = bytes([i, i+1, i+2, i+3, i+4])
        seed = bytes([i]) + seed[1:]
        sk: PrivateKey = AugSchemeMPL.key_gen(seed)
        pk: G1Element = sk.get_g1()
        sig: G2Element = AugSchemeMPL.sign(sk, m)
        sigs.append(sig)
        pks.append(pk)
        msgs.append(m)

    # aggregate signatures
    sig_agg: G2Element = AugSchemeMPL.aggregate(sigs)

    # verify
    start_time = time.time()
    ok = AugSchemeMPL.aggregate_verify(pks, msgs, sig_agg)
    end_time = time.time()
    total_time = end_time - start_time
    print("Simple aggregate verify with 100 elements: ", ok)
    print("total time: ", total_time)

    # Multi-signatures
    sigs = []
    pks = []
    for i in range(0, 100):
        seed = bytes([i]) + seed[1:]
        sk: PrivateKey = PopSchemeMPL.key_gen(seed)
        pk: G1Element = sk.get_g1()
        sig: G2Element = PopSchemeMPL.sign(sk, message)
        sigs.append(sig)
        pks.append(pk)

    # aggregate signatures
    sig_agg: G2Element = PopSchemeMPL.aggregate(sigs)

    # verify
    start_time = time.time()
    ok = PopSchemeMPL.fast_aggregate_verify(pks, message, sig_agg)
    end_time = time.time()
    total_time = end_time - start_time
    print("Multi-signatures aggregate verify with 100 elements: ", ok)
    print("total time: ", total_time)

    # Multi-signatures
    sigs = []
    pks = []
    for i in range(0, 100):
        seed = bytes([i]) + seed[1:]
        sk: PrivateKey = PopSchemeMPL.key_gen(seed)
        pk: G1Element = sk.get_g1()
        sig: G2Element = PopSchemeMPL.sign(sk, message)
        sigs.append(sig)
        pks.append(pk)

    # aggregate signatures
    sig_agg: G2Element = PopSchemeMPL.aggregate(sigs)

    # aggregate public keys
    agg_pk: G1Element = G1Element()
    for pk in pks:
        agg_pk += pk

    # verify
    start_time = time.time()
    ok = PopSchemeMPL.verify(agg_pk, message, sig_agg)
    end_time = time.time()
    total_time = end_time - start_time
    print("Multi-signatures aggregate verify with aggregate public keys, 100 elements: ", ok)
    print("total time: ", total_time)







