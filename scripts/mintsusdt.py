import os
import sys
import asyncio
import random
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style
from typing import List, Dict
import aiohttp
from aiohttp_socks import ProxyConnector

# Khởi tạo colorama
init(autoreset=True)

# Cấu hình
NETWORK_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network"
IP_CHECK_URL = "https://api.ipify.org?format=json"
SHUFFLE_WALLETS = True
MINT_SUSDT_SLEEP_RANGE = [10, 30]  # [min, max] in seconds
CONFIG = {
    "MAX_CONCURRENCY": 5,
    "MINIMUM_BALANCE": 0.001  # STT
}
BORDER_WIDTH = 80
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

# Constants
CONTRACT_ADDRESS = "0x65296738D4E5edB1515e40287B6FDf8320E6eE04"  # Hợp đồng sUSDT
MINT_AMOUNT = 1000  # Mint 1000 sUSDT
MINT_DATA = "0x1249c58b"  # Bytecode để mint

# ABI tối thiểu để kiểm tra số dư sUSDT
SUSDT_TOKEN_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': '✨ MINT sUSDT - SOMNIA TESTNET ✨',
        'info': 'ℹ Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_wallet': '⚙ XỬ LÝ VÍ',
        'checking_balance': 'Đang kiểm tra số dư...',
        'insufficient_balance': 'Số dư không đủ (cần ít nhất {required:.6f} STT cho giao dịch)',
        'success': '✅ Đã mint 1000 sUSDT thành công!',
        'failure': '❌ Mint sUSDT thất bại',
        'timeout': '⏰ Giao dịch chưa xác nhận sau {timeout} giây, kiểm tra trên explorer',
        'address': 'Địa chỉ ví',
        'amount': 'Số lượng: 1000 sUSDT',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư STT: {stt:.6f} STT | sUSDT: {susdt:.2f}',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': '🏁 HOÀN THÀNH: {successful}/{total} VÍ THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': '✅ Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': '❌ Không thể kết nối RPC',
        'web3_error': '❌ Kết nối Web3 thất bại',
        'pvkey_not_found': '❌ File pvkey.txt không tồn tại',
        'pvkey_empty': '❌ Không tìm thấy private key hợp lệ',
        'pvkey_error': '❌ Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': '⚠ Cảnh báo: Dòng',
        'estimating_gas': 'Đang ước lượng gas...',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'sending_tx': 'Đang gửi giao dịch...',
        'already_minted': '⚠ Ví này đã mint sUSDT! Không thực hiện lại yêu cầu này.'
    },
    'en': {
        'title': '✨ MINT sUSDT - SOMNIA TESTNET ✨',
        'info': 'ℹ Info',
        'found': 'Found',
        'wallets': 'wallets',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_wallet': '⚙ PROCESSING WALLET',
        'checking_balance': 'Checking balance...',
        'insufficient_balance': 'Insufficient balance (need at least {required:.6f} STT for transaction)',
        'success': '✅ Successfully minted 1000 sUSDT!',
        'failure': '❌ Failed to mint sUSDT',
        'timeout': '⏰ Transaction not confirmed after {timeout} seconds',
        'address': 'Wallet address',
        'amount': 'Amount: 1000 sUSDT',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance: {stt:.6f} STT | sUSDT: {susdt:.2f}',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '🏁 COMPLETED: {successful}/{total} WALLETS SUCCESSFUL',
        'error': 'Error',
        'connect_success': '✅ Success: Connected to Somnia Testnet',
        'connect_error': '❌ Failed to connect to RPC',
        'web3_error': '❌ Web3 connection failed',
        'pvkey_not_found': '❌ pvkey.txt file not found',
        'pvkey_empty': '❌ No valid private keys found',
        'pvkey_error': '❌ Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': '⚠ Warning: Line',
        'estimating_gas': 'Estimating gas...',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'no_proxies': 'No proxies found in proxies.txt',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'sending_tx': 'Sending transaction...',
        'already_minted': '⚠ This wallet has already minted sUSDT! Skipping this request.'
    }
}

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}", flush=True)
    print(f"{color}│{padded_text}│{Style.RESET_ALL}", flush=True)
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}", flush=True)

# Hàm hiển thị phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}", flush=True)

# Hàm in thông báo
def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}{message}{Style.RESET_ALL}", flush=True)

# Hàm kiểm tra private key hợp lệ
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Hàm đọc private keys từ file pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> List[tuple]:
    try:
        if not os.path.exists(file_path):
            print_message(f"  ✖ {LANG[language]['pvkey_not_found']}", Fore.RED)
            with open(file_path, 'w') as f:
                f.write("# Thêm private keys vào đây, mỗi key trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
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
                        print_message(f"  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}", Fore.YELLOW)
        
        if not valid_keys:
            print_message(f"  ✖ {LANG[language]['pvkey_empty']}", Fore.RED)
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print_message(f"  ✖ {LANG[language]['pvkey_error']}: {str(e)}", Fore.RED)
        sys.exit(1)

# Hàm đọc proxies từ proxies.txt
def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print_message(f"  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.", Fore.YELLOW)
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
            print_message(f"  ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.", Fore.YELLOW)
            return []
        
        print_message(f"  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}")
        return proxies
    except Exception as e:
        print_message(f"  ✖ {LANG[language]['error']}: {str(e)}", Fore.RED)
        return []

# Hàm lấy IP công khai qua proxy
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
                    return f"⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}"
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}"
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return f"⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}"
    except Exception as e:
        return f"⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}"

# Hàm kết nối Web3
def connect_web3(language: str):
    try:
        web3 = Web3(Web3.HTTPProvider(NETWORK_URL))
        if not web3.is_connected():
            print_message(f"  ✖ {LANG[language]['connect_error']}", Fore.RED)
            sys.exit(1)
        print_message(f"  ✔ {LANG[language]['connect_success']} │ Chain ID: {web3.eth.chain_id}", Fore.GREEN)
        return web3
    except Exception as e:
        print_message(f"  ✖ {LANG[language]['web3_error']}: {str(e)}", Fore.RED)
        sys.exit(1)

# Hàm kiểm tra số dư sUSDT
def get_susdt_balance(w3: Web3, address: str) -> float:
    try:
        contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=SUSDT_TOKEN_ABI)
        decimals = contract.functions.decimals().call()
        balance_wei = contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
        return balance_wei / (10 ** decimals)
    except Exception:
        return 0.0

# Hàm kiểm tra xem ví đã mint sUSDT chưa
def has_minted_susdt(w3: Web3, address: str, language: str = 'en') -> bool:
    try:
        balance = get_susdt_balance(w3, address)
        return balance > 0  # Nếu balance > 0, ví đã mint sUSDT
    except Exception as e:
        print_message(f"  ⚠ {'Không kiểm tra được số dư sUSDT' if language == 'vi' else 'Failed to check sUSDT balance'}: {str(e)}", Fore.YELLOW)
        return False

# Hàm mint sUSDT
async def mint_susdt(web3: Web3, private_key: str, wallet_index: int, proxy: str = None, language: str = 'en') -> Dict:
    result = {
        'index': wallet_index,
        'success': False,
        'output': [],
        'address': '',
        'tx_hash': '',
        'gas_used': 0,
        'block_number': 0,
        'new_stt_balance': 0.0,
        'new_susdt_balance': 0.0
    }
    
    def add_output(message: str, color=Fore.YELLOW):
        result['output'].append((message, color))

    try:
        account = Account.from_key(private_key)
        address = account.address
        result['address'] = address

        # Proxy info
        public_ip = await get_proxy_ip(proxy, language)
        proxy_display = proxy if proxy else LANG[language]['no_proxy']
        add_output(f"  🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}", Fore.CYAN)

        # Kiểm tra xem ví đã mint chưa
        if has_minted_susdt(web3, address, language):
            add_output(f"  ⚠ {LANG[language]['already_minted']}", Fore.YELLOW)
            return result

        # Kiểm tra số dư
        add_output(f"  > {LANG[language]['checking_balance']}", Fore.CYAN)
        stt_balance = web3.from_wei(web3.eth.get_balance(address), 'ether')
        susdt_balance = get_susdt_balance(web3, address)
        add_output(f"    - {LANG[language]['balance'].format(stt=stt_balance, susdt=susdt_balance)}", Fore.YELLOW)
        if stt_balance < CONFIG['MINIMUM_BALANCE']:
            add_output(f"  ✖ {LANG[language]['insufficient_balance'].format(required=CONFIG['MINIMUM_BALANCE'])}: {stt_balance:.6f} STT", Fore.RED)
            return result

        # Chuẩn bị giao dịch
        nonce = web3.eth.get_transaction_count(address)
        gas_price = int(web3.eth.gas_price * random.uniform(1.03, 1.1))  # Tăng nhẹ gasPrice
        tx = {
            'nonce': nonce,
            'to': Web3.to_checksum_address(CONTRACT_ADDRESS),
            'value': 0,
            'data': MINT_DATA,
            'chainId': CHAIN_ID,
            'gas': 200000,
            'gasPrice': gas_price
        }

        # Ước tính gas
        add_output(f"  > {LANG[language]['estimating_gas']}", Fore.CYAN)
        try:
            gas_estimate = web3.eth.estimate_gas(tx)
            add_output(f"    - Gas ước lượng: {gas_estimate}", Fore.YELLOW)
            tx['gas'] = gas_estimate + 10000  # Thêm buffer
        except Exception as e:
            add_output(f"  ✖ {LANG[language]['error']}: {LANG[language]['estimating_gas']} failed: {str(e)}", Fore.RED)
            return result

        # Ký và gửi giao dịch
        add_output(f"  > {LANG[language]['sending_tx']}", Fore.CYAN)
        signed_tx = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        result['tx_hash'] = tx_hash.hex()
        
        add_output(f"  ✔ {LANG[language]['success'].replace('Đã mint 1000 sUSDT thành công!', 'Đã gửi giao dịch')}: {EXPLORER_URL}/tx/0x{tx_hash.hex()}", Fore.GREEN)
        
        # Chờ xác nhận
        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
        if receipt.status == 1:
            new_stt_balance = web3.from_wei(web3.eth.get_balance(address), 'ether')
            new_susdt_balance = get_susdt_balance(web3, address)
            result['success'] = True
            result['gas_used'] = receipt['gasUsed']
            result['block_number'] = receipt['blockNumber']
            result['new_stt_balance'] = new_stt_balance
            result['new_susdt_balance'] = new_susdt_balance
            add_output(f"  ✔ {LANG[language]['success']}", Fore.GREEN)
            add_output(f"    - {LANG[language]['address']}: {address}", Fore.YELLOW)
            add_output(f"    - {LANG[language]['amount']}", Fore.YELLOW)
            add_output(f"    - {LANG[language]['gas']}: {receipt['gasUsed']}", Fore.YELLOW)
            add_output(f"    - {LANG[language]['block']}: {receipt['blockNumber']}", Fore.YELLOW)
            add_output(f"    - {LANG[language]['balance'].format(stt=new_stt_balance, susdt=new_susdt_balance)}", Fore.YELLOW)
        else:
            add_output(f"  ✖ {LANG[language]['failure']}", Fore.RED)
        return result

    except Exception as e:
        add_output(f"  ✖ {LANG[language]['failure']}: {str(e)}", Fore.RED)
        return result

# Hàm xử lý từng ví
async def process_wallet(profile_num: int, private_key: str, proxy: str, w3: Web3, language: str) -> Dict:
    return await mint_susdt(w3, private_key, profile_num, proxy, language)

# Hàm chính
async def run_mintsusdt(language: str = 'vi'):
    print_border(LANG[language]['title'], Fore.CYAN)

    private_keys = load_private_keys('pvkey.txt', language)
    proxies = load_proxies('proxies.txt', language)
    print_message(f"  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}", Fore.YELLOW)
    print()
    
    w3 = connect_web3(language)

    successful_mints = 0
    total_wallets = len(private_keys)
    CONFIG['TOTAL_WALLETS'] = total_wallets
    CONFIG['MAX_CONCURRENCY'] = min(CONFIG['MAX_CONCURRENCY'], total_wallets)

    if SHUFFLE_WALLETS:
        random.shuffle(private_keys)

    semaphore = asyncio.Semaphore(CONFIG['MAX_CONCURRENCY'])
    current_index = 0

    async def limited_task(profile_num, private_key, proxy):
        nonlocal current_index, successful_mints
        async with semaphore:
            current_index += 1
            result = await process_wallet(profile_num, private_key, proxy, w3, language)
            # Print header, results, and separator after task completes
            print_border(
                f"{LANG[language]['processing_wallet']} {profile_num} ({current_index}/{total_wallets})",
                Fore.MAGENTA
            )
            for message, color in result['output']:
                print_message(message, color)
            print_separator(Fore.GREEN if result['success'] else Fore.RED)
            if result['success']:
                successful_mints += 1
            # Add delay after processing each wallet (except the last one)
            if current_index < total_wallets:
                delay = random.uniform(MINT_SUSDT_SLEEP_RANGE[0], MINT_SUSDT_SLEEP_RANGE[1])
                print_message(f"  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                await asyncio.sleep(delay)

    # Chạy song song
    tasks = []
    for _, (profile_num, private_key) in enumerate(private_keys):
        proxy = proxies[len(tasks) % len(proxies)] if proxies else None
        tasks.append(limited_task(profile_num, private_key, proxy))

    await asyncio.gather(*tasks, return_exceptions=True)

    print_border(
        f"{LANG[language]['completed'].format(successful=successful_mints, total=total_wallets)}",
        Fore.GREEN
    )

if __name__ == "__main__":
    asyncio.run(run_mintsusdt('vi'))
