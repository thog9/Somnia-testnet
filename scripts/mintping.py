import os
import sys
import asyncio
import random
from web3 import Web3
from colorama import init, Fore, Style
from typing import List

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền cố định
BORDER_WIDTH = 80

# Cấu hình từ file config
SOMNIA_TESTNET_RPC_URL = 'https://dream-rpc.somnia.network'
SOMNIA_TESTNET_EXPLORER_URL = 'https://shannon-explorer.somnia.network'
SHUFFLE_WALLETS = True
MINT_PONGPING_SLEEP_RANGE = [100, 300]  # [min, max] in seconds

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."  # Cắt dài và thêm "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"\n{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}\n")

# Hàm kiểm tra private key hợp lệ
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key  # Thêm '0x' nếu thiếu
    try:
        # Kiểm tra xem key có phải hex hợp lệ không
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66  # Độ dài của private key hợp lệ (64 ký tự + '0x')
    except ValueError:
        return False

# Hàm đọc private keys từ file pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {'Lỗi: File pvkey.txt không tồn tại' if language == 'vi' else 'Error: pvkey.txt file not found'}{Style.RESET_ALL}")
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
                            key = '0x' + key  # Chuẩn hóa key
                        valid_keys.append(key)
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {'Cảnh báo: Dòng' if language == 'vi' else 'Warning: Line'} {i} {'không hợp lệ, bỏ qua' if language == 'vi' else 'is invalid, skipped'}: {key}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {'Lỗi: Không tìm thấy private key hợp lệ' if language == 'vi' else 'Error: No valid private keys found'}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Lỗi: Đọc pvkey.txt thất bại' if language == 'vi' else 'Error: Failed to read pvkey.txt'}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm xáo trộn danh sách ví
def shuffle_wallets(keys: List[str]) -> List[str]:
    return random.sample(keys, len(keys))

# Hàm tạo số ngẫu nhiên trong khoảng
def get_random_int(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)

# Hàm kết nối Web3
def connect_web3(language: str):
    try:
        web3 = Web3(Web3.HTTPProvider(SOMNIA_TESTNET_RPC_URL))
        if not web3.is_connected():
            print(f"{Fore.RED}  ✖ {'Lỗi: Không thể kết nối RPC' if language == 'vi' else 'Error: Failed to connect to RPC'}{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}  ✔ {'Thành công: Đã kết nối mạng Somnia Testnet' if language == 'vi' else 'Success: Connected to network Somnia Testnet'} │ Chain ID: {web3.eth.chain_id}{Style.RESET_ALL}")
        return web3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Lỗi: Kết nối Web3 thất bại' if language == 'vi' else 'Error: Web3 connection failed'}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm tạo bytecode mint
def bytecode_mint_pongping(address: str) -> str:
    address_clean = address.replace("0x", "").lower()
    return f"0x40c10f19000000000000000000000000{address_clean}00000000000000000000000000000000000000000000003635c9adc5dea00000"

# Hàm mint $PING
async def mint_pongping(web3: Web3, private_key: str, wallet_index: int, language: str) -> bool:
    try:
        account = web3.eth.account.from_key(private_key)
        address = account.address

        # Thông tin hợp đồng
        CONTRACT_ADDRESS = "0xbecd9b5f373877881d91cbdbaf013d97eb532154"
        
        # Kiểm tra số dư ETH
        balance = web3.eth.get_balance(address)
        print(f"{Fore.YELLOW}  ℹ {'Thông tin' if language == 'vi' else 'Info'}: Ví: {wallet_index} │ {'Số dư STT' if language == 'vi' else 'STT balance'}: {web3.from_wei(balance, 'ether')} STT{Style.RESET_ALL}")
        if balance < web3.to_wei(0.001, 'ether'):
            print(f"{Fore.YELLOW}  ⚠ {'Cảnh báo' if language == 'vi' else 'Warning'}: Ví: {wallet_index} │ {'Không đủ STT' if language == 'vi' else 'Insufficient STT'}: {address}{Style.RESET_ALL}")
            return False

        # Xây dựng giao dịch
        nonce = web3.eth.get_transaction_count(address)
        gas_price = web3.eth.gas_price
        tx = {
            'to': Web3.to_checksum_address(CONTRACT_ADDRESS),
            'value': 0,
            'data': bytecode_mint_pongping(address),
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': gas_price,
            'chainId': web3.eth.chain_id
        }

        # Ước tính gas
        try:
            gas_estimate = web3.eth.estimate_gas(tx)
            print(f"{Fore.YELLOW}  ℹ {'Thông tin' if language == 'vi' else 'Info'}: Ví: {wallet_index} │ {'Gas ước tính' if language == 'vi' else 'Estimated gas'}: {gas_estimate}{Style.RESET_ALL}")
            tx['gas'] = gas_estimate + 10000  # Thêm buffer
        except Exception as e:
            print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: Ví: {wallet_index} │ {'Ước tính gas thất bại' if language == 'vi' else 'Gas estimation failed'}: {str(e)}{Style.RESET_ALL}")

        # Ký và gửi giao dịch
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"{Fore.GREEN}  ✔ {'Thành công' if language == 'vi' else 'Success'}: Ví: {wallet_index} │ {'Đã gửi giao dịch' if language == 'vi' else 'Tx sent'}: {SOMNIA_TESTNET_EXPLORER_URL}/tx/0x{tx_hash.hex()}{Style.RESET_ALL}")
        
        # Chờ xác nhận
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {'Thành công' if language == 'vi' else 'Success'}: Ví: {wallet_index} │ {'Đã mint 1000 $PING' if language == 'vi' else 'Minted 1000 $PING successfully'}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: Ví: {wallet_index} │ {'Mint thất bại' if language == 'vi' else 'Mint failed'}{Style.RESET_ALL}")
            return False

    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: Ví: {wallet_index} │ {'Xử lý thất bại' if language == 'vi' else 'Processing failed'}: {str(e)}{Style.RESET_ALL}")
        return False

# Hàm chính chạy mintping
async def run_mintping(language: str):
    # Thông báo bắt đầu với khung
    print_border(f"{'BẮT ĐẦU MINT $PING' if language == 'vi' else 'START MINTING $PING'}", Fore.CYAN)
    
    # Tải private keys
    private_keys = load_private_keys(language=language)
    if SHUFFLE_WALLETS:
        private_keys = shuffle_wallets(private_keys)
    print(f"\n{Fore.YELLOW}  ℹ {'Thông tin' if language == 'vi' else 'Info'}: {'Tìm thấy' if language == 'vi' else 'Found'} {len(private_keys)} {'ví' if language == 'vi' else 'wallets'}{Style.RESET_ALL}")
    
    if not private_keys:
        print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: {'Không có ví nào để mint' if language == 'vi' else 'No wallets to mint'}{Style.RESET_ALL}")
        return
    
    # Kết nối Web3
    web3 = connect_web3(language)
    print()  # Thêm dòng trống
    
    # Mint cho từng ví
    successful_mints = 0
    for i, private_key in enumerate(private_keys, 1):
        print(f"{Fore.CYAN}  --- {'Xử lý ví:' if language == 'vi' else 'Processing wallet:'} {i}/{len(private_keys)} ---{Style.RESET_ALL}")
        print('')
        if await mint_pongping(web3, private_key, i, language):
            successful_mints += 1
        
        # Ngủ ngẫu nhiên nếu không phải ví cuối cùng
        if i < len(private_keys):
            delay = get_random_int(MINT_PONGPING_SLEEP_RANGE[0], MINT_PONGPING_SLEEP_RANGE[1])
            print(f"\n{Fore.YELLOW}  ℹ {'Thông tin' if language == 'vi' else 'Info'}: {'Ngủ' if language == 'vi' else 'Sleeping for'} {delay} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print()  # Thêm dòng trống sau mỗi ví

    # Thông báo hoàn thành với khung
    print_border(f"{'HOÀN THÀNH: ' if language == 'vi' else 'COMPLETED: '}{successful_mints}/{len(private_keys)} {'ví thành công' if language == 'vi' else 'wallets successful'}", Fore.GREEN)

if __name__ == "__main__":
    asyncio.run(run_mintping('en'))  # Ngôn ngữ mặc định là English nếu chạy trực tiếp
