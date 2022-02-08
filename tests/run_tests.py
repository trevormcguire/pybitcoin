import os
import sys
sys.path.append(os.path.abspath(os.pardir) + "/src")
import bitcoin
from bitcoin.utils import *
from bitcoin.keys import *
from bitcoin.testnet import TestNet
from bitcoin.tx import *
from bitcoin.block import *
from bitcoin.script import *

def test_ecc():
    assert modulardiv(8, 4, 5) == 2
    assert modulardiv(8, 3, 5) == 1
    assert modulardiv(11, 4, 5) == 4
    assert G == 1 * G
    assert G + G == 2 * G
    assert G + G + G == 3 * G
    print("Elliptic Curve Cryptography ... OK ")

def test_keys():
    sk = 1
    pk = PublicKey.from_private(sk)
    assert pk.x == bitcoin.G.x
    assert pk.y == bitcoin.G.y
    sk = 3
    pk = PublicKey.from_private(sk)
    assert pk.x == (3 * bitcoin.G).x
    wallet = pk.get_address(compressed=True) #also tests encode(compressed=True, hash_160=True)
    print("Keys ... OK ")

def test_api():
    wallet = "mk9chiypvYnYy6fs876jKLcCXfLSGoCj4k"
    net = TestNet()
    res = net.get_address(wallet)
    assert isinstance(res, list) and isinstance(res[0], dict) and len(res) > 0
    try:
        net.get_tx("3424242")
    except AssertionError:
        pass #this test should fail
    txid = "353f52fb1332a3c313b175f79a0cf022d44cce85d4ea433a552b510f7bab2c8b"
    res = net.get_tx(txid)
    assert isinstance(res, bytes)
    parent_path = os.path.abspath(os.pardir) + "/"
    cache_path = parent_path + "src/bitcoin/testnet/datacache/txdb"
    assert txid in os.listdir(cache_path) #ensure the txid file was cached so we don't stress the API
    print("API Wrapper ... OK ")

def test_tx():
    sk1 = int.from_bytes(b"A really not secure secret key", "big")
    pk1 = PublicKey.from_private(sk1)
    wallet1 = pk1.get_address(compressed=True)

    sk2 = int.from_bytes(b"Second sk", "big")
    pk2 = PublicKey.from_private(sk2)
    wallet2 = pk1.get_address(compressed=True)

    net = TestNet()
    sender_address = net.get_address(wallet1)
    prev_tx_id = sender_address[0]["txid"] #api sorts the newest first
    prev_tx = Tx.decode(net.get_tx(prev_tx_id)) 
    prev_idx = get_tx_idx(wallet1, prev_tx)
    assert prev_idx is not None

    ins = [{
        "prev_tx": bytes.fromhex(prev_tx_id),
        "prev_idx": prev_idx,
        "script_sig": p2pkh_script(base58.decode(wallet1)), #decode base58, wallet address hash pubkey hash in it
        "seq": 0xffffffff #not an important parameter, you can use this as default
    }]

    outs = [
        {"amount": 20000, "script_pubkey": p2pkh_script(base58.decode(wallet2))}, #goes to target wallet
        {"amount": 48000, "script_pubkey": p2pkh_script(base58.decode(wallet1))} #change that comes back to our wallet
        ]

    tx = Tx(
        version = 1, #using 1 as verison 
        inputs = ins, 
        outputs = outs,
    )

    message = tx.encode(sig_idx = 0) #point to the input UTXO we are trying to spend
    sig = Signature.from_private(sk1, z=int.from_bytes(hash256(message), "big"))
    sig = sig.encode() + b"\x01" 
    pubkey_bytes = PublicKey.from_point(pk1).encode(compressed=True, hash_160=False)
    script_sig = Script([sig, pubkey_bytes])
    tx.inputs[0]["script_sig"] = script_sig #sign our input

    #validate transaction
    assert validate_tx(prev_tx, tx, message, pk1)
    print("Transactions ... OK ")

def test_block():
    GENESIS_BLOCK.encode() #this tests both encoding and decoding in one step
    print("Blocks ... OK ")

if __name__ == "__main__":
    print("Running Tests...")
    test_ecc()
    test_keys()
    test_api()
    test_tx()
    test_block()
    print("All tests ran successfully.")
