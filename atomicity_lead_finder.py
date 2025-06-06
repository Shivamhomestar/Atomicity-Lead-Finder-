import re
import requests
from bs4 import BeautifulSoup
import vobject

# Regex to extract Indian mobile numbers (10 digits starting with 6-9, optional +91 or 0 prefix)
PHONE_REGEX = re.compile(r'(?:\+91[\-\s]?|0)?[6-9]\d{9}')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

SOURCES = {
    'olx': 'https://www.olx.in/items/q-{}',
    'quikr': 'https://www.quikr.com/search?query={}',
}

def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def extract_phone_numbers(text):
    return set(PHONE_REGEX.findall(text))

def scrape_site(site_name, keyword):
    url_template = SOURCES.get(site_name)
    if not url_template:
        return set()
    url = url_template.format(keyword.replace(' ', '+' if site_name == 'quikr' else '-'))
    print(f"Scraping {site_name} for '{keyword}' - {url}")
    html = fetch_html(url)
    if not html:
        return set()
    soup = BeautifulSoup(html, 'html.parser')
    page_text = soup.get_text(separator=' ')
    phones = extract_phone_numbers(page_text)
    return phones

def save_vcf(leads, filename='leads.vcf'):
    vcards = []
    for idx, (name, phone) in enumerate(leads):
        vcard = vobject.vCard()
        vcard.add('fn').value = name if name else f'Lead {idx+1}'
        tel = vcard.add('tel')
        tel.value = phone
        tel.type_param = 'CELL'
        vcards.append(vcard.serialize())
    with open(filename, 'w') as f:
        f.write('\n'.join(vcards))
    print(f"\nVCF file saved as '{filename}'")

def main():
    raw_input = input("Enter keywords separated by commas: ")
    keywords = [k.strip() for k in raw_input.split(',') if k.strip()]
    if not keywords:
        print("No keywords entered. Exiting.")
        return

    all_leads = set()
    for kw in keywords:
        for site in SOURCES.keys():
            phones = scrape_site(site, kw)
            for phone in phones:
                all_leads.add(('', phone))

    if not all_leads:
        print("No leads found.")
        return

    print(f"\nFound {len(all_leads)} unique leads:\n")
    for idx, (name, phone) in enumerate(all_leads, 1):
        print(f"{idx}. Name: {name or 'N/A'}, Phone: {phone}")

    save_vcf(all_leads)

if __name__ == "__main__":
    main()