"""
API to pull and push data from Bitcoin's TestNet
"""
from typing import *
import os
import requests
import json
from ..block import Block
import pathlib

def get_cache(filename: str, bin: bool = False) -> Union[bytes, dict, list]:
    read_type = "rb" if bin else "r"
    if os.path.isfile(filename):
        with open(filename, read_type) as f:
            raw = f.read()
        if not bin:
            return json.loads(raw) #object (list|dict)
        return raw #bytes

class TestNet:
    """
    Wrapper for Blockstream's Testnet API
    """
    def __init__(self):
        self.cache_dir = f"{pathlib.Path(__file__).parent.resolve()}/datacache/"
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
        self.url = "https://blockstream.info/testnet/api/"
        
    def get_tx(self, txid: str, as_hex: bool = False) -> bytes:
        cachefile = self.cache_dir + "txdb"
        cachefile = os.path.join(cachefile, txid)
        raw = get_cache(cachefile, bin=True)
        if raw is None:     
            url = self.url + f"tx/{txid}/hex"
            r = requests.get(url)
            assert r.ok, "Could not connect to API"
            raw = bytes.fromhex(r.text.strip())
            with open(cachefile, "wb") as f:
                f.write(raw)
        return raw if not as_hex else raw.hex()
    
    def get_tx_meta(self, txid: str) -> List:
        cachefile = self.cache_dir + "meta"
        cachefile = os.path.join(cachefile, txid) + ".json"
        raw = get_cache(cachefile, bin=False)
        if raw is None:
            url = self.url + txid
            r = requests.get(url)
            assert r.ok, "Could not connect to API"
            raw = json.loads(r.text.strip())
            with open(cachefile, "w") as f:
                f.write(str(raw))
        return raw
    
    def get_address(self, wallet: str) -> List:
        cachefile = self.cache_dir + "wallets"
        cachefile = os.path.join(cachefile, wallet) + ".json"
        url = self.url + f"/address/{wallet}/txs"
        r = requests.get(url)
        assert r.ok, "Could not connect to API"
        raw = r.text.strip()
        with open(cachefile, "w") as f:
            f.write(str(raw))
        return json.loads(raw)

    def get_tx_hashes(self, block_id: str) -> List:
        url = self.url + f"block/{block_id}/txids"
        r = requests.get(url)
        hashes = json.loads(r.text)
        return hashes

    def get_block_header(self, block_id: str) -> bytes:
        url = self.url + f"block/{block_id}/header"
        r = requests.get(url)
        return bytes.fromhex(r.text)

    def get_block(self, block_id: str) -> Block:
        block_header = self.get_block_header(block_id)
        block = Block.decode(block_header)
        block.tx_hashes = self.get_tx_hashes(block_id)
        return block

    def broadcast(self, tx: Union[bytes, str]) -> str:
        """
        Note tx must be hex of encoded signed transaction
        """
        if isinstance(tx, bytes):
            tx = tx.hex()
        url = self.url + "tx"
        r = requests.post(url, data=tx)
        assert r.ok, f"Bad POST: {r.status_code}"
        return r.text #return the txid
        

