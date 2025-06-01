import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_muslim_pray_facilities(start_page=1, end_page=5):
    """
    Scrape Muslim prayer facilities data from taiwan.net.tw
    
    Args:
        start_page: First page to scrape (default=1)
        end_page: Last page to scrape (default=5)
        
    Returns:
        DataFrame containing the scraped facility data
    """
    base_url = "https://www.taiwan.net.tw/m1.aspx"
    all_data = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    for page_num in range(start_page, end_page + 1):
        print(f"Scraping page {page_num}...")
        
        params = {
            "sNo": "0020119",  # Muslim prayer facilities section
            "keyString": "^63^",  # 臺北市
            "page": page_num
        }
        
        try:
            # Add delay to be respectful to the server
            time.sleep(2)
            
            response = requests.get(base_url, params=params, headers=headers)
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table with facility data
            table = soup.select_one("table.muslimDataTable")
            if not table:
                print(f"No facility data found on page {page_num}")
                continue
                
            # Process each facility (using tbody elements)
            tbodies = table.select("tbody")
            
            i = 0
            while i < len(tbodies):
                try:
                    # Get the first row with facility data
                    basic_row = tbodies[i].select_one("tr")
                    if not basic_row:
                        i += 1
                        continue
                    
                    cells = basic_row.find_all('td')
                    if len(cells) < 7:  # Need at least 7 columns
                        i += 1
                        continue
                    
                    # Extract facility name and basic info
                    facility_data = {
                        "單位名稱": cells[0].text.strip(),
                        "地區": cells[1].text.strip(),
                        "認證別": cells[2].text.strip(),
                        "淨下設備": "是" if cells[3].select_one(".myes") else "否" if cells[3].select_one(".mno") else "",
                        "小淨設備": "是" if cells[4].select_one(".myes") else "否" if cells[4].select_one(".mno") else "",
                        "祈禱室": "是" if cells[5].select_one(".myes") else "否" if cells[5].select_one(".mno") else "",
                        "認證單位": cells[6].text.strip(),
                    }
                    
                    # Check if next row has details
                    if i+1 < len(tbodies):
                        details_row = tbodies[i].select_one("tr:nth-child(2)")
                        if details_row:
                            details_div = details_row.select_one("div.moreInfo")
                            if details_div:
                                detail_divs = details_div.find_all("div")
                                
                                for div in detail_divs:
                                    if "電話" in div.text:
                                        facility_data["電話"] = div.text.replace("電話：", "").strip()
                                    elif "地址" in div.text:
                                        address = div.text.replace("地址：", "").strip()
                                        # Use link text if available
                                        if div.find("a"):
                                            address = div.find("a").text.strip()
                                        facility_data["地址"] = address
                    
                    all_data.append(facility_data)
                    
                except Exception as e:
                    print(f"Error processing facility at index {i}: {str(e)}")
                
                i += 1
            
            print(f"Scraped {len(all_data)} facilities so far")
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {str(e)}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    return df

if __name__ == "__main__":
    # Scrape pages 1 to 5
    muslim_pray_df = scrape_muslim_pray_facilities(1, 5)
    
    # Save to CSV
    output_file = "muslim_pray_facilities.csv"
    muslim_pray_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Scraped data saved to {output_file}")
    print(f"Total facilities found: {len(muslim_pray_df)}")
    
    # Display first few entries
    print("\nSample data:")
    print(muslim_pray_df.head())