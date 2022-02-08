from typing import *
from .utils import hash256

def get_merkle_parent(hashes: List[Union[str, bytes]], as_hex: bool = True) -> List:
    """
    Pair up all the hashes, concatenate them, and take a hash256 
    """
    parent = []
    for i in range(0, len(hashes)-1, 2):
        h1, h2 = hashes[i], hashes[i+1]
        if isinstance(h1, str):
            h1, h2 = bytes.fromhex(h1), bytes.fromhex(h2)
        new_hash = hash256(h1 + h2)
        if as_hex:
            new_hash = new_hash.hex()
        parent.append(new_hash)
    return parent

class MerkleTree(object):
    def __init__(self, tree: List):
        self.tree = tree
        self.root = tree[0][::-1] #convert to little endian
    
    def __repr__(self):
        return f"MerkleTree(root={self.root})"
    
    @classmethod
    def construct(cls, hashes: List[str]):
        """
        Constructs a Merkle Tree from a list of hashes
        """
        hashes = [bytes.fromhex(h)[::-1] for h in hashes] #little to big-endian
        #ensure even number of hashesh
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
            
        merkle_tree = [hashes] #bottom of merkle tree will all the hashes
        
        assert len(merkle_tree) > 0

        #loop until we reach a single hash
        while True:
            curr_level = merkle_tree[-1]
            if len(curr_level) == 1:
                break
            merkle_tree.append(get_merkle_parent(hashes=curr_level))
            
        return cls(list(reversed(merkle_tree)))