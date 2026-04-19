
import requests
import re
import json
import secrets
import base64
import time


def steinlogin(username, password):
    session = requests.Session()
    user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36"
    session.headers.update({
        'User-Agent': user_agent,
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Accept-Language': "en-US,en;q=0.9",
        'Sec-Fetch-Dest': "document",
        'Sec-Fetch-Mode': "navigate",
        'Sec-Fetch-Site': "none",
        'Sec-Fetch-User': "?1",
        'Upgrade-Insecure-Requests': "1"
    })
    tokens = {}

    print(f"\n[*] Starting full cookies login simulation for: {username}")

    response = session.get(
        "https://www.instagram.com/accounts/login/",
        params={'hl': "en", 'source': "logged_out_homepage"}
    )

    jaz_match = re.search(r'jazoest=([^"&]+)', response.text) or re.search(r'"jazoest":"([^"]+)"', response.text)
    if jaz_match:
        tokens['jazoest'] = jaz_match.group(1)
    lsd_match = re.search(r'"LSD",\[\],\{"token":"([A-Za-z0-9]+)"\}', response.text) or re.search(r'"lsd":"([^"]+)"', response.text)
    if lsd_match:
        tokens['lsd'] = lsd_match.group(1)
    bkv_match = re.search(r'"versioningID":"([^"]+)"', response.text)
    if bkv_match:
        tokens['__bkv'] = bkv_match.group(1)
    tokens['csrftoken'] = session.cookies.get('csrftoken')

    timestamp = str(int(time.time()))
    encoded_password = f"#PWD_BROWSER:0:{timestamp}:{password}"

    payload = {
        'hl': "en",
        '__d': "www",
        '__user': "0",
        '__a': "1",
        '__req': "b",
        '__hs': "20543.HYP:instagram_web_pkg.2.1...0",
        'dpr': "3",
        '__ccg': "POOR",
        '__comet_req': "7",
        'lsd': tokens.get('lsd', ''),
        'jazoest': tokens.get('jazoest', ''),
        '__crn': "comet.igweb.PolarisWebBloksLoginRoute",
        "params": json.dumps({
            "params": {
                "server_params": {
                    "next_uri": "/?hl=en",
                    "credential_type": "password",
                    "two_step_login_type": "one_step_login"
                },
                "client_input_params": {
                    "contact_point": username,
                    "password": encoded_password
                }
            }
        })
    }

    headers = {
        'User-Agent': user_agent,
        'origin': "https://www.instagram.com",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://www.instagram.com/accounts/login/?hl=en&source=logged_out_homepage",
        'X-Requested-With': "XMLHttpRequest",
        'X-CSRFToken': tokens.get('csrftoken', '')
    }

    session.cookies.set('ps_l', '0', domain=".instagram.com")
    session.cookies.set('ps_n', '0', domain=".instagram.com")
    session.cookies.set('wd', '384x692', domain=".instagram.com")
    session.cookies.set('mid', base64.urlsafe_b64encode(secrets.token_bytes(21)).decode().rstrip("="), domain=".instagram.com")

    url = f"https://www.instagram.com/async/wbloks/fetch/?appid=com.bloks.www.bloks.caa.login.async.send_login_request&type=action&__bkv={tokens.get('__bkv', '')}"

    response = session.post(url, data=payload, headers=headers)
    print(response.text)
    if "authenticated\":true" in response.text.lower() or "sessionid" in session.cookies.get_dict():
        print("\n[+] SUCCESS: Logged in successfully!")

        cookies_dict = session.cookies.get_dict()
        full_cookies = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])

        print("\n" + "=" * 60)
        print("EXTRACTED FULL COOKIES:")
        print("=" * 60)
        print(f"Full Cookie String:\n{full_cookies}")
        print("\nIndividual Key Cookies:")
        for k, v in cookies_dict.items():
            print(f"- {k}: {v}")
        print("=" * 60)
        with open("instagram_cookies.txt", "w") as f:
            f.write(full_cookies)
        print("[*] Full cookies saved to: instagram_cookies.txt")
        return True

    print("\n[-] FAILED: Login failed.")
    return False


username = input("Enter Instagram Username or Email: ")
password = input("Enter Instagram Password: ")
steinlogin(username, password)
