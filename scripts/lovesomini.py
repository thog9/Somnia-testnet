import os
import sys
import asyncio
import time
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network/tx/0x"
CONTRACT_ADDRESS = "0xf1D8eF3094034FBd27497a6aFE809b601F1d6ba9"

# ABI của contract
ABI = [
    {"inputs":[{"internalType":"uint256","name":"_fee","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[],"name":"EnforcedPause","type":"error"},
    {"inputs":[],"name":"ExpectedPause","type":"error"},
    {"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"OwnableInvalidOwner","type":"error"},
    {"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"OwnableUnauthorizedAccount","type":"error"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint256","name":"newFee","type":"uint256"}],"name":"FeeUpdated","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"sender","type":"address"}],"name":"LoveEvent","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},
    {"inputs":[],"name":"fee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"loveSomini","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"newFee","type":"uint256"}],"name":"updateFee","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': 'LOVE SOMINI - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'minting': 'Đang gửi Love Somini...',
        'success_mint': 'Gửi Love Somini thành công!',
        'failure': 'Thất bại',
        'address': 'Địa chỉ',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư STT',
        'pausing': 'Tạm nghỉ',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': 'Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'enter_love_count': 'Nhập số lần gửi Love Somini (mặc định: 1): ',
    },
    'en': {
        'title': 'LOVE SOMINI - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'minting': 'Sending Love Somini...',
        'success_mint': 'Successfully sent Love Somini!',
        'failure': 'Failed',
        'address': 'Address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'STT Balance',
        'pausing': 'Pausing',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'connect_success': 'Success: Connected to Somnia Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'enter_love_count': 'Enter number of Love Somini sends (default: 1): ',
    }
}

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

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

# Hàm kết nối Web3
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

# Class xử lý LoveSomini
class LoveSominiModule:
    def __init__(self, private_key: str, language: str, w3: Web3):
        self.account = Account.from_key(private_key)
        self.wallet_address = self.account.address
        self.language = language
        self.w3 = w3
        self.contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

    async def get_balance(self) -> float:
        balance_wei = self.w3.eth.get_balance(self.wallet_address)
        return self.w3.from_wei(balance_wei, 'ether')

    async def love_somini(self, attempt_num: int, total_attempts: int) -> bool:
        print(f"{Fore.CYAN}  > {LANG[self.language]['minting']} (Lần {attempt_num}/{total_attempts}){Style.RESET_ALL}")
        
        try:
            # Lấy fee từ contract (nếu cần)
            fee = self.contract.functions.fee().call()
            value = fee if fee > 0 else self.w3.to_wei(0, 'ether')  # Giả sử fee = 0

            # Kiểm tra số dư
            balance = await self.get_balance()
            print(f"{Fore.YELLOW}    {LANG[self.language]['balance']:<16}: {balance:.6f} STT{Style.RESET_ALL}")
            if balance < self.w3.from_wei(value, 'ether'):
                print(f"{Fore.RED}    Không đủ số dư để gửi Love Somini{Style.RESET_ALL}")
                return False

            # Lấy base fee từ block mới nhất
            latest_block = self.w3.eth.get_block('latest')
            base_fee = latest_block['baseFeePerGas']
            gas_price = max(base_fee + self.w3.to_wei('1', 'gwei'), self.w3.to_wei('5', 'gwei'))  # Đảm bảo >= base fee + tip

            # Xây dựng transaction
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            tx = self.contract.functions.loveSomini().build_transaction({
                'from': self.wallet_address,
                'value': value,
                'gas': 200000,  # Ước lượng gas
                'gasPrice': gas_price,  # Sử dụng gasPrice động
                'nonce': nonce,
                'chainId': CHAIN_ID
            })

            # Ký transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)

            # Gửi transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = tx_hash.hex()

            # Đợi receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            if receipt.status == 1:
                print(f"{Fore.GREEN}  ✔ {LANG[self.language]['success_mint']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {'Tx Hash':<16}: {EXPLORER_URL}{tx_hash_hex}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[self.language]['address']:<16}: {self.wallet_address}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[self.language]['block']:<16}: {receipt['blockNumber']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    {LANG[self.language]['gas']:<16}: {receipt['gasUsed']}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ✖ {LANG[self.language]['failure']}: Transaction failed{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}  ✖ {LANG[self.language]['failure']}: {str(e)}{Style.RESET_ALL}")
            return False

    async def run(self, love_count: int) -> int:
        successful_loves = 0
        for attempt in range(1, love_count + 1):
            if await self.love_somini(attempt, love_count):
                successful_loves += 1
            if attempt < love_count:  # Thêm delay giữa các lần trong cùng một ví
                await asyncio.sleep(5)  # Delay 5 giây giữa các lần
        return successful_loves

# Hàm chính để chạy từ main.py
async def run_lovesomini(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    # Yêu cầu nhập số lần gửi Love Somini
    while True:
        try:
            love_count_input = input(f"{Fore.CYAN}{LANG[language]['enter_love_count']}{Style.RESET_ALL}")
            love_count = int(love_count_input) if love_count_input.strip() else 1  # Mặc định là 1 nếu không nhập
            if love_count < 1:
                print(f"{Fore.RED}  ✖ Vui lòng nhập số lớn hơn 0!{Style.RESET_ALL}")
                continue
            break
        except ValueError:
            print(f"{Fore.RED}  ✖ Vui lòng nhập một số hợp lệ!{Style.RESET_ALL}")

    w3 = connect_web3(language)
    print()

    successful_tasks = 0
    total_tasks = len(private_keys) * love_count

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        print()
        
        module = LoveSominiModule(private_key, language, w3)
        successful_loves = await module.run(love_count)
        successful_tasks += successful_loves
        
        if i < len(private_keys):
            delay = 10  # Delay 10 giây giữa các ví
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_tasks, total=total_tasks)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_lovesomini('vi'))
