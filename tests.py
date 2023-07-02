import asyncio
from numpy import uint64
from chia.util.ints import uint64
from wallet import get_wallet

async def main():
    wallet = await get_wallet()
    await wallet.send_transaction(1, uint64(1), "txch1z65x68a3d9zqzg8wzr5kqnj2jdvs6k5e83xh00p7lsx6fngn77tqdlgssz", memos=["agg"])
    wallet.close()


if __name__ == "__main__":
    asyncio.run(main())
