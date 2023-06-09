import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Read data from the first file
    with open("data/fully_with_digest_generation.txt", 'r') as file:
        data1 = file.read()

    # Extract arrays from data1
    num1_transactions_str, times1_sum_str = data1.split("\n")

    # Convert strings back to NumPy arrays
    num1_transactions = np.fromstring(num1_transactions_str.split(": ")[1].strip('[]'), sep=',')
    times1_sum = np.fromstring(times1_sum_str.split(": ")[1].strip('[]'), sep=',')

    # Read data from the second file
    with open("data/single.txt", 'r') as file:
        data2 = file.read()

    # Extract arrays from data2
    num2_transactions_str, times2_sum_str = data2.split("\n")

    # Convert strings back to NumPy arrays
    num2_transactions = np.fromstring(num2_transactions_str.split(": ")[1].strip('[]'), sep=',')
    times2_sum = np.fromstring(times2_sum_str.split(": ")[1].strip('[]'), sep=',')

    # Print the extracted arrays
    print("num1_transactions:", num1_transactions)
    print("times1_sum:", times1_sum)
    print("num2_transactions:", num2_transactions)
    print("times2_sum:", times2_sum)

    print("minimal fully aggregated with digest verification time: ", np.min(times1_sum))
    print("maximal fully aggregated with digest verification time: ", np.max(times1_sum))

    print("minimal single verification time: ", np.min(times2_sum))
    print("maximal single verification time: ", np.max(times2_sum))


    plt.figure(figsize=(10, 6))  # Set the figure size (adjust as needed)
    plt.plot(num1_transactions[1:], times1_sum[1:], color='g', label='')
    plt.plot(num1_transactions[1:], times2_sum[1:], color='r', label='fully single')
    plt.xlabel('Number of coin spends')
    plt.ylabel('Verification time, s')
    plt.title('Verification time for SIGINT with 10% of stragglers vs. one-by-one signature verification')
    plt.legend()
    plt.tight_layout()  # Ensures that all elements are properly displayed
    plt.show()

