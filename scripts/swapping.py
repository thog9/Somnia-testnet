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
SWAP_PONGPING_SLEEP_RANGE = [100, 300]  # [min, max] in seconds

# ABI cho token ERC20 (chỉ cần hàm approve và decimals)
TOKEN_ABI = [
    {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."  # Cắt dài và thêm "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị tiêu đề phân cách
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
                            key = '0x' + key
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
        print(f"{Fore.GREEN}  ✔ {'Thành công: Đã kết nối mạng Somnia Testnet' if language == 'vi' else 'Success: Connected to Somnia Testnet'} │ Chain ID: {web3.eth.chain_id}{Style.RESET_ALL}")
        return web3
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Lỗi: Kết nối Web3 thất bại' if language == 'vi' else 'Error: Web3 connection failed'}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm nhập số lượng swap
def get_swap_amount(language: str) -> float:
    print_border(f"{'NHẬP SỐ LƯỢNG $PING' if language == 'vi' else 'ENTER $PING AMOUNT'}", Fore.YELLOW)
    while True:
        try:
            amount = float(input(f"{Fore.YELLOW}  > {'Số lượng $PING muốn swap (ví dụ: 10)' if language == 'vi' else 'Amount of $PING to swap (e.g., 10)'}: {Style.RESET_ALL}"))
            if amount <= 0:
                print(f"{Fore.RED}  ✖ {'Lỗi: Số lượng phải lớn hơn 0' if language == 'vi' else 'Error: Amount must be greater than 0'}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  ✔ {'Đã chọn' if language == 'vi' else 'Selected'}: {amount} $PING{Style.RESET_ALL}")
                return amount
        except ValueError:
            print(f"{Fore.RED}  ✖ {'Lỗi: Vui lòng nhập số hợp lệ' if language == 'vi' else 'Error: Please enter a valid number'}{Style.RESET_ALL}")

# Hàm nhập số lần swap (mặc định 1)
def get_swap_times(language: str) -> int:
    print_border(f"{'NHẬP SỐ LẦN SWAP' if language == 'vi' else 'ENTER NUMBER OF SWAPS'}", Fore.YELLOW)
    while True:
        try:
            input_text = input(f"{Fore.YELLOW}  > {'Số lần swap cho mỗi ví (mặc định 1, nhấn Enter để dùng mặc định)' if language == 'vi' else 'Number of swaps per wallet (default 1, press Enter for default)'}: {Style.RESET_ALL}")
            if input_text.strip() == "":
                print(f"{Fore.GREEN}  ✔ {'Đã chọn mặc định' if language == 'vi' else 'Default selected'}: 1 {Style.RESET_ALL}")
                return 1
            times = int(input_text)
            if times <= 0:
                print(f"{Fore.RED}  ✖ {'Lỗi: Số lần phải lớn hơn 0' if language == 'vi' else 'Error: Number of swaps must be greater than 0'}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  ✔ {'Đã chọn' if language == 'vi' else 'Selected'}: {times} {'lần' if language == 'vi' else 'times'}{Style.RESET_ALL}")
                return times
        except ValueError:
            print(f"{Fore.RED}  ✖ {'Lỗi: Vui lòng nhập số nguyên hợp lệ' if language == 'vi' else 'Error: Please enter a valid integer'}{Style.RESET_ALL}")

# Hàm approve token
async def approve_token(web3: Web3, private_key: str, token_address: str, spender_address: str, amount: float, wallet_index: int, language: str):
    try:
        account = web3.eth.account.from_key(private_key)
        token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=TOKEN_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))

        tx = token_contract.functions.approve(
            Web3.to_checksum_address(spender_address),
            amount_wei
        ).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': web3.eth.gas_price
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {'Thành công' if language == 'vi' else 'Success'}: Ví {wallet_index} │ {'Đã approve' if language == 'vi' else 'Approved'} {amount} $PING │ {SOMNIA_TESTNET_EXPLORER_URL}/tx/0x{tx_hash.hex()}{Style.RESET_ALL}")
            return tx_hash.hex()
        else:
            print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: Ví {wallet_index} │ {'Approve thất bại' if language == 'vi' else 'Approve failed'}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: Ví {wallet_index} │ {'Approve thất bại' if language == 'vi' else 'Approve failed'}: {str(e)}{Style.RESET_ALL}")
        return None

# Hàm swap token
async def swap_token(web3: Web3, private_key: str, token_in: str, token_out: str, amount_in: float, recipient: str, wallet_index: int, language: str):
    try:
        account = web3.eth.account.from_key(private_key)
        swap_router_address = "0x6aac14f090a35eea150705f72d90e4cdc4a49b2c"
        fee = 500
        amount_out_minimum = int(amount_in * 0.999 * (10 ** 18))
        amount_in_wei = int(amount_in * (10 ** 18))

        SWAP_ROUTER_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            {"name": "tokenIn", "type": "address"},
                            {"name": "tokenOut", "type": "address"},
                            {"name": "fee", "type": "uint24"},
                            {"name": "recipient", "type": "address"},
                            {"name": "amountIn", "type": "uint256"},
                            {"name": "amountOutMinimum", "type": "uint256"},
                            {"name": "sqrtPriceLimitX96", "type": "uint160"}
                        ],
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "exactInputSingle",
                "outputs": [{"name": "amountOut", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

        swap_router = web3.eth.contract(address=Web3.to_checksum_address(swap_router_address), abi=SWAP_ROUTER_ABI)

        tx_data = swap_router.functions.exactInputSingle(
            (
                Web3.to_checksum_address(token_in),
                Web3.to_checksum_address(token_out),
                fee,
                recipient,
                amount_in_wei,
                amount_out_minimum,
                0
            )
        ).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
            'chainId': web3.eth.chain_id
        })

        signed_tx = web3.eth.account.sign_transaction(tx_data, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status == 1:
            print(f"{Fore.GREEN}  ✔ {'Thành công' if language == 'vi' else 'Success'}: Ví {wallet_index} │ {'Đã swap' if language == 'vi' else 'Swapped'} {amount_in} $PING -> $PONG │ {SOMNIA_TESTNET_EXPLORER_URL}/tx/0x{tx_hash.hex()}{Style.RESET_ALL}")
            return tx_hash.hex()
        else:
            print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: Ví {wallet_index} │ {'Swap thất bại' if language == 'vi' else 'Swap failed'}{Style.RESET_ALL}")
            return None
    except Exception as e:
        print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: Ví {wallet_index} │ {'Swap thất bại' if language == 'vi' else 'Swap failed'}: {str(e)}{Style.RESET_ALL}")
        return None

# Hàm chính chạy swapping
async def run_swapping(language: str):
    print()
    print_border(f"{'BẮT ĐẦU SWAP $PING -> $PONG' if language == 'vi' else 'START SWAPPING $PING -> $PONG'}", Fore.CYAN)
    print()

    private_keys = load_private_keys(language=language)
    if SHUFFLE_WALLETS:
        private_keys = shuffle_wallets(private_keys)
    print(f"{Fore.YELLOW}  ℹ {'Thông tin' if language == 'vi' else 'Info'}: {'Tìm thấy' if language == 'vi' else 'Found'} {len(private_keys)} {'ví' if language == 'vi' else 'wallets'}{Style.RESET_ALL}")
    print()

    if not private_keys:
        print(f"{Fore.RED}  ✖ {'Lỗi' if language == 'vi' else 'Error'}: {'Không có ví nào để swap' if language == 'vi' else 'No wallets to swap'}{Style.RESET_ALL}")
        return

    # Nhập số lượng và số lần swap
    amount = get_swap_amount(language)
    swap_times = get_swap_times(language)
    print_separator()

    web3 = connect_web3(language)
    print()

    successful_swaps = 0
    for i, private_key in enumerate(private_keys, 1):
        print_border(f"{'XỬ LÝ VÍ' if language == 'vi' else 'PROCESSING WALLET'} {i}/{len(private_keys)}", Fore.MAGENTA)
        print()

        token_in = "0xbecd9b5f373877881d91cbdbaf013d97eb532154"  # $PING
        token_out = "0x7968ac15a72629e05f41b8271e4e7292e0cc9f90"  # $PONG
        spender_address = "0x6aac14f090a35eea150705f72d90e4cdc4a49b2c"  # Swap Router
        recipient = web3.eth.account.from_key(private_key).address

        # Approve token
        approve_tx = await approve_token(web3, private_key, token_in, spender_address, amount * swap_times, i, language)
        if not approve_tx:
            print_separator()
            continue
        print()

        # Thực hiện swap theo số lần yêu cầu
        for swap_iter in range(swap_times):
            print(f"{Fore.CYAN}  > {'Thực hiện swap lần' if language == 'vi' else 'Performing swap'} {swap_iter + 1}/{swap_times}{Style.RESET_ALL}")
            swap_tx = await swap_token(web3, private_key, token_in, token_out, amount, recipient, i, language)
            if swap_tx:
                successful_swaps += 1
            if swap_iter < swap_times - 1:
                delay = get_random_int(10, 30)
                print(f"{Fore.YELLOW}  ℹ {'Tạm nghỉ' if language == 'vi' else 'Pausing'} {delay} {'giây trước lần swap tiếp theo' if language == 'vi' else 'seconds before next swap'}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
            print()

        if i < len(private_keys):
            delay = get_random_int(SWAP_PONGPING_SLEEP_RANGE[0], SWAP_PONGPING_SLEEP_RANGE[1])
            print(f"{Fore.YELLOW}  ℹ {'Chờ' if language == 'vi' else 'Waiting'} {delay} {'giây trước khi xử lý ví tiếp theo' if language == 'vi' else 'seconds before processing next wallet'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()

    print()
    print_border(f"{'HOÀN THÀNH' if language == 'vi' else 'COMPLETED'}: {successful_swaps}/{len(private_keys) * swap_times} {'LẦN SWAP THÀNH CÔNG' if language == 'vi' else 'SWAPS SUCCESSFUL'}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_swapping('en'))  # Ngôn ngữ mặc định là English
