"""
-----------
Proof of Work (Mining), Explained
-----------
Proof-of-work is the requirement that the hash of every block header in Bitcoin must be below a certain target
The target is a 256-bit number that is computed directly from the bits field
The bits field is actually two different numbers. 
The first is the exponent, which is the last byte. 
The second is the coefficient, which is the other three bytes in little-endian. 
The formula for calculating the target from these two numbers is: coef * 256**(exp-3)

A valid proof-of-work is a hash of the block header that, when interpreted as a little-endian integer, is below the target number
Proof-of-work hashes are exceedingly rare, and the process of mining is the process of finding one of these hashes. 
To find a single proof-of-work with the preceding target, the network as a whole must calculate 3.8 × 10^21 hashes, 
which, when this block was found, could be done roughly every 10 minutes

To give this number some context, the best GPU mining card in the world would need to run for 50,000 years on average to 
find a single proof-of-work below this target

To check if Proof of Work is valid we do the below:
    assert decode_int(hash256(block_header_bytes)) < target

Targets are hard for human beings to comprehend. 
The target is the number that the hash must be below, but it’s not easy to see the difference between a 180-bit number and a 190-bit number. 
The first is a thousand times smaller, but from looking at targets, such large numbers are not easy to contextualize.
To help this, "difficulty" was born. To calculate the difficulty we use the following formula:
    (0xffff * 256**(0x1d - 3)) / target
difficulty of Bitcoin at the genesis block was 1


We already learned that proof-of-work can be calculated by computing the hash256 of the block header and interpreting this as a little-endian integer. 
If this number is lower than the target, we have a valid proof-of-work. If not, the block is not valid as it doesn’t have proof-of-work.

DIFFICULTY ADJUSTMENT
In Bitcoin, each group of 2,016 blocks is called a difficulty adjustment period. 
At the end of every difficulty adjustment period, the target is adjusted according to this formula:
time_differential = (block timestamp of last block in difficulty adjustment period) – (block timestamp of first block in difficulty adjustment period)
new_target = previous_target * time_differential / (2 weeks)
The time_differential is calculated so that if it’s greater than 8 weeks, 8 weeks is used, and if it’s less than 3.5 days, 3.5 days is used.

If each block took on average 10 minutes to create, 2,016 blocks should take 20,160 minutes. 
There are 1,440 minutes per day, which means that 2,016 blocks will take 20,160 / 1,440 = 14 days to create. 
The effect of the difficulty adjustment is that block times are regressed toward the mean of 10 minutes per block. 
This means that long-term, blocks will always go toward 10-minute blocks even if a lot of hashing power has entered or left the network.

Satoshi had an error in his code that would require a hardfork to fix, so its still there: (looked at first and last block of 2016--block period)
The time differential is the difference of blocks that are 2,015 blocks apart instead of 2,016 blocks apart.

It is a calculated number that is very hard to find.
Because SHA256 produces a uniform distribution, a hash is essentially a randomized number.
Finding proof of work requires the processing of about 10^22 bits on average. 
Miners use nonce to change the hash of the block header.

What miners can do when the nonce field is exhausted is change the coinbase transaction, 
which then changes the Merkle root, giving miners a fresh nonce space each time


MERKLE TREES
A Merkle tree is a computer science structure designed for efficient proofs of inclusion
Constructed like this:
    Take all transactions and hash them, in order
    Loop until there is only a single hash (this single hash is the merkle root)
    if there is an odd number of hashes, we duplicate the last one to make it even
    pair the transactions in order and hash the concatenation to get the "parent level" (called merkle parent)
Given [A, B, C] , we duplicate [A, B, C, C] and then do hash(hash(A, B), hash(C, C)) 
We use little-endian ordering for the leaves of the Merkle tree
So need to reverse the "leaves" at the start to big-endian and then convert the root back to little endian

"""

from __future__ import annotations
from typing import *
from .utils import encode_int, decode_int, ensure_stream, hash256
from io import BytesIO

class Block(object):
    """
    --------
    PARAMS
    --------
    1. version - which version of Bitcoin
    2. prev_block - the block id (hash256 little-endian) of previous block
                    Every block points to its previous block. This is why its called blockchain. 
    3. merkle_root - encodes all the ordered transactions in a 32-byte hash (see https://en.bitcoinwiki.org/wiki/Merkle_tree)
    4. timestamp - Unix timestamps are the number of seconds since January 1, 1970
                   used for calculating a new bits/target/difficulty every 2,016 blocks
    5. bits - encodes the proof-of-work necessary in this block
    6. nonce - “number used only once,” or n-once. This is what is changed by miners when looking for proof-of-work.

    """
    def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce, tx_hashes=None):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.tx_hashes = tx_hashes
    
    def __repr__(self):
        s = f"""
        Block(
            version: {self.version}
            prev_block: {self.prev_block.hex()}
            merkle_root: {self.merkle_root.hex()}
            timestamp: {self.timestamp}
            bits: {self.bits.hex()}
            nonce: {self.nonce.hex()}
            Difficulty: {self.difficulty()}
        )
        """
        return s

    def encode(self) -> bytes:
        """
        Returns the block header (80 bytes)
        """
        out = [encode_int(self.version, 4)] #4 bytes little endian
        out += [self.prev_block[::-1]] #32 bytes little endian
        out += [self.merkle_root[::-1]] #32 bytes little endian
        out += [encode_int(self.timestamp, 4)] #4 bytes little endian
        out += [self.bits, self.nonce] #4 bytes, 4 bytes
        return b"".join(out)

    @classmethod
    def decode(cls, b: Union[BytesIO, bytes]) -> Block:
        b = ensure_stream(b)
        version = decode_int(b, 4)
        prev_block = b.read(32)[::-1] #little to big endian
        root = b.read(32)[::-1]
        timestamp = decode_int(b, 4)
        bits = b.read(4)
        nonce = b.read(4)
        return cls(version, prev_block, root, timestamp, bits, nonce)
    
    def to_target(self):
        """
        Takes the bits and generates a number  (256 bits)
        Note this is compared to a target number for Proof of Work
        """
        exp = self.bits[-1] #last byte is the exponents
        coef = decode_int(BytesIO(self.bits[:-1]), 3) #first three are the coefficient
        return coef * 256**(exp - 3)
    
    def get_id(self):
        return hash256(self.encode())[::-1].hex()
    
    def difficulty(self) -> int:
        """
        Uses bits to calculate block difficulty
        Formula:
         (target of lowest difficulty) / (self's target)
        """
        lowest = 0xffff * 256**(0x1d - 3)
        return int(lowest / self.to_target())
    


GENESIS_BIN = {
    'main': bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c'),
    'test': bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4adae5494dffff001d1aa4ae18'),
}

GENESIS_BLOCK = Block.decode(GENESIS_BIN["test"])
