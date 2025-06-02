import os
import sys
import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
from typing import List
import aiohttp
from aiohttp_socks import ProxyConnector

# Initialize colorama
init(autoreset=True)

# Constants
SOMNIA_TESTNET_RPC_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network/tx/0x"
WSTT_CONTRACT = "0x4A3BC48C156384f9564Fd65A53a2f3D534D8f2b7"
IP_CHECK_URL = "https://api.ipify.org?format=json"
BORDER_WIDTH = 80
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

# Configuration
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [60, 180],
    "PAUSE_BETWEEN_SWAPS": [10, 30],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001,  # STT for gas
}

# Contract ABI
contract_abi = [
    {"constant": False, "inputs": [], "name": "deposit", "outputs": [], "payable": True, "stateMutability": "payable", "type": "function"},
    {"constant": False, "inputs": [{"name": "wad", "type": "uint256"}], "name": "withdraw", "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'WRAP STT - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallet': 'XỬ LÝ VÍ',
        'checking_balance': 'Kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} {symbol} < {required:.6f} {symbol}',
        'preparing_tx': 'Chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'wrap_success': 'Wrap {amount} STT → WSTT thành công!',
        'unwrap_success': 'Unwrap {amount} WSTT → STT thành công!',
        'failure': 'Thất bại',
        'address': 'Địa chỉ',
        'amount': 'Số dư',
        'gas': 'Gas',
        'gas_price': 'Gas Price',
        'total_cost': 'Total Cost',
        'block': 'Khối',
        'balance': 'Số dư: {stt:.6f} STT | WSTT: {wstt:.6f}',
        'balance_info': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'connect_success': 'Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'gas_estimation_failed': 'Không thể ước lượng gas: {error}',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': 'Giao dịch bị từ chối bởi hợp đồng hoặc mạng: {error}',
        'input_amount': 'Nhập số STT (0.000001 - 999): ',
        'input_error': 'Số phải từ 0.000001 đến 999 / Nhập lại số hợp lệ!',
        'cycles': 'SỐ VÒNG LẶP',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'timeout': '⏰ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'wallet_failed': 'Ví {profile_num} thất bại: {error}',
    },
    'en': {
        'title': 'WRAP STT - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallet': 'PROCESSING WALLET',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} {symbol} < {required:.6f} {symbol}',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'wrap_success': 'Successfully wrapped {amount} STT → WSTT!',
        'unwrap_success': 'Successfully unwrapped {amount} WSTT → STT!',
        'failure': 'Failed',
        'address': 'Address',
        'amount': 'Balance',
        'gas': 'Gas',
        'gas_price': 'Gas Price',
        'total_cost': 'Total Cost',
        'block': 'Block',
        'balance': 'Balance: {stt:.6f} STT | WSTT: {wstt:.6f}',
        'balance_info': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'connect_success': 'Success: Connected to Somnia Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'gas_estimation_failed': 'Failed to estimate gas: {error}',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': 'Transaction rejected by contract or network: {error}',
        'input_amount': 'Enter STT amount (0.000001 - 999): ',
        'input_error': 'Amount must be 0.000001-999 / Enter a valid number!',
        'cycles': 'NUMBER OF CYCLES',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds, check on explorer',
        'wallet_failed': 'Wallet {profile_num} failed: {error}',
    }
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}", flush=True)
    print(f"{color}│{padded_text}│{Style.RESET_ALL}", flush=True)
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}", flush=True)

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}", flush=True)

def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}{message}{Style.RESET_ALL}", flush=True)

def display_all_wallets_balances(w3: Web3, private_keys: List[str], language: str = 'en'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {'STT':<10} | {'WSTT':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10} | {'-' * 10}{Style.RESET_ALL}")
    
    contract = w3.eth.contract(address=Web3.to_checksum_address(WSTT_CONTRACT), abi=contract_abi)
    for i, key in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        stt_balance = check_balance(w3, address, None, language)
        wstt_balance = check_balance(w3, address, contract, language)
        print(f"{Fore.YELLOW}  {i:<6} | {stt_balance:>10.6f} | {wstt_balance:>10.6f}{Style.RESET_ALL}")
    
    print()

def display_token_balances(w3: Web3, address: str, contract, language: str = 'en'):
    stt_balance = check_balance(w3, address, None, language)
    wstt_balance = check_balance(w3, address, contract, language)
    print_message(f"    - {LANG[language]['balance'].format(stt=stt_balance, wstt=wstt_balance)}", Fore.YELLOW)

# Utility functions
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}", flush=True)
            with open(file_path, 'w') as f:
                f.write("# Add private keys here, one per line\n# Example: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
            sys.exit(1)
        
        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append(key)
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}{Style.RESET_ALL}", flush=True)
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}", flush=True)
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}", flush=True)
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}", flush=True)
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port or http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not line.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}", flush=True)
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}", flush=True)
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}", flush=True)
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'en') -> str:
    try:
        if proxy:
            if proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                connector = ProxyConnector.from_url(proxy)
            else:
                parts = proxy.split(':')
                if len(parts) == 4:  # host:port:user:pass
                    proxy_url = f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                    connector = ProxyConnector.from_url(proxy_url)
                elif len(parts) == 3 and '@' in proxy:  # user:pass@host:port
                    connector = ProxyConnector.from_url(f"socks5://{proxy}")
                else:
                    return LANG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return LANG[language]['unknown']
    except Exception as e:
        return LANG[language]['unknown']

def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(SOMNIA_TESTNET_RPC_URL))
        if not w3.is_connected():
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}", flush=True)
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} │ Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}", flush=True)
        return w3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}", flush=True)
        sys.exit(1)

async def wait_for_receipt(w3: Web3, tx_hash: str, max_wait_time: int = 180, language: str = 'en'):
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt
        except Exception:
            pass
        
        elapsed_time = asyncio.get_event_loop().time() - start_time
        if elapsed_time > max_wait_time:
            return None
        
        await asyncio.sleep(5)

def check_balance(w3: Web3, address: str, contract=None, language: str = 'en') -> float:
    if contract is None:  # Native STT
        try:
            balance = w3.eth.get_balance(address)
            return float(w3.from_wei(balance, 'ether'))
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}", flush=True)
            return -1
    else:
        try:
            balance = contract.functions.balanceOf(address).call()
            decimals = contract.functions.decimals().call()
            return balance / (10 ** decimals)
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}", flush=True)
            return -1

async def wrap_stt(w3: Web3, private_key: str, amount: int, proxy: str, language: str) -> bool:
    account = Account.from_key(private_key)
    sender_address = account.address
    contract = w3.eth.contract(address=Web3.to_checksum_address(WSTT_CONTRACT), abi=contract_abi)
    
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print_message(f"  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)

            print_message(f"  > {LANG[language]['checking_balance']}", Fore.CYAN)
            eth_balance = check_balance(w3, sender_address, None, language)
            wstt_balance = check_balance(w3, sender_address, contract, language)
            print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
            if eth_balance < CONFIG['MINIMUM_BALANCE'] or eth_balance < w3.from_wei(amount, 'ether'):
                print_message(f"  ✖ {LANG[language]['insufficient_balance'].format(balance=eth_balance, symbol='STT', required=max(CONFIG['MINIMUM_BALANCE'], w3.from_wei(amount, 'ether')))}", Fore.RED)
                return False

            print_message(f"  > {LANG[language]['preparing_tx']}", Fore.CYAN)
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
            tx_params = {
                'from': sender_address,
                'to': Web3.to_checksum_address(WSTT_CONTRACT),
                'value': amount,
                'data': '0xd0e30db0',
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': gas_price
            }

            try:
                estimated_gas = w3.eth.estimate_gas(tx_params)
                gas_limit = int(estimated_gas * 1.2)
                tx_params['gas'] = gas_limit
                print_message(f"    Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}", Fore.YELLOW)
            except Exception as e:
                tx_params['gas'] = 30000
                print_message(f"  ⚠ {LANG[language]['gas_estimation_failed'].format(error=str(e))}. {LANG[language]['default_gas_used'].format(gas=30000)}", Fore.YELLOW)

            print_message(f"  > {LANG[language]['sending_tx']}", Fore.CYAN)
            signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=180, language=language)
            if receipt is None:
                print_message(f"  {LANG[language]['timeout'].format(timeout=180)} - Tx: {tx_link}", Fore.YELLOW)
                return False
            elif receipt.status == 1:
                total_cost = w3.from_wei(receipt['gasUsed'] * tx_params['gasPrice'], 'ether')
                print_message(f"  ✔ {LANG[language]['wrap_success'].format(amount=w3.from_wei(amount, 'ether'))} │ Tx: {tx_link}", Fore.GREEN)
                print_message(f"    - {LANG[language]['address']}: {sender_address}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['gas_price']}: {w3.from_wei(tx_params['gasPrice'], 'gwei'):.6f} Gwei", Fore.YELLOW)
                print_message(f"    - {LANG[language]['total_cost']}: {total_cost:.12f} STT", Fore.YELLOW)
                eth_balance = check_balance(w3, sender_address, None, language)
                wstt_balance = check_balance(w3, sender_address, contract, language)
                print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
                return True
            else:
                print_message(f"  ✖ {LANG[language]['failure']} │ Tx: {tx_link}", Fore.RED)
                print_message(f"    - {LANG[language]['tx_rejected'].format(error='Unknown')}", Fore.RED)
                eth_balance = check_balance(w3, sender_address, None, language)
                wstt_balance = check_balance(w3, sender_address, contract, language)
                print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
                return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print_message(f"  ✖ {LANG[language]['failure']}: {str(e)} - Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
                print_message(f"  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
                continue
            print_message(f"  ✖ {LANG[language]['failure']}: {str(e)} - Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
            eth_balance = check_balance(w3, sender_address, None, language)
            wstt_balance = check_balance(w3, sender_address, contract, language)
            print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
            return False
    return False

async def unwrap_wstt(w3: Web3, private_key: str, amount: int, proxy: str, language: str) -> bool:
    account = Account.from_key(private_key)
    sender_address = account.address
    contract = w3.eth.contract(address=Web3.to_checksum_address(WSTT_CONTRACT), abi=contract_abi)
    
    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print_message(f"  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)

            print_message(f"  > {LANG[language]['checking_balance']}", Fore.CYAN)
            eth_balance = check_balance(w3, sender_address, None, language)
            wstt_balance = check_balance(w3, sender_address, contract, language)
            print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
            if eth_balance < CONFIG['MINIMUM_BALANCE']:
                print_message(f"  ✖ {LANG[language]['insufficient_balance'].format(balance=eth_balance, symbol='STT', required=CONFIG['MINIMUM_BALANCE'])}", Fore.RED)
                return False
            if wstt_balance * (10 ** 18) < amount:
                print_message(f"  ✖ {LANG[language]['insufficient_balance'].format(balance=wstt_balance, symbol='WSTT', required=w3.from_wei(amount, 'ether'))}", Fore.RED)
                return False

            print_message(f"  > {LANG[language]['preparing_tx']}", Fore.CYAN)
            nonce = w3.eth.get_transaction_count(sender_address)
            gas_price = int(w3.eth.gas_price * random.uniform(1.03, 1.1))
            amount_hex = format(amount, '064x')
            tx_data = f"0x2e1a7d4d{amount_hex}"
            tx_params = {
                'from': sender_address,
                'to': Web3.to_checksum_address(WSTT_CONTRACT),
                'data': tx_data,
                'nonce': nonce,
                'chainId': CHAIN_ID,
                'gasPrice': gas_price
            }

            try:
                estimated_gas = w3.eth.estimate_gas(tx_params)
                gas_limit = int(estimated_gas * 1.2)
                tx_params['gas'] = gas_limit
                print_message(f"    Gas ước lượng: {estimated_gas} | Gas limit sử dụng: {gas_limit}", Fore.YELLOW)
            except Exception as e:
                tx_params['gas'] = 30000
                print_message(f"  ⚠ {LANG[language]['gas_estimation_failed'].format(error=str(e))}. {LANG[language]['default_gas_used'].format(gas=30000)}", Fore.YELLOW)

            print_message(f"  > {LANG[language]['sending_tx']}", Fore.CYAN)
            signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            receipt = await wait_for_receipt(w3, tx_hash, max_wait_time=180, language=language)
            if receipt is None:
                print_message(f"  {LANG[language]['timeout'].format(timeout=180)} - Tx: {tx_link}", Fore.YELLOW)
                return False
            elif receipt.status == 1:
                total_cost = w3.from_wei(receipt['gasUsed'] * tx_params['gasPrice'], 'ether')
                print_message(f"  ✔ {LANG[language]['unwrap_success'].format(amount=w3.from_wei(amount, 'ether'))} │ Tx: {tx_link}", Fore.GREEN)
                print_message(f"    - {LANG[language]['address']}: {sender_address}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
                print_message(f"    - {LANG[language]['gas_price']}: {w3.from_wei(tx_params['gasPrice'], 'gwei'):.6f} Gwei", Fore.YELLOW)
                print_message(f"    - {LANG[language]['total_cost']}: {total_cost:.12f} STT", Fore.YELLOW)
                eth_balance = check_balance(w3, sender_address, None, language)
                wstt_balance = check_balance(w3, sender_address, contract, language)
                print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
                return True
            else:
                print_message(f"  ✖ {LANG[language]['failure']} │ Tx: {tx_link}", Fore.RED)
                print_message(f"    - {LANG[language]['tx_rejected'].format(error='Unknown')}", Fore.RED)
                eth_balance = check_balance(w3, sender_address, None, language)
                wstt_balance = check_balance(w3, sender_address, contract, language)
                print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
                return False
        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print_message(f"  ✖ {LANG[language]['failure']}: {str(e)} - Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
                print_message(f"  ⚠ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
                continue
            print_message(f"  ✖ {LANG[language]['failure']}: {str(e)} - Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}", Fore.RED)
            eth_balance = check_balance(w3, sender_address, None, language)
            wstt_balance = check_balance(w3, sender_address, contract, language)
            print_message(f"    - {LANG[language]['balance'].format(stt=eth_balance, wstt=wstt_balance)}", Fore.YELLOW)
            return False
    return False

async def process_wallet(index: int, private_key: str, proxy: str, w3: Web3, amount: float, cycles: int, language: str) -> int:
    total_wallets = CONFIG.get('TOTAL_WALLETS', 1)
    wallet_index = index + 1
    
    print_border(f"{LANG[language]['processing_wallet']} {wallet_index}/{total_wallets}", Fore.MAGENTA)
    print()
    
    account = Account.from_key(private_key)
    print_message(f"  {LANG[language]['address']}: {account.address}", Fore.YELLOW)
    print()
    
    successful_txs = 0
    total_txs = cycles * 2
    amount_wei = int(amount * 10 ** 18)
    
    try:
        for cycle in range(1, cycles + 1):
            print_message(f"  > Cycle {cycle}/{cycles}", Fore.CYAN)
            
            # Wrap STT to WSTT
            if await wrap_stt(w3, private_key, amount_wei, proxy, language):
                successful_txs += 1
            
            print()
            delay = random.uniform(CONFIG['PAUSE_BETWEEN_SWAPS'][0], CONFIG['PAUSE_BETWEEN_SWAPS'][1])
            print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
            await asyncio.sleep(delay)
            print()
            
            # Unwrap WSTT to STT
            if await unwrap_wstt(w3, private_key, amount_wei, proxy, language):
                successful_txs += 1
            
            if cycle < cycles:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_SWAPS'][0], CONFIG['PAUSE_BETWEEN_SWAPS'][1])
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)
            print()
        
        print_separator(Fore.GREEN if successful_txs > 0 else Fore.RED)
        return successful_txs
    except Exception as e:
        print_message(f"  ✖ {LANG[language]['wallet_failed'].format(profile_num=wallet_index, error=str(e))}", Fore.RED)
        print_separator(Fore.RED)
        return 0

async def run_wrapquick(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    proxies = load_proxies('proxies.txt', language)
    random.shuffle(private_keys)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}", flush=True)
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    # Display balance table for all wallets
    display_all_wallets_balances(w3, private_keys, language)
    print_separator()

    # Get amount from user
    while True:
        print_border(LANG[language]['input_amount'], Fore.YELLOW)
        try:
            amount = float(input(f"{Fore.GREEN}  ➤ {Style.RESET_ALL}"))
            if 0.000001 <= amount <= 999:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['input_error']}{Style.RESET_ALL}", flush=True)
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['input_error']}{Style.RESET_ALL}", flush=True)

    # Get number of cycles
    while True:
        try:
            print_border(LANG[language]['cycles'], Fore.YELLOW)
            cycles = input(f"{Fore.GREEN}  ➤ {'Nhập số (mặc định 1): ' if language == 'vi' else 'Enter number (default 1): '}{Style.RESET_ALL}")
            cycles = int(cycles) if cycles else 1
            if cycles > 0:
                break
            print(f"{Fore.RED}  ✖ {'Số phải lớn hơn 0 / Number must be > 0'}{Style.RESET_ALL}", flush=True)
        except ValueError:
            print(f"{Fore.RED}  ✖ {'Nhập số hợp lệ / Enter a valid number'}{Style.RESET_ALL}", flush=True)

    print_separator()
    total_txs = len(private_keys) * cycles * 2
    successful_txs = 0
    CONFIG['TOTAL_WALLETS'] = len(private_keys)
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], len(private_keys))

    async def limited_task(index, private_key, proxy):
        nonlocal successful_txs
        async with semaphore:
            result = await process_wallet(index, private_key, proxy, w3, amount, cycles, language)
            successful_txs += result
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    tasks = []
    for i, private_key in enumerate(private_keys):
        proxy = proxies[i % len(proxies)] if proxies else None
        tasks.append(limited_task(i, private_key, proxy))

    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_txs, total=total_txs)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_wrapquick('en'))
