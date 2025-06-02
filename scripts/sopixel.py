import os
import sys
import asyncio
import random
import time
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector
from typing import List

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network/tx/0x"
CONTRACT_ADDRESS = Web3.to_checksum_address("0x496eF0E9944ff8c83fa74FeB580f2FB581ecFfFd")
IP_CHECK_URL = "https://api.ipify.org?format=json"
MAX_WAIT_TIME = 180  # Timeout 3 minutes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}
CONFIG = {
    "PAUSE_BETWEEN_ATTEMPTS": [10, 30],
    "PAUSE_BETWEEN_PIXELS": [20, 40],
    "MAX_CONCURRENCY": 5,
    "MAX_RETRIES": 3,
    "MINIMUM_BALANCE": 0.001,  # WSTT
    "PIXEL_VALUE": 0.01,  # 0.01 WSTT per pixel
    "DEFAULT_GAS": 300000
}

# Contract ABI
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "x", "type": "uint256"},
            {"internalType": "uint256", "name": "y", "type": "uint256"},
            {"internalType": "uint24", "name": "color", "type": "uint24"}
        ],
        "name": "colorPixel",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': '✨ SOPIXEL - SOMNIA TESTNET ✨',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallets': '⚙ ĐANG XỬ LÝ {count} VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ: {balance:.6f} WSTT (cần ít nhất {required:.6f})',
        'preparing_tx': 'Đang chuẩn bị giao dịch...',
        'estimating_gas': 'Đang ước lượng gas...',
        'sending_tx': 'Đang gửi giao dịch...',
        'success_pixel': '✅ Tô màu pixel thành công!',
        'failure': '❌ Tô màu pixel thất bại',
        'address': 'Địa chỉ ví',
        'pixel': 'Pixel',
        'color': 'Màu sắc',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư WSTT',
        'balance_info': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} PIXEL THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối với mạng Somnia Testnet',
        'connect_error': '❌ Không thể kết nối với RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ Không tìm thấy tệp pvkey.txt',
        'pvkey_empty': '❌ Không tìm thấy khóa riêng hợp lệ',
        'pvkey_error': '❌ Không thể đọc pvkey.txt',
        'invalid_key': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'gas_estimation_failed': 'Không thể ước tính gas: {error}',
        'default_gas_used': 'Sử dụng gas mặc định: {gas}',
        'tx_rejected': '⚠ Giao dịch bị từ chối bởi hợp đồng hoặc mạng',
        'pixel_count_prompt': '⚛️ Nhập số lượng pixel cần tô màu cho mỗi ví: ',
        'invalid_pixel_count': '❌ Số lượng pixel phải là số nguyên dương',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
    },
    'en': {
        'title': '✨ SOPIXEL - SOMNIA TESTNET ✨',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallets': '⚙ PROCESSING {count} WALLETS',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance: {balance:.6f} WSTT (need at least {required:.6f})',
        'preparing_tx': 'Preparing transaction...',
        'estimating_gas': 'Estimating gas...',
        'sending_tx': 'Sending transaction...',
        'success_pixel': '✅ Successfully colored pixel!',
        'failure': '❌ Failed to color pixel',
        'address': 'Wallet address',
        'pixel': 'Pixel',
        'color': 'Color',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'WSTT Balance',
        'balance_info': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} PIXELS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Somnia Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'gas_estimation_failed': 'Failed to estimate gas: {error}',
        'default_gas_used': 'Using default gas: {gas}',
        'tx_rejected': '⚠ Transaction rejected by contract or network',
        'pixel_count_prompt': '⚛️ Enter the number of pixels to color per wallet: ',
        'invalid_pixel_count': '❌ Pixel count must be a positive integer',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
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

def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}{message}{Style.RESET_ALL}")

def print_wallets_summary(count: int, language: str = 'en'):
    print_border(
        LANG[language]['processing_wallets'].format(count=count),
        Fore.MAGENTA
    )
    print()

def display_all_wallets_balances(w3: Web3, private_keys: List[tuple], language: str = 'en'):
    print_border(LANG[language]['balance_info'], Fore.CYAN)
    print(f"{Fore.CYAN}  Wallet | {LANG[language]['balance']:<10}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {'-' * 6} | {'-' * 10}{Style.RESET_ALL}")
    
    for i, (profile_num, key) in enumerate(private_keys, 1):
        address = Account.from_key(key).address
        balance = check_balance(w3, address, language)
        print(f"{Fore.YELLOW}  {i:<6} | {balance:>10.6f}{Style.RESET_ALL}")
    
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
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}{Style.RESET_ALL}")
        
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
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm proxy vào đây, mỗi proxy trên một dòng\n# Ví dụ: socks5://user:pass@host:port hoặc http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not line.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
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

def check_balance(w3: Web3, address: str, language: str = 'en') -> float:
    try:
        balance = w3.eth.get_balance(address)
        return float(w3.from_wei(balance, 'ether'))
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return -1

async def color_pixel(w3: Web3, private_key: str, wallet_index: int, pixel_count: int, proxy: str = None, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    successful_pixels = 0
    
    nonce = w3.eth.get_transaction_count(sender_address, 'pending')
    
    for i in range(pixel_count):
        print_border(f"Pixel {i+1}/{pixel_count} for Wallet {wallet_index}", Fore.YELLOW)
        print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
        
        public_ip = await get_proxy_ip(proxy, language)
        proxy_display = proxy if proxy else LANG[language]['no_proxy']
        print(f"{Fore.CYAN}  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")
        
        balance = check_balance(w3, sender_address, language)
        required_balance = CONFIG['PIXEL_VALUE'] * (i + 1)
        if balance < required_balance or balance < CONFIG['MINIMUM_BALANCE']:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=balance, required=max(required_balance, CONFIG['MINIMUM_BALANCE']))}{Style.RESET_ALL}")
            break
        
        print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
        x = random.randint(0, 1023)
        y = random.randint(0, 1023)
        color = random.randint(0, 0xFFFFFF)
        
        try:
            latest_block = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.get_block('latest'))
            base_fee = latest_block.get('baseFeePerGas', w3.to_wei('1', 'gwei'))
            priority_fee = w3.to_wei('2', 'gwei')
            if base_fee > w3.to_wei('20', 'gwei'):
                priority_fee = w3.to_wei('3', 'gwei')
            if base_fee > w3.to_wei('50', 'gwei'):
                priority_fee = w3.to_wei('5', 'gwei')
            if base_fee > w3.to_wei('100', 'gwei'):
                priority_fee = w3.to_wei('8', 'gwei')
            max_fee = base_fee + priority_fee + (base_fee // 5)
            
            tx_params = contract.functions.colorPixel(x, y, color).build_transaction({
                'nonce': nonce,
                'from': sender_address,
                'value': w3.to_wei(CONFIG['PIXEL_VALUE'], 'ether'),
                'chainId': CHAIN_ID,
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': priority_fee
            })
            
            print(f"{Fore.CYAN}  > {LANG[language]['estimating_gas']}{Style.RESET_ALL}")
            try:
                estimated_gas = w3.eth.estimate_gas(tx_params)
                tx_params['gas'] = int(estimated_gas * 1.2)
                print(f"{Fore.YELLOW}    Gas estimated: {tx_params['gas']}{Style.RESET_ALL}")
            except Exception as e:
                tx_params['gas'] = CONFIG['DEFAULT_GAS']
                print(f"{Fore.YELLOW}    {LANG[language]['gas_estimation_failed'].format(error=str(e))}. {LANG[language]['default_gas_used'].format(gas=CONFIG['DEFAULT_GAS'])}{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
            for attempt in range(CONFIG['MAX_RETRIES']):
                try:
                    signed_tx = w3.eth.account.sign_transaction(tx_params, private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
                    
                    receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=MAX_WAIT_TIME))
                    
                    if receipt.status == 1:
                        successful_pixels += 1
                        balance_after = check_balance(w3, sender_address, language)
                        print(f"{Fore.GREEN}  ✔ {LANG[language]['success_pixel']} │ Tx: {tx_link}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[language]['address']:<12}: {sender_address}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[language]['pixel']:<12}: x={x}, y={y}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[language]['color']:<12}: #{hex(color)[2:].zfill(6).upper()}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[language]['gas']:<12}: {receipt['gasUsed']}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[language]['block']:<12}: {receipt['blockNumber']}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[language]['balance']:<12}: {balance_after:.6f}{Style.RESET_ALL}")
                        nonce += 1
                        break
                    else:
                        print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
                        print(f"{Fore.RED}    {LANG[language]['tx_rejected']}{Style.RESET_ALL}")
                        break
                
                except Exception as e:
                    if attempt < CONFIG['MAX_RETRIES'] - 1:
                        delay = random.uniform(5, 15)
                        print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                        await asyncio.sleep(delay)
                        continue
                    print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)} │ Tx: {tx_link if 'tx_hash' in locals() else 'Chưa gửi'}{Style.RESET_ALL}")
                    break
            
            if i < pixel_count - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_PIXELS'][0], CONFIG['PAUSE_BETWEEN_PIXELS'][1])
                print(f"{Fore.YELLOW}    {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
        
        except Exception as e:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']}: {str(e)}{Style.RESET_ALL}")
            break
    
    return successful_pixels

async def run_sopixel(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    proxies = load_proxies('proxies.txt', language)
    
    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    # Display balance table for all wallets
    display_all_wallets_balances(w3, private_keys, language)
    print_separator()

    # Get pixel count
    while True:
        print(f"{Fore.CYAN}{LANG[language]['pixel_count_prompt']}{Style.RESET_ALL}")
        try:
            pixel_count = int(input(f"{Fore.GREEN}  > {Style.RESET_ALL}"))
            if pixel_count > 0:
                break
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_pixel_count']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_pixel_count']}{Style.RESET_ALL}")

    print(f"{Fore.GREEN}  ℹ {LANG[language]['info']}: Số pixel sẽ tô màu cho mỗi ví: {pixel_count}{Style.RESET_ALL}")
    print_separator()

    total_pixels = 0
    successful_pixels = 0

    print_wallets_summary(len(private_keys), language)
    random.shuffle(private_keys)

    # Process wallets with concurrency
    async def process_wallet(index, profile_num, private_key):
        nonlocal successful_pixels, total_pixels
        proxy = proxies[index % len(proxies)] if proxies else None
        
        async with semaphore:
            pixels = await color_pixel(w3, private_key, profile_num, pixel_count, proxy, language)
            successful_pixels += pixels
            total_pixels += pixel_count
            if index < len(private_keys) - 1:
                delay = random.uniform(CONFIG['PAUSE_BETWEEN_ATTEMPTS'][0], CONFIG['PAUSE_BETWEEN_ATTEMPTS'][1])
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    tasks = [process_wallet(i, profile_num, key) for i, (profile_num, key) in enumerate(private_keys)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_pixels, total=total_pixels)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_sopixel('vi'))
