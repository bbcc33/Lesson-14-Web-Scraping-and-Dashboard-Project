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
            href = a['href'].split("/")[-1]
            link = "https://www.baseball-almanac.com/yearly/" + href
            year_links.append({"year": year, "url": link})

    df = pd.DataFrame(year_links).drop_duplicates()
    df.to_csv("mlb_year_links.csv", index=False)
    print("Saved MLB year links to mlb_year_links.csv")
    return df


def scrape_year_pages(driver, year_links_df):
    output_dir = "mlb_yearly_data"
    os.makedirs(output_dir, exist_ok=True)

    for _, row in year_links_df.iterrows():
        year = row["year"]
        url = row["url"]
        print(f"Scraping year: {year} → {url}")

        try:
            driver.get(url)
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            tables = soup.find_all("table")

            for idx, table in enumerate(tables):
                rows = table.find_all("tr")
                table_rows = []
                for tr in rows:
                    cells = tr.find_all(["td", "th"])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        table_rows.append(row_data)

                header, body = None, []

                for i, row in enumerate(table_rows):
                    if len(row) > 1 and all(cell.strip() for cell in row):
                        header = row
                        body = table_rows[i + 1:]
                        break

                if header and body:
                    try:
                        df = pd.DataFrame(body, columns=header)
                        df.columns = [col.strip().replace(" ", "_").replace("-", "_") for col in df.columns]
                        filename = f"{output_dir}/mlb_{year}_table_{idx+1}.csv"
                        df.to_csv(filename, index=False)
                        print(f"Saved {filename}")
                    except Exception as e:
                        print(f"Skipped malformed table {idx+1} for year {year}: {e}")
                else:
                    print(f"No valid header found in table {idx+1} for year {year}")

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    print("All year pages scraped and saved.")


def main():
    driver = get_driver()
    try:
        year_links_df = get_year_links(driver)
        scrape_year_pages(driver, year_links_df)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
