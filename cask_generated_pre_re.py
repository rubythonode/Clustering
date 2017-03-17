# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup
#Easy to crawl data from DB
import MySQLdb
import random

freq = 0
low_centroid = 0

class Cluster(object):
    centroids = []
    ClusterSize = 0
    ClusterFreq = []
    Elements = []
    ClusterPer = []

KClusters = []  #Updated clusters
prevKClusters = []  #clusters before update
RClusters = {}  #To calculate precision and recall, get all data from Database as dictionary

'''
Class : Function
Name : CalculateSimilarity

* Calculate 'similarity = CapSimilarity / CupSimilarity'
CupSimilarity = Intersection
CapSimilarity = Union

'''

def CalculateSimilarity(cid,tags):
    global KClusters
    centroid = KClusters[cid].centroids
    centroidfreq = KClusters[cid].ClusterFreq

    CapSimilarity = 0
    CupSimilarity = 0
    similarity = 0
    for i in range(0,len(centroid)):
        CupSimilarity = CupSimilarity + centroidfreq[i]
        for j in range(0,len(tags)):
            if tags[j] == centroid[i]:
                CapSimilarity = CapSimilarity + centroidfreq[i]
    
    CupSimilarity = CupSimilarity + len(tags) - CapSimilarity
    if CupSimilarity != 0:
        similarity = float(CapSimilarity) / float(CupSimilarity)
    #print similarity
    return similarity

def getClosedCluster(tags):
    global KClusters
    SimilarityMax = 0.0
    MaxCluster = 0
    for i in range(0,len(KClusters)):
        sim = CalculateSimilarity(i,tags)
        #print "Similarity of " + str(i) + " cluster and post is " + str(sim)
        if SimilarityMax < sim:
            SimilarityMax = sim
            MaxCluster = i
    if SimilarityMax == 0.0:
        MaxCluster = -1
    return MaxCluster

def DoAssign(Post):
    global KClusters
    for p in Post:
       pid = int(p[0]) 
       ptags = p[1].split(" ")
       ptags = ptags[0:len(ptags)-1]

       Cid = getClosedCluster(ptags)
       if Cid == -1:
           #print str(pid) + " is outlier!!"
           continue
       KClusters[Cid].Elements.append(pid)

def CalculateCentroid():
    global prevKClusters
    global freq
    global KClusters
    global low_centroid
    freq_min = 99
    freq_max = -1
    freq_avg = 0
    numofcent = 0
    newKClusters = []
    
    for i in range(0,len(KClusters)):
        cl = KClusters[i]
        elements = cl.Elements
        newTags = []
        newFreqs = []
        newPer = []
        for j in range(0,len(elements)):
            db = MySQLdb.connect("localhost","root","ahqkdlf!@#","Instagram")
            cursor = db.cursor()
            sqlstring = "SELECT * FROM CreatedData WHERE Id = " + str(elements[j]) + ";"
            cursor.execute(sqlstring)
            result = cursor.fetchall()
            tags = result[0][1].split(" ")
        #    print tags
            tags = tags[0:len(tags)-1]
         #   print tags

            for l in range(0,len(tags)):
                temp = 0
                for m in range(0,len(newTags)):
                    if tags[l] == newTags[m]:
                        newFreqs[m] = newFreqs[m] + 1
                        temp = 1
                        break
                if temp == 0:
                    newTags.append(tags[l])
                    newFreqs.append(1)
        deletedTags = []
        if len(newTags) == 0:
            continue
        for j in range(0, len(newTags)):
            if newFreqs[j] < len(elements) * freq:
                deletedTags.append(j)
        for l in range(0, len(deletedTags)):
            del newFreqs[deletedTags[l]-l]
            del newTags[deletedTags[l]-l]
        for j in range(0, len(newTags)):
            newPer.append(float(newFreqs[j])/float(len(elements)))
            
        if len(newTags) == 0:
            continue
        newCl = Cluster()
        newCl.ClusterFreq = newFreqs
        newCl.centroids = newTags
        newCl.ClusterPer = newPer
        newCl.ClusterSize = 0
        newCl.Elements = []
        newKClusters.append(newCl)
        
        for j in range(0, len(newPer)):
            if freq_min > newPer[j]:
                freq_min = newPer[j]

#minimum
    if freq < freq_min:
        freq = freq_min
    check = 0
    if len(newKClusters) != len(KClusters) or len(prevKClusters) == 0:
        prevKClusters = KClusters
        KClusters = newKClusters
        min_size_centroid = 999999
        for l in range(0,len(newKClusters)):
            if min_size_centroid > len(newKClusters[l].centroids):
                min_size_centroid = len(newKClusters[l].centroids)
        low_centroid = min_size_centroid
        return 0

    else:
        for l in range(0,len(KClusters)):
            minPer = 999
            for m in range(0, len(KClusters[l].centroids)):
                if KClusters[l].ClusterPer[m] < minPer:
                    minPer = KClusters[l].ClusterPer[m]
            newminPer = 999
            while True:
                for m in range(0, len(newKClusters[l].centroids)):
                    if newKClusters[l].ClusterPer[m] < newminPer:
                        newminPer = newKClusters[l].ClusterPer[m]
                if minPer >= newminPer and low_centroid >= len(newKClusters[l].centroids):
                    check = check + 1
                    break
                elif minPer >= newminPer and low_centroid < len(newKClusters[l].centroids):
                    minimumPerIndex = 0
                    minimumPer = 99
                    for c in range(0,len(newKClusters[l].ClusterPer)):
                        if minimumPer > newKClusters[l].ClusterPer[c]:
                            minimumPerIndex = c
                            minimumPer = newKClusters[l].ClusterPer[c]
                    del newKClusters[l].ClusterPer[minimumPerIndex]
                    del newKClusters[l].ClusterFreq[minimumPerIndex]
                    del newKClusters[l].centroids[minimumPerIndex]
                else:
                    break
    if check != 0:
        return 1
    else:
        prevKClusters = KClusters
        KClusters = newKClusters
        for l in range(0,len(newKClusters)):
            if min_size_centroid > len(newKClusters[l].centroids):
                min_size_centroid = len(newKClusters[l].centroids)
        low_centroid = min_size_centroid
        return 0
        

"""
Class : Function
Name : Performance_Check
Input : X
Output : precision, recall

* Calculate precision and recall
"""

def Performance_Check(N, K):
    global KClusters
    global RClusters    #Dictionary Cid : { keywords set }

    pre_count = 0
    re_count = 0
    pre_sum = 0
    re_sum = 0
    data_size = 0

    db = MySQLdb.connect("localhost", "root", "ahqkdlf!@#", "Instagram")
    cursor = db.cursor()

    for i in range(0, K):
        sqlstring = "SELECT * FROM CreatedData WHERE ClusterLabel = " + str(i+1) + ";"
        cursor.execute(sqlstring)
        result = cursor.fetchall()

        data_size = data_size + len(result)
        word_set = set()

        for post in result:
            word_set.add(int(post[0]))

        RClusters[i] = word_set

#    print data_size

#Calculate precision
    for i in range(0, N):
        pre_max_count = 0
        for j in range(0, K):
            temp_set = set(KClusters[i].Elements)
            CAP = set(RClusters[j]) & temp_set   #실제 클러스터와 내 클러스터의 교집합.
#            print "Pre_inter = ", i, j, CAP, len(CAP)
            pre_count = len(CAP)

            if pre_count > pre_max_count:
                pre_max_count = pre_count

        pre_sum = pre_sum + pre_max_count
    print pre_sum

    precision = float(pre_sum) / float(data_size)


#Calculate recall
    for j in range(0, K):
        re_max_count = 0
        for i in range(0, N):
            temp_set = set(KClusters[i].Elements)
            CAP = set(RClusters[j]) & temp_set   #실제 클러스터와 내 클러스터의 합집합.
#            print "Re_inter = ", j, i, CAP, len(CAP)
            re_count = len(CAP)

            if re_count > re_max_count:
                re_max_count = re_count

        re_sum = re_sum + re_max_count

    print re_sum
    recall = float(re_sum) / float(data_size)

    return precision, recall

            


def StartClustering(i,k):
    global KClusters
    initialCentroidID = []

    db = MySQLdb.connect("localhost","root","ahqkdlf!@#","Instagram")
    cursor = db.cursor()

    sqlstring = "SELECT * FROM CreatedData;"
    cursor.execute(sqlstring)
    result = cursor.fetchall()
    
    if i == 0:
        j = 0
        while True:
            r_id = random.randrange(1,len(result))
            temp = 0
            for j in range(0,len(initialCentroidID)):
                if r_id == initialCentroidID[j-1]:
                    temp = 1
            if temp == 0:
                initialCentroidID.append(r_id)
                j = j + 1
            if j == k:
                break

        initialCentroidID.sort(key=int)
        temp = 1
        currentloc = 0
        for post in result:
            post_id = post[0]
            post_tags = post[1].split(' ')
            if currentloc < k:
                if temp == initialCentroidID[currentloc]:
                    cl = Cluster()
                    cl.ClusterSize = 0
                    cl.centroids = post_tags[0:len(post_tags)-1]
                    cl.ClusterFreq = []
                    cl.Elements = []
                    for l in range(0,len(cl.centroids)):
                        cl.ClusterFreq.append(1)
                    currentloc = currentloc + 1
                    KClusters.append(cl)
            temp = temp + 1
    DoAssign(result)    
    fin = CalculateCentroid()
    return fin

def PrintResult():
	global KClusters
        global RClusters
	
	db = MySQLdb.connect("localhost","root","ahqkdlf!@#","Instagram")
	cursor = db.cursor()	
	for i in range(0,len(KClusters)):
                print "-------------" + str(i+1) + "-------------"
		print KClusters[i].centroids
                print KClusters[i].Elements
		for j in range(0, len(KClusters[i].Elements)):
			sqlstring = "SELECT ClusterLabel FROM CreatedData WHERE Id = " +str(KClusters[i].Elements[j]) + ";"
			cursor.execute(sqlstring)
			result = cursor.fetchone()
                        print result[0],
                print("\n")

        print RClusters


##############################
### Main class ###############
##############################

k = input("Insert the number of clusters : ")   #Initial K
freq = input("Insert freq : ") #Initial threshold
i = 0
while True:
    print str(i+1) + "th pass....."
    fin = StartClustering(i,k)
    i = i + 1
    print "Number of Current clusters : " + str(len(KClusters))
    print "Current Freq : " + str(freq)
    if fin == 1:
        break

print "======== Result ========"
for j in range(0,len(KClusters)):
    print "KClusters[" + str(j+1) + "].centroids",
    print KClusters[j].centroids
    print "KClusters[" + str(j+1) +"].ClusterFreq",
    print KClusters[j].ClusterFreq
    print "KClusters[" + str(j+1) + "].ClusterPer",
    print KClusters[j].ClusterPer
print "== Precision & Recall =="
print Performance_Check(len(KClusters), k)
print "======= elements ======="
PrintResult()

