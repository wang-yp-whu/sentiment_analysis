import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def set_cookies(driver, cookie_str):
    """
    将字符串形式的 Cookie 设置到 Selenium WebDriver
    :param driver: WebDriver 实例
    :param cookie_str: Cookie 字符串
    """
    for item in cookie_str.split("; "):
        name, value = item.split("=", 1)
        driver.add_cookie({"name": name, "value": value})

def get_hot_search_with_cookies(cookie_str):
    """
    爬取微博热搜榜，支持 Cookie
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    hot_search = []

    try:
        url = "https://s.weibo.com/top/summary"
        driver.get(url)

        # 设置 Cookie
        set_cookies(driver, cookie_str)
        driver.refresh()
        time.sleep(2)

        # 获取热搜列表
        elements = driver.find_elements(By.CSS_SELECTOR, ".td-02 a")
        for element in elements:
            hot_search.append({
                "title": element.text.strip(),
                "url": element.get_attribute("href")
            })

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        driver.quit()

    return hot_search
