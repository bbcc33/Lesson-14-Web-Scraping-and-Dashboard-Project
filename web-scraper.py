from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return webdriver.Chrome(options=options)

def get_year_links(driver):
    driver.get("https://www.baseball-almanac.com/yearmenu.shtml")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    year_links = []
    for td in soup.find_all("td", class_="datacolBox"):
        a = td.find("a")
        if a:
            year = a.text.strip()
            link = "https://www.baseball-almanac.com/yearly/" + a['href'].split("/")[-1]
            year_links.append({"year": year, "url": link})

    df = pd.DataFrame(year_links)
    df.to_csv("mlb_year_links.csv", index=False)
    print("Saved MLB year links to mlb_year_links.csv")

    return df.drop_duplicates()


def scrape_year_pages(driver, year_links_df):
    output_dir = "mlb_yearly_data"
    # os.makedirs(output_dir, exist_ok=True)
    os.makedirs("mlb_yearly_data", exist_ok=True)


    for _, row in year_links_df.iterrows():
        year = row["year"]
        url = row["url"]
        print(f"Scraping year: {year} → {url}")
        
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tables = soup.find_all("table")
        tables_data = []

        for idx, table in enumerate(tables):
            rows = table.find_all("tr")
            table_rows = []
            for tr in rows:
                cells = tr.find_all(["td", "th"])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    table_rows.append(row_data)
            
            if len(table_rows) > 1:
                df = pd.DataFrame(table_rows[1:], columns=table_rows[0]) if len(table_rows[0]) == len(table_rows[1]) else pd.DataFrame(table_rows)
                tables_data.append((f"table_{idx+1}", df))

        if tables_data:
            for table_name, df in tables_data:
                filename = f"{output_dir}/mlb_{year}_{table_name}.csv"
                df.to_csv(filename, index=False)


    print("All year pages scraped and saved")

def main():
    driver = get_driver()
    try:
        year_links_df = get_year_links(driver)
        year_links_df.to_csv("mlb_year_links.csv", index=False)
        scrape_year_pages(driver, year_links_df)  # ← THIS was missing
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
