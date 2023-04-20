from blspy import (PrivateKey, AugSchemeMPL, G1Element, G2Element)

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

    ok = AugSchemeMPL.aggregate_verify([pk1, pk2], [message, message2], agg_sig)
    print(ok)
    assert ok