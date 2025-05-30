import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_halal_restaurants(start_page=1, end_page=5):
    """
    Scrape halal restaurant data from taiwan.net.tw from specified page range.
    
    Args:
        start_page: First page to scrape (default=1)
        end_page: Last page to scrape (default=5)
        
    Returns:
        DataFrame containing the scraped restaurant data
    """
    base_url = "https://www.taiwan.net.tw/m1.aspx"
    all_data = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    for page_num in range(start_page, end_page + 1):
        print(f"Scraping page {page_num}...")
        
        params = {
            "sNo": "0020118",
            "keyString": "^63^",  # 臺北市
            "page": page_num
        }
        
        try:
            # Add delay to be respectful to the server
            time.sleep(2)
            
            response = requests.get(base_url, params=params, headers=headers)
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all restaurant entries (each entry has 2 tbody elements)
            tbodies = soup.select("table.muslimDataTable tbody")
            
            if not tbodies:
                print(f"No restaurant data found on page {page_num}")
                continue
            
            # Process each restaurant entry
            for i in range(0, len(tbodies), 1):
                if i + 1 >= len(tbodies):  # Ensure we have both basic info and details
                    continue
                    
                # Basic info row (name, type, area, cuisine, certification)
                basic_row = tbodies[i].find('tr')
                if not basic_row:
                    continue
                    
                cells = basic_row.find_all('td')
                if len(cells) < 5:
                    continue
                    
                # Additional info (address, phone)
                details_div = tbodies[i+1].select_one("div.moreInfo")
                if not details_div:
                    continue
                
                detail_divs = details_div.find_all("div")
                phone = ""
                address = ""
                
                for div in detail_divs:
                    if "電話" in div.text:
                        phone = div.text.replace("電話：", "").strip()
                    elif "地址" in div.text:
                        address = div.text.replace("地址：", "").strip()
                        # Remove the Google Maps text from address if present
                        if div.find("a"):
                            address = div.find("a").text.strip()
                
                restaurant_data = {
                    "名稱": cells[0].text.strip(),
                    "認證別": cells[1].text.strip(),
                    "地區": cells[2].text.strip(),
                    "性質": cells[3].text.strip(),
                    "認證單位": cells[4].text.strip(),
                    "電話": phone,
                    "地址": address
                }
                
                all_data.append(restaurant_data)
            
            print(f"Scraped {len(all_data)} restaurants so far")
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {str(e)}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    return df

if __name__ == "__main__":
    # Scrape pages 1 to 5
    halal_restaurants_df = scrape_halal_restaurants(1, 5)
    
    # Save to CSV
    output_file = "halal_restaurants.csv"
    halal_restaurants_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Scraped data saved to {output_file}")
    print(f"Total restaurants found: {len(halal_restaurants_df)}")
    
    # Display first few entries
    print("\nSample data:")
    print(halal_restaurants_df.head())