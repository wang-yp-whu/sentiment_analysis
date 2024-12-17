import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
from utils.cookie import cookie_str
import os
from datetime import datetime

# 爬取微博数据函数
def get_weibo_data(keyword, pages=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Cookie':cookie_str
    }
    base_url = f"https://s.weibo.com/weibo?q={keyword}&page="
    data = []

    for page in range(1, pages + 1):
        url = base_url + str(page)
        print(f"正在爬取关键词 '{keyword}' 的第 {page} 页: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"爬取失败，状态码：{response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('.card-wrap')

        for card in cards:
            try:
                text_element = card.select_one('.txt')
                text = text_element.get_text(strip=True) if text_element else None

                # 获取点赞数
                likes_element = card.select_one('.icon-attitude + em')
                likes = int(likes_element.get_text(strip=True)) if likes_element and likes_element.get_text(strip=True).isdigit() else 0

                # 获取评论数
                comments_element = card.select_one('.icon-comment + em')
                comments_count = int(comments_element.get_text(strip=True)) if comments_element and comments_element.get_text(strip=True).isdigit() else 0

                # 获取分享数
                shares_element = card.select_one('.icon-share + em')
                shares = int(shares_element.get_text(strip=True)) if shares_element and shares_element.get_text(strip=True).isdigit() else 0

                if text:  # 确保内容不为空
                    data.append({
                        'keyword': keyword,
                        'text': text,
                        'likes': likes,
                        'comments_count': comments_count,
                        'shares': shares
                    })
            except Exception as e:
                print(f"解析失败：{e}")
                continue

        time.sleep(2)  # 延迟避免被封

    return data

# 数据保存函数
def save_to_csv(data, filename='weibo_data.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"数据已保存到 {filename}")

# 主程序
if __name__ == "__main__":
    # 定义关键词池
    keyword_pool = [
        '电影', '科技', '教育', '健康', '娱乐', '音乐', '明星', '体育', '旅游', '社会',
        '财经', '文化', '政治', '生活', '新闻', '历史', '汽车', '科学', '读书', '爱情'
    ]

    # 定义需要爬取更多页面的关键词
    high_relevance_keywords = {'新闻', '社会', '财经', '教育', '政治', '明星', '财经'}

    all_data = []
    for keyword in keyword_pool:
        # 根据关键词设置爬取页数
        pages_to_crawl = 4 if keyword in high_relevance_keywords else 2
        print(f"关键词 '{keyword}' 将爬取 {pages_to_crawl} 页")

        # 爬取每个关键词的微博数据
        weibo_data = get_weibo_data(keyword, pages=pages_to_crawl)
        all_data.extend(weibo_data)

    # 保存所有数据到CSV文件
    save_to_csv(all_data, filename='../static/weibo_dynamic_pages_data.csv')

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d")
    time_floder = os.path.join('../static', f"{formatted_time}")
    if not os.path.exists(time_floder):
        os.makedirs(time_floder)
    save_to_csv(all_data, filename=f"../static/{formatted_time}/weibo_dynamic_pages_data.csv")