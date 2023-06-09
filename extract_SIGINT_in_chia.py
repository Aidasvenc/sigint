import re
import time

import matplotlib.pyplot as plt
import numpy as np
from blspy import (PrivateKey, AugSchemeMPL, PopSchemeMPL, G1Element, G2Element)
from random import randint
from pymerkle import MerkleTree

if __name__ == '__main__':

# Initialize empty arrays
    block_nums = []
    coins = []
    msg_lengths = []
    validation_times = []

    # Open the text file
    with open('data/log.txt', 'r') as file:
        # Read each line
        for line in file:
            # Extract numbers using regular expressions
            match = re.match(r".*block (\d+), (\d+) coins, msg of (\d+) bytes validated in (\d+\.\d+)", line)
            if match:
                if float(match.group(4)) < 30 and int(match.group(2)) > 0:
                    # Extract numbers from the matched groups
                    block_num = int(match.group(1))
                    coin_num = int(match.group(2))
                    msg_length = int(match.group(3))
                    validation_time = float(match.group(4))

                    # Append the numbers to their respective arrays
                    block_nums.append(block_num)
                    coins.append(coin_num)
                    msg_lengths.append(msg_length)
                    validation_times.append(validation_time)

    validation_times = []

    msg = bytes([randint(0, 255) for _ in range(96)])
    seed: bytes = bytes([0, 50, 6, 244, 24, 199, 1, 25, 52, 88, 192,
                         19, 18, 12, 89, 6, 220, 18, 102, 58, 209, 82,
                         12, 62, 89, 110, 182, 9, 44, 20, 254, 22])
    sk: PrivateKey = AugSchemeMPL.key_gen(seed)
    pk: G1Element = sk.get_g1()
    sig: G2Element = AugSchemeMPL.sign(sk, msg)
    for coins_block_i in coins:
        verification_start = time.time()
        digest = MerkleTree()
        for i in range(0, coins_block_i):
            digest.append_entry(msg)
        ok: bool = AugSchemeMPL.verify(pk, msg, sig)
        assert ok
        verification_end = time.time()
        validation_times.append(verification_end - verification_start)
        print(len(validation_times))

    np.array(validation_times)

    max_validation_time = np.max(validation_times)
    max_coins = max(coins)
    mean_coins = np.mean(coins)
    mean_validation_time = np.mean(validation_times)
    min_validation_time = np.min(validation_times)

    # Create the dot plot
    plt.figure(figsize=(19, 14))  # Set the figure size (adjust as needed)
    plt.scatter(block_nums, validation_times, color='blue', label='Validation Time, s', s=6)
    plt.axhline(mean_validation_time, color='red', linestyle='--', label='Mean Validation Time')
    plt.xlabel('Block index, i', fontsize=18)  # Increase the font size
    plt.ylabel('Validation Time, s', fontsize=18)  # Increase the font size
    plt.title('Validation time per block using SIGINT', fontsize=20)  # Increase the font size
    plt.legend(fontsize=16)  # Increase the font size

    # Set custom x-axis tick positions and labels
    block_nums_ticks = np.arange(min(block_nums), max(block_nums) + 1, 50000)
    plt.xticks(block_nums_ticks)
    plt.xticks(rotation=45)  # Rotate the x-axis tick labels by 45 degrees (adjust as needed)


    # Print the statistics
    print("Max Validation Time:", max_validation_time)
    print("Mean Validation Time:", mean_validation_time)
    print("Min Validation Time:", min_validation_time)
    print("Max Coins:", max_coins)
    print("Mean Coins:", mean_coins)

    # Display the plot
    plt.tight_layout()  # Ensures that all elements are properly displayed
    plt.show()
