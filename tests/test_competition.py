import ape
import pytest
from eth_abi import encode
from web3 import Web3

# @pytest.fixture(scope="session")
# def Deployer(accounts):
#     return accounts[0]

# @pytest.fixture(scope="session")
# def Admin(accounts):
#     return accounts[1]

# @pytest.fixture(scope="session")
# def Alice(accounts):
#     return accounts[2]

# @pytest.fixture(scope="session")
# def Compass(accounts):
#     return accounts[3]

# @pytest.fixture(scope="session")
# def USDT(Deployer, project):
#     return Deployer.deploy(project.testToken, "USDT", "USDT", 6, 10000000000000)

# @pytest.fixture(scope="session")
# def CompetitionArb(Deployer, project, Compass, USDT, Alice, Admin):
#     contract = Deployer.deploy(project.competitionArb, Compass, USDT, Alice, Admin)
#     funcSig = function_signature("set_paloma()")
#     addPayload = encode(["bytes32"], [b'123456'])
#     payload = funcSig + addPayload
#     contract(sender=Compass, data=payload)

#     return contract

# def function_signature(str):
#     return Web3.keccak(text=str)[:4]

# def test_add():
#     assert 1 + 1 == 2

# def test_competition_arb(Deployer, accounts, CompetitionArb, Compass, Alice, chain):
#     assert Deployer == accounts[0]

#     func_sig = function_signature(
#         "set_active_epoch((uint256,uint256,uint256,uint256,uint256))")
#     enc_abi = encode(["(uint256,uint256,uint256,uint256,uint256)"], [(1, 1716249600, 1716336000, 0, 10000000)])
#     add_payload = encode(["bytes32"], [b'123456'])
#     payload = func_sig + enc_abi + add_payload
#     CompetitionArb(sender=Compass, data=payload)

#     assert CompetitionArb.epoch_info().epoch_id == 1
#     assert CompetitionArb.epoch_info().competition_start == 1716249600
#     assert CompetitionArb.epoch_info().competition_end == 1716336000
#     assert CompetitionArb.epoch_info().entry_cnt == 0
#     assert CompetitionArb.epoch_info().prize_amount == 10000000
import pytest
from vyper import testing

from competitionArb import CompetitionArb, EpochInfo, BidInfo, WinnerInfo, SwapInfo

@pytest.fixture(scope="module")
def contract():
    return testing.compile_contract(
        "competitionArb.vy",
        "CompetitionArb",
    )

def test_set_paloma(contract):
    contract.set_paloma()
    assert contract.paloma() != 0

def test_update_compass(contract):
    new_compass = "0x1234567890123456789012345678901234567890"
    contract.update_compass(new_compass)
    assert contract.compass() == new_compass

def test_update_admin(contract):
    new_admin = "0x0987654321098765432109876543210987654321"
    contract.update_admin(new_admin)
    assert contract.admin() == new_admin

def test_emergency_withdraw(contract):
    amount = 1000
    contract.emergency_withdraw(amount)
    assert contract.claimable_amount(contract.admin()) == amount

def test_send_reward(contract):
    daily_amount = 1000
    days = 5
    contract.send_reward(daily_amount, days)
    assert contract.epoch_cnt() == days

def test_set_winner_list(contract):
    winner_infos = [
        WinnerInfo("0x1111111111111111111111111111111111111111", 100),
        WinnerInfo("0x2222222222222222222222222222222222222222", 200),
        WinnerInfo("0x3333333333333333333333333333333333333333", 300)
    ]
    contract.set_winner_list(winner_infos)
    assert contract.active_epoch_num() == 2

def test_bid(contract):
    token_asset = "0x4444444444444444444444444444444444444444"
    chain_id = 1
    aave_version = 2
    contract.bid(token_asset, chain_id, aave_version)
    assert contract.epoch_info(contract.active_epoch_num()).entry_cnt == 1

def test_create_bot(contract):
    swap_infos = [
        SwapInfo(["0x5555555555555555555555555555555555555555"], [[1, 2, 3, 4, 5]], 100, 200, ["0x6666666666666666666666666666666666666666"])
    ]
    collateral = "0x7777777777777777777777777777777777777777"
    debt = 1000
    N = 10
    callbacker = "0x8888888888888888888888888888888888888888"
    callback_args = [1, 2, 3, 4, 5]
    leverage = 2
    deleverage_percentage = 50
    health_threshold = 80
    expire = 10000
    number_trades = 5
    interval = 10

    contract.create_bot(
        swap_infos,
        collateral,
        debt,
        N,
        callbacker,
        callback_args,
        leverage,
        deleverage_percentage,
        health_threshold,
        expire,
        number_trades,
        interval
    )

    assert contract.claimable_amount(msg.sender) == 0