# Somnia Testnet Automation Scripts

This repository contains a collection of Python scripts designed to automate various tasks on the Somnia Testnet, including faucet claiming, token minting, swapping, contract deployment, transaction sending, and memecoin trading. These scripts are integrated with a central `main.py` file for streamlined execution, supporting multiple private keys and a user-friendly CLI interface.

## Features Overview

### General Features

- **Multi-Account Support**: Reads private keys from `pvkey.txt` to perform actions across multiple accounts.
- **Colorful CLI**: Uses `colorama` for visually appealing output with colored text and borders.
- **Asynchronous Execution**: Built with `asyncio` for efficient blockchain interactions.
- **Error Handling**: Comprehensive error catching for blockchain transactions and RPC issues.
- **Bilingual Support**: Supports both Vietnamese and English output based on user selection.

### Included Scripts

#### 1. `faucetstt.py` - Faucet Token $STT
- **Description**: Claims $STT tokens from the Somnia Testnet faucet via API.
- **Features**:
  - Reads addresses from `addressFaucet.txt`.
  - Supports proxy usage from `proxies.txt` (optional).
  - Displays public IP via proxy and API response.
  - Random delays (5-15 seconds) between requests.
- **Usage**: Select from `main.py` menu; requires `addressFaucet.txt`.

#### 2. `sendtx.py` - Send Transactions
- **Description**: Sends transactions on Somnia Testnet, either to random addresses or from `address.txt`.
- **Features**:
  - User-configurable transaction count and STT amount (default: 0.000001 STT).
  - Random delays (1-3 seconds) between transactions.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu, input transaction count and amount.

#### 3. `deploytoken.py` - Deploy ERC-20 Token Contract
- **Description**: Deploys a custom ERC-20 token smart contract on Somnia Testnet.
- **Features**:
  - User inputs for token name, symbol, decimals (default: 18), and total supply.
  - Compiles and deploys using `solcx` (Solidity 0.8.22).
  - Saves deployed contract addresses to `contractERC20.txt`.
  - Random delays (10-30 seconds) between deployments.
- **Usage**: Select from `main.py` menu, provide token details.

#### 4. `sendtoken.py` - Send ERC-20 Tokens
- **Description**: Transfers ERC-20 tokens to random addresses or from `addressERC20.txt`.
- **Features**:
  - User inputs for contract address and amount.
  - Random delays (10-30 seconds) between transfers.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu, input contract address and amount.

#### 5. `deploynft.py` - Deploy NFT Contract
- **Description**: Deploys an NFT smart contract on Somnia Testnet.
- **Features**:
  - Automates NFT contract deployment for multiple wallets.
  - Displays deployed contract address.
- **Usage**: Select from `main.py` menu.

#### 6. `mintpong.py` - Mint $PONG
- **Description**: Mints 1000 $PONG tokens on Somnia Testnet.
- **Features**:
  - Random delays (100-300 seconds) between mints.
  - Checks STT balance before minting (minimum 0.001 STT).
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu.

#### 7. `mintping.py` - Mint $PING
- **Description**: Mints $PING tokens on Somnia Testnet.
- **Features**:
  - Similar functionality to `mintpong.py` with $PING token specifics.
  - Random delays (100-300 seconds) between mints.
- **Usage**: Select from `main.py` menu.

#### 8. `swappong.py` - Swap $PONG to $PING
- **Description**: Swaps $PONG to $PING on Somnia Testnet using a swap router.
- **Features**:
  - User inputs for swap amount and number of swaps.
  - Approves and swaps tokens with random delays (10-30 seconds between swaps, 100-300 seconds between wallets).
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu, input swap amount and times.

#### 9. `swapping.py` - Swap $PING to $PONG
- **Description**: Swaps $PING to $PONG on Somnia Testnet using a swap router.
- **Features**:
  - Similar to `swappong.py` but in reverse direction.
  - User-configurable swap amount and cycles.
- **Usage**: Select from `main.py` menu, input swap amount and times.

#### 10. `conftnft.py` - Mint Community NFT (CoNFT)
- **Description**: Mints the Community Member of Somnia (CMS - CoNFT) NFT for 0.1 STT.
- **Features**:
  - Checks if wallet has already minted (via `balanceOf`).
  - Verifies STT balance (minimum 0.1 STT).
  - Random delays (10-30 seconds) between mints.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu.

#### 11. `mintsusdt.py` - Mint 1000 sUSDT
- **Description**: Mints 1000 sUSDT tokens on Somnia Testnet.
- **Features**:
  - Checks if wallet has already minted to avoid duplicates.
  - Random delays (10-30 seconds) between mints.
  - Detailed transaction logs with explorer links.
- **Usage**: Select from `main.py` menu.

#### 12. `buymeme.py` - Buy Memecoins
- **Description**: Buys memecoins (SOMI, SMSM, SMI) with sUSDT on Somnia Testnet.
- **Features**:
  - User selects token (SOMI, SMSM, or SMI) and sUSDT amount.
  - Approves and swaps with 5% slippage tolerance.
  - Displays balance, price, and market cap.
  - Random delays (10-30 seconds) between buys.
- **Usage**: Select from `main.py` menu, choose token and amount.

#### 13. `sellmeme.py` - Sell Memecoins
- **Description**: Sells memecoins (SOMI, SMSM, SMI) for sUSDT on Somnia Testnet.
- **Features**:
  - User selects token and amount to sell.
  - Approves and executes swaps with random delays (10-30 seconds).
  - Displays balance, price, and market cap.
- **Usage**: Select from `main.py` menu, choose token and amount.

## Prerequisites
- **Python 3.8+**
- **Dependencies**: Install via `pip install -r requirements.txt` (ensure `web3.py`, `colorama`, `aiohttp`, `aiohttp_socks`, `solcx`, and `eth-account` are included).
- **pvkey.txt**: Add private keys (one per line) for wallet automation.
- **address.txt** / **addressERC20.txt** / **addressFaucet.txt** / **proxies.txt**: Optional files for specifying addresses or proxies.

## Installation

1. **Clone this repository:**
- Open cmd or Shell, then run the command:
```sh
git clone https://github.com/thog9/Somnia-testnet.git
```
```sh
cd Somnia-testnet
```
2. **Install Dependencies:**
- Open cmd or Shell, then run the command:
```sh
pip install -r requirements.txt
```
3. **Prepare Input Files:**
- Open the `pvkey.txt`: Add your private keys (one per line) in the root directory.
```sh
nano pvkey.txt 
```
- Open the `address.txt`(optional): Add recipient addresses (one per line) for `sendtx.py`, `faucetstt.py`, `deploytoken.py`, `sendtoken.py`, `proxies.txt`.
```sh
nano address.txt 
```
```sh
nano addressERC20.txt
```
```sh
nano addressFaucet.txt
```
```sh
nano proxies.txt
```
```sh
nano contractERC20.txt
```
4. **Run:**
- Open cmd or Shell, then run command:
```sh
python main.py
```
- Choose a language (Vietnamese/English).

## Contact

- **Telegram**: [thog099](https://t.me/thog099)
- **Channel**: [thogairdrops](https://t.me/thogairdrops)
- **Replit**: Thog
