from __future__ import annotations
from typing import *
from .utils import encode_int, encode_varint, decode_int, decode_varint, ensure_stream, base58, hash256
from .script import Script
from io import BytesIO
from .keys import PublicKey
from .ecdsa import Signature, validate_signature

def get_tx_idx(wallet, prev_tx):
    pkhash = base58.decode(wallet) #get the pkhash of the wallet
    for idx in range(len(prev_tx.outputs)):
        out = prev_tx.outputs[idx]
        out_pkhash = [x for x in out["script_pubkey"].commands if not type(x) is int]
        if out_pkhash:
            match = list(filter(lambda x: x, [x == pkhash for x in out_pkhash]))
            if match:
                return idx
    return None

def validate_tx(utxo: Tx, 
                tx: Tx,
                message: bytes, 
                public_key: PublicKey) -> bool:
    """
    -----------
    Verify a p2pkh Transaction
    -----------
    """
    prev_idx = tx.inputs[0]["prev_idx"] #index of the UTXO spent
    script_sig = tx.inputs[0]["script_sig"].commands #ScriptSig -> <der_sig> <sec_pubkey>
    script_pubkey = utxo.outputs[prev_idx]["script_pubkey"].commands #"locking" script of UTXO
    input_amt = utxo.outputs[prev_idx]["amount"] #UTXO amount
    
    output_amt = sum([out["amount"] for out in tx.outputs])
    if output_amt > input_amt: #ensure no new bitcoins are created
        return False

    pkhash = public_key.encode(compressed=True, hash_160=True) #hash of the sender's public key
    #remember we are using p2pkh, so our pkhash is the third element
    if pkhash != script_pubkey[2]: #==OP_EQUALVERIFY
        return False

    sig, pk = Signature.decode(script_sig[0]), PublicKey.decode(script_sig[1]) 
    if not validate_signature(p=pk, 
                              message=message, 
                              sig=sig): #==OP_CHECKSIG
        return False
    
    #To do: hook into UTXO set to check if Tx is unspent
    return True

class Tx(object):
    """
    Object Representing a Bitcoin Transaction
    """
    def __init__(self, 
                 version: int, 
                 inputs: List[dict], 
                 outputs: List[dict], 
                 locktime: int = 0):
        self.version = version
        self.inputs = inputs
        self.outputs = outputs
        self.locktime = locktime
        
    def __repr__(self):
        s = f"Version: {self.version}\nNum Inputs: {len(self.inputs)}\nInputs:\n"""
        for i in self.inputs:
            s += f'{i["prev_tx"].hex()} - {i["script_sig"]}\n'
            s += f'Index: {i["prev_idx"]}\n'
        s += f"Num Outputs: {len(self.outputs)}\nOutputs:\n"
        for o in self.outputs:
            s += f'{o["amount"]} SAT - {o["script_pubkey"]}\n'
        s += f'Locktime: {self.locktime}'
        return s
    
    def encode(self, sig_idx: int = -1):
        #version
        out = [encode_int(self.version, 4)] #4 byte little-endian
        
        #encode inputs
        out += [encode_varint(len(self.inputs))]
        out += [self.encode_inputs(sig_idx=sig_idx)]
        
        #encode outputs
        out += [encode_varint(len(self.outputs))]
        out += [self.encode_outputs()]
        
        #locktime and SIGHASH
        out += [encode_int(self.locktime, 4)]
        out += [encode_int(1, 4) if sig_idx != -1 else b""] #SIGHASH_ALL
        return b"".join(out)
    
    def encode_inputs(self, sig_idx: int = -1):
        """
        prev_tx is encoded to be little endian
        prev_idx, seq are 4 byte little endian encoded integers
        script_sig uses Script encoding
        """
        out = []
        for idx in range(len(self.inputs)):
            inp = self.inputs[idx]
            if sig_idx == -1 or sig_idx == idx:
                script_sig = inp["script_sig"].encode()  
            else:
                script_sig = Script([]).encode()
            out += [
                inp["prev_tx"][::-1], #reverse bytes
                encode_int(inp["prev_idx"], 4),
                script_sig,
                encode_int(inp["seq"], 4)
            ]
            
        return b"".join(out)

    def encode_outputs(self):
        out = []
        for o in self.outputs:
            encoded = [
                encode_int(o["amount"], 8),
                o["script_pubkey"].encode()
            ]
            out += encoded
        return b"".join(out)

    def get_id(self):
        return hash256(self.encode())[::-1].hex() #little-endian, hexadecimal
    
    @classmethod
    def decode(cls, b: Union[bytes, BytesIO]) -> Tx:
        """
        Decodes the raw bytes of a transaction into a Tx object
        """
        b = ensure_stream(b)
        segwit, witness = False, []
        
        version = decode_int(b, 4)
        
        num_inputs = decode_varint(b)
        if num_inputs == 0:
            assert b.read(1) == b"\x01" #segwit marker -- need to read one more
            num_inputs = decode_varint(b)
            segwit = True
            
        inputs = []
        for n in range(num_inputs):
            prev_tx = b.read(32)[::-1] #little to big endian
            prev_idx = decode_int(b, 4)
            script_sig = Script.decode(b)
            seq = decode_int(b, 4)
            inputs.append({"prev_tx": prev_tx, 
                           "prev_idx": prev_idx, 
                           "script_sig": script_sig, 
                           "seq": seq})

        num_outputs = decode_varint(b)
        outputs = []
        for n in range(num_outputs):
            amt = decode_int(b, 8)
            script_pubkey = Script.decode(b)
            outputs.append({"amount": amt, 
                            "script_pubkey": script_pubkey})

        if segwit:
            for i in inputs:
                num_items = decode_varint(b)
                items = []
                for _ in range(num_items):
                    item_len = decode_varint(b)
                    if item_len == 0:
                        items.append(0)
                    else:
                        items.append(b.read(item_len))
                witness.append(items)

        locktime = decode_int(b, 4)
        return cls(version, inputs, outputs, locktime) #can include segwit, witness here
    

