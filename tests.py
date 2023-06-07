# from aggregator import Aggregator
from aggregator import Aggregator
from wallet import get_wallet
import asyncio
from chia.util.ints import uint64
from chia.util.keychain import Keychain

async def main():
    wallet = await get_wallet()
    await wallet.send_transaction(1, uint64(1), "txch1z65x68a3d9zqzg8wzr5kqnj2jdvs6k5e83xh00p7lsx6fngn77tqdlgssz", memos=["agg"])
    fingerprints = await wallet.get_public_keys()
    keys = Keychain()
    pks = [keys.get_private_key_by_fingerprint(fingerprint) for fingerprint in fingerprints]
    keys.get_all_public_keys()
    print(pks)
    Aggregator(wallet)
    wallet.close()

if __name__ == "__main__":
    asyncio.run(main())
