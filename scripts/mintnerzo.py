import os
import sys
import asyncio
import random
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
NERZO_SHANNON_CONTRACT = "0x715A73f6C71aB9cB32c7Cc1Aa95967a1b5da468D"
TIMEOUT = 300  # Timeout 5 phút
SYMBOL = "STT"

# Minimal ABI for NFT balance checking
NFT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    }
]

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': 'MINT SHANNON (NERZO-SH) - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'checking_balance': 'Đang kiểm tra số dư NFT...',
        'has_nft': 'Ví này đã mint! Không thực hiện lại yêu cầu này',
        'no_balance': 'Số dư ví không đủ (< 0.006 STT), không thể mint',
        'preparing_tx': 'Chuẩn bị giao dịch...',
        'sending_tx': 'Đang gửi giao dịch...',
        'success': 'Mint Shannon (NERZO-SH) thành công!',
        'failure': 'Mint Shannon (NERZO-SH) thất bại',
        'timeout': 'Giao dịch chưa được xác nhận sau {timeout} giây, kiểm tra lại sau...',
        'address': 'Địa chỉ ví',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư STT',
        'error': 'Lỗi',
        'connect_success': 'Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Đọc pvkey.txt thất bại',
        'invalid_key': 'không hợp lệ, bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG'
    },
    'en': {
        'title': 'MINT SHANNON (NERZO-SH) - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'checking_balance': 'Checking NFT balance...',
        'has_nft': 'This wallet has already minted! Skipping this request',
        'no_balance': 'Insufficient wallet balance (< 0.006 STT), cannot mint',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'success': 'Successfully minted Shannon (NERZO-SH)!',
        'failure': 'Failed to mint Shannon (NERZO-SH)',
        'timeout': 'Transaction not confirmed after {timeout} seconds, check later...',
        'address': 'Wallet address',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'STT Balance',
        'error': 'Error',
        'connect_success': 'Success: Connected to Somnia Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL'
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

# Hàm mint Nerzo Shannon NFT
async def mint_nerzo_nft(w3: Web3, private_key: str, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    print(f"{Fore.CYAN}  > {LANG[language]['checking_balance']}{Style.RESET_ALL}")
    nft_contract = w3.eth.contract(address=Web3.to_checksum_address(NERZO_SHANNON_CONTRACT), abi=NFT_ABI)
    nft_balance = nft_contract.functions.balanceOf(sender_address).call()
    
    if nft_balance >= 1:
        print(f"{Fore.GREEN}  ✔ {LANG[language]['has_nft']}{Style.RESET_ALL}")
        return True

    balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
    print(f"{Fore.YELLOW}    {LANG[language]['balance']:<16}: {balance:.6f} STT{Style.RESET_ALL}")

    print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
    mint_price = w3.to_wei(0.001, 'ether')  
    data = (
        "0x84bb1e42"
        + sender_address[2:].lower().zfill(64)
        + "0000000000000000000000000000000000000000000000000000000000000001"
        + "000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        + "00000000000000000000000000000000000000000000000000038d7ea4c68000"  
        + "00000000000000000000000000000000000000000000000000000000000000c0"
        + "0000000000000000000000000000000000000000000000000000000000000160"
        + "0000000000000000000000000000000000000000000000000000000000000080"
        + "0000000000000000000000000000000000000000000000000000000000000000"
        + "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        + "0000000000000000000000000000000000000000000000000000000000000000"
        + "0000000000000000000000000000000000000000000000000000000000000000"
        + "0000000000000000000000000000000000000000000000000000000000000000"
    )

    latest_block = w3.eth.get_block('latest')
    base_fee = latest_block['baseFeePerGas']
    gas_price = max(base_fee + w3.to_wei('1', 'gwei'), w3.to_wei('5', 'gwei'))  # Đảm bảo >= base fee + tip

    try:
        estimated_gas = w3.eth.estimate_gas({
            'from': sender_address,
            'to': Web3.to_checksum_address(NERZO_SHANNON_CONTRACT),
            'value': mint_price,
            'data': data
        })
        gas_limit = int(estimated_gas * 1.2)
    except Exception as e:
        print(f"{Fore.YELLOW}    Không thể ước lượng gas: {str(e)}. Dùng gas mặc định: 500000{Style.RESET_ALL}")
        gas_limit = 500000

    required_balance = w3.from_wei(gas_limit * gas_price + mint_price, 'ether')
    if balance < required_balance:
        print(f"{Fore.RED}  ✖ {LANG[language]['no_balance']} (Cần: {required_balance:.6f} STT){Style.RESET_ALL}")
        return False

    nonce = w3.eth.get_transaction_count(sender_address)
    tx = {
        'from': sender_address,
        'to': Web3.to_checksum_address(NERZO_SHANNON_CONTRACT),
        'value': mint_price,
        'data': data,
        'nonce': nonce,
        'chainId': CHAIN_ID,
        'gas': gas_limit,
        'gasPrice': gas_price
    }

    print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    tx_link = f"{EXPLORER_URL}{tx_hash_hex}"

    try:
        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=TIMEOUT))
        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {LANG[language]['success']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {'Tx Hash':<16}: {tx_link}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['address']:<16}: {sender_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['block']:<16}: {receipt['blockNumber']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['gas']:<16}: {receipt['gasUsed']}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']} | Tx: {tx_link}{Style.RESET_ALL}")
            return False
    except Exception:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['timeout'].format(timeout=TIMEOUT)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}    {'Tx Hash':<16}: {tx_link}{Style.RESET_ALL}")
        return True  # Giả định thành công nếu timeout để tiếp tục

# Hàm chính để chạy từ main.py
async def run_mintnerzo(language: str = 'en'):
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

    successful_mints = 0
    total_wallets = len(private_keys)

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        print()
        
        if await mint_nerzo_nft(w3, private_key, profile_num, language):
            successful_mints += 1
        
        if i < len(private_keys):
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}  ℹ {'Tạm nghỉ' if language == 'vi' else 'Pausing'} {delay:.2f} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()
    
    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_mints, total=total_wallets)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_mintnerzo('en'))
