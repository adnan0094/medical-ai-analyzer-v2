import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_gold_master_prices():
    try:
        # 1. Get the main exchange rates page to find the latest bulletin link
        main_url = "https://goldmastersy.com/%d8%a3%d8%b3%d8%b9%d8%a7%d8%b1-%d8%a7%d9%84%d8%b5%d8%b1%d9%81/"
        response = requests.get(main_url, timeout=10)
        if response.status_code != 200:
            return {"error": f"Failed to load main page: {response.status_code}"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        bulletin_url = None
        for link in links:
            href = link.get('href')
            if href and 'daily_rates' in href:
                bulletin_url = href
                break
        
        if not bulletin_url:
            return {"error": "Could not find latest bulletin link"}
            
        # 2. Fetch the bulletin page
        response = requests.get(bulletin_url, timeout=10)
        if response.status_code != 200:
            return {"error": f"Failed to load bulletin page: {response.status_code}"}
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract prices from the text content
        # Based on the observed structure:
        # Currency Name | Buy | Sell
        text = soup.get_text()
        
        prices = {}
        
        # Patterns to look for
        # Example: "الدولار الليرة السورية 134 134.75"
        patterns = {
            "USD_SYP": r"الدولار\s+الليرة\s+السورية\s+(\d+\.?\d*)\s+(\d+\.?\d*)",
            "TRY_USD": r"الليرة\s+التركية\s+الدولار\s+(\d+\.?\d*)\s+(\d+\.?\d*)",
            "EUR_SYP": r"اليورو\s+الليرة\s+السورية\s+(\d+\.?\d*)\s+(\d+\.?\d*)",
            "TRY_SYP": r"الليرة\s+التركية\s+الليرة\s+السورية\s+(\d+\.?\d*)\s+(\d+\.?\d*)",
            "EUR_USD": r"اليورو\s+الدولار\s+(\d+\.?\d*)\s+(\d+\.?\d*)",
            "SAR_USD": r"الريال\s+السعودي\s+الدولار\s+(\d+\.?\d*)\s+(\d+\.?\d*)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                prices[key] = {
                    "buy": match.group(1),
                    "sell": match.group(2)
                }
        
        return {
            "source": bulletin_url,
            "prices": prices
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    data = fetch_gold_master_prices()
    print(json.dumps(data, ensure_ascii=False, indent=2))
