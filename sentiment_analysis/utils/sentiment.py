import pandas as pd
from snownlp import SnowNLP
import matplotlib.pyplot as plt

# 加载数据
def load_data(file_path):
    try:
        data = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"数据加载成功，共 {len(data)} 条记录")
        return data.dropna(subset=['text'])  # 剔除空文本行
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

# 情感分析
def perform_sentiment_analysis(data, text_column='text'):
    """
    对指定列的文本数据进行情感分析
    - 返回添加了情感得分和分类的数据
    """
    sentiments = []
    sentiment_labels = []

    for text in data[text_column]:
        try:
            s = SnowNLP(text)
            score = s.sentiments  # 获取情感得分（0-1）
            sentiments.append(score)

            # 根据情感得分进行分类
            if score > 0.7:
                sentiment_labels.append('positive')
            elif score < 0.3:
                sentiment_labels.append('negative')
            else:
                sentiment_labels.append('neutral')
        except Exception as e:
            print(f"情感分析失败: {e}")
            sentiments.append(None)
            sentiment_labels.append(None)

    data['sentiment_score'] = sentiments
    data['sentiment_label'] = sentiment_labels
    return data

# 情感结果统计并生成环形图
def generate_sentiment_pie_chart(data, sentiment_column='sentiment_label', output_file="sentiment_pie_chart.png"):
    """
    统计情感结果并生成环形图
    """
    sentiment_counts = data[sentiment_column].value_counts()
    print(f"情感结果统计:\n{sentiment_counts}")

    # 生成环形图
    plt.figure(figsize=(8, 6))
    plt.pie(
        sentiment_counts,
        labels=sentiment_counts.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=['#4CAF50', '#FF9800', '#2196F3'],  # 自定义颜色：正面（绿）、负面（橙）、中性（蓝）
        wedgeprops={'width': 0.3}  # 环形宽度
    )
    plt.title("the rate of every sentiment", fontsize=16)
    plt.savefig(output_file, format='png', dpi=300)
    print(f"环形图已保存到 {output_file}")
    plt.show()

# 主程序
if __name__ == "__main__":
    file_path = "../static/weibo_dynamic_pages_data.csv"  # 替换为您的文件路径

    # 加载数据
    data = load_data(file_path)

    if data is not None:
        # 对文本数据进行情感分析
        data_with_sentiment = perform_sentiment_analysis(data, text_column='text')

        # 保存结果到新文件
        data_with_sentiment.to_csv("weibo_sentiment_analysis_results.csv", index=False, encoding='utf-8-sig')
        print("情感分析结果已保存到 weibo_sentiment_analysis_results.csv")

        # 生成情感环形图
        generate_sentiment_pie_chart(data_with_sentiment, sentiment_column='sentiment_label', output_file="../static/sentiment_pie_chart.png")
