import os
import sys
import asyncio
import random
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network/tx/0x"
PING_CONTRACT = Web3.to_checksum_address("0x33E7fAB0a8a5da1A923180989bD617c9c2D1C493")
IP_CHECK_URL = "https://api.ipify.org?format=json"
MAX_WAIT_TIME = 180  # Timeout 3 minutes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001,  # STT
    "DEFAULT_GAS": 500000
}

# Token information
TOKENS = [
    {"symbol": "PING", "address": PING_CONTRACT, "amount": 1000, "decimals": 18}
]

# PING contract ABI
PING_ABI = [
    {
        "inputs": [],
        "name": "mint",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "isMinter",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': '✨ MINT $PING - SOMNIA TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'already_minted': '❌ Ví này đã mint $PING rồi! Vui lòng không thử lại.',
        'insufficient_balance': 'Số dư không đủ (cần ít nhất {required:.6f} STT cho giao dịch)',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'waiting_tx': 'Đang đợi xác nhận giao dịch...',
        'success': '✅ Mint thành công {amount} {symbol}!',
        'failure': '❌ Mint {symbol} thất bại',
        'timeout': '⚠ Giao dịch chưa nhận được receipt sau {timeout} giây, kiểm tra trên explorer...',
        'address': 'Địa chỉ ví',
        'amount': 'Số dư {symbol}',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư STT',
        'balance_info': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': '❌ Không thể kết nối với RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'debugging_tx': 'Đang debug giao dịch...',
        'gas_estimation_failed': '⚠ Không thể ước lượng gas',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': '⚠ Giao dịch bị từ chối bởi hợp đồng hoặc mạng',
        'stop_wallet': 'Dừng xử lý ví {wallet}: Quá nhiều giao dịch thất bại liên tiếp',
        'balance_check_failed': '⚠ Không kiểm tra được số dư {symbol}',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'invalid_contract_data': '⚠ Hợp đồng từ chối giao dịch. Kiểm tra dữ liệu giao dịch hoặc trạng thái hợp đồng tại https://shannon-explorer.somnia.network/address/0x9beaA0016c22B646Ac311Ab171270B0ECf23098F'
    },
    'en': {
        'title': '✨ MINT $PING - SOMNIA TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'already_minted': '❌ Wallet already minted $PING! Please do not try again.',
        'insufficient_balance': 'Insufficient balance (need at least {required:.6f} STT for transaction)',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'waiting_tx': 'Waiting for transaction confirmation...',
        'success': '✅ Successfully minted {amount} {symbol}!',
        'failure': '❌ Failed to mint {symbol}',
        'timeout': '⚠ Transaction receipt not received after {timeout} seconds, check on explorer...',
        'address': 'Wallet address',
        'amount': '{symbol} Balance',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'STT Balance',
        'balance_info': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Somnia Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': '⚠ Warning: Line',
        'debugging_tx': 'Debugging transaction...',
        'gas_estimation_failed': '⚠ Failed to estimate gas',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': '⚠ Transaction rejected by contract or network',
        'stop_wallet': 'Stopping wallet {wallet}: Too many consecutive failed transactions',
        'balance_check_failed': '⚠ Failed to check {symbol} balance',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'invalid_contract_data': '⚠ Contract rejected transaction. Check transaction data or contract status at https://shannon-explorer.somnia.network/address/0x9beaA0016c22B646Ac311Ab171270B0ECf23098F'
    }
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_wallets_summary(private_keys: list, language: str = 'en'):
    print_border(
        LANG[language]['processing_wallets'].format(count=len(private_keys)),
        Fore.MAGENTA
    )
    print()

def display_all_wallets_balances(w3: Web3, private_keys: list, language: str = 'en'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {'STT':<10} | {'PING':<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10} | {'-' * 10}{Style.RESET_ALL}")
    
    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        eth_balance = check_balance(w3, address, "native", 18, language)
        ping_balance = check_balance(w3, address, TOKENS[0]["address"], TOKENS[0]["decimals"], language)
        print(f"{Fore.YELLOW}  {i:<6} | {eth_balance:>10.6f} | {ping_balance:>10.6f}{Style.RESET_ALL}")
    
    print()

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

def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
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
                        valid_keys.append((i, key))
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key[:10]}...{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
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
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
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
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}{Style.RESET_ALL}")
        return LANG[language]['unknown']

def connect_web3(language: str = 'en'):
    try:
        w3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not w3.is_connected():
            print(f"{Fore.RED}  ✖ {LANG[language]['connect_error']}{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ {LANG[language]['connect_success']} │ Chain ID: {w3.eth.chain_id}{Style.RESET_ALL}")
        return w3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['web3_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def check_balance(w3: Web3, address: str, token_address: str, decimals: int, language: str = 'en') -> float:
    if token_address == "native":
        try:
            balance = w3.eth.get_balance(address)
            return float(w3.from_wei(balance, 'ether'))
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['balance_check_failed'].format(symbol='STT')}: {str(e)}{Style.RESET_ALL}")
            return -1
    else:
        contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=PING_ABI)
        try:
            balance = contract.functions.balanceOf(address).call()
            return balance / (10 ** decimals)
        except Exception as e:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['balance_check_failed'].format(symbol='PING')}: {str(e)}{Style.RESET_ALL}")
            return -1

def debug_transaction(w3: Web3, tx_params: dict, language: str = 'en') -> str:
    try:
        print(f"{Fore.CYAN}  > {LANG[language]['debugging_tx']}{Style.RESET_ALL}")
        w3.eth.call(tx_params)
        return "Transaction expected to succeed"
    except Exception as e:
        return f"Transaction expected to fail: {str(e)}"

async def mint_token(w3: Web3, private_key: str, wallet_index: int, token: dict, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address
    contract = w3.eth.contract(address=Web3.to_checksum_address(token['address']), abi=PING_ABI)

    # Check if wallet has already minted
    token_balance = check_balance(w3, sender_address, token['address'], token['decimals'], language)
    if token_balance > 0:
        print(f"{Fore.RED}  ✖ {LANG[language]['already_minted']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  - {LANG[language]['amount'].format(symbol=token['symbol'])}: {token_balance:.6f} {token['symbol']}{Style.RESET_ALL}")
        return False

    for attempt in range(CONFIG['MAX_RETRIES']):
        try:
            # Display proxy info
            public_ip = await get_proxy_ip(proxy, language)
            proxy_display = proxy if proxy else LANG[language]['no_proxy']
            print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
            eth_balance = float(w3.from_wei(w3.eth.get_balance(sender_address), 'ether'))
            print(f"{Fore.YELLOW}  - {LANG[language]['balance']}: {eth_balance:.6f} STT{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  - {LANG[language]['amount'].format(symbol=token['symbol'])}: {token_balance if token_balance >= 0 else 'N/A'} {token['symbol']}{Style.RESET_ALL}")

            if eth_balance < CONFIG['MINIMUM_BALANCE']:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'])}{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
            nonce = w3.eth.get_transaction_count(sender_address, 'pending')
            tx_params = contract.functions.mint().build_transaction({
                'nonce': nonce,
                'from': sender_address,
                'chainId': CHAIN_ID,
                'gasPrice': int(w3.eth.gas_price * random.uniform(1.03, 1.1)),
                'value': 0
            })

            try:
                estimated_gas = w3.eth.estimate_gas(tx_params)
                gas_limit = int(estimated_gas * 1.2)
                tx_params['gas'] = gas_limit
                print(f"{Fore.YELLOW}  - Gas estimated: {estimated_gas} | Gas limit used: {gas_limit}{Style.RESET_ALL}")
            except Exception as e:
                tx_params['gas'] = CONFIG['DEFAULT_GAS']
                print(f"{Fore.YELLOW}  - {LANG[language]['gas_estimation_failed']}: {str(e)}. {LANG[language]['default_gas_used'].format(gas=CONFIG['DEFAULT_GAS'])}{Style.RESET_ALL}")

            total_required = tx_params['gas'] * tx_params['gasPrice']
            total_required_eth = float(w3.from_wei(total_required, 'ether'))
            if eth_balance < total_required_eth:
                print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(required=total_required_eth)}{Style.RESET_ALL}")
                return False

            debug_result = debug_transaction(w3, tx_params, language)
            print(f"{Fore.YELLOW}  - {debug_result}{Style.RESET_ALL}")
            if "fail" in debug_result.lower():
                print(f"{Fore.RED}  ✖ {LANG[language]['invalid_contract_data']}{Style.RESET_ALL}")
                return False

            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
            signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"

            print(f"{Fore.CYAN}  > {LANG[language]['waiting_tx']}{Style.RESET_ALL}")
            receipt = await wait_for_receipt(w3, tx_hash, MAX_WAIT_TIME, language)

            if receipt is None:
                print(f"{Fore.YELLOW}  {LANG[language]['timeout'].format(timeout=MAX_WAIT_TIME)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - Tx: {tx_link}{Style.RESET_ALL}")
                return True
            elif receipt.status == 1:
                token_balance = check_balance(w3, sender_address, token['address'], token['decimals'], language)
                print(f"{Fore.GREEN}  ✔ {LANG[language]['success'].format(amount=token['amount'], symbol=token['symbol'])} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['balance']}: {eth_balance:.6f} STT{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['amount'].format(symbol=token['symbol'])}: {token_balance if token_balance >= 0 else 'N/A'} {token['symbol']}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(symbol=token['symbol'])} | Tx: {tx_link}{Style.RESET_ALL}")
                print(f"{Fore.RED}  - {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
                return False

        except Exception as e:
            if attempt < CONFIG['MAX_RETRIES'] - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(symbol=token['symbol'])}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  - {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_contract_data']}: {str(e)} | Tx: {tx_link if 'tx_hash' in locals() else 'Not sent'}{Style.RESET_ALL}")
            return False

async def wait_for_receipt(w3: Web3, tx_hash: str, max_wait_time: int, language: str = 'en'):
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

async def run_mintping(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    proxies = load_proxies('proxies.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    # Display balance table
    display_all_wallets_balances(w3, private_keys, language)
    print_separator()

    successful_mints = 0
    total_mints = len(private_keys) * len(TOKENS)
    failed_attempts = 0
    CONFIG['TOTAL_WALLETS'] = len(private_keys)
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], len(private_keys))

    print_wallets_summary(private_keys, language)

    random.shuffle(private_keys)
    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    async def limited_task(index, profile_num, private_key, proxy):
        nonlocal successful_mints, failed_attempts
        async with semaphore:
            account = Account.from_key(private_key)
            print(f"{Fore.YELLOW}Processing wallet: {account.address} ({index + 1}/{len(private_keys)}){Style.RESET_ALL}")
            print()
            for token in TOKENS:
                if await mint_token(w3, private_key, profile_num, token, proxy, language):
                    successful_mints += 1
                    failed_attempts = 0
                else:
                    failed_attempts += 1
                    if failed_attempts >= 3:
                        print(f"{Fore.RED}  ✖ {LANG[language]['stop_wallet'].format(wallet=profile_num)}{Style.RESET_ALL}")
                        return
                await asyncio.sleep(random.uniform(5, 10))
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
            print_separator(Fore.GREEN if successful_mints > 0 else Fore.RED)

    tasks = []
    for i, (profile_num, private_key) in enumerate(private_keys):
        proxy = proxies[i % len(proxies)] if proxies else None
        tasks.append(limited_task(i, profile_num, private_key, proxy))

    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        f"{LANG[language]['completed'].format(successful=successful_mints, total=total_mints)}",
        Fore.GREEN
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_mintping('vi'))
