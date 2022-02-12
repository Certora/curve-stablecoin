import pytest

PRICE = 3000


@pytest.fixture(scope="module", autouse=True)
def PriceOracle(DummyPriceOracle, accounts):
    return DummyPriceOracle.deploy(accounts[0], PRICE * 10**18, {'from': accounts[0]})


@pytest.fixture(scope="module", autouse=True)
def collateral_token(ERC20Mock, accounts):
    return ERC20Mock.deploy("Colalteral", "ETH", 18, {'from': accounts[0]})


@pytest.fixture(scope="module", autouse=True)
def borrowed_token(ERC20Mock, accounts):
    return ERC20Mock.deploy("Brrr", "USD", 18, {'from': accounts[0]})


@pytest.fixture(scope="module", autouse=True)
def amm(AMM, PriceOracle, collateral_token, borrowed_token, accounts):
    return AMM.deploy(
        collateral_token, borrowed_token,
        100, PRICE * 10**18, 10**16,
        accounts[0],
        PriceOracle, PriceOracle.price.signature,
        {'from': accounts[0]})
