#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Name: main.py
Description: SKY airdrop boosted rewards calculation.
Author: 0xcommanderkeen
Date: 2024-10-15
"""

# Import necessary libraries
from collections import defaultdict
import csv
import datetime
from decimal import Decimal
import json
import os
import sys
import logging
from dotenv import load_dotenv
from chain_harvester.networks.ethereum.mainnet import EthereumMainnetChain
from chain_harvester.utils import normalize_to_decimal

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

load_dotenv()


CONTRACT_START_BLOCK = 20692595
START_BLOCK = 20777633
END_BLOCK = 20978279

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHEREUM_RPC_NODE = os.getenv("ETHEREUM_RPC_NODE")

FARM_ADDRESS = "0x0650caf159c5a49f711e8169d4336ecb9b950275"


def get_start_block(chain):
    timestamp = int(
        datetime.datetime(
            2024, 9, 18, 13, 0, 0, tzinfo=datetime.timezone.utc
        ).timestamp()
    )
    return chain.get_block_for_timestamp(timestamp)


def get_end_block(chain):
    timestamp = int(
        datetime.datetime(
            2024, 10, 16, 13, 0, 0, tzinfo=datetime.timezone.utc
        ).timestamp()
    )
    return chain.get_block_for_timestamp(timestamp)


def get_rewards_paid_events(chain):
    logging.info(f"Fetching RewardPaid events")
    event_name = "RewardPaid"
    topics = chain.get_events_topics(FARM_ADDRESS, events=[event_name])
    return chain.get_events_for_contract_topics(
        FARM_ADDRESS, topics, CONTRACT_START_BLOCK, END_BLOCK
    )


def get_farm_staked_events(chain):
    logging.info(f"Fetching Staked events")
    event_name = "Staked"
    topics = chain.get_events_topics(FARM_ADDRESS, events=[event_name])
    return chain.get_events_for_contract_topics(
        FARM_ADDRESS, topics, CONTRACT_START_BLOCK, END_BLOCK
    )


def get_all_farm_wallets(chain):
    logging.info(f"Fetching all farm wallets")
    farm_staked_events = get_farm_staked_events(chain)
    return set(event["args"]["user"].lower() for event in farm_staked_events)


def get_boosted_rewards_wallets():
    logging.info(f"Fetching all boosted rewards wallets")
    wallets = set()
    with open("wallets.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")

        for row in reader:
            wallet_address = row["id"].lower()
            wallets.add(wallet_address)
    return wallets


def get_farm_boosted_wallets(chain):
    logging.info(f"Getting unique boosted wallets which are staking in farm")
    farm_wallets = get_all_farm_wallets(chain)
    boosted_wallets = get_boosted_rewards_wallets()

    return farm_wallets.intersection(boosted_wallets)


def get_claimed_balances(chain):
    logging.info(f"Fetching claimed balances")
    ignore_claimed_rewards = defaultdict(Decimal)
    claimed_rewards = defaultdict(Decimal)
    for event in get_rewards_paid_events(chain):
        wallet_address = event["args"]["user"].lower()
        reward = event["args"]["reward"]
        if event["blockNumber"] < START_BLOCK:
            ignore_claimed_rewards[wallet_address] += reward
        else:
            claimed_rewards[wallet_address] += reward
    return ignore_claimed_rewards, claimed_rewards


def get_boosted_wallets_rewards(chain):
    logging.info(f"Fetching wallets rewards")
    ignore_claimed_rewards, claimed_rewards = get_claimed_balances(chain)
    boosted_wallets = get_farm_boosted_wallets(chain)

    calls = []
    for wallet in boosted_wallets:

        calls.append(
            (
                FARM_ADDRESS,
                ["earned(address)(uint256)", wallet],
                [f"{wallet}", None],
            )
        )

    ignore_earned = chain.multicall(calls, block_identifier=START_BLOCK - 1)
    earned = chain.multicall(calls, block_identifier=END_BLOCK)
    total_rewards = 0
    boosted_rewards = defaultdict(Decimal)
    for wallet in boosted_wallets:
        rewards = (
            claimed_rewards[wallet]
            + earned[wallet]
            - (ignore_claimed_rewards[wallet] + ignore_earned[wallet])
        )
        boosted_rewards[wallet] = rewards
        total_rewards += rewards

    return boosted_rewards, total_rewards


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type 'Decimal' is not JSON serializable")


def generate_json(data):
    logging.info(f"Generating JSON file")
    with open("wallets.json", "w") as f:
        json.dump(dict(data), f, default=decimal_default, indent=4)


def main():

    logging.info("Script started.")

    chain = EthereumMainnetChain(
        rpc=ETHEREUM_RPC_NODE,
        api_key=ETHERSCAN_API_KEY,
        abis_path="abis/",
        step=1000000,
    )

    boosted_rewards, total_rewards = get_boosted_wallets_rewards(chain)

    generate_json(boosted_rewards)

    logging.info(f"Total Rewards: {total_rewards}")
    logging.info("Script finished.")


if __name__ == "__main__":
    main()
