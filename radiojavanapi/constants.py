API_DOMAIN = "https://rj-deskcloud.com/api2/{}"

# Current Radio Javan web API; newer podcast records may include synchronized tracks.
PLAY_API_DOMAIN = "https://play.radiojavan.com/api/p/{}"

PLAY_API_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://play.radiojavan.com/",
    "Origin": "https://play.radiojavan.com",
    "X-Requested-With": "XMLHttpRequest",
}

BASE_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'rj-deskcloud.com',
    'Connection': 'keep-alive',
    'x-rj-user-agent': 'Radio Javan/5.0.0 (Desktop) com.radioJavan.rj.desktop',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) RadioJavan/5.2.0 Chrome/130.0.6723.118 Electron/33.2.0 Safari/537.36',
}
