from __future__ import division

import os
import time

import original
import algorithm
import sparsity
import genetic_som
import pickle

from random import randrange


"""
Target one:
Divide the data set into 5 equal divisions.
Perform and persist clustering on these.

Target two:
MAE for each cluster, record values obtained.
"""

#dict of items just removed
testing_prefs = {}
#new prefs after removal
mod_prefs = {}

#cluster centroids
cluster_centroid = {}

original_MAE = []
algorithm_MAE = []
deleted_users = []
removed_items= []

USERS = 943
ITEMS = 1682

orgdetails = {}
algodetails = {}

def deleteUsers(prefs, percent):
    new_prefs = {}
    #hard copy to new dict mod_prefs
    for user in prefs:
        new_prefs.setdefault(user, {})
        for item in prefs[user]:
            new_prefs[user][item] = prefs[user][item]

    #calculate number of users to delete
    count = int(percent/100 * 943)
    print "Number of users to be deleted: %d"%(count)
    
    while count >= 0:
        uid = randrange(943)
        if uid not in deleted_users:
            print "Deleting user %d"%(uid)
            try:
                del new_prefs[str(uid)]
                count = count - 1
                deleted_users.append(uid)
            except Exception,e:
                print "Unknown key %d :("%(uid)
                print e
    return new_prefs


def getMAE(ranking,user,type='org'):
    li = []
    done = []
    
    curdic = {}
    
    for (i,v) in ranking:
        if v in removed_items:
            value = abs(original_prefs[user][v] - i)
            li.append(value)
            done.append(v)
            curdic[v] = i
            
    for k in removed_items:
        if k not in done:
            curdic[k] = 0.0
            li.append(original_prefs[user][k])

    if len(li) > 0:
        if type == 'org':
            orgdetails[user] = curdic
        else:
            algodetails[user] = curdic
        return sum(li)/len(li)
    

def calMAE(ranking, user):
    li = []
    doneitems = []
    for (rating,item) in ranking:
        if item in original_prefs[user]:
            li.append(abs(original_prefs[user][item] - rating))
            doneitems.append(item)

    #housekeeping
    newitems = []
    for item in removed_items:
        if item not in doneitems:
            newitems.append(item)
    for item in newitems:
        li.append(abs(original_prefs[user][item]))

    print "For user %s"%(user)
    print li

    if (len(li) > 0):
        return sum(li)/len(li)
    

def getRemovedPrefs(userDict, maxi=10):
    """
    Returns
    1. Perfs with removed items with number equal to maxi.
    2. List of removed items
    
    """
    removed_items = []
    temp = {}
    for item in userDict:
        temp[item] = userDict[item]
    count = 0
    for item in userDict:
        #keep track of items deleted
        removed_items.append(item)

        del temp[item]
        count = count + 1
        if count == maxi:
            break

    #print removed_items    
    return temp, removed_items



def getClusterCentroids(cluster):
    """
    Returns a dictionary of cluster centroids.
    """
    for cid in range(8):
        li = []

        for i in range(1682):
            li.append(0)

        for user in cluster[cid]:
            if len(cluster[cid][user]) != 0:
                for item in range(1682):
                    li[item] += cluster[cid][user][str(item+1)]
        for i in range(1682):
            li[i] = li[i] / len(cluster[cid])

        cluster_centroid[cid] = li
    return cluster_centroid


def getBestCluster(userdict):
    """
      Returns the best cluster for adding a user.
        """
    li = []
    for cid in range(8):
        fittness = 10000
        best = 0
        diff = 0
        for item in userdict:
            try:
                diff += abs(userdict[item] - cluster_centroids[cid][int(item)+1])
            except:
                print "list index out of range :("
        li.append(diff)
    val, idx = min((val, idx) for (idx, val) in enumerate(li))
    return idx


def DEP_getClusterCentroids(clusterPrefs):
    """
    Do not use! Testing.
    """
    centroids = []
    totals = {}
    avg = {}
    for cluster in clusterPrefs:
        sizeOfCluster = len(cluster)
        
        for user in cluster:
            for item in range(ITEMS):
                totals.setdefault(item+1,0)
                totals[item + 1] += cluster[user][str(item+1)]

        for item in range(ITEMS):
            avg[item+1] = totals[item+1] / sizeOfCluster

    return avg
    
def getTestPrefs(prefs, n=5):
    """
    Removes a determined number of items from each user prefs.
    """
    #hard copy to new dict mod_prefs
    for user in prefs:
        mod_prefs.setdefault(user, {})
        for item in prefs[user]:
            mod_prefs[user][item] = prefs[user][item]
    
    #creates a dict of removed items for each user.
    for user in prefs:
        testing_prefs.setdefault(user,{})

        count = 0
        for item in prefs[user]:
            if count < n:
                #print count
                testing_prefs[user][item] = mod_prefs[user][item]
                count = count + 1
            else:
                break

    #del items from prefs 
    for user in testing_prefs:
        for item in testing_prefs[user]:
            del mod_prefs[user][item]
    
    return mod_prefs


def copyDict(prefs):
    new_prefs = {}
    #hard copy to new dict mod_prefs
    for user in prefs:
        new_prefs.setdefault(user, {})
        for item in prefs[user]:
            new_prefs[user][item] = prefs[user][item]
    return new_prefs

def dumpPickles(id):
    """
    Persist memory intensive data structures, item similarities.
    """
    print 'Pickle id %s'%(id)
    
    foldername = '../kfold_cluster_' + id + '/'
    print foldername
    cluster = algorithm.createPrefs(folder=foldername)
    
    for c in range(8):
        prefs = cluster[c]
        itemsim = algorithm.calculateSimilarItems(prefs, n=50)
        dumpname = "../pickle/" +id + "/oitemsim_" + str(c) + ".pickle"
        pickle.dump(itemsim, open(dumpname, "wb"))
        #itemsim = pickle.load( open( dumpname, "rb" ) )

        
if __name__ == '__main__':
    
        
    """
    validation - 188
    training - 188 to 943

    validation - 188 to 376
    training - 188, 376 to 943

    validation - 376 to 564
    training - 376, 564 to 943

    validation - 564 to 752
    training - 564, 752 to 943

    validation - 752 to 943
    training - 752
    """

    
    #load original prefs
    original_prefs = original.load()

    validation = {}
    for key in range(188,376):
        validation[str(key + 1)] = original_prefs[str(key+1)]
    training = {}
    for key in range(188,943):
        training[str(key + 1)] = original_prefs[str(key+1)]
    #for key in range(752,943):
    #    training[str(key + 1)] = original_prefs[str(key+1)]

    cid = 'two'
    
    for user in validation:
        user_dict, removed_items = getRemovedPrefs(validation[user], 10)
        
        
        org_prefs = {}
        org_prefs = validation
        org_prefs[user] = user_dict
        print "Length of org_prefs %d"%(len(org_prefs))
        
        
        #use the original prefs here.
        print 'Calculating original item similarity...'
        oitemsim = pickle.load( open( '../pickle/original/oitemsim_' + cid + '.pickle', "rb" ))
        #oitemsim = original.calculateSimilarItems(org_prefs, n=50)

        
        print 'Calculating original ranking...'
        oranking = original.getRecommendedItems(org_prefs, oitemsim,user)

        print 'Calculating MAE for original...'
        original_MAE.append(getMAE(oranking,user, 'org'))

        
    #print original_MAE
    #print algorithm_MAE
    print sum(original_MAE)/len(original_MAE)
    
    pickle.dump(orgdetails, open("../rating_details/" + cid +"/orgdetails_" + cid, "wb"))
    