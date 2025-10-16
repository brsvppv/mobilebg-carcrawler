"""
Data extractors for AutoGetCars Crawler
Extracts car information from mobile.bg listings
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def extract_car_info_unified(url, timeout=10, retries=2, logger=None):
    """
    Unified car info extractor - dispatches to appropriate site-specific extractor.
    
    Args:
        url (str): Car listing URL
        timeout (int): Request timeout in seconds
        retries (int): Number of retry attempts
        logger (logging.Logger, optional): Logger instance
        
    Returns:
        dict: Extracted car information
    """
    netloc = urlparse(url).netloc.lower()
    
    if 'mobile.bg' in netloc:
        return extract_car_info_mobile(url, timeout=timeout, logger=logger)
    else:
        if logger:
            logger.warning(f"Unsupported site for URL: {url}")
        return {}


def extract_car_info_mobile(url, timeout=10, logger=None):
    """
    Extract car information from mobile.bg listing page.
    
    Args:
        url (str): Mobile.bg listing URL
        timeout (int): Request timeout in seconds
        logger (logging.Logger, optional): Logger instance
        
    Returns:
        dict: Extracted car information
    """
    try:
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize result dictionary
        car_info = {
            'Brand': '',
            'Model': '',
            'Production Date': '',
            'Price': '',
            'Price_EUR': '',
            'Price_BGN': '',
            'Engine': '',
            'Fuel Type': '',
            'Transmission': '',
            'Mileage': '',
            'Color': '',
            'Location': '',
            'Phone': '',
            'Link': url,
            'Описание': '',
            'Car Extras': ''
        }
        
        # Extract title (brand and model)
        title_elem = soup.find('h1')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # Remove "Обява: XXXXXXXX" part and extract brand/model
            title_clean = re.sub(r'Обява:.*', '', title_text).strip()
            # Clean up any extra whitespace and normalize
            title_clean = re.sub(r'\s+', ' ', title_clean)
            parts = title_clean.split()
            if parts:
                car_info['Brand'] = parts[0]
                # Clean up the model part - remove common suffixes and extra info
                model_parts = parts[1:] if len(parts) > 1 else []
                model_text = ' '.join(model_parts)
                # Remove trailing numbers that might be years (already extracted separately)
                model_text = re.sub(r'\s*\d{4}\s*$', '', model_text)
                car_info['Model'] = model_text.strip()
        
        # Extract price
        price_elem = soup.find('div', class_='Price')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Clean up price text - remove extra parts
            price_clean = re.sub(r'История.*', '', price_text).strip()
            car_info['Price'] = price_clean
            
            # Extract separate Euro and BGN prices
            # Look for Euro price (format: "2 964.98 €")
            euro_match = re.search(r'([\d\s]+\.?\d*)\s*€', price_text.replace(' ', ''))
            if euro_match:
                euro_price = euro_match.group(1).replace(' ', '')
                try:
                    car_info['Price_EUR'] = float(euro_price)
                except ValueError:
                    car_info['Price_EUR'] = ''
            
            # Look for BGN price (format: "5 799 лв.")
            bgn_match = re.search(r'([\d\s]+)\s*лв', price_text.replace(' ', ''))
            if bgn_match:
                bgn_price = bgn_match.group(1).replace(' ', '')
                try:
                    car_info['Price_BGN'] = int(bgn_price)
                except ValueError:
                    car_info['Price_BGN'] = ''
            
            # Keep the old price_numeric for compatibility
            if bgn_match:
                try:
                    car_info['price_numeric'] = int(bgn_match.group(1).replace(' ', ''))
                except ValueError:
                    pass
        
        # Extract additional specifications from mpLabel elements
        labels = soup.find_all('div', class_='mpLabel')
        for label in labels:
            label_text = label.get_text(strip=True)
            # Find the corresponding value (usually the next sibling)
            next_sibling = label.find_next_sibling()
            if next_sibling:
                value_text = next_sibling.get_text(strip=True)
                
                # Map labels to our data fields
                if 'двигател' in label_text.lower() or 'engine' in label_text.lower():
                    car_info['Fuel Type'] = value_text
                elif 'мощност' in label_text.lower() or 'power' in label_text.lower():
                    car_info['Engine'] = value_text
                elif 'скоростна' in label_text.lower() or 'transmission' in label_text.lower():
                    car_info['Transmission'] = value_text
                elif 'пробег' in label_text.lower() or 'mileage' in label_text.lower():
                    car_info['Mileage'] = value_text
                elif 'дата на производство' in label_text.lower():
                    # Extract full production date (e.g., "май 2005")
                    if value_text and not car_info.get('Production Date'):
                        car_info['Production Date'] = value_text.strip()
        # Extract color and other info from item structures (different pattern)
        item_divs = soup.find_all('div', class_='item')
        for item in item_divs:
            # Get all div children
            divs = item.find_all('div', recursive=False)
            if len(divs) == 2:
                label_text = divs[0].get_text(strip=True)
                value_text = divs[1].get_text(strip=True)
                
                # Map labels to our data fields
                if 'цвят' in label_text.lower() or 'color' in label_text.lower():
                    car_info['Color'] = value_text
                elif 'дата на производство' in label_text.lower():
                    # Extract full production date from item format (e.g., "юли 2008") 
                    if value_text and not car_info.get('Production Date'):
                        car_info['Production Date'] = value_text.strip()
        
        # Extract phone number
        phone_elems = soup.find_all(attrs={'class': lambda x: x and 'phone' in str(x).lower()})
        if phone_elems:
            phone_text = phone_elems[0].get_text(strip=True)
            # Extract actual phone number
            phone_match = re.search(r'(\d{10})', phone_text.replace(' ', ''))
            if phone_match:
                car_info['Phone'] = phone_match.group(1)
        
        # Extract location - try multiple methods
        location_found = False
        
        # Method 1: Look for elements with location-related classes
        location_elems = soup.find_all(attrs={'class': lambda x: x and 'location' in str(x).lower()})
        if location_elems and not location_found:
            location_text = location_elems[0].get_text(strip=True)
            city_match = re.search(r'гр\.\s*([^,\n\s]+)', location_text)
            if city_match:
                car_info['Location'] = city_match.group(1).strip()
                location_found = True
        
        # Method 2: Look for text containing 'гр.' anywhere in the page
        if not location_found:
            city_elements = soup.find_all(string=lambda text: text and 'гр.' in str(text))
            for elem in city_elements:
                city_match = re.search(r'гр\.\s*([А-Яа-я]+)', elem.strip())
                if city_match:
                    car_info['Location'] = city_match.group(1).strip()
                    location_found = True
                    break
        
        # Extract description - look for text areas or description divs
        descriptions = []
        
        # Look for common description selectors on mobile.bg
        desc_selectors = [
            '.description', '.desc', '.car-description',
            '.ad-description', '.announcement-description'
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                text = desc_elem.get_text(strip=True)
                if len(text) > 30:
                    descriptions.append(text)
        
        # If no specific selectors found, look for longer text blocks
        if not descriptions:
            # Look for divs/paragraphs with meaningful text content
            text_elements = soup.find_all(['div', 'p', 'span'])
            for elem in text_elements:
                text = elem.get_text(strip=True)
                # More strict filtering for descriptions - avoid navigation/header text
                if (len(text) > 50 and 
                    not text.isdigit() and
                    'лв' not in text and 'EUR' not in text and
                    'к.с' not in text and 'к.м' not in text and
                    'см3' not in text and
                    # Filter out common navigation/header text
                    not any(x in text.lower() for x in [
                        'tel:', 'gsm:', '+359', '08',  # Phone numbers
                        'mobile.bg', 'категории в mobile',  # Site navigation
                        'автомобили и джипове', 'бусове', 'камиони',  # Menu items
                        'област', 'софия-град', 'пловдив', 'варна',  # Location menus
                        'регистрация', 'вход', 'излез'  # User menu
                    ]) and
                    # Avoid short repetitive text patterns
                    text.count(',') < len(text) / 20):  # Not too many commas (lists)
                    descriptions.append(text)
        
        if descriptions:
            # Get the longest meaningful description
            car_info['Описание'] = max(descriptions, key=len)[:800]  # Increased length limit
        
        # Extract extras/features - look for lists or feature divs
        extras = []
        
        # Look for common car features/extras on mobile.bg
        extras_selectors = [
            '.extras', '.features', '.car-extras', '.car-features',
            '.equipment', '.additional', '.options'
        ]
        
        for selector in extras_selectors:
            extras_elem = soup.select_one(selector)
            if extras_elem:
                # Look for lists within the extras section
                items = extras_elem.find_all(['li', 'span', 'div'])
                for item in items:
                    text = item.get_text(strip=True)
                    if text and 5 <= len(text) <= 80:  # Feature-like text length
                        extras.append(text)
        
        # If no specific extras section found, look for common car feature keywords
        if not extras:
            # Look for elements containing common car features
            feature_keywords = [
                'климатик', 'кондиционер', 'abs', 'esp', 'airbag', 'серво',
                'централно', 'електрически', 'кожа', 'навигация', 'cd', 'mp3',
                'bluetooth', 'webasto', 'ксенон', 'led', 'халоген', 'алуминиеви',
                'джанти', 'металик', 'перлен', 'автоматик', 'ръчна'
            ]
            
            all_elements = soup.find_all(['li', 'span', 'div', 'p'])
            for elem in all_elements:
                text = elem.get_text(strip=True).lower()
                if (5 <= len(text) <= 80 and 
                    any(keyword in text for keyword in feature_keywords) and
                    'лв' not in text and 'км' not in text):
                    extras.append(elem.get_text(strip=True))
        
        # Remove duplicates and limit
        unique_extras = []
        for extra in extras:
            if extra not in unique_extras and len(unique_extras) < 15:
                unique_extras.append(extra)
        
        car_info['Car Extras'] = ', '.join(unique_extras)
        
        return car_info
        
    except requests.exceptions.RequestException as e:
        if logger:
            logger.error(f"Error fetching the webpage: {e}")
        else:
            print(f"Error fetching the webpage: {e}")
        return {}
    except Exception as e:
        if logger:
            logger.error(f"Error parsing car info from {url}: {e}")
        else:
            print(f"Error parsing car info from {url}: {e}")
        return {}