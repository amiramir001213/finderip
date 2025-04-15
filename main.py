import random
import asyncio
import aiohttp
import platform
from colorama import init, Fore
import threading

# فعال‌سازی رنگ‌ها
init()

# تنظیم کشورها و تعداد IP مورد نیاز
target_countries = {
    "Germany": [],
    "France": [],
    "United Arab Emirates": [],
    "Turkey": [],
    "Azerbaijan": [],
    "Russia": [],
    "Canada": [],
    "United States": [],
    "Netherlands": [],
    "Singapore": [],
    "Japan": [],
    "South Korea": [],
    "United Kingdom": []
}
REQUIRED_IP_COUNT = 5

lock = threading.Lock()

def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

async def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    proc = await asyncio.create_subprocess_exec(
        "ping", param, "1", ip,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await proc.communicate()
    if proc.returncode == 0:
        print(f"{Fore.GREEN}[PING OK] {ip}{Fore.RESET}")
    else:
        print(f"{Fore.RED}[PING FAIL] {ip}{Fore.RESET}")

async def monitor_and_ping():
    checked = set()
    while any(len(ips) < REQUIRED_IP_COUNT for ips in target_countries.values()):
        tasks = []
        with lock:
            for country, ips in target_countries.items():
                for ip in ips:
                    if ip not in checked:
                        checked.add(ip)
                        tasks.append(ping_ip(ip))
        if tasks:
            await asyncio.gather(*tasks)
        await asyncio.sleep(1)  # کمتر برای سرعت بیشتر

async def fetch_ips(session):
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
    async with aiohttp.ClientSession() as session:
        fetch_tasks = [asyncio.create_task(fetch_ips(session)) for _ in range(20)]  # افزایش تعداد تسک‌ها
        ping_task = asyncio.create_task(monitor_and_ping())
        await asyncio.gather(*fetch_tasks)
        await ping_task

# اجرای اصلی
asyncio.run(main())

# چاپ نتیجه نهایی
print("\n[RESULTS]")
for country, ips in target_countries.items():
    print(f"{country}: {ips}")
