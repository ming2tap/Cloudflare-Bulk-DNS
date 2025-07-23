import sys
import subprocess
import os
import time


def check_dependencies():
    """检查并安装必要的依赖库"""
    try:
        import pkg_resources
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'setuptools'])
        import pkg_resources

    required = {'requests'}
    installed = {pkg.key for pkg in pkg_resources.working_set}

    missing = required - installed

    if missing:
        print(f"⚠️ 缺少必要的库: {', '.join(missing)}")
        print("正在尝试安装...")
        try:
            python = sys.executable
            subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
            print("✅ 依赖安装完成")
            import importlib
            importlib.invalidate_caches()
            globals()['requests'] = importlib.import_module('requests')
        except Exception as e:
            print(f"❌ 安装失败: {str(e)}")
            print("请手动运行: pip install requests")
            sys.exit(1)


check_dependencies()

# 现在可以安全导入requests
import requests
import json


def get_input(prompt, required=True, default=None):
    """获取用户输入，支持默认值和必填校验"""
    while True:
        user_input = input(prompt).strip()
        if not user_input and required:
            print("⚠️ 此项为必填项，请重新输入")
            continue
        if not user_input and default is not None:
            return default
        if user_input:
            return user_input


def add_dns_records(api_token, zone_id, subdomains, ip_addresses, record_type="A", ttl=1, proxied=False):
    """批量添加DNS记录到Cloudflare"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"

    # 计算总记录数（子域名数 × 每个子域名的IP数）
    total_records = len(subdomains) * len(ip_addresses)
    current_count = 0
    success_count = 0

    for subdomain in subdomains:
        for ip in ip_addresses:
            current_count += 1
            record = {
                "type": record_type,
                "name": subdomain,
                "content": ip,
                "ttl": ttl,
                "proxied": proxied
            }

            try:
                response = requests.post(base_url, headers=headers, json=record, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    if result["success"]:
                        print(f"✅ [{current_count}/{total_records}] 成功添加: {subdomain} → {ip}")
                        success_count += 1
                    else:
                        error_msg = result["errors"][0]["message"] if result.get("errors") else "未知错误"
                        print(f"❌ [{current_count}/{total_records}] 添加失败 [{subdomain}]: {error_msg}")
                else:
                    print(
                        f"⛔ [{current_count}/{total_records}] 请求失败 [{subdomain}]: (HTTP {response.status_code}) {response.text}")

                # 避免触发Cloudflare的API速率限制（免费账户每分钟1200次）
                time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                print(f"🚨 [{current_count}/{total_records}] 网络错误 [{subdomain}]: {str(e)}")

    print(f"\n操作完成: 成功 {success_count}/{total_records} 条记录")
    return success_count > 0


def main():
    print("=" * 50)
    print("Cloudflare DNS批量添加工具")
    print("=" * 50)

    # 从环境变量获取或用户输入API令牌
    api_token = os.getenv('CF_API_TOKEN')
    if not api_token:
        api_token = get_input("1. 请输入Cloudflare API令牌: ")

    # 获取Zone ID
    zone_id = get_input("2. 请输入Zone ID: ")

    # 记录类型选择 - 优化提示信息
    record_type = get_input("3. 记录类型 [默认A] (支持：A, AAAA, CNAME, MX, TXT, NS 等): ",
                            required=False, default="A").upper()

    # 子域名输入
    sub_input = get_input("4. 输入子域名(多个用逗号/空格分隔, @表示根域名):\n  例如: www,api,@\n> ")
    subdomains = [s.strip() for s in sub_input.replace(" ", ",").split(",") if s.strip()]

    # 替换@为根域名标识
    subdomains = ["@" if s == "" or s.lower() == "@" else s for s in subdomains]

    # IP地址输入
    ip_input = get_input("5. 输入IP地址(多个用逗号/空格分隔):\n  例如: 192.168.1.1 或 1.1.1.1,2.2.2.2\n> ")
    ip_addresses = [ip.strip() for ip in ip_input.replace(" ", ",").split(",") if ip.strip()]

    # TTL设置 - 修改默认值为自动(1)
    ttl_input = get_input("6. TTL设置 (1=自动, 默认自动): ", required=False, default="1")
    try:
        ttl = int(ttl_input)
        if ttl == 1:
            # 自动TTL，保留1
            pass
        elif ttl < 60 or ttl > 86400:
            print("⚠️ TTL值应在60-86400之间，已设置为自动(1)")
            ttl = 1
    except ValueError:
        print("⚠️ 无效的TTL值，已设置为自动(1)")
        ttl = 1

    # 代理设置 - 修改默认值为不开启(N)
    proxy_input = get_input("7. 启用Cloudflare代理? [默认N] (y/N): ", required=False, default="n")
    proxied = proxy_input.lower() in ["y", "yes"]

    # 计算总记录数（子域名数 × IP数）
    total_records = len(subdomains) * len(ip_addresses)

    print("\n" + "=" * 50)
    print("即将添加以下DNS记录:")
    print(f"子域名数量: {len(subdomains)}")
    print(f"IP地址数量: {len(ip_addresses)}")
    print(f"总记录数: {total_records}")
    print(f"子域名列表: {', '.join(subdomains)}")
    print(f"IP地址列表: {', '.join(ip_addresses)}")
    print(f"记录类型: {record_type}")
    print(f"TTL: {'自动' if ttl == 1 else f'{ttl}秒'}")
    print(f"代理: {'启用' if proxied else '禁用'}")
    print("=" * 50)

    confirm = input("确认添加? [Y/n]: ").strip().lower()
    if confirm not in ["", "y", "yes"]:
        print("操作已取消")
        return

    print("\n开始添加DNS记录...")
    add_dns_records(api_token, zone_id, subdomains, ip_addresses, record_type, ttl, proxied)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"❌ 发生未预期错误: {str(e)}")
        print("请检查网络连接或参数设置")
