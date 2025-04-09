import os
import sys
import asyncio
import time
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from colorama import init, Fore, Style
import aiohttp

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Constants
NETWORK_URL = "https://dream-rpc.somnia.network"
CHAIN_ID = 50312
EXPLORER_URL = "https://shannon-explorer.somnia.network/tx/0x"

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'QUILLS FUN - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'auth': 'Đang xác thực...',
        'minting': 'Đang mint tin nhắn NFT...',
        'success_auth': 'Xác thực thành công!',
        'success_mint': 'Mint tin nhắn NFT thành công!',
        'failure': 'Thất bại',
        'address': 'Địa chỉ',
        'message': 'Tin nhắn',
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
        'enter_message': 'Nhập tin nhắn vui của bạn: ',
        'tx_check': 'Kiểm tra giao dịch...',
    },
    'en': {
        'title': 'QUILLS FUN - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'auth': 'Authenticating...',
        'minting': 'Minting message NFT...',
        'success_auth': 'Authentication successful!',
        'success_mint': 'Successfully minted message NFT!',
        'failure': 'Failed',
        'address': 'Address',
        'message': 'Message',
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
        'enter_message': 'Enter your fun message: ',
        'tx_check': 'Checking transaction...',
    }
}

# Display bordered text
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Display separator
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Validate private key
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Load private keys from pvkey.txt
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

# Connect to Web3
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

# Quills Fun processing class
class QuillsMessageModule:
    def __init__(self, private_key: str, language: str, w3: Web3):
        self.account = Account.from_key(private_key)
        self.wallet_address = self.account.address
        self.language = language
        self.session = None
        self.w3 = w3  # Web3 instance for tx checking

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_headers(self) -> dict[str, str]:
        return {
            'authority': 'quills.fun',
            'accept': '*/*',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://quills.fun',
            'pragma': 'no-cache',
            'referer': 'https://quills.fun/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }

    async def auth(self) -> bool:
        print(f"{Fore.CYAN}  > {LANG[self.language]['auth']}{Style.RESET_ALL}")
        message = f"I accept the Quills Adventure Terms of Service at https://quills.fun/terms\n\nNonce: {int(time.time() * 1000)}"
        signature = self.account.sign_message(encode_defunct(text=message)).signature.hex()
        
        json_data = {
            'address': self.wallet_address,
            'signature': f"0x{signature}",
            'message': message,
        }
        
        async with self.session.post(
            "https://quills.fun/api/auth/wallet",
            json=json_data,
            headers=self._get_headers(),
            ssl=False
        ) as resp:
            response = await resp.json()
        
        if response.get("success"):
            print(f"{Fore.GREEN}  ✔ {LANG[self.language]['success_auth']}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {LANG[self.language]['failure']}: {response}{Style.RESET_ALL}")
            return False

    async def mint_message_nft(self, fun_message: str) -> bool:
        print(f"{Fore.CYAN}  > {LANG[self.language]['minting']}{Style.RESET_ALL}")
        
        json_data = {
            'walletAddress': self.wallet_address,
            'message': fun_message,
        }
        
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"{Fore.YELLOW}    Attempt {attempt}/{max_attempts}{Style.RESET_ALL}")
                async with self.session.post(
                    "https://quills.fun/api/mint-nft",
                    json=json_data,
                    headers=self._get_headers(),
                    ssl=False
                ) as resp:
                    response = await resp.json()
                
                if response.get("success"):
                    print(f"{Fore.GREEN}  ✔ {LANG[self.language]['success_mint']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[self.language]['address']:<12}: {self.wallet_address}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}    {LANG[self.language]['message']:<12}: {fun_message}{Style.RESET_ALL}")
                    
                    # Giả sử API trả về tx_hash (nếu có)
                    tx_hash = response.get("tx_hash")
                    if tx_hash:
                        print(f"{Fore.CYAN}  > {LANG[self.language]['tx_check']}{Style.RESET_ALL}")
                        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
                        if receipt.status == 1:
                            print(f"{Fore.YELLOW}    Tx Hash: {EXPLORER_URL}{tx_hash}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}    {LANG[self.language]['block']:<12}: {receipt['blockNumber']}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}    {LANG[self.language]['gas']:<12}: {receipt['gasUsed']}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}    Transaction failed on-chain{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}  ✖ {LANG[self.language]['failure']}: {response}{Style.RESET_ALL}")
                    if attempt < max_attempts:
                        await asyncio.sleep(2 * attempt)
            except Exception as e:
                print(f"{Fore.RED}  ✖ {LANG[self.language]['failure']} (attempt {attempt}): {str(e)}{Style.RESET_ALL}")
                if attempt < max_attempts:
                    await asyncio.sleep(2 * attempt)
        return False

    async def run(self, fun_message: str) -> bool:
        if not await self.auth():
            return False
        return await self.mint_message_nft(fun_message)

# Main function to run from main.py
async def run_fun(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()

    successful_tasks = 0
    total_tasks = len(private_keys)
    
    fun_message = input(f"{Fore.CYAN}{LANG[language]['enter_message']}{Style.RESET_ALL}")

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        print()
        
        async with QuillsMessageModule(private_key, language, w3) as quills:
            if await quills.run(fun_message):
                successful_tasks += 1
        
        if i < len(private_keys):
            delay = 10
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_tasks, total=total_tasks)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_fun('en'))
