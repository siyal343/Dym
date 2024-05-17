# %%
from math import ceil

import pandas as pd
from botasaurus import browser
from botasaurus.anti_detect_driver import AntiDetectDriver
from bs4 import BeautifulSoup

addy_of_interest = "0x089258ed79f140d73638e1bb59ea9599603f3222"

url = f"https://dym.fyi/address/{addy_of_interest}"


def get_tx_links(driver: AntiDetectDriver):
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    driver.sleep(1)
    table = soup.find_all("table", {"class": "table"})
    all_href = table[0].find_all("a")
    step = 3
    links = []

    for i in range(0, len(all_href), step):
        # print the text of the href
        link = f"https://dym.fyi/tx/{all_href[i].text}']"
        links.append(link)

    return links


def get_url(url, driver: AntiDetectDriver):
    driver.get(url)
    driver.sleep(2)
    driver.refresh()
    driver.sleep(2)


@browser(block_images=True, reuse_driver=True, window_size=(800, 600))
def scrape_links_task(driver: AntiDetectDriver, data):
    links = []
    get_url(url=url, driver=driver)

    # getting total tx number for the address
    tx_num = driver.get_element_or_none("/html/body/main/main/div[3]/div[1]/div/div[1]")
    tx_num = tx_num.text
    tx_num = tx_num.split(" ")[1]
    tx_num = int(tx_num)
    print(tx_num)
    page_num = 0

    # Extracting the Tx links
    for i in range(ceil(tx_num / 25)):
        links.extend(get_tx_links(driver))
        driver.click(
            "div.col-sm-6:nth-child(2) > nav:nth-child(1) > ul:nth-child(1) > li:nth-child(4) > span:nth-child(1)"
        )
        driver.sleep(2)

    links = [link.strip("']") for link in links]

    df = pd.DataFrame(links)
    df.to_csv("links.csv")

    return {"Total Links": len(links), "Links": links}

# %%
@browser(block_images=True, reuse_driver=True, window_size=(800, 600))
def scrape_address_task(driver: AntiDetectDriver, data):
    addresses = []
    links = pd.read_csv("links.csv")
    links = links.values.tolist()
    for link in links:
        driver.get(link[1])
        driver.sleep(2)
        driver.click(".row-msg-summary")
        driver.sleep(1)
        # getting the address of the tx number
        print(f"Getting address number {link[0]} of {len(links)}")
        address = driver.get_element_or_none(
            "/html/body/main/main/div[2]/div/div/div[1]/div/table/tbody/tr[2]/td/div/div/div[1]/div[1]/div[2]/div[1]/div[2]/a"
        )
        address = address.text
        addresses.append(address)

    return {"Total Addresses": len(addresses), "Addresses": addresses}


# Runnung the tasks
scraped_links = scrape_links_task()
address_list = scrape_address_task()


# %%
#exporting the addresses as a csv file
df = pd.DataFrame(address_list)
df.to_csv("addresses.csv", index=False)
