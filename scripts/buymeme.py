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
ROUTER_ADDRESS = "0x6aac14f090a35eea150705f72d90e4cdc4a49b2c"
SPENDER_ADDRESS = "0x6aac14f090a35eea150705f72d90e4cdc4a49b2c"
SUSDT_ADDRESS = "0x65296738D4E5edB1515e40287B6FDf8320E6eE04"
TOKENS = {
    "SOMI": {"address": "0x7a7045415f3682C3349E4b68d2940204b81fFF33", "price": 0.99960},
    "SMSM": {"address": "0x6756B4542d545270CacF1F15C3b7DefE589Ba1aa", "price": 0.99959},
    "SMI": {"address": "0xC9005DD5C562bDdEF1Cf3C90Ad5B1Bf54fB8aa9d", "price": 0.99959},
    "sUSDT": {"address": "0x65296738D4E5edB1515e40287B6FDf8320E6eE04", "price": 1.0}
}

# ABI cho token ERC-20 và Router
TOKEN_ABI = [
    {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

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

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': 'MUA TOKEN MEME - SOMNIA TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'wallets': 'ví',
        'processing_wallet': 'XỬ LÝ VÍ',
        'select_token': 'Chọn token để mua (1: SOMI │ 2: SMSM │ 3: SMI): ',
        'enter_amount': 'Nhập số lượng sUSDT để mua token: ',
        'approve_success': 'Đã approve {amount} sUSDT thành công!',
        'buy_success': 'Đã mua {token} bằng {amount} sUSDT thành công!',
        'approve_failure': 'Approve thất bại',
        'buy_failure': 'Mua thất bại',
        'balance': 'Số dư        : {balance} {token}',
        'price': 'Giá          : {price} sUSDT/{token}',
        'market_cap': 'Vốn hóa      : {market_cap} sUSDT',
        'insufficient_balance': 'Số dư sUSDT không đủ: {balance} < {amount}',
        'pausing': 'Tạm nghỉ',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO DỊCH THÀNH CÔNG',
        'error': 'Lỗi',
        'connect_success': 'Thành công: Đã kết nối mạng Somnia Testnet',
        'invalid_input': 'Lựa chọn không hợp lệ',
        'pvkey_not_found': 'File pvkey.txt không tồn tại',
        'pvkey_empty': 'Không tìm thấy private key hợp lệ'
    },
    'en': {
        'title': 'BUY MEME TOKEN - SOMNIA TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'select_token': 'Select token to buy (1: SOMI │ 2: SMSM │ 3: SMI): ',
        'enter_amount': 'Enter sUSDT amount to buy token: ',
        'approve_success': 'Successfully approved {amount} sUSDT!',
        'buy_success': 'Successfully bought {token} with {amount} sUSDT!',
        'approve_failure': 'Approve failed',
        'buy_failure': 'Buy failed',
        'balance': 'Balance       : {balance} {token}',
        'price': 'Price         : {price} sUSDT/{token}',
        'market_cap': 'Market Cap   : {market_cap} sUSDT',
        'insufficient_balance': 'Insufficient sUSDT balance: {balance} < {amount}',
        'pausing': 'Pausing',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL',
        'error': 'Error',
        'connect_success': 'Success: Connected to Somnia Testnet',
        'invalid_input': 'Invalid selection',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found'
    }
}

# Hàm hiển thị viền
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = f" {text} "
    padded_text = text.center(width - 2, "─")
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")
    print()

# Hàm hiển thị phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
    print()

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

# Hàm đọc private keys từ pvkey.txt
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
                        valid_keys.append((i, key))
        
        if not valid_keys:
            print(f"{Fore.RED}  ✖ {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
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
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm lấy thông tin token
def get_token_info(w3: Web3, token_symbol: str, wallet_address: str, language: str = 'en'):
    contract = w3.eth.contract(address=Web3.to_checksum_address(TOKENS[token_symbol]["address"]), abi=TOKEN_ABI)
    try:
        balance = contract.functions.balanceOf(wallet_address).call() / 10**contract.functions.decimals().call()
        total_supply = contract.functions.totalSupply().call() / 10**contract.functions.decimals().call()
        price = TOKENS[token_symbol]["price"]
        market_cap = price * total_supply
        print(f"{Fore.YELLOW}    {LANG[language]['balance'].format(balance=f'{balance:,.2f}', token=token_symbol)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}    {LANG[language]['price'].format(price=f'{price:,.5f}', token=token_symbol)}{Style.RESET_ALL}")
        if token_symbol != "sUSDT":  # Chỉ hiển thị Market Cap cho token không phải sUSDT
            total_supply = contract.functions.totalSupply().call() / 10**contract.functions.decimals().call()
            market_cap = price * total_supply
            print(f"{Fore.YELLOW}    {LANG[language]['market_cap'].format(market_cap=f'{market_cap:,.2f}')}{Style.RESET_ALL}")
        print()
        return balance
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return 0

# Hàm chọn token để mua
def select_token(language: str = 'en'):
    print_border("CHỌN TOKEN ĐỂ MUA / SELECT TOKEN TO BUY", Fore.YELLOW)
    print(f"{Fore.CYAN}  1. Somini (SOMI){Style.RESET_ALL}")
    print(f"{Fore.CYAN}  2. Somsom (SMSM){Style.RESET_ALL}")
    print(f"{Fore.CYAN}  3. Somi (SMI){Style.RESET_ALL}")
    print()
    while True:
        choice = input(f"{Fore.YELLOW}  > {LANG[language]['select_token']}{Style.RESET_ALL}")
        if choice == "1":
            return "SOMI"
        elif choice == "2":
            return "SMSM"
        elif choice == "3":
            return "SMI"
        else:
            print(f"{Fore.RED}  ✖ {LANG[language]['invalid_input']}{Style.RESET_ALL}")

# Hàm nhập số lượng sUSDT
def get_amount(language: str = 'en'):
    while True:
        try:
            amount = float(input(f"{Fore.YELLOW}  > {LANG[language]['enter_amount']}{Style.RESET_ALL}"))
            if amount <= 0:
                print(f"{Fore.RED}  ✖ {LANG[language]['error']}: Amount must be greater than 0{Style.RESET_ALL}")
            else:
                return amount
        except ValueError:
            print(f"{Fore.RED}  ✖ {LANG[language]['error']}: Invalid number{Style.RESET_ALL}")

# Hàm approve token
async def approve_token(w3: Web3, private_key: str, token_address: str, spender_address: str, amount: float, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    token_contract = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=TOKEN_ABI)
    decimals = token_contract.functions.decimals().call()
    amount_wei = int(amount * (10 ** decimals))

    tx = token_contract.functions.approve(
        Web3.to_checksum_address(spender_address),
        amount_wei
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    if receipt.status == 1:
        print(f"{Fore.GREEN}  ✔ {LANG[language]['approve_success'].format(amount=f'{amount:,.2f}')}{Style.RESET_ALL}")
        print()
        return tx_hash.hex()
    else:
        print(f"{Fore.RED}  ✖ {LANG[language]['approve_failure']}{Style.RESET_ALL}")
        return None

# Hàm mua token
async def buy_token(w3: Web3, private_key: str, token_symbol: str, amount: float, wallet_index: int, language: str = 'en'):
    account = Account.from_key(private_key)
    token_in = SUSDT_ADDRESS
    token_out = TOKENS[token_symbol]["address"]
    swap_router = w3.eth.contract(address=Web3.to_checksum_address(ROUTER_ADDRESS), abi=SWAP_ROUTER_ABI)
    
    susdt_contract = w3.eth.contract(address=Web3.to_checksum_address(token_in), abi=TOKEN_ABI)
    decimals = susdt_contract.functions.decimals().call()
    amount_in_wei = int(amount * (10 ** decimals))
    amount_out_minimum = int(amount * 0.95 * (10 ** decimals))  # 5% slippage

    tx_data = swap_router.functions.exactInputSingle(
        (
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out),
            500,  # Fee
            account.address,
            amount_in_wei,
            amount_out_minimum,
            0
        )
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID
    })

    signed_tx = w3.eth.account.sign_transaction(tx_data, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_link = f"{EXPLORER_URL}{tx_hash.hex()}"
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    if receipt.status == 1:
        print(f"{Fore.GREEN}  ✔ {LANG[language]['buy_success'].format(token=token_symbol, amount=f'{amount:,.2f}')} │ Tx: {tx_link}{Style.RESET_ALL}")
        print()
        return True
    else:
        print(f"{Fore.RED}  ✖ {LANG[language]['buy_failure']} │ Tx: {tx_link}{Style.RESET_ALL}")
        return False

# Hàm chính
async def run_buymeme(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    if not private_keys:
        return

    w3 = connect_web3(language)
    print()
    token_symbol = select_token(language)
    amount = get_amount(language)
    print_separator()

    successful_buys = 0
    total_wallets = len(private_keys)

    random.shuffle(private_keys)
    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        
        account = Account.from_key(private_key)
        susdt_balance = get_token_info(w3, "sUSDT", account.address, language)
        if susdt_balance < amount:
            print(f"{Fore.RED}  ✖ {LANG[language]['insufficient_balance'].format(balance=f'{susdt_balance:,.2f}', amount=f'{amount:,.2f}')}{Style.RESET_ALL}")
            print_separator()
            continue
        
        get_token_info(w3, token_symbol, account.address, language)
        approve_tx = await approve_token(w3, private_key, SUSDT_ADDRESS, SPENDER_ADDRESS, amount, i, language)
        if not approve_tx:
            print_separator()
            continue
        
        if await buy_token(w3, private_key, token_symbol, amount, i, language):
            successful_buys += 1
        
        if i < len(private_keys):
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            print()
            await asyncio.sleep(delay)
        print_separator()
    
    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_buys, total=total_wallets)}", Fore.GREEN)

if __name__ == "__main__":
    asyncio.run(run_buymeme('vi'))
