import io
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import jieba.posseg as pseg
from collections import Counter
import os
from datetime import datetime
# 加载数据
def load_data(file_path):
    try:
        data = pd.read_csv(file_path, encoding='utf-8-sig')
        #print(f"数据加载成功，共 {len(data)} 条记录")
        return data.dropna(subset=['text'])  # 剔除空文本行
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

# 加载停用词
def load_stop_words(stop_words_path):
    try:
        with open(stop_words_path, 'r', encoding='utf-8') as f:
            stop_words = set(f.read().splitlines())
        #print(f"成功加载停用词，共 {len(stop_words)} 个")
        return stop_words
    except Exception as e:
        print(f"加载停用词失败: {e}")
        return set()

# 过滤低频名词
def filter_low_frequency_nouns(data, text_column='text', stop_words=None, frequency_threshold=5):
    """
    过滤掉低频出现的名词，仅保留出现次数大于 frequency_threshold 的名词
    """
    if stop_words is None:
        stop_words = set()

    # 提取所有文本并分词
    all_text = " ".join(data[text_column].dropna())
    words = pseg.cut(all_text)

    # 统计名词词频
    word_counts = Counter([word for word, flag in words if flag.startswith('n') and word not in stop_words and len(word) > 1])

    # 仅保留高频名词
    filtered_words = {word for word, count in word_counts.items() if count >= frequency_threshold}
    print(f"保留的高频名词数量：{len(filtered_words)}")
    return filtered_words

def extract_nouns(data, text_column='text', stop_words=None, filtered_nouns=None):
    """
    从微博文本中提取名词，仅保留过滤后的高频名词
    """
    if stop_words is None:
        stop_words = set()
    if text_column not in data.columns:
        print(f"数据中没有 '{text_column}' 列")
        return None

    all_text = data[text_column].dropna()
    extracted_nouns = []

    for text in all_text:
        words = pseg.cut(text)
        # 仅保留高频名词
        extracted_nouns.append(" ".join([word for word, flag in words if flag.startswith('n') and word in filtered_nouns]))

    #print(f"提取的名词样例：{extracted_nouns[:5]}")
    return extracted_nouns

# 话题识别（层次聚类）
def identify_topics_hierarchical(nouns, distance_threshold=1.8):
    vectorizer = TfidfVectorizer(max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(nouns)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        linkage='ward'
    )
    labels = clustering.fit_predict(tfidf_matrix.toarray())

    #print(f"层次聚类生成的聚类标签：{set(labels)}")
    return labels, clustering

# 统计话题关键词的出现次数作为热度
def calculate_heat(data, labels):
    data['topic'] = labels

    # 初始化热度列
    data['heat'] = 0

    # 遍历数据，计算每条微博中话题关键词的出现次数作为热度
    for index, row in data.iterrows():
        text = row['text']
        heat = 0
        # 统计每条微博中的话题关键词（基于名词提取结果）的出现次数
        for noun in row['nouns']:
            heat += text.count(noun)  # 计算名词在文本中的出现次数
        data.at[index, 'heat'] = heat

    return data

# 创建柱状图
def plot_and_save_topic_heat(topic_heat, save_path='topic_heat.png'):

    if topic_heat.empty:
        print("无法绘制图表：话题热度为空")
        return

    # 绘制柱状图
    topic_heat.plot(kind='bar', figsize=(12, 6), color='skyblue')
    plt.title("topic_anlysis", fontsize=16)
    plt.xlabel("t_id", fontsize=12)
    plt.ylabel("heap_value", fontsize=12)

    # 设置横坐标标签
    plt.xticks(rotation=45, fontsize=10, ha='right')  # 旋转45度，右对齐
    plt.tight_layout()  # 自动调整布局，避免挤压

    # 保存图片
    plt.savefig(save_path, format='png', dpi=300, bbox_inches='tight')
    print(f"话题热度图已保存到文件: {save_path}")

    # 显示图表
    plt.show()


# 为每个话题生成实际名称
def generate_topic_names(data, labels):
    """
    根据每个话题中的名词生成话题名称
    """
    data['topic'] = labels
    topic_names = {}

    for topic_id in sorted(data['topic'].unique()):
        # 获取该话题中所有微博的名词
        topic_nouns = " ".join(data[data['topic'] == topic_id]['nouns'].tolist())

        if not topic_nouns.strip():  # 如果名词为空，跳过或设置默认名称
            print(f"话题 {topic_id} 的名词列表为空，将使用默认名称")
            topic_names[topic_id] = f"话题 {topic_id}（无关键词）"
            continue

        # 提取每个话题的关键词
        vectorizer = TfidfVectorizer(max_features=5)  # 提取前 5 个关键词
        tfidf_matrix = vectorizer.fit_transform([topic_nouns])

        # 检查是否有有效关键词
        if tfidf_matrix.shape[1] == 0:  # 如果没有有效关键词
            print(f"话题 {topic_id} 的关键词为空，将使用默认名称")
            topic_names[topic_id] = f"话题 {topic_id}（无关键词）"
        else:
            keywords = vectorizer.get_feature_names_out()
            topic_names[topic_id] = ", ".join(keywords)

    # print(f"话题编号与名称映射:\n{topic_names}")
    return topic_names

# 保存话题名称到CSV文件
def save_topic_names_to_csv(topic_names, save_path):
    """
    将话题编号与名称保存到CSV文件
    """
    try:
        # 转换为DataFrame
        topic_names_df = pd.DataFrame(list(topic_names.items()), columns=['topic_id', 'topic_name'])

        # 保存到CSV
        topic_names_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"话题编号与名称已保存到文件: {save_path}")
    except Exception as e:
        print(f"保存话题名称失败: {e}")

# 主程序
if __name__ == "__main__":
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d")
    file_path = f"../static/{formatted_time}/weibo_dynamic_pages_data.csv"  # 替换为您的文件路径
    stop_words_path = "../stop_words.txt"  # 替换为停用词文件路径

    # 加载数据
    data = load_data(file_path)
    stop_words = load_stop_words(stop_words_path)

    if data is not None:
        # 过滤低频名词
        high_frequency_nouns = filter_low_frequency_nouns(data, text_column='text', stop_words=stop_words, frequency_threshold=5)

        # 提取高频名词
        nouns = extract_nouns(data, text_column='text', stop_words=stop_words, filtered_nouns=high_frequency_nouns)

        # 将提取的名词添加到数据中
        data['nouns'] = nouns

        # 话题识别（层次聚类）
        labels, clustering = identify_topics_hierarchical(nouns, distance_threshold=2.0)

        # 为每个话题生成实际名称
        topic_names = generate_topic_names(data, labels)
        save_topic_names_to_csv(topic_names, f"../static/{formatted_time}/topic_names.csv")
        # 计算热度（基于名词频率）
        data_with_heat = calculate_heat(data, labels)

        # 根据话题标签统计热度
        topic_heat = data_with_heat.groupby('topic')['heat'].sum().sort_values(ascending=False)
        #print(f"话题热度统计:\n{topic_heat}")

        print("\n话题编号与名称映射:")
        for topic_id, name in topic_names.items():
            print(f"话题编号 {topic_id}: {name}")
        # 可视化并保存话题热度
        plot_and_save_topic_heat(topic_heat, save_path=f"../static/{formatted_time}/topic_heat.png")
