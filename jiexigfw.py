import base64
import re
from typing import Optional
import urllib.request
from urllib.parse import urlparse

GFWLIST_URL = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"

# 常见合法域名/IP正则
DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)
IPV4_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def extract_host(candidate: str) -> Optional[str]:
    s = candidate.strip()
    if not s or s.startswith(("!", "[")):
        return None

    # 跳过例外规则
    if s.startswith("@@"):
        return None

    # 跳过纯正则表达式规则
    if s.startswith("/") and s.endswith("/"):
        return None

    # 去掉前缀匹配符号
    if s.startswith("||"):
        s = s[2:]
    elif s.startswith("|"):
        s = s[1:]

    if s.startswith("."):
        s = s[1:]

    # 若包含协议头，直接用 urlparse 解析主机名
    if "://" in s:
        parsed = urlparse(s)
        host = parsed.hostname
    else:
        # 截断路径、查询参数、端口和通配符
        s = re.split(r"[/?#]", s, maxsplit=1)[0]
        s = s.split(":", maxsplit=1)[0]
        if "*" in s:
            parts = s.split(".")
            cleaned_parts = [p for p in parts if p and "*" not in p]
            if len(cleaned_parts) >= 2:
                s = ".".join(cleaned_parts)
            else:
                return None
        host = s.strip(".").lower()

    if not host:
        return None

    if DOMAIN_RE.match(host) or IPV4_RE.match(host):
        return host
    return None


def main() -> None:
    raw_b64 = urllib.request.urlopen(GFWLIST_URL, timeout=30).read()
    decoded = base64.b64decode(b"".join(raw_b64.split())).decode("utf-8", errors="ignore")

    domains = set()
    for line in decoded.splitlines():
        host = extract_host(line)
        if host:
            domains.add(host)

    sorted_domains = sorted(domains)
    with open("gfwlist_domains.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted_domains) + "\n")

    print(f"共提取出 {len(sorted_domains)} 个域名/IP，已保存至 gfwlist_domains.txt")


if __name__ == "__main__":
    main()