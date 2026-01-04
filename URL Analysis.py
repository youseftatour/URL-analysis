from urllib.parse import urlparse, parse_qs
import requests
import re

# --------------------------------------------------
# Input URLs
# --------------------------------------------------

urls = [
    "https://edition.cnn.com/2025/12/22/media/60-minutes-cecot-bari-weiss-canada-global-tv?iid=cnn_buildContentRecirc_end_recirc&recs_exp=most-popular-article-end&tenant_id=popular.en",
    "https://www.nhm.ac.uk/visit/exhibitions/wildlife-photographer-of-the-year.html",
    "https://is-web.hevra.haifa.ac.il/images/2025_SEM._aa.pdf"
]

# --------------------------------------------------
# URL Analysis Function
# --------------------------------------------------

def analyze_url(url):
    parsed = urlparse(url)

    host_parts = parsed.hostname.split('.')
    tld = host_parts[-1]
    domain = host_parts[-2]
    subdomain = '.'.join(host_parts[:-2]) if len(host_parts) > 2 else None

    file_name = parsed.path.split('/')[-1] if '.' in parsed.path.split('/')[-1] else None

    return {
        "TLD": tld,
        "Domain": domain,
        "Subdomain": subdomain,
        "Path": parsed.path,
        "File name": file_name,
        "Query parameters": parse_qs(parsed.query),
        "Port": parsed.port
    }

# --------------------------------------------------
# robots.txt Analysis
# --------------------------------------------------

def analyze_robots(subdomain, domain, tld):
    robots_url = f"https://{subdomain + '.' if subdomain else ''}{domain}.{tld}/robots.txt"

    try:
        response = requests.get(robots_url, timeout=5)
        if response.status_code != 200:
            return None

        text = response.text

        disallow = re.findall(r"Disallow:\s*(.*)", text)
        user_agents = re.findall(r"User-agent:\s*(.*)", text)
        crawl_delay = re.findall(r"Crawl-delay:\s*(.*)", text)

        return {
            "robots_url": robots_url,
            "Disallow paths": disallow,
            "User-agents": user_agents,
            "Crawl-delay": crawl_delay[0] if crawl_delay else None
        }

    except Exception:
        return None

# --------------------------------------------------
# Run Analysis
# --------------------------------------------------

for url in urls:
    print("=" * 80)
    print("URL:", url)

    info = analyze_url(url)
    for k, v in info.items():
        print(f"{k}: {v}")

    robots = analyze_robots(info["Subdomain"], info["Domain"], info["TLD"])

    if robots:
        print("\nrobots.txt found at:", robots["robots_url"])

        print("Disallowed paths:")
        for p in robots["Disallow paths"]:
            print(" ", p)

        print("User-agents:")
        for ua in robots["User-agents"]:
            print(" ", ua)

        print("Crawl-delay:", robots["Crawl-delay"])
    else:
        print("\nrobots.txt not found")

print("=" * 80)
