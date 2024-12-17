import pandas as pd
import jieba.posseg as pseg
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# 加载 CSV 文件
def load_data(file_path):
    """
    加载本地 CSV 文件
    """
    try:
        data = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"数据加载成功，共 {len(data)} 条记录")
        return data
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None

# 加载停用词
def load_stop_words(stop_words_path):
    """
    加载停用词文件
    """
    try:
        with open(stop_words_path, 'r', encoding='utf-8') as f:
            stop_words = set(f.read().splitlines())
        print(f"成功加载停用词，共 {len(stop_words)} 个")
        return stop_words
    except Exception as e:
        print(f"加载停用词失败: {e}")
        return set()

# 数据统计
def analyze_data(data, text_column='text', stop_words=None):
    """
    使用 jieba.posseg 分词和词性标注，仅统计名词的词频
    """
    if stop_words is None:
        stop_words = set()
    if text_column not in data.columns:
        print(f"数据中没有 '{text_column}' 列")
        return None

    # 合并所有文本
    all_text = " ".join(data[text_column].dropna())

    # 使用 jieba.posseg 分词和词性标注
    words = pseg.cut(all_text)

    # 仅保留名词，并过滤停用词和长度小于2的词
    filtered_words = [word for word, flag in words if flag.startswith('n') and word not in stop_words and len(word) > 1]

    # 统计词频
    word_counts = Counter(filtered_words)
    print(f"名词词频统计前10:\n{word_counts.most_common(10)}")
    return word_counts

# 生成词云
def generate_wordcloud(word_counts, output_file):
    """
    根据名词词频生成词云
    """
    try:
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            font_path='../simhei.ttf',  # 中文字体
        ).generate_from_frequencies(word_counts)

        # 显示词云
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title("weibo_WordCloud")
        plt.show()

        # 保存词云图
        wordcloud.to_file(output_file)
        print(f"词云图已保存到 {output_file}")
    except Exception as e:
        print(f"生成词云失败: {e}")

# 主程序
if __name__ == "__main__":
    # 文件路径
    file_path = "../static/weibo_dynamic_pages_data.csv"  # 替换为您的文件路径
    stop_words_path = "../stop_words.txt"  # 替换为您的停用词文件路径

    # 加载数据
    data = load_data(file_path)

    # 加载停用词
    stop_words = load_stop_words(stop_words_path)

    if data is not None:
        # 数据统计
        word_counts = analyze_data(data, text_column='text', stop_words=stop_words)

        # 生成词云
        if word_counts:
            generate_wordcloud(word_counts, output_file="../static/weibo_wordcloud_nouns.png")
