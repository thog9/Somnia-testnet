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

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': 'SEND TX - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'enter_tx_count': 'NHẬP SỐ LƯỢNG GIAO DỊCH',
        'tx_count_prompt': 'Số giao dịch (mặc định 1)',
        'selected': 'Đã chọn',
        'transactions': 'giao dịch',
        'enter_amount': 'NHẬP SỐ LƯỢNG STT',
        'amount_prompt': 'Số lượng STT (mặc định 0.000001, tối đa 999)',
        'amount_unit': 'STT',
        'select_tx_type': 'CHỌN LOẠI GIAO DỊCH',
        'random_option': 'Gửi đến địa chỉ ngẫu nhiên',
        'file_option': 'Gửi đến địa chỉ từ file (address.txt)',
        'choice_prompt': 'Nhập lựa chọn (1/2)',
        'start_random': 'BẮT ĐẦU GỬI {tx_count} GIAO DỊCH NGẪU NHIÊN',
        'start_file': 'BẮT ĐẦU GỬI GIAO DỊCH ĐẾN {addr_count} ĐỊA CHỈ TỪ FILE',
        'processing_wallet': 'XỬ LÝ VÍ',
        'transaction': 'Giao dịch',
        'to_address': 'Giao dịch đến địa chỉ',
        'sending': 'Đang gửi giao dịch...',
        'success': 'Giao dịch thành công!',
        'failure': 'Giao dịch thất bại',
        'sender': 'Người gửi',
        'receiver': 'Người nhận',
        'amount': 'Số lượng',
        'gas': 'Gas',
        'block': 'Khối',
        'balance': 'Số dư',
        'pausing': 'Tạm nghỉ',
        'seconds': 'giây',
        'completed': 'HOÀN THÀNH',
        'tx_successful': 'GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'invalid_number': 'Vui lòng nhập số hợp lệ',
        'tx_count_error': 'Số giao dịch phải lớn hơn 0',
        'amount_error': 'Số lượng phải lớn hơn 0 và không quá 999',
        'invalid_choice': 'Lựa chọn không hợp lệ',
        'connect_success': 'Thành công: Đã kết nối mạng Somnia Testnet',
        'connect_error': 'Không thể kết nối RPC',
        'web3_error': 'Kết nối Web3 thất bại',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ',
        'pvkey_error': 'Đọc pvkey.txt thất bại',
        'addr_not_found': 'File address.txt không tồn tại',
        'addr_empty': 'Không tìm thấy địa chỉ hợp lệ trong address.txt',
        'addr_error': 'Đọc address.txt thất bại',
        'invalid_addr': 'không phải địa chỉ hợp lệ, bỏ qua',
        'warning_line': 'Cảnh báo: Dòng'
    },
    'en': {
        'title': 'SEND TX - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'enter_tx_count': 'ENTER NUMBER OF TRANSACTIONS',
        'tx_count_prompt': 'Number of transactions (default 1)',
        'selected': 'Selected',
        'transactions': 'transactions',
        'enter_amount': 'ENTER AMOUNT OF STT',
        'amount_prompt': 'Amount of STT (default 0.000001, max 999)',
        'amount_unit': 'STT',
        'select_tx_type': 'SELECT TRANSACTION TYPE',
        'random_option': 'Send to random address',
        'file_option': 'Send to addresses from file (address.txt)',
        'choice_prompt': 'Enter choice (1/2)',
        'start_random': 'STARTING {tx_count} RANDOM TRANSACTIONS',
        'start_file': 'STARTING TRANSACTIONS TO {addr_count} ADDRESSES FROM FILE',
        'processing_wallet': 'PROCESSING WALLET',
        'transaction': 'Transaction',
        'to_address': 'Transaction to address',
        'sending': 'Sending transaction...',
        'success': 'Transaction successful!',
        'failure': 'Transaction failed',
        'sender': 'Sender',
        'receiver': 'Receiver',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'balance': 'Balance',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': 'COMPLETED',
        'tx_successful': 'TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'tx_count_error': 'Number of transactions must be greater than 0',
        'amount_error': 'Amount must be greater than 0 and not exceed 999',
        'invalid_choice': 'Invalid choice',
        'connect_success': 'Success: Connected to Somnia Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'addr_not_found': 'address.txt file not found',
        'addr_empty': 'No valid addresses found in address.txt',
        'addr_error': 'Failed to read address.txt',
        'invalid_addr': 'is not a valid address, skipped',
        'warning_line': 'Warning: Line'
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
                        valid_keys.append(key)
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_addr']}: {key}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm đọc địa chỉ từ address.txt
def load_addresses(file_path: str = "address.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['addr_not_found']}{Style.RESET_ALL}")
            return None
        
        addresses = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                addr = line.strip()
                if addr:
                    try:
                        addresses.append(Web3.to_checksum_address(addr))
                    except ValueError:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_addr']}: {addr}{Style.RESET_ALL}")
        
        if not addresses:
            print(f"{Fore.RED}  ✖ {LANG[language]['addr_empty']}{Style.RESET_ALL}")
            return None
        
        return addresses
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['addr_error']}: {str(e)}{Style.RESET_ALL}")
        return None

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

# Địa chỉ ngẫu nhiên với checksum
def get_random_address(w3: Web3):
    random_address = '0x' + ''.join(random.choices('0123456789abcdef', k=40))
    return w3.to_checksum_address(random_address)

# Hàm gửi giao dịch
async def send_transaction(w3: Web3, private_key: str, to_address: str, amount: float, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    try:
        nonce = w3.eth.get_transaction_count(sender_address)
        latest_block = w3.eth.get_block('latest')
        base_fee_per_gas = latest_block['baseFeePerGas']
        max_priority_fee_per_gas = w3.to_wei(2, 'gwei')  # Phí ưu tiên hợp lý
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

        tx = {
            'nonce': nonce,
            'to': w3.to_checksum_address(to_address),
            'value': w3.to_wei(amount, 'ether'),
            'gas': 21000,  # Gas cố định cho giao dịch ETH
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'chainId': CHAIN_ID,
        }

        print(f"{Fore.CYAN}  > {LANG[language]['sending']}{Style.RESET_ALL}")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
        
        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))
        
        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {LANG[language]['success']} │ Tx: {tx_link}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['sender']}: {sender_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['receiver']}: {to_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['amount']}: {amount:.6f} {LANG[language]['amount_unit']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
            balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
            print(f"{Fore.YELLOW}    {LANG[language]['balance']}: {balance:.6f} {LANG[language]['amount_unit']}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Thất bại / Failed'}: {str(e)}{Style.RESET_ALL}")
        return False

# Hàm nhập số lượng giao dịch
def get_tx_count(language: str = 'en') -> int:
    print_border(LANG[language]['enter_tx_count'], Fore.YELLOW)
    while True:
        try:
            tx_count_input = input(f"{Fore.YELLOW}  > {LANG[language]['tx_count_prompt']}: {Style.RESET_ALL}")
            tx_count = int(tx_count_input) if tx_count_input.strip() else 1
            if tx_count <= 0:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['tx_count_error']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {tx_count} {LANG[language]['transactions']}{Style.RESET_ALL}")
                return tx_count
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Hàm nhập số lượng STT
def get_amount(language: str = 'en') -> float:
    print_border(LANG[language]['enter_amount'], Fore.YELLOW)
    while True:
        try:
            amount_input = input(f"{Fore.YELLOW}  > {LANG[language]['amount_prompt']}: {Style.RESET_ALL}")
            amount = float(amount_input) if amount_input.strip() else 0.000001
            if 0 < amount <= 999:
                print(f"{Fore.GREEN}  ✔ {LANG[language]['selected']}: {amount} {LANG[language]['amount_unit']}{Style.RESET_ALL}")
                return amount
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['amount_error']}{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")

# Gửi giao dịch đến địa chỉ ngẫu nhiên
async def send_to_random_addresses(w3: Web3, amount: float, tx_count: int, private_keys: list, language: str = 'en'):
    print_border(LANG[language]['start_random'].format(tx_count=tx_count), Fore.CYAN)
    print()
    
    successful_txs = 0
    for i, private_key in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {i}/{len(private_keys)}", Fore.MAGENTA)
        print()
        
        for tx_iter in range(tx_count):
            print(f"{Fore.CYAN}  > {LANG[language]['transaction']} {tx_iter + 1}/{tx_count}{Style.RESET_ALL}")
            to_address = get_random_address(w3)
            if await send_transaction(w3, private_key, to_address, amount, i, language):
                successful_txs += 1
            if tx_iter < tx_count - 1 or i < len(private_keys):
                delay = random.uniform(1, 3)
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
            print()
        print_separator()
    
    return successful_txs

# Gửi giao dịch đến địa chỉ từ file
async def send_to_file_addresses(w3: Web3, amount: float, addresses: list, private_keys: list, language: str = 'en'):
    print_border(LANG[language]['start_file'].format(addr_count=len(addresses)), Fore.CYAN)
    print()
    
    successful_txs = 0
    for i, private_key in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {i}/{len(private_keys)}", Fore.MAGENTA)
        print()
        
        for addr_iter, to_address in enumerate(addresses, 1):
            print(f"{Fore.CYAN}  > {LANG[language]['to_address']} {addr_iter}/{len(addresses)}{Style.RESET_ALL}")
            if await send_transaction(w3, private_key, to_address, amount, i, language):
                successful_txs += 1
            if addr_iter < len(addresses) or i < len(private_keys):
                delay = random.uniform(1, 3)
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
            print()
        print_separator()
    
    return successful_txs

# Hàm chính
async def run_sendtx(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    tx_count = get_tx_count(language)
    amount = get_amount(language)
    print_separator()

    w3 = connect_web3(language)
    print()

    while True:
        print_border(LANG[language]['select_tx_type'], Fore.YELLOW)
        print(f"{Fore.CYAN}  1. {LANG[language]['random_option']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  2. {LANG[language]['file_option']}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}  > {LANG[language]['choice_prompt']}: {Style.RESET_ALL}")

        if choice == '1':
            successful_txs = await send_to_random_addresses(w3, amount, tx_count, private_keys, language)
            break
        elif choice == '2':
            addresses = load_addresses('address.txt', language)
            if addresses:
                successful_txs = await send_to_file_addresses(w3, amount, addresses, private_keys, language)
            else:
                return
            break
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
            print()

    print()
    total_txs = tx_count * len(private_keys) if choice == '1' else len(addresses) * len(private_keys)
    print_border(f"{LANG[language]['completed']}: {successful_txs}/{total_txs} {LANG[language]['tx_successful']}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_sendtx('vi'))  # Ngôn ngữ mặc định là Tiếng Việt, có thể đổi thành 'en'
