import ape
import pytest
from eth_abi import encode
from web3 import Web3

@pytest.fixture(scope="session")
def Deployer(accounts):
    return accounts[0]

@pytest.fixture(scope="session")
def Admin(accounts):
    return accounts[1]

@pytest.fixture(scope="session")
def Alice(accounts):
    return accounts[2]

@pytest.fixture(scope="session")
def Compass(accounts):
    return accounts[3]

@pytest.fixture(scope="session")
def USDT(Deployer, project):
    print(project)
    return Deployer.deploy(project.testToken, "USDT", "USDT", 6, 10000000000000)

def function_signature(str):
    return Web3.keccak(text=str)[:4]

def test_add():
    assert 1 + 1 == 2

@pytest.fixture(scope="session")
def CompetitionArb(Deployer, project, Compass, USDT, Alice, Admin):
    contract = Deployer.deploy(project.competitionArb, Compass, USDT, Alice, Admin)
    funcSig = function_signature("set_paloma()")
    addPayload = encode(["bytes32"], [b'123456'])
    payload = funcSig + addPayload
    contract(sender=Compass, data=payload)

    return contract

def test_competition_arb(Deployer, accounts, CompetitionArb, Compass, Alice, USDT, Admin, chain):
    assert Deployer == accounts[0]

    assert CompetitionArb.epoch_cnt() == 0
    USDT.approve(CompetitionArb.address, 1000000000, sender=Deployer)
    receipt = CompetitionArb.send_reward(1000000000, 1, sender=Deployer)
    assert not receipt.failed
    assert CompetitionArb.epoch_cnt() == 1
    assert CompetitionArb.active_epoch_num() == 1

    USDT.approve(CompetitionArb.address, 4000000000, sender=Deployer)
    receipt = CompetitionArb.send_reward(2000000000, 2, sender=Deployer)
    assert not receipt.failed
    assert CompetitionArb.epoch_cnt() == 3

    with ape.reverts():
        USDT.approve(CompetitionArb.address, 6000000000, sender=Deployer)
        receipt = CompetitionArb.send_reward(1000000000, 6, sender=Deployer)

    assert CompetitionArb.epoch_info(1).competition_start == 1719360000
    assert CompetitionArb.epoch_info(1).competition_end == 1719446400

    assert CompetitionArb.epoch_info(2).competition_start == 1719446400
    assert CompetitionArb.epoch_info(2).competition_end == 1719532800

    active_epoch_num = CompetitionArb.active_epoch_num()
    chain.pending_timestamp += 86400
    CompetitionArb.bid(3000, sender=Alice)
    assert CompetitionArb.epoch_info(active_epoch_num).entry_cnt == 1
    with ape.reverts():
        CompetitionArb.bid(4000, sender=Alice)

    func_sig = function_signature(
        "set_winner_list((address,uint256)[])")
    enc_abi = encode(["(address,uint256)[]"], [[(Deployer.address, 1000000000)]])
    # enc_abi = encode(["(address,uint256)[]"], [[]])
    add_payload = encode(["bytes32"], [b'123456'])
    payload = func_sig + enc_abi + add_payload
    with ape.reverts():
        CompetitionArb.set_winner_list([], sender=Compass)
    CompetitionArb(sender=Compass, data=payload)
    assert CompetitionArb.active_epoch_num() == 2
    assert CompetitionArb.epoch_info(2).prize_amount == 2000000000

    chain.pending_timestamp += 86400
    active_epoch_num = CompetitionArb.active_epoch_num()
    CompetitionArb.bid(4000, sender=Alice)
    CompetitionArb.bid(4000, sender=Deployer)
    assert CompetitionArb.epoch_info(active_epoch_num).entry_cnt == 2
    with ape.reverts():
        CompetitionArb.bid(4000, sender=Alice)

    assert CompetitionArb.claimable_amount(Deployer.address) == 1000000000

    balance = USDT.balanceOf(CompetitionArb.address)
    CompetitionArb.emergency_withdraw(balance, sender=Admin)

    balance = USDT.balanceOf(CompetitionArb.address)
    assert balance == 0
# import pytest
# from vyper import testing

# from competitionArb import CompetitionArb, EpochInfo, BidInfo, WinnerInfo, SwapInfo

# @pytest.fixture(scope="module")
# def contract():
#     return testing.compile_contract(
#         "competitionArb.vy",
#         "CompetitionArb",
#     )

# def test_set_paloma(contract):
#     contract.set_paloma()
#     assert contract.paloma() != 0

# def test_update_compass(contract):
#     new_compass = "0x1234567890123456789012345678901234567890"
#     contract.update_compass(new_compass)
#     assert contract.compass() == new_compass

# def test_update_admin(contract):
#     new_admin = "0x0987654321098765432109876543210987654321"
#     contract.update_admin(new_admin)
#     assert contract.admin() == new_admin

# def test_emergency_withdraw(contract):
#     amount = 1000
#     contract.emergency_withdraw(amount)
#     assert contract.claimable_amount(contract.admin()) == amount

# def test_send_reward(contract):
#     daily_amount = 1000
#     days = 5
#     contract.send_reward(daily_amount, days)
#     assert contract.epoch_cnt() == days

# def test_set_winner_list(contract):
#     winner_infos = [
#         WinnerInfo("0x1111111111111111111111111111111111111111", 100),
#         WinnerInfo("0x2222222222222222222222222222222222222222", 200),
#         WinnerInfo("0x3333333333333333333333333333333333333333", 300)
#     ]
#     contract.set_winner_list(winner_infos)
#     assert contract.active_epoch_num() == 2

# def test_bid(contract):
#     token_asset = "0x4444444444444444444444444444444444444444"
#     chain_id = 1
#     aave_version = 2
#     contract.bid(token_asset, chain_id, aave_version)
#     assert contract.epoch_info(contract.active_epoch_num()).entry_cnt == 1

# def test_create_bot(contract):
#     swap_infos = [
#         SwapInfo(["0x5555555555555555555555555555555555555555"], [[1, 2, 3, 4, 5]], 100, 200, ["0x6666666666666666666666666666666666666666"])
#     ]
#     collateral = "0x7777777777777777777777777777777777777777"
#     debt = 1000
#     N = 10
#     callbacker = "0x8888888888888888888888888888888888888888"
#     callback_args = [1, 2, 3, 4, 5]
#     leverage = 2
#     deleverage_percentage = 50
#     health_threshold = 80
#     expire = 10000
#     number_trades = 5
#     interval = 10

#     contract.create_bot(
#         swap_infos,
#         collateral,
#         debt,
#         N,
#         callbacker,
#         callback_args,
#         leverage,
#         deleverage_percentage,
#         health_threshold,
#         expire,
#         number_trades,
#         interval
#     )

#     assert contract.claimable_amount(msg.sender) == 0