# @version 0.3.9

STABLECOIN: public(address)
ADMIN: public(address)
FEE_RECEIVER: public(address)
WETH: public(address)

@external
def __init__():
    self.STABLECOIN = empty(address)
    self.ADMIN = empty(address)
    self.FEE_RECEIVER = empty(address)
    self.WETH = empty(address)

@external
def stablecoin() -> address:
    return self.STABLECOIN

@external
def admin() -> address: 
    return self.ADMIN

@external
def fee_receiver() -> address:
    return self.FEE_RECEIVER

@external
def weth() -> address:
    return self.WETH

@external
def log2(_x: uint256) -> int256:
    x: int256 = 1
    return x
