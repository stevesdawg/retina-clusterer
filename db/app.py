from pymongo import MongoClient, errors
from bson.objectid import ObjectId
import time
import hashlib
import md5
import json
from datetime import datetime, date, timedelta
from collections import namedtuple

client = MongoClient('mongodb://146.148.59.202:27017/')
db = client['big_data']

Article = namedtuple('Article', ['title', 'text', 'category', 'clusterDate', 'id', 'keywords', 'img'])

def getArticlesByTimeStamp(timeStamp, limit=1000):
    timeObj = datetime.utcfromtimestamp(timeStamp);
    version = getCrawlerVersion()
    articles = db.articles.find({'$and': [{"v": version}, {"text": {'$ne': ''}}, {"title": {'$ne': ''}}, {"recent_download_date": {"$gte":  timeObj}}]}).limit(limit);
    returnObject = [];
    for article in articles:
        cat = ''
        if article['categories'] is not None:
            cat = article['categories'][0];
        img = ''
        if len(article['images']) > 0:
            img = article['images'][0]
        returnObject.append(Article(article['title'], article['text'], cat, article['recent_download_date'], article['_id'], [], img)) # this is old categories, be careful
    return returnObject

def getArticlesInLastNDays(n=10, limit=1000):
    return getArticlesByTimeStamp(time.time() - n*24*3600, limit)

def getNbArticlesInXDays(days=60):
    return db.cleanarticles.find({'download_time': {'$gte': datetime.utcfromtimestamp(time.time() - days*24*3600)}}).count()

def getArticlesBetweenTimes(time1=0, time2=1):
    articles = db.cleanarticles.find({'$and': [{'download_time': {'$gte': datetime.utcfromtimestamp(time1)}}, {'download_time': {'$lte': datetime.utcfromtimestamp(time2)}}]})
    clean_articles = []
    for article in articles:
        img = ''
        if 'img' in article:
            img = article['img']
        clean_articles.append(Article(article['title'], article['text'], article['category'], article['download_time'], article['_id'], article['keywords'], img))
    return clean_articles    

def getCrawlerVersion():
    doc = db.articles.find_one({"_id" : "version"})
    return doc["number"]

def getArticleClusterList():
    articles = db.clusters.distinct('clusterName')
    clusterNameArray = []

    for article in articles:
        clusterNameArray.append(article)

    return clusterNameArray

def createCluster(clusterName, articleIds):
    db.clusters.insert( { "clusterName": clusterName, "_id": hashlib.md5(clusterName).hexdigest(), "articles": articleIds } )

def deleteCluster(clusterName):
    db.clusters.remove( { "clusterName": clusterName })

def insertToCluster(articleIDs, clusterName): # articleIDs is an array
    db.clusters.update( { "clusterName": clusterName }, { "$addToSet": { "articles": {'$each': articleIDs} } } )

def deleteFromCluster(articleIDs, clusterName):
    db.clusters.update( { "clusterName": clusterName }, { "$pull": { "articles": {'$in': articleIDs} } } )

def getLatestCluster(clusterName, limit = 50, skip=0):
    if limit == 0: # If limit is 0, get ALL articles.
        limit = getClusterArticleCount(clusterName);
    articles = db.cleanarticles.find({ "$query": { "category":  clusterName }, "$orderby": { 'download_time' : -1 } }).skip(skip).limit(limit)
    clean_articles = []
    for article in articles:
        img = ''
        if 'img' in article:
            img = article['img']
        clean_articles.append(Article(article['title'], article['text'], clusterName, article['download_time'], article['_id'], article['keywords'], article['img']))
    return clean_articles

def getTrainingSet(limit = 50, skip=0):
    clusterList = getArticleClusterList()
    trainingSet = []

    for cluster in clusterList:
        articles = getLatestCluster(cluster, limit, skip)
        for article in articles:
            if article.text is not None:
                trainingSet.append(article)

    return trainingSet

def getClusterArticleCount(clusterName):
    return db.cleanarticles.find({'category': clusterName}).count()

def getArticleCluster(articleID):
    clusterList = getArticleClusterList()
    cursor = db.clusters.find({"articles": ObjectId(articleID)}, {"clusterName": 1, "_id":0})
    for cluster in cursor:
        return cluster.get("clusterName")

def insertCleanArticle(article):
    if (article.title == '') | (article.title is None):
        return -1
    elif article.text == '':
        return -1
    else:
        try:
            db.cleanarticles.insert( { "_id": article.id, "title": article.title, "text": article.text, "download_time": article.clusterDate, "category": article.category, "keywords": [], "img": article.img } )
        except:
            pass # print "0" # what happened here is there was a duplicate key

def getArticlesNoKeywords(limit=30):
    articles = db.cleanarticles.find({ "$query": { "keywords":  [] }, "$orderby": { 'download_time' : -1 } }).limit(limit)
    clean_articles = []
    for article in articles:
        img = ''
        if 'img' in article:
            img = article['img']
        clean_articles.append(Article(article['title'], article['text'], article['category'], article['download_time'], article['_id'], [], img))
    return clean_articles

def getLatestCleanArticles(limit=30):
    articles = db.cleanarticles.find({ "$query": { "title": {'$ne': ''}  }, "$orderby": { 'download_time' : -1 } }).limit(limit)
    clean_articles = []
    for article in articles:
        img = ''
        if 'img' in article:
            img = article['img']
        clean_articles.append(Article(article['title'], article['text'], article['category'], article['download_time'], article['_id'], article['keywords'], img))
    return clean_articles

def updateKeywords(articleID, keywords):
    db.cleanarticles.update({ "_id": articleID },{"$set": {"keywords": keywords}})

def articlesWithKeywordsCount():
    return db.cleanarticles.find({'keywords': {'$ne': []}}).count()

def insertCleanArticles(articles):
    jsonArticles = []
    for article in articles:
        if (article.title == '') | (article.title is None):
            return -1
        elif article.text == '':
            return -1
        else:
            data = { "_id": article.id, "title": article.title, "text": article.text, "download_time": article.clusterDate, "category": article.categories, "keywords": [], "img": article.img}
            jsonArticle = json.dumps(data)
            jsonArticles.append(jsonArticle)
    try:
        db.cleanarticles.insert(jsonArticles)
    except:
        pass