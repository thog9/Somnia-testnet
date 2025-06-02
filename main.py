import os
import sys
import asyncio
from colorama import init, Fore, Style
import inquirer

# Khởi tạo colorama
init(autoreset=True)

# Độ rộng viền cố định
BORDER_WIDTH = 80

# Hàm hiển thị viền đẹp mắt
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."  # Cắt dài và thêm "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

# Hàm hiển thị banner
def _banner():
    banner = r"""


░██████╗░█████╗░███╗░░░███╗███╗░░██╗██╗░█████╗░  ████████╗███████╗░██████╗████████╗███╗░░██╗███████╗████████╗
██╔════╝██╔══██╗████╗░████║████╗░██║██║██╔══██╗  ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝████╗░██║██╔════╝╚══██╔══╝
╚█████╗░██║░░██║██╔████╔██║██╔██╗██║██║███████║  ░░░██║░░░█████╗░░╚█████╗░░░░██║░░░██╔██╗██║█████╗░░░░░██║░░░
░╚═══██╗██║░░██║██║╚██╔╝██║██║╚████║██║██╔══██║  ░░░██║░░░██╔══╝░░░╚═══██╗░░░██║░░░██║╚████║██╔══╝░░░░░██║░░░
██████╔╝╚█████╔╝██║░╚═╝░██║██║░╚███║██║██║░░██║  ░░░██║░░░███████╗██████╔╝░░░██║░░░██║░╚███║███████╗░░░██║░░░
╚═════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░╚═╝  ░░░╚═╝░░░╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══╝╚══════╝░░░╚═╝░░░


    """
    print(f"{Fore.GREEN}{banner:^80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
    print_border("SOMNIA TESTNET", Fore.GREEN)
    print(f"{Fore.YELLOW}│ {'Liên hệ / Contact'}: {Fore.CYAN}https://t.me/thog099{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Discord'}: {Fore.CYAN}https://discord.gg/MnmYBKfHQf{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}│ {'Channel Telegram'}: {Fore.CYAN}https://t.me/thogairdrops{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

# Hàm xóa màn hình
def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Các hàm giả lập cho các lệnh (cần triển khai thực tế)

async def run_faucetstt(language: str):
    from scripts.faucetstt import run_faucetstt as faucetstt_run
    await faucetstt_run(language)

async def run_sendtx(language: str):
    from scripts.sendtx import run_sendtx as sendtx_run
    await sendtx_run(language)

async def run_deploytoken(language: str):
    from scripts.deploytoken import run_deploytoken as deploytoken_run
    await deploytoken_run(language)

async def run_sendtoken(language: str):
    from scripts.sendtoken import run_sendtoken as sendtoken_run
    await sendtoken_run(language)

async def run_deploynft(language: str):
    from scripts.deploynft import run_deploynft as deploynft_run
    await deploynft_run(language)

async def run_mintpong(language: str):
    from scripts.mintpong import run_mintpong as mintpong_run
    await mintpong_run(language)

async def run_mintping(language: str):
    from scripts.mintping import run_mintping as mintping_run
    await mintping_run(language)

async def run_swappong(language: str):
    from scripts.swappong import run_swappong as swappong_run
    await swappong_run(language)

async def run_swapping(language: str):
    from scripts.swapping import run_swapping as swapping_run
    await swapping_run(language)

async def run_conftnft(language: str):
    from scripts.conftnft import run_conftnft as conftnft_run
    await conftnft_run(language)

async def run_mintsusdt(language: str):
    from scripts.mintsusdt import run_mintsusdt as mintsusdt_run
    await mintsusdt_run(language)

async def run_buymeme(language: str):
    from scripts.buymeme import run_buymeme as buymeme_run
    await buymeme_run(language)

async def run_sellmeme(language: str):
    from scripts.sellmeme import run_sellmeme as sellmeme_run
    await sellmeme_run(language)

async def run_fun(language: str):
    from scripts.fun import run_fun as fun_run
    await fun_run(language)

async def run_lovesomini(language: str):
    from scripts.lovesomini import run_lovesomini as lovesomini_run
    await lovesomini_run(language)

async def run_mintnerzo(language: str):
    from scripts.mintnerzo import run_mintnerzo as mintnerzo_run
    await mintnerzo_run(language)

async def run_mintaura(language: str):
    from scripts.mintaura import run_mintaura as mintaura_run
    await mintaura_run(language)

async def run_nftcollection(language: str):
    from scripts.nftcollection import run_nftcollection as nftcollection_run
    await nftcollection_run(language)

async def run_mintair(language: str):
    from scripts.mintair import run_mintair as mintair_run
    await mintair_run(language)

async def run_mintalze(language: str):
    from scripts.mintalze import run_mintalze as mintalze_run
    await mintalze_run(language)

async def run_quickswap(language: str):
    from scripts.quickswap import run_quickswap as quickswap_run
    await quickswap_run(language)

async def run_wrapquick(language: str):
    from scripts.wrapquick import run_wrapquick as wrapquick_run
    await wrapquick_run(language)

async def run_wrapsoex(language: str):
    from scripts.wrapsoex import run_wrapsoex as wrapsoex_run
    await wrapsoex_run(language)

async def run_mintomnihub(language: str):
    from scripts.mintomnihub import run_mintomnihub as mintomnihub_run
    await mintomnihub_run(language)

async def run_swapsoex(language: str):
    from scripts.swapsoex import run_swapsoex as swapsoex_run
    await swapsoex_run(language)

async def run_sopixel(language: str):
    from scripts.sopixel import run_sopixel as sopixel_run
    await sopixel_run(language)


async def cmd_exit(language: str):
    print_border(f"Exiting...", Fore.GREEN)
    sys.exit(0)

# Danh sách lệnh menu
SCRIPT_MAP = {
    "faucetstt": run_faucetstt,
    "sendtx": run_sendtx,
    "deploytoken": run_deploytoken,
    "sendtoken": run_sendtoken,
    "deploynft": run_deploynft,
    "mintpong": run_mintpong,
    "mintping": run_mintping,
    "swappong": run_swappong,
    "swapping": run_swapping,
    "conftnft": run_conftnft,
    "mintsusdt": run_mintsusdt,
    "buymeme": run_buymeme,
    "sellmeme": run_sellmeme,
    "fun": run_fun,
    "lovesomini": run_lovesomini,
    "mintnerzo": run_mintnerzo,
    "mintaura": run_mintaura,
    "nftcollection": run_nftcollection,
    "mintair": run_mintair,
    "mintalze": run_mintalze,
    "quickswap": run_quickswap,
    "wrapquick": run_wrapquick,
    "wrapsoex": run_wrapsoex,
    "mintomnihub": run_mintomnihub,
    "swapsoex": run_swapsoex,
    "sopixel": run_sopixel,
    "exit": cmd_exit
}

def get_available_scripts(language):
    scripts = {
        'vi': [
            {"name": "1. Faucet token $STT | Somnia Testnet", "value": "faucetstt", "locked": True},
            {"name": "2. Mint $PONG | Somnia Testnet", "value": "mintpong"},
            {"name": "3. Mint $PING | Somnia Testnet", "value": "mintping"},
            {"name": "4. QuickSwap [ STT | USDC | WETH | WSTT ] | Somnia Testnet", "value": "quickswap", "locked": True},
            {"name": "5. Somnia Exchange [ STT | USDT.g | NIA | WSTT ] | Somnia Testnet", "value": "swapsoex", "locked": True},   
            {"name": "6. Wrap/Unwrap STT -> QuickSwap | Somnia Testnet", "value": "quickswap"},
            {"name": "7. Wrap/Unwrap STT -> Somnia Exchange | Somnia Testnet", "value": "wrapsoex"},
            {"name": "8. Swap $PONG -> $PING | Somnia Testnet", "value": "swappong", "locked": True},
            {"name": "9. Swap $PING -> $PONG | Somnia Testnet", "value": "swapping", "separator": True, "locked": True},
            {"name": "10. Mint NFT Community Member of Somnia (CMS - CoNFT) | Somnia Testnet", "value": "conftnft", "locked": True},
            #{"name": "11. Mint 1000 sUSDT [END] | Somnia Testnet", "value": "mintsusdt"},
            #{"name": "12. Memecoin Trading - Mua Memecoin ( SOMI / SMSM / SMI ) [END] | Somnia Testnet", "value": "buymeme"},
            #{"name": "13. Memecoin Trading - Bán Memecoin ( SOMI / SMSM / SMI )[END] | Somnia Testnet", "value": "sellmeme"},
            {"name": "11. Quills Fun - Mint Tin Nhắn NFT | Somnia Testnet", "value": "fun", "locked": True},
            {"name": "12. Love Somini | Somnia Testnet", "value": "lovesomini", "locked": True},
            {"name": "13. Mint NFTs NERZO | Somnia Testnet", "value": "mintnerzo", "locked": True},
            {"name": "14. Mint Somni ✨ | Somnia Testnet", "value": "mintaura", "locked": True},
            {"name": "15. Mint ALZE | Somnia Testnet", "value": "mintalze", "locked": True},
            {"name": "16. Mint OmniHub [ OMNIHUB x SOMNIA | Somnia Cats ] | Somnia Testnet", "value": "mintomnihub", "locked": True},
            {"name": "17. Deploy Smart Contract Mintair | Somnia Testnet", "value": "mintair", "locked": True},
            {"name": "18. Deploy NFT - Quản lý bộ sưu tập NFT [ Tạo | Mint | Đốt ] | Somnia Testnet", "value": "nftcollection"},
            {"name": "19. Send TX ngẫu nhiên hoặc File (address.txt) | Somnia Testnet", "value": "sendtx"},
            {"name": "20. Deploy Token smart-contract | Somnia Testnet", "value": "deploytoken"},
            {"name": "21. Send Token ERC20 ngẫu nhiên hoặc File (addressERC20.txt) | Somnia Testnet", "value": "sendtoken"},
            {"name": "22. Tô màu Somnia Pixel | Somnia Testnet", "value": "sopixel"},

            {"name": "23. Exit", "value": "exit"},
            
        ],
        'en': [
            {"name": "1. Faucet token $STT", "value": "faucetstt", "locked": True},
            {"name": "2. Mint $PONG | Somnia Testnet", "value": "mintpong"},
            {"name": "3. Mint $PING | Somnia Testnet", "value": "mintping"},
            {"name": "4. QuickSwap [ STT | USDC | WETH | WSTT ] | Somnia Testnet", "value": "quickswap", "locked": True},
            {"name": "5. Somnia Exchange [ STT | USDT.g | NIA | WSTT ] | Somnia Testnet", "value": "swapsoex", "locked": True},   
            {"name": "6. Wrap/Unwrap STT -> QuickSwap | Somnia Testnet", "value": "wrapquick"},
            {"name": "7. Wrap/Unwrap STT -> Somnia Exchange | Somnia Testnet", "value": "wrapsoex"},     
            {"name": "8. Swap $PONG -> $PING | Somnia Testnet", "value": "swappong", "locked": True},
            {"name": "9. Swap $PING -> $PONG | Somnia Testnet", "value": "swapping", "separator": True, "locked": True},
            {"name": "10. Mint NFT Community Member of Somnia (CMS - CoNFT) | Somnia Testnet", "value": "conftnft", "locked": True},
            #{"name": "11. Mint 1000 sUSDT [END] | Somnia Testnet", "value": "mintsusdt"},
            #{"name": "12. Memecoin Trading - Buy Memecoin ( SOMI / SMSM / SMI ) [END] | Somnia Testnet", "value": "buymeme"},
            #{"name": "13. Memecoin Trading - Sell Memecoin ( SOMI / SMSM / SMI ) [END] | Somnia Testnet", "value": "sellmeme"},
            {"name": "11. Quills Fun - Mint Message NFT | Somnia Testnet", "value": "fun", "locked": True},
            {"name": "12. Love Somini | Somnia Testnet", "value": "lovesomini", "locked": True},
            {"name": "13. Mint NFTs NERZO | Somnia Testnet", "value": "mintnerzo", "locked": True},
            {"name": "14. Mint Somni ✨ | Somnia Testnet", "value": "mintaura", "locked": True},
            {"name": "15. Mint ALZE | Somnia Testnet", "value": "mintalze", "locked": True},
            {"name": "16. Mint OmniHub [ OMNIHUB x SOMNIA | Somnia Cats ] | Somnia Testnet", "value": "mintomnihub", "locked": True},
            {"name": "17. Deploy Smart Contract Mintair | Somnia Testnet", "value": "mintair", "locked": True},
            {"name": "18. Deploy NFT - Manage NFT Collection [ Create | Mint | Burn ] | Somnia Testnet", "value": "nftcollection"},
            {"name": "19. Send Random TX or File (address.txt) | Somnia Testnet", "value": "sendtx"},
            {"name": "20. Deploy Token smart-contract", "value": "deploytoken"},
            {"name": "21. Send Token ERC20 Random or File (addressERC20.txt) | Somnia Testnet", "value": "sendtoken"},
            {"name": "22. Somnia Pixel Color | Somnia Testnet", "value": "sopixel"},

            {"name": "23. Exit", "value": "exit"},
        ]
    }
    return scripts[language]

def run_script(script_func, language):
    """Chạy script bất kể nó là async hay không."""
    if asyncio.iscoroutinefunction(script_func):
        asyncio.run(script_func(language))
    else:
        script_func(language)

def select_language():
    while True:
        _clear()
        _banner()
        print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border("CHỌN NGÔN NGỮ / SELECT LANGUAGE", Fore.YELLOW)
        questions = [
            inquirer.List('language',
                          message=f"{Fore.CYAN}Vui lòng chọn / Please select:{Style.RESET_ALL}",
                          choices=[("1. Tiếng Việt", 'vi'), ("2. English", 'en')],
                          carousel=True)
        ]
        answer = inquirer.prompt(questions)
        if answer and answer['language'] in ['vi', 'en']:
            return answer['language']
        print(f"{Fore.RED}❌ {'Lựa chọn không hợp lệ / Invalid choice':^76}{Style.RESET_ALL}")

def main():
    _clear()
    _banner()
    language = select_language()

    messages = {
        "vi": {
            "running": "Đang thực thi: {}",
            "completed": "Đã hoàn thành: {}",
            "error": "Lỗi: {}",
            "press_enter": "Nhấn Enter để tiếp tục...",
            "menu_title": "MENU CHÍNH",
            "select_script": "Chọn script để chạy",
            "locked": "🔒 Script này bị khóa! Vui lòng vào group hoặc donate để mở khóa."
        },
        "en": {
            "running": "Running: {}",
            "completed": "Completed: {}",
            "error": "Error: {}",
            "press_enter": "Press Enter to continue...",
            "menu_title": "MAIN MENU",
            "select_script": "Select script to run",
            "locked": "🔒 This script is locked! Please join our group or donate to unlock."
        }
    }

    while True:
        _clear()
        _banner()
        print(f"{Fore.YELLOW}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
        print_border(messages[language]["menu_title"], Fore.YELLOW)
        print(f"{Fore.CYAN}│ {messages[language]['select_script'].center(BORDER_WIDTH - 4)} │{Style.RESET_ALL}")

        available_scripts = get_available_scripts(language)
        questions = [
            inquirer.List('script',
                          message=f"{Fore.CYAN}{messages[language]['select_script']}{Style.RESET_ALL}",
                          choices=[script["name"] for script in available_scripts],
                          carousel=True)
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            continue

        selected_script_name = answers['script']
        selected_script = next(script for script in available_scripts if script["name"] == selected_script_name)
        selected_script_value = selected_script["value"]

        if selected_script.get("locked"):
            _clear()
            _banner()
            print_border("SCRIPT BỊ KHÓA / LOCKED", Fore.RED)
            print(f"{Fore.YELLOW}{messages[language]['locked']}")
            print('')
            print(f"{Fore.CYAN}→ Telegram: https://t.me/thogairdrops")
            print(f"{Fore.CYAN}→ Donate: https://buymecafe.vercel.app{Style.RESET_ALL}")
            print('')
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        script_func = SCRIPT_MAP.get(selected_script_value)
        if script_func is None:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(f"{'Chưa triển khai / Not implemented'}: {selected_script_name}", Fore.RED)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
            continue

        try:
            print(f"{Fore.CYAN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["running"].format(selected_script_name), Fore.CYAN)
            run_script(script_func, language)
            print(f"{Fore.GREEN}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["completed"].format(selected_script_name), Fore.GREEN)
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")
        except Exception as e:
            print(f"{Fore.RED}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")
            print_border(messages[language]["error"].format(str(e)), Fore.RED)
            print('')
            input(f"{Fore.YELLOW}⏎ {messages[language]['press_enter']}{Style.RESET_ALL:^76}")

if __name__ == "__main__":
    main()
