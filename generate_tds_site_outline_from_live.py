from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

URL = "https://tds.s-anand.net/#/"

# Setup Selenium browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(URL)
time.sleep(3)  # wait for Docsify to render

# Use BeautifulSoup to parse rendered HTML
soup = BeautifulSoup(driver.page_source, "html.parser")

# Extract landing page text
landing_elem = soup.select_one(".markdown-section")
landing_text = landing_elem.get_text(separator="\n", strip=True) if landing_elem else ""

# Extract sidebar links
sections = []
for a in soup.select("div.sidebar-nav a[href^='#/../']"):
    route = a.get("href", "").replace("#", "").strip()
    title = a.get("title", "").strip()
    if route and title:
        sections.append({"route": route, "title": title})

driver.quit()

# Save output
with open("tds_site_outline.json", "w", encoding="utf-8") as f:
    json.dump({"landing": landing_text, "sections": sections}, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(sections)} sections to tds_site_outline.json")
