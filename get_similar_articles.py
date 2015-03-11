import time
from db import app
import numpy as np
from StringIO import StringIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.neighbors import KNeighborsClassifier


<<<<<<< HEAD
def getSimilarArticles(article, numOfDays, numOfNeighbors):
	articles = app.getTrainingSet(40, 1)
	neigh = KNeighborsClassifier()
	count_vect = CountVectorizer(stop_words='english')
	tfidf_trans = TfidfTransformer()
	trainingText = [x.text for x in articles]
	rainingLabels = [x.category for x in articles]
=======
def getSimilarArticles(target, numOfDays, numOfNeighbors):
    articles = app.getTrainingSet(500, 70)
    neigh = KNeighborsClassifier()
    count_vect = CountVectorizer(stop_words='english', ngram_range=(1,2))
    tfidf_trans = TfidfTransformer()
    trainingTitle = [x.title for x in articles]
    trainingLabels = [x.categories for x in articles]
    targetTitleCounts = count_vect.fit_transform([target.title])
    targetCounts = count_vect.transform([target.text]) + targetTitleCounts
    trainingCounts = count_vect.transform(trainingTitle)
    print count_vect.get_feature_names()
    trainingCountsTfidf = tfidf_trans.fit_transform(trainingCounts)
    targetCountsTfidf = tfidf_trans.transform(targetTitleCounts)
    print targetCounts
    print 'After weighted by tfidf:'
    targetCounts = targetCounts.multiply(targetCountsTfidf)
    print targetCounts
    neigh.fit(trainingCounts, trainingLabels)
    similar_articles_index = neigh.kneighbors(targetCounts, numOfNeighbors, False)
    similar_articles = []
    for index in similar_articles_index[0]:
        similar_articles.append(articles[index].title)
    return similar_articles


trainingArticles = app.getTrainingSet(1, 69)
target = trainingArticles[3]
print 'Target article title:'
>>>>>>> 64d8c9e2e07103016ac4168d92496e5571e41776

print target.title
print '--------------------------------------'
similar_articles = getSimilarArticles(target, 6, 10)
print "Similar articles' title:"
for article in similar_articles:
    print article
