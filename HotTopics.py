import jieba
import os
import math
import jieba.analyse
from config import *

# Load stopword list
with open(STOPWORDS_PATH, 'r', encoding='utf-8') as f:
    sw = [line.strip() for line in f]


# Corpus Loading and text segmentation
class ReadCorpus():
    def __init__(self, path):
        self.__path = path
        if not os.path.isdir(path):
            print(path, 'is not a directory')

    def __iter__(self):
        for file in os.walk(self.__path):
            for fname in file[2]:
                text = open(os.path.join(file[0], fname), 'r', encoding='utf-8').read()
                yield jieba.cut(text, cut_all=False, HMM=True)


# Compute idf based on corpus
def idf_compute(output_path, corpus):
    w_freq = {}
    n_docs = 0
    for doc in corpus:
        doc = [x for x in doc if x not in sw]
        for x in doc:
            x.strip()
            w_freq[x] = w_freq.get(x, 0) + 1
        n_docs += 1
    with open(output_path, 'w', encoding='utf-8') as f:
        for k in w_freq.keys():
            if k not in ['', ' ', '　', '\n', '\r', '\t', '\a', '\f', '\n\n']:
                f.write(k + ' ' + str(math.log(n_docs / w_freq[k], 2)) + '\n')


# Config extractor
def config_extractor(re_idf=False, ustop=False):

    # Recompute user idf
    if re_idf ==True:
        corpus = ReadCorpus(CORPUS_PATH)
        idf_compute(IDF_PATH, corpus=corpus)

    # Jieba loading user idf file
    # Raise exception if user idf file has certain special characters
    try:
        jieba.analyse.set_idf_path(IDF_PATH)
    except Exception:
        print('Loading user idf file failed, used default idf instead')
        pass

    if ustop == True:
        # Jieba loading user stopwords file
        jieba.analyse.set_stop_words(STOPWORDS_PATH)
        # Jieba loading user dict
        jieba.load_userdict(USER_DICT_PATH)

# text for test keywords extraction
# text = """
# 导读：近年来，随着NLP技术的日益成熟，开源实现的分词工具越来越多，如Ansj、盘古分词等。在本文中，我们选取了Jieba进行介绍和案例展示，主要基于以下考虑：
#
# 社区活跃。截止本文发布前，Jieba在Github上已经有17,670的star数目。社区活跃度高，代表着该项目会持续更新，实际生产实践中遇到的问题能够在社区反馈并得到解决，适合长期使用。
# 功能丰富。Jieba其实并不是只有分词这一个功能，其是一个开源框架，提供了很多在分词之上的算法，如关键词提取、词性标注等。
# 提供多种编程语言实现。Jieba官方提供了Python、C++、Go、R、iOS等多平台多语言支持，不仅如此，还提供了很多热门社区项目的扩展插件，如ElasticSearch、solr、lucene等。在实际项目中，进行扩展十分容易。
# 使用简单。Jieba的API总体来说并不多，且需要进行的配置并不复杂，方便上手。
# """

