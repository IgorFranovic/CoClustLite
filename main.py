from collections import defaultdict
import operator
import time


import numpy as np

from sklearn.cluster import SpectralCoclustering
from sklearn.cluster import MiniBatchKMeans
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.cluster import v_measure_score



from matplotlib import pyplot as plt

import sys


if __name__=='__main__':
    from __init__ import __doc__













def number_normalizer(tokens):
    """ Map all numeric tokens to a placeholder.

    For many applications, tokens that begin with a number are not directly
    useful, but the fact that such a token exists can be relevant.  By applying
    this form of dimensionality reduction, some methods may perform better.
    """
    return ("#NUMBER" if token[0].isdigit() else token for token in tokens)


class NumberNormalizingVectorizer(TfidfVectorizer):
    def build_tokenizer(self):
        tokenize = super().build_tokenizer()
        return lambda doc: list(number_normalizer(tokenize(doc)))


# exclude 'comp.os.ms-windows.misc'
categories = ['alt.atheism', 'comp.graphics',
              'comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware',
              'comp.windows.x', 'misc.forsale', 'rec.autos',
              'rec.motorcycles', 'rec.sport.baseball',
              'rec.sport.hockey', 'sci.crypt', 'sci.electronics',
              'sci.med', 'sci.space', 'soc.religion.christian',
              'talk.politics.guns', 'talk.politics.mideast',
              'talk.politics.misc', 'talk.religion.misc']
newsgroups = fetch_20newsgroups(categories=categories)
####
dataset_name = ''
print("Enter dataset path (Fetch20Newsgroups by 'default'): \n $ ", end = '')
github_link = 'https://github.com/IgorFranovic/CoClustLite'
def quit():
    print("Thank you for using CoClustLite\n")
    print(github_link)
    sys.exit()
inq = str(input())

if 'default' not in inq:
    print('Invalid path!')
    quit()
dataset_name = 'Fetch20Newsgroups'

print('Enter additional parameters (type -help for additional information): \n $ ', end ='')
inp = str(input())
inq = inp.split()


def progress(n):
    print('Progress [', end='')
    for _ in range(n):
        print('#', end='')
        time.sleep(0.01)
    print(']')
####
y_true = newsgroups.target
print(y_true)

vectorizer = NumberNormalizingVectorizer(stop_words='english', min_df=5)

cocluster = SpectralCoclustering(n_clusters=len(categories),
                                 svd_method='arpack', random_state=0)
kmeans = MiniBatchKMeans(n_clusters=len(categories), batch_size=20000,
                         random_state=0)

print('Performing coclustering vs clustering comparison on the ' + dataset_name + ' dataset.')

print(" -- Vectorizing data...")

X = vectorizer.fit_transform(newsgroups.data)

progress(30)

print(" -- Coclustering ...")
progress(30)

start_time = time.time()
cocluster.fit(X)
y_cocluster = cocluster.row_labels_
print(y_cocluster)
print(" -- Completed in {:.2f}s.\n -- V-measure score: {:.4f}".format(
    time.time() - start_time,
    v_measure_score(y_cocluster, y_true)))

print("________________________")
print(" -- MiniBatchKMeans...")
start_time = time.time()
y_kmeans = kmeans.fit_predict(X)
print(" -- Completed in {:.2f}s. V-measure: {:.4f}".format(
    time.time() - start_time,
    v_measure_score(y_kmeans, y_true)))

feature_names = vectorizer.get_feature_names()
document_names = list(newsgroups.target_names[i] for i in newsgroups.target)


def bicluster_ncut(i):
    rows, cols = cocluster.get_indices(i)
    if not (np.any(rows) and np.any(cols)):
        import sys
        return sys.float_info.max
    row_complement = np.nonzero(np.logical_not(cocluster.rows_[i]))[0]
    col_complement = np.nonzero(np.logical_not(cocluster.columns_[i]))[0]
    # Note: the following is identical to X[rows[:, np.newaxis],
    # cols].sum() but much faster in scipy <= 0.16
    weight = X[rows][:, cols].sum()
    cut = (X[row_complement][:, cols].sum() +
           X[rows][:, col_complement].sum())
    return cut / weight


def most_common(d):
    """Items of a defaultdict(int) with the highest values.

    Like Counter.most_common in Python >=2.7.
    """
    return sorted(d.items(), key=operator.itemgetter(1), reverse=True)





bicluster_ncuts = list(bicluster_ncut(i)
                       for i in range(len(newsgroups.target_names)))
best_idx = np.argsort(bicluster_ncuts)[:5]

print()
print("Best biclusters:")
print("----------------")

####

####
subplot_count = 5
#fig, axs = plt.subplots(5, 1, sharex=False, sharey=False, figsize=(12, 8))
sp_cnt = 0

visualization_data = [[] for _ in range(subplot_count)]


for idx, cluster in enumerate(best_idx):
    n_rows, n_cols = cocluster.get_shape(cluster)
    cluster_docs, cluster_words = cocluster.get_indices(cluster)
    if not len(cluster_docs) or not len(cluster_words):
        continue

    # categories
    counter = defaultdict(int)
    for i in cluster_docs:
        counter[document_names[i]] += 1


    cat_string = ""
    for name, c in most_common(counter)[:3]:
        score = float(c) / n_rows * 100
        cat_string += "{:.0f}% {}, ".format(score, name)
        visualization_data[sp_cnt].append((name, score))

    cat_string = cat_string[:-2]


    # words
    out_of_cluster_docs = cocluster.row_labels_ != cluster
    out_of_cluster_docs = np.where(out_of_cluster_docs)[0]
    word_col = X[:, cluster_words]
    word_scores = np.array(word_col[cluster_docs, :].sum(axis=0) -
                           word_col[out_of_cluster_docs, :].sum(axis=0))
    word_scores = word_scores.ravel()
    important_words = list(feature_names[cluster_words[i]]
                           for i in word_scores.argsort()[:-11:-1])

    print("bicluster {} : {} documents, {} words".format(
        idx, n_rows, n_cols))
    print("categories   : {}".format(cat_string))
    print("words        : {}\n".format(', '.join(important_words)))

    sp_cnt += 1

#print("DONE")


if '-v' in inq or '-visualize' in inq:
    from visualization import plotter
    method = [True, False]
    method[0] = 'tf' in inq or 'to_file' in inq
    method[1] = 'ts' in inq or 'to_screen' in inq
    path = 'visualization/saves/test.png'
    if '-p' in inq:
        path = inq[inq.index('-p')+1]
    my_bar_plot = plotter.Visualizer(type='bar', data=visualization_data, to_file = method[0], to_screen = method[1], file_path = path)
    my_bar_plot.visualize()


quit()
