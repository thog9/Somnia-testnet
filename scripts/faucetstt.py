import os
import asyncio
import random
import json
import aiohttp
from aiohttp_socks import ProxyConnector
from colorama import init, Fore, Style
from web3 import Web3

# Khởi tạo colorama
init(autoreset=True)

# Constants
FAUCET_API_URL = "https://testnet.somnia.network/api/faucet"
IP_CHECK_URL = "https://api.ipify.org?format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://testnet.somnia.network",
    "referer": "https://testnet.somnia.network/",
}

# Từ vựng song ngữ
LANG = {
    'vi': {
        'title': 'FAUCET SOMNIA TESTNET',
        'info': 'Thông tin',
        'found_addresses': 'Tìm thấy {count} địa chỉ trong addressFaucet.txt',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'processing_address': 'XỬ LÝ ĐỊA CHỈ',
        'init_faucet': '🚀 Khởi tạo Faucet cho địa chỉ - [{address}]',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'success': '✅ Faucet đã được yêu cầu thành công cho địa chỉ - [{address}]',
        'api_response': '🔗 Phản hồi API: {response}',
        'failure': '⚠️ Yêu cầu Faucet thất bại với mã - [{code}] Phản hồi API: {response}',
        'retrying': '🔄 Thử lại sau {delay:.2f} giây...',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'no_addresses': 'Không tìm thấy địa chỉ trong addressFaucet.txt',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'completed': '✅ Đã hoàn tất yêu cầu Faucet!',
        'error': 'Lỗi',
        'invalid_proxy': '⚠️ Proxy không hợp lệ: {proxy}',
        'rate_limit': '⚠️ Đã vượt quá giới hạn yêu cầu (rate limit), thử lại sau',
        'wait_24h': '⚠️ Vui lòng đợi 24 giờ giữa các yêu cầu',
        'register_first': '⚠️ Đăng ký tài khoản Somnia trước rồi quay lại yêu cầu token'
    },
    'en': {
        'title': 'SOMNIA TESTNET FAUCET',
        'info': 'Info',
        'found_addresses': 'Found {count} addresses in addressFaucet.txt',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'processing_address': 'PROCESSING ADDRESS',
        'init_faucet': '🚀 Initializing Faucet for address - [{address}]',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'success': '✅ Faucet successfully claimed for address - [{address}]',
        'api_response': '🔗 API Response: {response}',
        'failure': '⚠️ Faucet request failed with code - [{code}] API Response: {response}',
        'retrying': '🔄 Retrying after {delay:.2f} seconds...',
        'no_proxy': 'None',
        'unknown': 'Unknown',
        'no_addresses': 'No addresses found in addressFaucet.txt',
        'no_proxies': 'No proxies found in proxies.txt',
        'completed': '✅ Faucet claim completed!',
        'error': 'Error',
        'invalid_proxy': '⚠️ Invalid proxy: {proxy}',
        'rate_limit': '⚠️ Rate limit exceeded, try again later',
        'wait_24h': '⚠️ Please wait 24 hours between requests',
        'register_first': '⚠️ Register an account with Somnia first, then request tokens'
    }
}

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=80):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * 80}{Style.RESET_ALL}")

# Hàm đọc địa chỉ từ addressFaucet.txt
def load_addresses(file_path: str = "addressFaucet.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED} ✖ {LANG[language]['no_addresses']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm địa chỉ vào đây, mỗi địa chỉ trên một dòng\n# Ví dụ: 0x1234567890abcdef1234567890abcdef1234567890\n")
            return []
        
        addresses = []
        with open(file_path, 'r') as f:
            for line in f:
                addr = line.strip()
                if addr and not addr.startswith('#') and Web3.is_address(addr):
                    addresses.append(Web3.to_checksum_address(addr))
        
        if not addresses:
            print(f"{Fore.RED} ✖ {LANG[language]['no_addresses']}{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW} ℹ {LANG[language]['found_addresses'].format(count=len(addresses))}{Style.RESET_ALL}")
        return addresses
    except Exception as e:
        print(f"{Fore.RED} ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

# Hàm đọc proxies từ proxies.txt
def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW} ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm proxy vào đây, mỗi proxy trên một dòng\n# Ví dụ: socks5://user:pass@host:port hoặc http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW} ⚠ {LANG[language]['no_proxies']}. Dùng không proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW} ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED} ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
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
                    print(f"{Fore.YELLOW} {LANG[language]['invalid_proxy'].format(proxy=proxy)}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW} {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return LANG[language]['unknown']

# Hàm yêu cầu faucet
async def claim_faucet(address: str, proxy: str = None, language: str = 'en', max_retries: int = 3):
    for attempt in range(max_retries):
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
                        raise ValueError(f"Invalid proxy format: {proxy}")
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(FAUCET_API_URL, json={"address": address}, headers=HEADERS) as response:
                        data = await response.json()
                        if response.status == 200:
                            return data
                        elif response.status == 403:
                            raise Exception(403, "First register an account with Somnia")
                        elif "error" in data:
                            if "24 hours" in data["error"]:
                                raise Exception(response.status, "Please wait 24 hours between requests")
                            elif "Rate limit exceeded" in data["error"]:
                                raise Exception(response.status, "Rate limit exceeded")
                            else:
                                raise Exception(response.status, data.get("details", str(data)))
                        else:
                            raise Exception(response.status, await response.text())
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(FAUCET_API_URL, json={"address": address}, headers=HEADERS) as response:
                        data = await response.json()
                        if response.status == 200:
                            return data
                        elif response.status == 403:
                            raise Exception(403, "First register an account with Somnia")
                        elif "error" in data:
                            if "24 hours" in data["error"]:
                                raise Exception(response.status, "Please wait 24 hours between requests")
                            elif "Rate limit exceeded" in data["error"]:
                                raise Exception(response.status, "Rate limit exceeded")
                            else:
                                raise Exception(response.status, data.get("details", str(data)))
                        else:
                            raise Exception(response.status, await response.text())
        except Exception as e:
            code = e.args[0] if len(e.args) > 0 else "Unknown"
            response = e.args[1] if len(e.args) > 1 else str(e)
            if "try again" in response.lower() and attempt < max_retries - 1:
                delay = random.uniform(5, 15)
                print(f"{Fore.YELLOW} {LANG[language]['retrying'].format(delay=delay)}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            raise Exception(code, response)

# Hàm xử lý từng địa chỉ
async def process_address(address: str, proxy: str = None, language: str = 'en'):
    print(f"{Fore.CYAN} {LANG[language]['init_faucet'].format(address=address)}{Style.RESET_ALL}")
    
    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN} {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")
    
    try:
        api_response = await claim_faucet(address, proxy, language)
        print(f"{Fore.GREEN} {LANG[language]['success'].format(address=address)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} {LANG[language]['api_response'].format(response=json.dumps(api_response))}{Style.RESET_ALL}")
        print()
    except Exception as e:
        code, response = e.args[0], e.args[1]
        if code == 403:
            print(f"{Fore.RED} {LANG[language]['register_first']}{Style.RESET_ALL}")
        elif "24 hours" in response:
            print(f"{Fore.YELLOW} {LANG[language]['wait_24h']}{Style.RESET_ALL}")
        elif "Rate limit" in response:
            print(f"{Fore.YELLOW} {LANG[language]['rate_limit']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED} {LANG[language]['failure'].format(code=code, response=response)}{Style.RESET_ALL}")
        print()

# Hàm xử lý tất cả địa chỉ
async def process_addresses(addresses: list, proxies: list, language: str = 'en'):
    for i, address in enumerate(addresses, 1):
        print_border(f"{LANG[language]['processing_address']} {i}/{len(addresses)} - {address}", Fore.MAGENTA)
        print()
        
        proxy = proxies[i-1] if i-1 < len(proxies) else None
        await process_address(address, proxy, language)
        
        if i < len(addresses):
            delay = random.uniform(5, 15)
            print(f"{Fore.YELLOW} ℹ {'Tạm nghỉ' if language == 'vi' else 'Pausing'} {delay:.2f} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()

# Hàm chính
async def run_faucetstt(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    addresses = load_addresses('addressFaucet.txt', language)
    if not addresses:
        return

    proxies = load_proxies('proxies.txt', language)
    print()
    
    await process_addresses(addresses, proxies, language)
    
    print_border(LANG[language]['completed'], Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_faucetstt('vi'))
