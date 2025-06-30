import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_bidv_rates():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options)

    driver.get("https://www.bidv.com.vn/vn/ty-gia-ngoai-te")

    # Tùy vào trang bạn cần parse lại đúng element
    page_source = driver.page_source

    # BeautifulSoup parse
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # ... xử lý để lấy tỷ giá

    driver.quit()
    return [...]  # Trả về danh sách tỷ giá
