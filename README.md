# Interactive Signature Verification for Chia Blockchain
Bachelor's project by Alberto Centonze and Aidas Venckunas. Research performed under supervision Distributed Computing Laboratory, School of Computer and Communication Sciences, École Polytechnique Fédérale de Lausanne.

## Motivation
Digital signatures are a fundamental cryptographic building block of the internet. In essence, a message
signature enables a verifier to ensure both the (1) authenticity of the identity of the message signer and
the (2) integrity of the signed message. While each signature is small and quick to verify, verifying even
thousands of signatures takes a non-negligible amount of space and time, **linear space and time** to be exact.
To circumvent this scalability challenge, cryptographers have built upon signature schemes such as BLS and
Schnorr to propose mechanisms for signature aggregation that offer multiple benefits.

First, signature aggregation always saves **space**: an arbitrarily large number of signatures can be
compacted into a signature of constant space, usually equivalent to the space required for just one signature.
Second, signature aggregation can save **verification time**: akin to space, verification also takes a constant
amount of time regardless of the number of signatures being verified, and is equivalent to verifying just one
signature.

While aggregating several signatures always reduces the space footprint to a constant, it does not
automatically translate into an equal reduction of the verification time. The latter ability depends on
whether the signatures are: first, by the same signer for all messages, or, second, all on the same message.
In the first case, aggregating BLS signatures from the same signer allows constant-time verification. In
the second case, aggregating signatures on the same message and from different signers is referred to as
multi-signatures as first conceptualized in 1983. Multi-signatures with constant-time verification - and with
aggregatable public keys - have been proposed in 2018 for the BLS and Schnorr schemes.
**SIGINT** is the first scheme that **enables aggregate signatures to be both short and rapidly verifiable**
for different messages from different signers.

![image](https://github.com/Aidasvenc/sigint/assets/79483254/c3b7c66f-81f9-4d21-89aa-63efcb14163e)

## Chia Blockchain
Chia is a decentralized blockchain platform designed to provide a more energy-efficient and sustainable
alternative to traditional cryptocurrencies. Chia introduces a unique consensus algorithm called **Proof of
Space and Time (PoST)**, which leverages unused storage space on hard drives to secure the network. This
approach ensures a more equitable distribution of mining power and reduces the reliance on energy-intensive
mining processes.
The main reason why we chose to work with Chia blockchain is that it is one of very few blockchains to
use BLS signatures for signature and block verification procedures. This capability significantly reduces our
need to re-structure the codebase extensively and makes it relatively simple to run SIGINT scheme inside
and outside of the blockchain compared to other blockchains.

## SIGINT implementation and performance evaluation
Our research was divided into two phases: implementation phase and benchmarking phase. During the first
phase SIGINT interaction protocol was implemented and Chia Blockchain structure was adapted to work
with SIGINT protocol. The second phase was focused on testing the signature validation performance in the
current blockchain structure and evaluating performance that is achieved by using SIGINT protocol. These
benchmarks then were compared in an extensive way

## SIGINT protocol
SIGINT protocol enables fast validation of cryptographic signatures. It’s key
structure consists of three entity groups that perform different actions and communicate between each other
interactively: **clients, aggregator and validator**. Unfortunately, due to a pending patent as of 2023, we cannot discuss the details of the protocol mechanism publicly.

## Where SIGINT and Chia interleave
Chia blockchain and SIGINT protocol have matching similarities which let us try to implement SIGINT
into Chia blockchain and establish ties between them.

1. It can be observed that Chia blockchain has 2 entities that communicate with the help of mempool:
(1) the client and (2) the farmer (which equals to validator in SIGINT terms). This allows to introduce
a 3rd middle-man entity that is apparent in SIGINT - the aggregator.
2. Clients have to wait until their transactions are included in a block, so introducing minimal additional
delay to interact with aggregator does not impact transaction execution time critically.
3. BLS signatures are used in Chia blockchain and so it is compatible with SIGINT protocol that scales
using BLS signatures.

## Overview of the changes in the Chia codebase
To make the SIGINT scheme work some changes were required to the chia blockchain code. The release
used as a base and to which the report refers to is 1.8.1 and can be found at https://github.com/ChiaNetwork/chia-blockchain/tree/1.8.1.
Most of the changes were implemented in the WalletRpcApi.py a file that exposes some JSON-RPC
endpoints that can be used and consequently reflected in its python wrapper used by the aggregator
WalletRpcClient.py.
The most significant additions were two new wallet endpoints that can only be called by aggregators:
• `sigint_sign_digest` to send requests to sign the aggregated digests
• `sigint_send_aggregated_transactions` to send aggregated transaction to the mempool

## Evaluation of the hypothesis
In order to test our hypothesis of SIGINT interactive signature validation protocol multiple testing phases
were carried out. Initially, the current Chia blockchain performance was evaluated, where bottleneck
verification points were observed. Then, isolated SIGINT protocol efficiency was benchmarked to stress-test
these bottleneck points and verify that it provides a more efficient solution for verification. Optimal
interactive protocol parameters were also established during this phase. Finally, adapted version of Chia
blockchain that uses SIGINT multi-signatures was benchmarked to observe the changes in signature
validation efficiency.

Due to the complexity of Chia blockchain and other limiting factors, some necessary simplification
constraints were established. The testing was executed in a non-isolated environment that does not have
dedicated hardware or any specialized software - a computer equipped with an SSD and an installation of
Ubuntu 22.04 was used for this task. More in-depth set-up and constraint details for these phases as well as
observed outcomes are discussed in the following sub-sections.

## Efficiency evaluation of current blockchain structure
Initially, to be able to operate and execute transactions as an independent entity without a proxy, a full
node client has to be initiated and synced with the blockchain. This requires the client node to bootstrap a
chain of blocks which is an essential data structure that stores all crucial information about the history and
state of the blockchain. To perform syncing, blocks are fetched in batches from peer nodes that reside in
the blockchain network and contain all blocks up to the current one. Upon fetching each batch, the node
then performs the block validation procedure block-by-block. BLS signature
verification needs to be performed during this procedure requiring the node to perform the following:

1. Acquire k (public key, message) pairs, where k is the number of coin spends in the block. These pairs
are stored in the block as a separate data structure (Conditions). Each BLS public key is called a
G1Element and has a size of 48 bytes. Each message as generated by a CLVM puzzle is 96 bytes in
size.
2. Acquire an aggregated signature that encapsulates all signatures from each of the coin spend in a
block. This signature is also stored in the block and is called a G2Element in BLS cryptographical
terms. It is has a size of 96 bytes.
3. Perform BLS aggregate-verify procedure to validate the aggregated signature by
supplying the elements acquired in parts 1-2: signature itself, the list of public keys (k × 48 bytes in
total) and the list of messages (k × 96 bytes in total).

This procedure is an important component of overall block validation time and it is the reason why it
was decided to measure how critical it is in current Chia blockchain.

## Syncing
A full node syncing operation was performed and it took 26 hours and 21 minutes to sync 1017931
out of 3775228 blocks that were in the blockchain at the time of syncing (07.06.2023) in total. Due
to the complexity and average size of a block increasing on a block-by-block basis it was decided not to
continue until the node would be fully synced. Chia developer team confirmed that on 07.06.2023 the overall
blockchain size was 113 GB and average full sync time on a high-bandwidth machine was around 3 days.

## Metrics per block
Average block size in terms of coins spent in that block was calculated in the following way:

1. In Chia blockchain, about 40% of the blocks are left empty for consensus purposes.
https://docs.chia.net/consensus-foliage#transaction-block-time These blocks are marked as nontransaction blocks in Chia and they were not included in the calculation
2. First 270000 blocks did not contain any transactions, so there were no coins spent in them. It was
because for some time after the blockchain launched, Chia did not support sending transactions. These
initial blocks were not included in the calculation.
3. All the blocks that were not excluded in steps 1-2 were measured and their average coin spend count
was calculated.

The final measure is 36.5 coins spent per block with a maximal number of 890 coins spent per block.
Average block size in bytes is 28800 bytes with the maximum accepted size of 400KB. More
information on how the block size depends on different factors and how it is calculated is presented in
https://docs.chia.net/coin-set-costs. Since the main focus of interest for this project was in signature
validation time, this measure is not as important as the previous measure of average coins per block, since it
does not impact the signature validation time directly.
Average block signatures validation time was calculated in the following way:

1. Empty blocks: empty transaction blocks and non-transaction blocks do not undergo the signature
validation, so the time spent to validate signatures for these blocks is equal to 0. All empty blocks
were therefore not included in the calculation.
2. All non-empty blocks were considered in average time calculation. The time spent for signature
validation is equal to the time that BLS aggregate verify function took to execute.
The result on the measure of time spent per block to validate the signatures is 0.167 seconds per block
with a maximal time of 6.02 seconds per block.

![image](https://github.com/Aidasvenc/sigint/assets/79483254/d1191a62-c0d5-4228-bd4b-864674447c9b)


## Modified Chia blockchain block validation metrics
After executing all previous tests and selecting optimal parameters, a simplified SIGINT verification protocol
was established inside of Chia blockchain (as explained in section 3), which enabled the possibility to come
back to syncing the blockchain under assumptions that: (1) all blocks contains only one fully aggregated
multi-signature of all coin spends in the block and (2) there are no straggler signers in that block. This
assumption can be called a perfect SIGINT scenario.
The perfect SIGINT scenario essentially enables all blocks to take full advantage of fast verification. To
evaluate the impact it would have on Chia blockchain syncing performance, same benchmarking was carried
out as before by syncing the full node up to 1017931 out of 3775228 blocks and comparing the
measurements between the classic Chia blockchain and perfect scenario SIGINT-enabled blockchain.

![image](https://github.com/Aidasvenc/sigint/assets/79483254/a894ddb0-aeac-4550-ac53-3b05f711cf7d)


The new result on the measure of average time spent per block to validate its signatures is 0.004 seconds
per block with a maximal time of 0.17 seconds per block. On average, 0.163 seconds are saved per one
non-empty block validation resulting in a 42 times faster validation process. With the new SIGINT-enabled
blockchain the same syncing process as performed initially would take 14 hours and 40 minutes instead
of 26 hours and 21 minutes for original Chia blockchain.
One can observe that SIGINT certainly enables the blockchain to be more efficient than it originally
is. Even though to evaluate the exact behavior extensive real-life tests would need to be performed, these
benchmarks still provide valuable insights for the research of SIGINT protocol.

## Project Outcome
The successful implementation of integrating SIGINT within a UTXO-like blockchain has demonstrated its
feasibility.
Chia’s unique apporach to UTXO transactions forced us to reitarate over the aggregator implementation
multiple times due to the complex design behind coins spends with respect to other UTXO systems like
Bitcoin.
Chia also proved to be a flexible blockchain for swiftly implementing and testing changes. Its Pythonbased architecture minimizes recompilation times and provides the freedom to modify components without
the limitations of a strongly typed system.

## Final Considerations
Integrating SIGINT in a real-life system becomes significantly harder when it is requires to integrate BLS
signatures into the underlying system. If on the other hand, the existing infrastructure already supports
BLS signatures, the integration process becomes relatively straightforward.

An additional challenge to face when considering the integration of SIGINT capabilities into an existing
blockchain project is the task of convincing the community to adopt a system that requires significant
modifications to the execution layer. The community’s agreement and consensus are crucial for the successful
implementation of any changes in a decentralized network.

Developing a SIGINT-native blockchain project, such as Chop Chop has the potential to be more
successful in terms of integrating SIGINT functionalities seamlessly. By designing the blockchain from
the ground up with SIGINT in mind, the system can be built to accommodate and support the necessary
features without compromising on performance or security.

A promising middle ground compromise for the future involves leveraging SIGINT to establish a gas
factory within the smart contract layer of an existing blockchain. In the context of Ethereum, proposals
like EIP-2537 propose incorporating BLS Precompiles, which facilitate the consolidation of numerous
transactions from diverse users into batches through the concept of account abstraction. This approach
enables the creation of a gas factory, where a smart wallet serves as the sender on behalf of multiple users,
thereby optimizing gas costs and acting as an onchain aggregator.

## Possible Future Improvements
As mentioned in the implementation section many design and structural simplifications as well as assumptions
were made to respect the time and depth constraints of the project. Hence, the following points are left as a
future reference for continued exploration of SIGINT interactive protocol.
• Communication between the aggregator and the the node should fully happen over the SSL secured
JSON-RPC native protocol.
• All the placeholder verifications functions should actually make sure of the correctness of the transactions
received. Ideally this should be done by referencing the same code used in the blockchain to verify
blocks/transactions by eventually modularizing it when necessary to avoid code duplication.
• Gas costs for the transaction has not been taken into account in the sandboxed environment used for
testing. Aggregating transaction could even help saving gas since multiple senders can pay together.
• Testing should be executed in a real blockchain-dedicated environment that is efficient in executing
blockchain operations.
• SIGINT interactive protocol part should be extensively tested with a system of multiple clients,
aggregators and validators that would continuously send and generate new payloads. Stress-testing
and safety-testing could also be performed to remark the issues and bottlenecks.
• Further in-depth collaboration with Chia blockchain developer team may be established to work on
natively implementing SIGINT protocol in the blockchain.

## Attributions
A sentence of gratitude to our supportive and helpful project supervisor Pierre-Louis. It was a pleasure to
perform research on a state-of-art invention and to explore possible ways of implementing it.
We would also like to mention the developers of the Chia network since were remarkably accessible and
provided valuable assistance in addressing our inquiries regarding the specifics of the protocol.
