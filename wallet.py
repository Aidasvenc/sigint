from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.config import load_config
from pathlib import Path
from chia.util.ints import uint16
import os

__SIMULATOR_ROOT_PATH = Path(str(os.getenv('CHIA_ROOT')))


async def get_wallet():
    self_hostname = "localhost"
    # port = 26926
    port = 12252
    config = load_config(Path(__SIMULATOR_ROOT_PATH), "config.yaml")

    wallet_rpc_client = await WalletRpcClient.create(self_hostname, uint16(port), __SIMULATOR_ROOT_PATH, config)

    return wallet_rpc_client


# if __name__ == '__main__':
    # wallet: WalletRpcClient = asyncio.run(__get_wallet_rpc_client())
