# -*- coding: utf-8 -*-
__author__ = 'Sehee Lee'
__editor__ = 'Yongdam Kim'

#Generating virtual data set for checking precision and recall
#This version checks revised CASK algorithm.

import requests
import MySQLdb
#SQL을 사용하기 위한 패키지
import random

#cluster class
class Cluster(object):
    ClusterID = 0
    centroids = []
    ClusterSize = 0 #number of data
    ClusterFreq = [] #represetative value
    Elements = []   #actual elements
    ClusterPer = []
#constructor
    def __init__(self):
        self.ClusterID = 0
        self.centroids = []
        self.ClusterSize = 0
        self.ClusterFreq = []
        self.Elements = []
        self.ClusterPer = []

#Define attributes for each data
class Attribute(object):
    keyword = ""
    freq = 0.0
    def __init__(self):
        self.keyword = ""
        self.freq = 0.0

class KeywordSetData(object):
    id = 0
    at = []     #attributes
    def __init__(self):
        self.at = []



#####################################
# Main Class
#####################################



#Inputs
'''
k : number of clusters
t : initial threshold
Nmin : minimum number of keyword set data in a cluster
Nmax : maximum number of keyword set data in a cluster
### Each cluster has N elements, Nmin <= N <= Nmax

Mmin : minimum number of keyword in a representative
Mmax : maximum number of keyword in a representative
### Each representative has M keywords, Mmin <= M <= Mmax

Kmin : minimum number of kind of keywords in a cluster
Kmax : maximum number of kind of keywords in a cluster
### Each cluster has K keywords, Kmin <= K <= Kmax

'''
k = input("Input Number of clusters : ")
t = input("Input threshold : ")
Nmin = input("Input minimum number of keyword set data in a cluster : ")
Nmax = input("Input maximum number of keyword set data in a cluster : ")
Mmin = input("Input minimum number of keyword in a representative : ")
Mmax = input("Input maximum number of keyword in a representative : ")
Kmin = input("Input minimum number of kind of keywords in a cluster : ")
Kmax = input("Input maximum number of kind of keywords in a cluster : ")


#Set as list
kClusters = []

id = 1

#iterate k times
for i in range(0,k):
    cl = Cluster()  #make cluster as called 'cl'
    cl.ClusterID = i + 1    #because i starts with 0
    if Nmin is not Nmax:
#        cl.ClusterSize = random.randrange(Nmin,Nmax)    #N = number of keyword set in each cluster
        cl.ClusterSize = Nmin
    else:
        cl.ClusterSize = Nmin

    if Mmin is not Mmax:
#        M = random.randrange(Mmin,Mmax) #M = number of representatives
        M = Mmin
    else:
        M = Mmin

#Make M representatives
    for j in range(0,M):
        at = Attribute()
#freq of representative should be larger than threshold rate
#        at.freq = random.randrange(int(t*cl.ClusterSize), cl.ClusterSize)
        at.freq = int(t * cl.ClusterSize) + 1
#set keyword as i1j1
        at.keyword = str(i+1) +'_' + str(j+1)
#set as centroid
        cl.centroids.append(at)

    if Kmin is not Kmax:        #K = number of kind of keywords in cluster
#        K = random.randrange(Kmin,Kmax)
        K = Kmin
    else:
        K = Kmin


#Make K - M keywords
    for j in range(M,K):
        at = Attribute()
#        at.freq = random.randrange(0, int(t*cl.ClusterSize)-1)
        at.freq = int(t * cl.ClusterSize) - 1
        at.keyword = str(i+1) + '_' + str(j+1)
        cl.centroids.append(at)

#Make N keyword data set
    for j in range (0,cl.ClusterSize):
        sd = KeywordSetData()
        sd.id = id
        id += 1
        cl.Elements.append(sd)


    c = 0 #flag
    loc = 0 #location for assign
#For each centroids
    for Q in cl.centroids:
        if c == 0:
                #Make elements in Elements[loc] with Q.freq times
            for k in range(0,Q.freq):
                at = Attribute()
                at.freq = 1
                at.keyword = Q.keyword
                cl.Elements[loc].at.append(at)
                loc += 1
                if loc == cl.ClusterSize: #If done, set c = 1
                    c = 1
                    break
        if c == 1: #After make elements
            checkList = []
            temp = 0
            for j in range(0,Q.freq):
                rd = random.randrange(0,cl.ClusterSize) #pick random number

                for k in range(0, len(checkList)):
                    if rd == checkList[k-1]: #If picked attribute is last element, repeat j loop.
                        temp = 1

                if temp == 0:
                    checkList.append(rd) #assign rd in checkList
                    at = Attribute()
                    at.freq = 1
                    at.keyword = Q.keyword
                    temp1 = 0
                    for att in cl.Elements[rd].at:
#If picked attribute is representative, repeat j loop.
                        if att.keyword is Q.keyword:
                            j -= 1
                            temp1 = 1
                            break
                    if temp1 == 0:
                        cl.Elements[rd].at.append(at)
                else: #If picked last one, repeat j loop
                    j -= 1

    db = MySQLdb.connect("localhost","root","ahqkdlf!@#","Instagram")
    cursor = db.cursor()
    print("================ Result ==============")
    print("Cluster id : " + str(i+1))
    print("Q : "),
    sqlquery = "INSERT INTO CreatedDataSetInfo (ClusterLabel, Representative, NumberOfData) VALUES('" + str(cl.ClusterID).encode('utf-8') + "','"
#set virtual DB we made in server.
    for Q in cl.centroids:

        if Q.freq > t*cl.ClusterSize:
            sqlquery = sqlquery + "(" + Q.keyword.encode('utf-8') +","+ str(Q.freq).encode('utf-8') +"),"
            print(Q.keyword + "|" + str(Q.freq)),
    print("\n")
    sqlquery = sqlquery + "','" + str(cl.ClusterSize).encode('utf-8')+"');"
    print(sqlquery)
    cursor.execute(sqlquery)
    db.commit()
    for sd in cl.Elements:
        sqlstring = "INSERT INTO CreatedData (Id, Keywords, ClusterLabel) VALUES('"+str(sd.id).encode('utf-8')+"','"
        print("Data id : " + str(sd.id)),
        print("Attributes : "),
        for at in sd.at:

            sqlstring = sqlstring  + at.keyword.encode('utf-8')+" "
            print(at.keyword + " | " + str(at.freq)),
        print("\n")
        sqlstring = sqlstring + "','" + str(cl.ClusterID).encode('utf-8')+"');"
        print(sqlstring)
        cursor.execute(sqlstring)
        db.commit()


#until every cluster done. (i loop, k times)
