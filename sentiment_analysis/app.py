from flask import Flask, render_template, redirect, url_for
from utils.cookie import cookie_str
from utils.get_hot_search import get_hot_search_with_cookies
import csv
import random
import os
import pandas as pd

app = Flask(__name__)

# 替换为你的有效 Cookie
COOKIE_STRING = cookie_str

@app.route("/")
def index():
    """
    主页面，显示热搜榜
    """
    # 获取热搜榜
    hot_search = get_hot_search_with_cookies(COOKIE_STRING)
    return render_template("index.html", hot_search=hot_search)

@app.route('/analysis')
def analysis():
    # 获取应用的绝对路径
    app_root = os.path.dirname(os.path.abspath(__file__))

    # 拼接正确的文件路径
    file_path = os.path.join(app_root, 'static', 'weibo_dynamic_pages_data.csv')

    try:
        # 打开 CSV 文件并读取数据
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # 随机选择 20 条数据
        if len(rows) > 20:
            random_data = random.sample(rows, 20)
        else:
            random_data = rows  # 数据少于20条时返回所有数据

        return render_template('analysis.html', random_data=random_data)

    except Exception as e:
        return f"Error: {e}"

@app.route('/topic')
def topic():
    # 获取应用的绝对路径
    app_root = os.path.dirname(os.path.abspath(__file__))

    # 拼接正确的文件路径
    topic_names_path = os.path.join(app_root, 'static', 'topic_names.csv')
    #print(f"读取的文件路径：{topic_names_path}")

    try:
        # 使用 csv.reader 读取 CSV 文件
        with open(topic_names_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # 如果没有数据，返回空页面
        if len(rows) == 0:
            return render_template('topic.html', topic_names=None)

        # 传递数据到模板
        return render_template('topic.html', topic_names=rows)

    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return render_template('topic.html', topic_names=None)

@app.route('/sentiment')
def sentiment():
    # 假设你已经计算出情感分析结果，并准备了两个图片文件
    return render_template('sentiment.html')


if __name__ == "__main__":
    app.run(debug=True)
