from selenium import webdriver


def test_test():
    assert 2 == 2


def test_main_page():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    browser = webdriver.Chrome(options=options)
    try:
        browser.get('http://127.0.0.1:8000')
        assert 'Home' in browser.title
    finally:
        browser.quit()
