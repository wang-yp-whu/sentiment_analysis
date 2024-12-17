import pandas as pd
from snownlp import SnowNLP
import matplotlib.pyplot as plt
from collections import defaultdict
import os
from datetime import datetime
# 加载数据
def load_data(file_path):
    try:
        data = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"数据加载成功，共 {len(data)} 条记录")
        return data.dropna(subset=['text'])  # 剔除空文本行
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

# 细粒度情感分析
def perform_fine_grained_sentiment_analysis(data, text_column='text'):
    """
    对指定列的文本数据进行细粒度情感分析
    """
    sentiment_scores = []
    sentiment_labels = []
    detailed_sentiments = defaultdict(list)

    for text in data[text_column]:
        try:
            s = SnowNLP(text)

            # 整体情感得分
            score = s.sentiments  # 获取情感得分（0-1）
            sentiment_scores.append(score)

            # 情感分类
            if score > 0.7:
                sentiment_labels.append('正面')
            elif score < 0.3:
                sentiment_labels.append('负面')
            else:
                sentiment_labels.append('中性')

            # 提取文本关键词并分析每个关键词的情感
            keywords = s.keywords(limit=5)  # 提取前5个关键词
            for keyword in keywords:
                detailed_sentiments[keyword].append(score)  # 为每个关键词保存情感得分

        except Exception as e:
            print(f"情感分析失败: {e}")
            sentiment_scores.append(None)
            sentiment_labels.append(None)

    # 添加整体情感分析结果
    data['sentiment_score'] = sentiment_scores
    data['sentiment_label'] = sentiment_labels

    # 计算每个关键词的平均情感得分
    detailed_sentiment_summary = {k: sum(v) / len(v) for k, v in detailed_sentiments.items()}

    return data, detailed_sentiment_summary

# 可视化细粒度情感分析结果（仅显示得分）
def visualize_fine_grained_sentiments_only_scores(detailed_sentiments, output_file="fine_grained_sentiment.png"):
    """
    Visualize fine-grained sentiment analysis results, showing only the sentiment scores without labels
    """
    scores = list(detailed_sentiments.values())
    indices = range(1, len(scores) + 1)  # Use indices as the data points

    plt.figure(figsize=(12, 6))

    # Plot the scores without any labels
    plt.bar(indices, scores, color='skyblue', alpha=0.8)
    plt.xlabel('Data Index', fontsize=12)  # Use index as X-axis
    plt.ylabel('Sentiment Score', fontsize=12)  # Y-axis for scores
    plt.title('Fine-Grained Sentiment Analysis Scores', fontsize=16)  # Chart title
    # Remove X-axis ticks and labels to avoid clutter
    plt.xticks([])  # No labels on X-axis
    plt.tight_layout()

    # Save the chart to a file
    plt.savefig(output_file, format='png', dpi=300)
    print(f"Fine-grained sentiment analysis chart saved to {output_file}")
    plt.show()

if __name__ == "__main__":
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d")
    file_path = f"../static/{formatted_time}/weibo_dynamic_pages_data.csv"  # 替换为您的文件路径

    # 加载数据
    data = load_data(file_path)

    if data is not None:
        # 进行细粒度情感分析
        analyzed_data, detailed_sentiments = perform_fine_grained_sentiment_analysis(data, text_column='text')

        # 保存结果到新文件
        analyzed_data.to_csv("weibo_fine_grained_sentiment_analysis.csv", index=False, encoding='utf-8-sig')
        print("细粒度情感分析结果已保存到 weibo_fine_grained_sentiment_analysis.csv")

        # 可视化关键词情感分析结果
        visualize_fine_grained_sentiments_only_scores(detailed_sentiments, output_file=f"../static/{formatted_time}/fine_grained_sentiment.png")

# 改进空间，每隔100条数据就打印一张图，这样更加清晰