from ape import accounts, project, networks

def main():
    with networks.parse_network_choice("arbitrum:mainnet:alchemy") as provider:
        acct = accounts.load("Deployer")
        print(acct.address, acct.balance)
        compass = "0x2E68518cC9351843d11B3F41c08a63cd5B72Eb71"    # new compass arb-main
        reward = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"     # USDT
        factory = "0x9A500317a2332B9D659DC36615a9e95516B51639"    # llamalend bot factory
        admin = "0xF48F4e86dE6a30D75dbe3A6C67E17Cf3cbDE5768"      # need to confirm
        investor = "0x2175e091176F43eD55313e4Bc31FE4E94051A6fE"   # fund investor
        spamFeeWallet = "0x26075E00a66415398bdD773DF080DAdd6f26C18F"
        spamFee = 2000000000000000

        competitionArb = project.competitionArb.deploy(compass, reward, factory, admin, investor, spamFeeWallet, spamFee, sender=acct)
        print(competitionArb)