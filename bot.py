from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Xage:
    def __init__(self) -> None:
        self.BASE_API = "https://xage.app/api"
        self.REF_CODE = "2AE97610" # U can change it with yours.
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.sessions = {}
        self.ua_index = 0
        
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}X Age {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_cookies(self):
        filename = "cookies.txt"
        try:
            with open(filename, 'r') as file:
                cookies = [line.strip() for line in file if line.strip()]
            return cookies
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Cookies: {e}{Style.RESET_ALL}")
            return None
        
    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def get_next_user_agent(self):
        ua = self.USER_AGENTS[self.ua_index]
        self.ua_index = (self.ua_index + 1) % len(self.USER_AGENTS)
        return ua
    
    def initialize_headers(self, cookie: str):
        if cookie not in self.HEADERS:
            self.HEADERS[cookie] = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Cookie": cookie,
                "Origin": "https://xage.app",
                "Pragma": "no-cache",
                "Referer": "https://xage.app/app",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": self.get_next_user_agent()
            }
        return self.HEADERS[cookie]
    
    def get_session(self, cookie: str, proxy_url=None, timeout=60):
        if cookie not in self.sessions:
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            
            session = ClientSession(
                connector=connector,
                timeout=ClientTimeout(total=timeout)
            )
            
            self.sessions[cookie] = {
                'session': session,
                'proxy': proxy,
                'proxy_auth': proxy_auth
            }
        
        return self.sessions[cookie]
    
    async def close_session(self, cookie: str):
        if cookie in self.sessions:
            await self.sessions[cookie]['session'].close()
            del self.sessions[cookie]
    
    async def close_all_sessions(self):
        for cookie in list(self.sessions.keys()):
            await self.close_session(cookie)
    
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return proxy_choice, rotate_proxy

    async def ensure_ok(self, response):
        if response.status >= 400:
            raise Exception(f"HTTP {response.status}:{await response.text()}")
    
    async def check_connection(self, cookie: str, proxy_url=None):
        url = "https://api.ipify.org?format=json"

        try:
            session_info = self.get_session(cookie, proxy_url, 15)
            session = session_info["session"]
            proxy = session_info["proxy"]
            proxy_auth = session_info["proxy_auth"]

            async with session.get(
                url=url, proxy=proxy, proxy_auth=proxy_auth
            ) as response:
                await self.ensure_ok(response)
                return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status:{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def user_data(self, cookie: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/auth/me"
        headers = self.initialize_headers(cookie)

        for attempt in range(retries):
            try:
                session_info = self.get_session(cookie, proxy_url)
                session = session_info["session"]
                proxy = session_info["proxy"]
                proxy_auth = session_info["proxy_auth"]

                async with session.get(
                    url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth
                ) as response:
                    await self.ensure_ok(response)
                    return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Points:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Points {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def set_referral(self, cookie: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/referral/set"
        headers = self.initialize_headers(cookie)
        headers["Content-Type"] = "application/json"
        payload = {"code": self.REF_CODE}

        for attempt in range(retries):
            try:
                session_info = self.get_session(cookie, proxy_url)
                session = session_info["session"]
                proxy = session_info["proxy"]
                proxy_auth = session_info["proxy_auth"]

                async with session.post(
                    url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth
                ) as response:
                    if response.status == 400: return None
                    response.raise_for_status()
                    return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Apply Ref {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def task_lists(self, cookie: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/tasks"
        headers = self.initialize_headers(cookie)

        for attempt in range(retries):
            try:
                session_info = self.get_session(cookie, proxy_url)
                session = session_info["session"]
                proxy = session_info["proxy"]
                proxy_auth = session_info["proxy_auth"]

                async with session.get(
                    url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Tasks :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Available Tasks {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def complete_task(self, cookie: str, task_id: str, task_name: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/tasks/{task_id}/complete"
        headers = self.initialize_headers(cookie)
        headers["Content-Type"] = "application/json"

        for attempt in range(retries):
            try:
                session_info = self.get_session(cookie, proxy_url)
                session = session_info["session"]
                proxy = session_info["proxy"]
                proxy_auth = session_info["proxy_auth"]

                async with session.post(
                    url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{task_name}{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Completed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def process_check_connection(self, cookie: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(cookie) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(cookie, proxy)
            if is_valid: return True

            if rotate_proxy:
                await self.close_session(cookie)
                proxy = self.rotate_proxy_for_account(cookie)
                await asyncio.sleep(1)
                continue

            return True
        
    async def process_accounts(self, cookie: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(cookie, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(cookie) if use_proxy else None

            user = await self.user_data(cookie, proxy)
            if user:

                has_referrer = user.get("user", {}).get("hasReferrer")
                if not has_referrer:
                    await self.set_referral(cookie, proxy)

                points = user.get("user", {}).get("points")
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Points:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {points} XAGE{Style.RESET_ALL}"
                )
            
            task_lists = await self.task_lists(cookie, proxy)
            if task_lists:
                self.log(f"{Fore.CYAN + Style.BRIGHT}Tasks :{Style.RESET_ALL}")

                tasks = task_lists.get("tasks", [])
                for task in tasks:
                    task_id = task.get("id")
                    task_name = task.get("name")
                    task_reward = task.get("points")
                    is_complete = task.get("completed")

                    if is_complete:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{task_name}{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} Already Completed {Style.RESET_ALL}"
                        )
                        continue

                    complete = await self.complete_task(cookie, task_id, task_name, proxy)
                    if complete:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{task_name}{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Completed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{task_reward} $XAGE{Style.RESET_ALL}"
                        )

                    await asyncio.sleep(random.uniform(2.0, 3.0))                

    async def main(self):
        try:
            cookies = self.load_cookies()
            if not cookies: return
            
            proxy_choice, rotate_proxy = self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(cookies)}{Style.RESET_ALL}"
                )

                use_proxy = True if proxy_choice == 1 else False
                if use_proxy: self.load_proxies()
                
                separator = "=" * 26
                for idx, cookie in enumerate(cookies, 1):
                    if cookie:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(cookies)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if "connect.sid" not in cookie:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Cookie Data {Style.RESET_ALL}"
                            )
                            continue
                            
                        await self.process_accounts(cookie, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*63)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Xage()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] X Age - BOT{Style.RESET_ALL}                                       "                              
        )
