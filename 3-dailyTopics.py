from db import app
from dbco import *
from article import *
from time import *
from datetime import datetime
import time
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from collections import defaultdict
from dateutil import tz
from igraph import *

def generateGraphForDay(daysAgo):
	endTime = time.time() - daysAgo*24*3600
	beginTime = endTime - 1.5*24*3600
	articles = app.getArticlesBetweenTimes(beginTime, endTime)

	i = 0
	nodesClean = []
	edgesClean = []
	connectedNodes = []
	g = Graph()
	g.add_vertices(len(articles))

	for i in range(0, len(articles)-2):
		for j in range(i+1, len(articles)-1):
			commonKeywords = list(set(articles[i].keywords).intersection(articles[j].keywords))
			if len(commonKeywords) > 1:
				edgesClean.append({"source": articles[i].guid, "target": articles[j].guid, "value": len(commonKeywords)})
				connectedNodes.extend([i,j])
				g.add_edges([(i, j)])

	connectedNodes = list(set(connectedNodes))
	coloring = g.community_infomap()
	memberships = coloring.membership

	for i, membership in zip(range(0,len(articles)-1), memberships):
		if i in connectedNodes:
			nodesClean.append({"id": articles[i].guid, "name": articles[i].title.encode('utf-8').replace('"', ''), "group": str(membership), "keywords": articles[i].keywords[:5], "img": '', 'source': articles[i].source, 'url': articles[i].url})
		#articles[i].img

	endDate = datetime.utcfromtimestamp(endTime)
	date1 = datetime(endDate.year, endDate.month, endDate.day)
	time1 = (date1 - datetime(1970,1,1)).total_seconds()
	time2 = time1 + 86399
	date2 = datetime.utcfromtimestamp(time2)
	print datetime.utcfromtimestamp(endTime)
	db.graph_topics.update({'$and': [{'date': {'$gte': datetime.utcfromtimestamp(time1)}}, {'date': {'$lte': datetime.utcfromtimestamp(time2)}}]}, {'$set': {'date': datetime.utcfromtimestamp(endTime), 'graph': {'nodes': nodesClean, 'edges': edgesClean}}}, upsert=True)

generateGraphForDay(0)
