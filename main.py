import random
import requests
import threading
import subprocess
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore
import asyncio
import aiohttp

# فعال‌سازی رنگ‌ها
init()

def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

target_countries = {
    "Germany": [],
    "France": [],
    "United Arab Emirates": [],
    "Turkey": [],
    "Azerbaijan": [],
    "Russia": [],
    "Canada": []
}

REQUIRED_IP_COUNT = 5  # تعداد IP مورد نیاز برای هر کشور

lock = threading.Lock()

async def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", param, "4", ip]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        print(f"{Fore.GREEN}[PING OK] {ip}{Fore.RESET}")
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}[PING FAIL] {ip}{Fore.RESET}")

async def monitor_and_ping():
    checked = set()
    while any(len(ips) < REQUIRED_IP_COUNT for ips in target_countries.values()):
        with lock:
            for country, ips in target_countries.items():
                for ip in ips:
                    if ip not in checked:
                        checked.add(ip)
                        await ping_ip(ip)
        await asyncio.sleep(2)

async def fetch_ips():
    async with aiohttp.ClientSession() as session:
        while any(len(ips) < REQUIRED_IP_COUNT for ips in target_countries.values()):
            ip = random_ip()
            try:
                async with session.get(f"https://api.iplocation.net/?ip={ip}", timeout=5) as response:
                    data = await response.json()
                    country = data.get("country_name", "")

                    with lock:
                        if country in target_countries and len(target_countries[country]) < REQUIRED_IP_COUNT:
                            print(f"[FOUND] {ip} -> {country}")
                            target_countries[country].append(ip)

            except Exception:
                continue

async def main():
    fetch_ips_task = asyncio.create_task(fetch_ips())
    monitor_ping_task = asyncio.create_task(monitor_and_ping())

    await fetch_ips_task
    await monitor_ping_task

# شروع نخ‌ها
asyncio.run(main())

# نمایش نتیجه
print("\n[RESULTS]")
for country, ips in target_countries.items():
    print(f"{country}: {ips}")
  
