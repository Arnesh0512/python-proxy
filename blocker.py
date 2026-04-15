from mitmproxy import http
import requests
from listBlocked import blocking
import ahocorasick
from urllib.parse import urlparse

LOG_URL = "http://127.0.0.1:9000/log"

def log(msg):
    try:
        requests.post(
            LOG_URL,
            json={"msg": msg},
            timeout=0.1,
            proxies={"http": None, "https": None}
        )
    except:
        pass


# 🔹 Allowlist domains (NO blocking here)
ALLOW_DOMAINS = [
    "google.com",
    "github.com",
    "stackoverflow.com",
    "railway.com"
]

# 🔹 Block keywords
BLOCK_KEYWORDS = [
    "games",
    "reddit",
    "instagram",
    "shorts",
    "ads"
]
BLOCK_KEYWORDS.extend(blocking)
BLOCK_KEYWORDS = list(set(BLOCK_KEYWORDS))


# 🔹 Build Aho-Corasick automaton
A = ahocorasick.Automaton()
for word in BLOCK_KEYWORDS:
    A.add_word(word, word)
A.make_automaton()


# 🔹 Load blocked HTML
with open("C:/blocker/blocked.html", "r", encoding="utf-8") as f:
    HTML = f.read()


# 🔹 Helper: check if domain is allowed
def is_allowed_domain(url):
    try:
        domain = urlparse(url).netloc.lower()

        # Remove port if exists (example.com:443 → example.com)
        domain = domain.split(":")[0]

        for allowed in ALLOW_DOMAINS:
            if domain.endswith(allowed):
                return True
    except:
        pass

    return False


def request(flow: http.HTTPFlow):
    url = flow.request.pretty_url.lower()

    # ✅ Skip blocking if domain is allowed
    if is_allowed_domain(url):
        log(f"[ALLOWLIST] {url}")
        return

    # 🔴 Keyword blocking
    for _, keyword in A.iter(url):
        flow.response = http.Response.make(
            200,
            HTML.encode("utf-8"),
            {"Content-Type": "text/html"}
        )

        log(f"[BLOCKED] keyword='{keyword}' url='{url}'")
        return

    log(f"[ALLOWED] {url}")


def responseheaders(flow: http.HTTPFlow):
    if flow.response and flow.response.status_code == 403:
        flow.response.stream = False
    else:
        flow.response.stream = True