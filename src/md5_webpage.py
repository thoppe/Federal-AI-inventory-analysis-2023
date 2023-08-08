import requests
import hashlib
import sys
import datetime


# Record the date/time in ISO 8601 
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.isoformat()

# Use a header otherwise we might get firewall blocks
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def calculate_md5(content):
    md5_hash = hashlib.md5()
    md5_hash.update(content.encode("utf-8"))
    return md5_hash.hexdigest()

# Get URL from command line arguments
url = sys.argv[1]

try:
    r = requests.get(url, headers=headers)

    if r.ok:
        webpage_content = r.text
        md5_hash = calculate_md5(webpage_content)
    else:
        print(f"Failed to fetch webpage. Status code: {r.status_code}")
        exit(2)

except requests.RequestException as E:
    exit(3)
    print(f"An error occurred: {E}")

print(f"{formatted_datetime},{md5_hash}")
