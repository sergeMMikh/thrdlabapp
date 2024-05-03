from selenium import webdriver


def test_test():
    assert 2 == 2


def test_main_page():
    browser = webdriver.Chrome()

    browser.get('http://127.0.0.1:8000')

    assert 'Home' in browser.title
