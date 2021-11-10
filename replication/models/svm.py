# Copyright 2020 Vraj Shah, Arun Kumar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import pandas as pd
from sklearn import metrics, svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler

np.random.seed(512)


# %%
def ProcessStats(data, y):

    data1 = data[
        [
            'total_vals',
            'num_nans',
            '%_nans',
            'num_of_dist_val',
            '%_dist_val',
            'mean',
            'std_dev',
            'min_val',
            'max_val',
            'has_delimiters',
            'has_url',
            'has_email',
            'has_date',
            'mean_word_count',
            'std_dev_word_count',
            'mean_stopword_total',
            'stdev_stopword_total',
            'mean_char_count',
            'stdev_char_count',
            'mean_whitespace_count',
            'stdev_whitespace_count',
            'mean_delim_count',
            'stdev_delim_count',
            'is_list',
            'is_long_sentence',
        ]
    ]
    data1 = data1.reset_index(drop=True)
    data1 = data1.fillna(0)

    def abs_limit(x):
        if abs(x) > 10000:
            return 10000 * np.sign(x)
        return x

    column_names_to_normalize = [
        'total_vals',
        'num_nans',
        '%_nans',
        'num_of_dist_val',
        '%_dist_val',
        'mean',
        'std_dev',
        'min_val',
        'max_val',
        'has_delimiters',
        'has_url',
        'has_email',
        'has_date',
        'mean_word_count',
        'std_dev_word_count',
        'mean_stopword_total',
        'stdev_stopword_total',
        'mean_char_count',
        'stdev_char_count',
        'mean_whitespace_count',
        'stdev_whitespace_count',
        'mean_delim_count',
        'stdev_delim_count',
        'is_list',
        'is_long_sentence',
    ]

    for col in column_names_to_normalize:
        data1[col] = data1[col].apply(abs_limit)

    print(column_names_to_normalize)
    x = data1[column_names_to_normalize].values
    x = np.nan_to_num(x)
    x_scaled = StandardScaler().fit_transform(x)
    df_temp = pd.DataFrame(
        x_scaled, columns=column_names_to_normalize, index=data1.index
    )
    data1[column_names_to_normalize] = df_temp

    y.y_act = y.y_act.astype(float)

    print(f"> Data mean: {data1.mean()}\n")
    print(f"> Data median: {data1.median()}\n")
    print(f"> Data stdev: {data1.std()}")

    return data1


vectorizerName = CountVectorizer(ngram_range=(2, 2), analyzer='char')
vectorizerSample = CountVectorizer(ngram_range=(2, 2), analyzer='char')


def FeatureExtraction(data, data1, flag):

    arr = data['Attribute_name'].values
    arr = [str(x) for x in arr]

    arr1 = data['sample_1'].values
    arr1 = [str(x) for x in arr1]
    arr2 = data['sample_2'].values
    arr2 = [str(x) for x in arr2]
    arr3 = data['sample_3'].values
    arr3 = [str(x) for x in arr3]
    print(len(arr1), len(arr2))
    if flag:
        X = vectorizerName.fit_transform(arr)
        X1 = vectorizerSample.fit_transform(arr1)
        X2 = vectorizerSample.transform(arr2)

    else:
        X = vectorizerName.transform(arr)
        X1 = vectorizerSample.transform(arr1)
        X2 = vectorizerSample.transform(arr2)

    #     print(f"> Length of vectorized feature_names: {len(vectorizer.get_feature_names())}")

    attr_df = pd.DataFrame(X.toarray())
    sample1_df = pd.DataFrame(X1.toarray())
    sample2_df = pd.DataFrame(X2.toarray())
    print(len(data1), len(attr_df), len(sample1_df), len(sample2_df))

    data2 = pd.concat([data1, attr_df], axis=1, sort=False)
    print(len(data2))
    return data2


# %%
xtrain = pd.read_csv('../../Benchmark-Labeled-Data/data_train.csv')
xtest = pd.read_csv('../../Benchmark-Labeled-Data/data_test.csv')


xtrain = xtrain.sample(frac=1, random_state=100).reset_index(drop=True)
print(len(xtrain))

y_train = xtrain.loc[:, ['y_act']]
y_test = xtest.loc[:, ['y_act']]


# %%
dict_label = {
    'numeric': 0,
    'categorical': 1,
    'datetime': 2,
    'sentence': 3,
    'url': 4,
    'embedded-number': 5,
    'list': 6,
    'not-generalizable': 7,
    'context-specific': 8,
}

y_train['y_act'] = [dict_label[i] for i in y_train['y_act']]
y_test['y_act'] = [dict_label[i] for i in y_test['y_act']]
y_train


# %%
xtrain1 = ProcessStats(xtrain, y_train)
xtest1 = ProcessStats(xtest, y_test)


X_train = FeatureExtraction(xtrain, xtrain1, 1)
X_test = FeatureExtraction(xtest, xtest1, 0)


X_train_new = X_train.reset_index(drop=True)
y_train_new = y_train.reset_index(drop=True)
X_train_new = X_train_new.values
y_train_new = y_train_new.values

k = 5
kf = KFold(n_splits=k)
avg_train_acc, avg_test_acc = 0, 0

cvals = [0.1, 1, 10, 100, 1000]
gamavals = [0.0001, 0.001, 0.01, 0.1, 1, 10]

# cvals = [1]
# gamavals = [0.0001]

bestPerformingModel = svm.SVC(
    C=100, decision_function_shape="ovo", gamma=0.001, cache_size=20000
)
bestscore = 0


avgsc_lst, avgsc_train_lst, avgsc_hld_lst = [], [], []
avgsc, avgsc_train, avgsc_hld = 0, 0, 0

for train_index, test_index in kf.split(X_train_new):
    X_train_cur, X_test_cur = X_train_new[train_index], X_train_new[test_index]
    y_train_cur, y_test_cur = y_train_new[train_index], y_train_new[test_index]
    X_train_train, X_val, y_train_train, y_val = train_test_split(
        X_train_cur, y_train_cur, test_size=0.25, random_state=100
    )

    bestPerformingModel = svm.SVC(
        C=100, decision_function_shape="ovo", gamma=0.001, cache_size=20000
    )
    bestscore = 0
    for cval in cvals:
        for gval in gamavals:
            clf = svm.SVC(
                C=cval,
                decision_function_shape="ovo",
                gamma=gval,
                cache_size=20000,
            )
            clf.fit(X_train_train, y_train_train)
            sc = clf.score(X_val, y_val)

            if bestscore < sc:
                bestscore = sc
                bestPerformingModel = clf
    #                 print(bestPerformingModel)

    bscr_train = bestPerformingModel.score(X_train_cur, y_train_cur)
    bscr = bestPerformingModel.score(X_test_cur, y_test_cur)
    bscr_hld = bestPerformingModel.score(X_test, y_test)

    avgsc_train_lst.append(bscr_train)
    avgsc_lst.append(bscr)
    avgsc_hld_lst.append(bscr_hld)

    avgsc_train = avgsc_train + bscr_train
    avgsc = avgsc + bscr
    avgsc_hld = avgsc_hld + bscr_hld

    print(bscr_train)
    print(bscr)
    print(bscr_hld)


# %%
print(avgsc_train_lst)
print(avgsc_lst)
print(avgsc_hld_lst)

print(avgsc_train / k)
print(avgsc / k)
print(avgsc_hld / k)

y_pred = bestPerformingModel.predict(X_test)
bscr_hld = bestPerformingModel.score(X_test, y_test)
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
print('Confusion Matrix: Actual (Row) vs Predicted (Column)')
print(cnf_matrix)


# %%
