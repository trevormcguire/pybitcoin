# Bitcoin From Scratch 

A while ago I decided I really wanted to understand how Bitcoin works. So, being a firm believer in the notion that the best way to understand something is by doing it, I decided to code it from scratch.

## Examples

Create a private and public key:
```
>>> import bitcoin
>>> sk = bitcoin.keys.randsk() #random key between 1 and N
>>> pk = bitcoin.keys.PublicKey.from_private(sk)
>>> pk
PublicKey(curve=EllipticCurve(a=0, b=7) in Field(115792089237316195423570985008687907853269984665640564039457584007908834671663), x=104876481166172619266302667503882439808238160863585748282537657252844545120779, y=29374428700451408797720524861165054253400273225790811919690932588156595332593)
```

Create two wallet addresses to create a transaction:
```
>>> from bitcoin.keys import PublicKey
>>> from bitcoin.testnet import TestNet
>>> 
>>> net = TestNet()
>>> 
>>> sk = int.from_bytes(b"A really not secure secret key", "big")
>>> pk = PublicKey.from_private(sk)
>>> wallet1 = pk.get_address(compressed=True)
>>> 
>>> sk2 = int.from_bytes(b"A second secret", "big")
>>> pk2 = PublicKey.from_private(sk2)
>>> wallet2 = pk2.get_address(compressed=True)
>>> 
>>> print(f"Wallet 1 Address {wallet1}")
Wallet 1 Address mk9chiypvYnYy6fs876jKLcCXfLSGoCj4k
>>> print(f"Wallet 2 Address {wallet2}")
Wallet 2 Address myNvYqYXSzcw3GnnGfFk7nwQ3xDvjC2oSM
```

Fetch Previous Transactions
```
>>> from bitcoin.tx import *
>>> sender = net.get_address(wallet1)
>>> prev_tx_id = sender[0]["txid"]
>>> prev_tx = net.get_tx(prev_tx_id)
>>> prev_tx = Tx.decode(prev_tx)
>>>
>>> prev_idx = get_tx_idx(wallet1, prev_tx)
>>> prev_tx
Version: 1
Num Inputs: 1
Inputs:
353f52fb1332a3c313b175f79a0cf022d44cce85d4ea433a552b510f7bab2c8b - Script(['3044022036599108a992c27a2fcca6f28309b3e6e4d17de9f575f0052e107edc69bdff23022023c9eccd0cf44271ed3b20f84b5db1df109b43edbe3807ca6d5294adba35670b01', '03fd4d7c6c072c9ae5e96139fcf99c36aac902c18a0d99948bc2cb54fd08f8b073'])
Index: 1
Num Outputs: 2
Outputs:
25000 SAT - Script([118, 169, '349bf5d7b45c6366433d985a09735a26d2208539', 136, 172])
70000 SAT - Script([118, 169, '32cf8a0b81f63473be3f88efe281f4b1f13c857e', 136, 172])
Locktime: 0
```

Construct Transactions
```
>>> ins = [{"prev_tx":bytes.fromhex(prev_tx_id), "prev_idx":prev_idx, "script_sig": p2pkh_script(base58.decode(wallet1)), "seq":0xffffffff}]
>>> outs = [
... {"amount":25000, "script_pubkey":p2pkh_script(base58.decode(wallet2))},
... {"amount":44000, "script_pubkey":p2pkh_script(base58.decode(wallet1))}
... ]
>>> tx = Tx(version=1, inputs=ins, outputs=outs)
>>> tx
Version: 1
Num Inputs: 1
Inputs:
aaf1a4fa390bdbfcf543a0ace7b93e406d78667ca32568edcb01e7598e3828d4 - Script([118, 169, '32cf8a0b81f63473be3f88efe281f4b1f13c857e', 136, 172])
Index: 1
Num Outputs: 2
Outputs:
25000 SAT - Script([118, 169, 'c3ed7acbba3080a947ce28eab9789cb0273cf8cf', 136, 172])
44000 SAT - Script([118, 169, '32cf8a0b81f63473be3f88efe281f4b1f13c857e', 136, 172])
Locktime: 0
```

Sign Transactions
```
>>> from bitcoin.ecdsa import Signature
>>> message = tx.encode(sig_idx=0)
>>> sig = Signature.from_private(sk, z=int.from_bytes(hash256(message), "big"))
>>> sig = sig.encode() + b"\x01"
>>> pkbytes = pk.encode(compressed=True, hash_160=True)
>>> script_sig = Script([sig, pkbytes])
>>> tx.inputs[0]["script_sig"] = script_sig
>>> tx.encode().hex()
'0100000001d428388e59e701cbed6825a37c66786d403eb9e7aca043f5fcdb0b39faa4f1aa010000005d47304402201af22482425c6ca93c1a88dc4adf4cb5933522bb498ace0b52e8176800f121cd02204fc75b2f6af2251ea4678de7b19361d8b64f93e5535687972509e650b3755dc2011432cf8a0b81f63473be3f88efe281f4b1f13c857effffffff0290d00300000000001976a914c3ed7acbba3080a947ce28eab9789cb0273cf8cf88acc0b60600000000001976a91432cf8a0b81f63473be3f88efe281f4b1f13c857e88ac00000000'
```

Broadcast Transactions
```
>>> txid = net.broadcast(tx.encode().hex())
>>> hash256(tx.encode())[::-1].hex() == txid
True
```

Verify Transactions
```
>>> validate_tx(prev_tx, tx, message, pk)
True
```

Fetch and Build Blocks
```
>>> from bitcoin.block import *
>>> block_id = "0000000000000078bf9dd673997fdcdd3534af881a6157ec6e6e4e24ba789e45"
>>> block = net.get_block(block_id)
>>> block

        Block(
            version: 547356672
            prev_block: 00000000000000743e49b3225ffd42d52596ae5dad3bfbf4795f360d78c1a5f2
            merkle_root: 5e34b461770ef7ea619e799efd77d0704d219d6bdcefc6a8c76471ab54b5a7c0
            timestamp: 1644176836
            bits: 63ac001a
            nonce: 28496580
            Difficulty: 24914342
        )

>>> block.tx_hashes
['5f9919bc99300f2044bcf598349721cbdd38d193f125dee1ef0d11cc97a37f9c', 'ae75b6aeee0d9a4bb61513501156ae0d4fcc7332eb5df5571cbecc2ec7d39a11', 'd5af62ac37c2b8bc751a330f5663e27fa4d04a2cc21f235e5e62731fffe25c2c', 'a7dbf945a4faa2ed4310ab8c12fe307d3b4e71a0c63e52af955d6e2340b1a43b', '35f70e4989db093b537adb15e5fa1d9fd2e79c79c6faa94e521af5fdf3c83588', '48ec729785266344d6b057749f1d073c2dd046d4c34363332c358a5ef793c3a5', 'e25ed01adc6bf06abbeae9b6bb66e7b3e4d7b1abbb75aed99d287f8de6128b1a', '8fa08e7012b550db2f31bdabec949770e441a0f44bb33df4f7d3746c64482e22', '6c3bf9e0b082090f40304b627f2e6cd8f08337cb7cca5aac9f3862c72f82e2d0', 'dcfa9133ee0d76f4a7a0732b7ce1295884b6abd45b7d42a6a0d7d7fbea9d1009', '261a087fd4115f5cad8659be79f30edb222849fa97f780e66eb1a3bd06aa214a', 'a5ac0ab7769f178249c6e3090e6340811d648b23a9ff7b719a3386c323de1fb3', '1ad7d64b0d10b41fd3de148e864bc1e1fe6c8498deafc41d7e76cd5ed997c960', '488a395a62ce30e0111894eca014c7c385a08a97647887175b2ba28a4d409686', '48a176a0722f35a276db11bc97aa525a2f2e937f1d34dbef4e021bd4085da7da', 'a2c3444142f69195f03aa67a7af5474a24c929af7a206df08cad7e95e816c414', 'e474977a7edbd0159ace7468964161af60e2c1041b965d47984423700313a289', 'c00dbe87b69f1832ee78ab499bbef86d5d247cfe90d883a8f09486560c45625c', '5f41cb6ca9a01f01e1d9bb72c5836eaf5c9fbedd0625185208f2725e9353510f', '3cf15688fda32c3d7347682f7e39b31c79fbe00389c61ccc6a76384a5c0a391b', '384c6b0b150c78539e70abd222e14a467e0790cacbd03f77f511176ea7a215e0', '4d310028925e514f16349e31fe9499373d7d7e008c671eb72fdba1a92556b364', '3c6dcbe97f7230e458d9d64f84d0791e706b924cfef815dd1c1dc4cf968588eb', '24eae3989ba8e67638415539e06b1f8cd1945f7da8fa6adb414eefb26f36ccf1', 'f3eb5540dd3b131c0b6189c37ba4ae70d915a0c759089dd262df2947fcc12abe', 'efbe5405409cdbaf3cb19d08bace9b7b053f19fa00d2a8fc922d3e8807b80b25', 'ae56a0ee929cfe0b58665fe9e39474a5bfafd0f365ef633f6f4bc16a3bab0944', '5a2f3b6ec5508b9ce77e8586cd32989d62007742b4919b7cfdbc246f633e9fa1', 'c897906ad27a7fdf406c8deaf9cd070ff529498d262b2a8ff6f320ada3c130c2', 'c3b2d92dee3f753ff45929ac90c873e49e325d7fa5ecb27d45c109a7acbe38ca', '8601a65d10938b1f244dbcd443e4ed28bca7f939b036cb8fdb946d69a37914d0', 'c4c501e5baf66052071cba66743e8e72975946569e604252bb0d5a64cb6452da', '220da7461b039b5a10529c5472b1159e31e4e3aba4b00278fad54593be7b92e7']
```

Construct Merkle Trees
```
>>> from bitcoin.merkle import MerkleTree
>>> merkle = MerkleTree.construct(block.tx_hashes)
>>> merkle
MerkleTree(root=['ba2959ce1206c38acc833e47e1f688fe7d8e9f953da2bba50cac137abe739d57'])
```
