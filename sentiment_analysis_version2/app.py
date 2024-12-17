from flask import Flask, render_template, redirect, url_for, request, jsonify
from utils.cookie import cookie_str
from utils.get_hot_search import get_hot_search_with_cookies
import csv
import random
import os
import pandas as pd

time_select = ''  # 全局变量，用于存储用户选择的结果
app = Flask(__name__)

# 替换为你的有效 Cookie
COOKIE_STRING = cookie_str  # 这里应该是一个有效的cookie字符串
app_root = os.path.dirname(os.path.abspath(__file__))
@app.route("/")
def index():
    """
    主页面，显示热搜榜
    """
    # 获取热搜榜
    hot_search = get_hot_search_with_cookies(COOKIE_STRING)
    # 获取static文件夹下的子文件夹名称
    sub_folders = [f for f in os.listdir(os.path.join(app.root_path, 'static')) if os.path.isdir(os.path.join(app.root_path, 'static', f))]
    return render_template("index.html", hot_search=hot_search, sub_folders=sub_folders)

@app.route('/select_folder', methods=['POST'])
def select_folder():
    """
    处理用户选择文件夹的请求
    """
    global time_select
    folder_name = request.json.get('folder_name')
    time_select = folder_name  # 更新全局变量
    print(time_select)
    return jsonify({'status': 'success', 'selected': folder_name})

@app.route('/analysis')
def analysis():
    # 检查time_select变量是否有值
    if not time_select:
        return redirect(url_for('index'))  # 如果没有选择，重定向到首页

    # 获取应用的绝对路径

    # 拼接正确的文件路径（这里假设用户选择的文件夹内有数据文件）
    file_path = os.path.join(app_root, f"static/{time_select}", 'weibo_dynamic_pages_data.csv')
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

        return render_template('analysis.html', random_data=random_data, src_select=f"static/{time_select}/weibo_wordcloud_nouns.png")

    except Exception as e:
        return f"Error: {e}"

@app.route('/topic')
def topic():
    # 获取应用的绝对路径

    # 拼接正确的文件路径
    topic_names_path = os.path.join(app_root,f"static/{time_select}", 'topic_names.csv')
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
        return render_template('topic.html', topic_names=rows, src_select=f"static/{time_select}/topic_heat.png")

    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return render_template('topic.html', topic_names=None)


@app.route('/sentiment')
def sentiment():
    # 假设你已经计算出情感分析结果，并准备了两个图片文件
    return render_template('sentiment.html',src_select1=f"static/{time_select}/sentiment_pie_chart.png", src_select2=f"static/{time_select}/fine_grained_sentiment.png")

if __name__ == "__main__":
    app.run(debug=True)