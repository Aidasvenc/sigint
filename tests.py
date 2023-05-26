# from aggregator import Aggregator
from wallet import get_wallet
import asyncio
from chia.util.ints import uint64
from chia.wallet.transaction_record import TransactionRecord

async def main():
    # agg = Aggregator(batch_threshold=3)
    wallet = await get_wallet()
    # await wallet.log_in(475838479)
    # print(await wallet.get_logged_in_fingerprint())
    res = await wallet.send_transaction(1, uint64(1), "txch1z65x68a3d9zqzg8wzr5kqnj2jdvs6k5e83xh00p7lsx6fngn77tqdlgssz", memos=["agg"])
    wallet.close()

if __name__ == "__main__":
    asyncio.run(main())
