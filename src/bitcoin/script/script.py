"""
Script
"""
from __future__ import annotations
from typing import *
from ..utils import ensure_stream, decode_varint, encode_varint, decode_int, encode_int

class Script:
    def __init__(self, commands: List):
        self.commands = commands
    
    def __repr__(self):
        return f"Script({[x if isinstance(x, int) else x.hex() for x in self.commands]})"
    
    def __add__(self, other: Script):
        """
        Used to merge ScriptSig with ScriptPubKey
        """
        return self.__class__(other.commands + self.commands)
    
    @classmethod
    def decode(cls, b: bytes) -> Script:
        """
        -------------
        Decodes raw bytes into a Script object
        -------------
        First byte is supposed to be a varint, however when retrieving data from blockstream.info 
            API, the varint is missing--so make it optional
        -------------
        Procedure
        -------------
        If n between 0x01 and 0x4b (75), we read the next n bytes (element)
        Special handling if data to push is larger than 75 bytes:
            OP CODES 76, 77 
        If greater than 77, its an OP- take integer representation
        -------------
        """ 
        b = ensure_stream(b)
        l = decode_varint(b)
        if l == 0:
            return cls([])
        cmds = []
        i = 0
        while i < l:
            curr = int.from_bytes(b.read(1), "big")
            if 1 <= curr <= 75:
                cmds.append(b.read(curr))
                i += curr
            elif curr == 76:
                datalen = decode_int(b, 1, "little")
                cmds.append(b.read(datalen))
                i += datalen
            elif curr == 77:
                datalen = decode_int(b, 2, "little")
                cmds.append(b.read(datalen))
                i += datalen
            else:
                cmds.append(curr)
            i += 1
        return cls(cmds)

    def encode(self) -> List[bytes]:
        out = []
        for cmd in self.commands:
            if isinstance(cmd, int):
                out += [encode_int(cmd, 1)] #OP_CODE -- encode as single byte
            elif isinstance(cmd, bytes):
                cmd_len = len(cmd)
                if cmd_len < 75:
                    out += [encode_int(cmd_len, 1)]
                elif 76 <= cmd_len <= 255:
                    out += [encode_int(76, 1), encode_int(cmd_len, 1)] #OP_PUSHDATA1
                elif 256 <= cmd_len <= 520:
                    out += [encode_int(77, 1), encode_int(cmd_len, 2)] #OP_PUSHDATA2
                else:
                    raise ValueError(f"Command Length ({cmd_len}) is too long. Must be <= 520")
                out += [cmd]
                
        ret = b"".join(out)
        return encode_varint(len(ret)) + ret #encode length as varint

def p2pkh_script(pkhash: bytes) -> Script:
    """
    --------------
    Params
    --------------
        1. pkhash -> hash160 of public key (20 bytes)
    --------------
    Op Codes for P2PKH
    --------------
    118 - OP_DUP
    169 - OP_HASH160
    136 - OP_EQUALVERIFY
    172 - OP_CHECKSIG
    --------------
    Returns
    --------------
        1. -> P2PKH ScriptPubKey 
    --------------
    """
    assert len(pkhash) == 20, "Must be a hash160 resulting in 20 bytes"
    return Script([118, 169, pkhash, 136, 172])

