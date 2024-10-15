
# SKY Airdrop Boosted Rewards Calculation

This script calculates the boosted rewards for SKY airdrop participants who have staked in a farming contract. It uses Ethereum blockchain data to fetch event logs for rewards claimed by wallets and identifies wallets eligible for boosted rewards.

## Prerequisites

### Python Dependencies

Make sure you have the following Python dependencies installed:

- `python-dotenv`
- `chain_harvester`
- `decimal`
- `json`
- `argparse`
- `csv`
- `logging`

You can install these dependencies by running:

```bash
pip install -r requirements.txt
```

### Create `.env` File

The script relies on environment variables for interacting with Ethereum nodes and the Etherscan API. You need to create a `.env` file in the root directory of the project. Use the `.env.example` as a reference.

**.env.example:**

```plaintext
ETHEREUM_RPC_NODE=
ETHERSCAN_API_KEY=
```

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then, add your Ethereum RPC node URL and Etherscan API key to the `.env` file:

```plaintext
ETHEREUM_RPC_NODE=your_ethereum_rpc_url
ETHERSCAN_API_KEY=your_etherscan_api_key
```

## Script Configuration

### Parameters to Modify

Before running the script, you may need to modify the following parameters inside the `main.py` file:

- **`END_BLOCK`**: The `END_BLOCK` is set to a specific Ethereum block height. You will need to update it with the block number you want to check the rewards for.

```python
END_BLOCK = 20969822  # Update this value when the final block is known
```

## Running the Script

Once the `.env` file is set and the parameters are configured, you can run the script by executing:

```bash
python main.py
```

### Output

- The script will fetch the event data and calculate the boosted rewards for eligible wallets.
- The rewards data will be saved as `wallets.json` in the current directory.

## Notes

- **Input Wallets**: The script reads the boosted wallets from a `wallets.csv` file, which should be present in the root directory. The file should contain wallet addresses under the `id` column.
- **Output**: The calculated boosted rewards are saved as `wallets.json`. You can modify the output filename or location in the script if needed.
