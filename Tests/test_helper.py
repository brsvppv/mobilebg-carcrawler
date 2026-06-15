import requests
from bs4 import BeautifulSoup

def get_active_test_urls(count=3):
    """Dynamically fetches active listing URLs from mobile.bg to avoid 404 test failures."""
    url = "https://www.mobile.bg/obiavi/avtomobili-dzhipove/audi/a4/sedan/dizelov?price=5000&price1=50000"
    links = []
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href and '/obiava-' in href:
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('//'):
                        full_url = 'https:' + href
                    elif href.startswith('/'):
                        full_url = 'https://www.mobile.bg' + href
                    else:
                        full_url = 'https://www.mobile.bg/' + href
                    if full_url not in links:
                        links.append(full_url)
                        if len(links) >= count:
                            break
    except Exception:
        pass
        
    # Fallback to hardcoded list if we couldn't fetch enough live links
    if len(links) < count:
        fallback = [
            'https://www.mobile.bg/obiava-21748341999589220-mitsubishi-outlander-2-4-awd-sheytsariya',
            'https://www.mobile.bg/obiava-21729451673697804-mitsubishi-outlander-4x4',
            'https://www.mobile.bg/obiava-11759077895164151-toyota-corolla'
        ]
        needed = count - len(links)
        links.extend(fallback[:needed])
        
    return links
