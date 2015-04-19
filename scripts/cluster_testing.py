from __future__ import division

import os
import time

import original
import algorithm
import sparsity
import genetic_som

from random import randrange

#dict of items just removed
testing_prefs = {}
#new prefs after removal
mod_prefs = {}

#cluster centroids
cluster_centroid = {}

original_MAE = []
algorithm_MAE = []
deleted_users = []

USERS = 943
ITEMS = 1682

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
    return new_prefs


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

    return sum(li)/len(li)


def getRemovedPrefs(userDict, maxi):
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


def getMAE(ranking,user):
    li = []
    done = []
    for (i,v) in ranking:
        if v in testing_prefs[user]:
            value = abs(testing_prefs[user][v] - i)
            li.append(value)
            done.append(v)

    for k in testing_prefs[user]:
        if k not in done:
            li.append(testing_prefs[user][k])

    if len(li) > 0:
        print li
        return sum(li)/len(li)


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
            diff += abs(userdict[item] - cluster_centroids[cid][int(item)+1])
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

    
if __name__ == '__main__':

    #load original prefs
    original_prefs = original.load()
    
    #get the required testing set.
    mod_prefs = deleteUsers(original_prefs, 1) #specify percentage
    
    """
    sparsity.caseone_doFillUsingCBR(mod_prefs, deleted_users)
    sparsity.caseone_doAverageFilling(mod_prefs, deleted_users)
    sparsity.saveDenseMatrix(mod_prefs,filename='..\\dataset\\cluster_testing10.tab')
    
    genetic_som.MAX_CLUSTERS = 10
    genetic_som.MIN_CLUSTERS = 4
    
    genetic_som.setFilename= '../dataset/cluster_testing10.tab'
    
    genetic_som.genetic(pop=20,max_evals=100,elites=4)

    #persist clusters onto files. UNVERIFIED
    genetic_som.persistClusters(genetic_som.getChromosomeList(genetic_som.final_pop),
                                filename='../dataset/cluster_testing10.tab', folder='cluster',clustername='cluster_testing')
    
    """
    cluster = algorithm.createPrefs(folder='../cluster/')
    
    #get cluster mean centroids.
    cluster_centroids = getClusterCentroids(cluster)

    for user in deleted_users:
        user_dict, removed_items = getRemovedPrefs(original_prefs[str(user)], 10)
        b = getBestCluster(user_dict)
        
        print "User %s Cluster %s"%(user, b)
        print "Prefs after removal of items: "
        print user_dict
        
        new_prefs = {}
        new_prefs = cluster[int(b)]
        new_prefs[str(user)] = user_dict
        
        print "Length of new_prefs %d"%(len(new_prefs))
        
        org_prefs = {}
        org_prefs = copyDict(mod_prefs)
        org_prefs[str(user)] = user_dict
        print "Length of org_prefs %d"%(len(org_prefs))

        #use the original prefs here.
        print 'Calculating original item similarity...'
        oitemsim = original.calculateSimilarItems(org_prefs, n=50)

        #use the modified prefs here.
        print 'Calculating algorithm item similarity...'
        itemsim = algorithm.calculateSimilarItems(new_prefs, n=50)

        print 'Calculating original ranking...'
        oranking = original.getRecommendedItems(org_prefs, oitemsim,str(user))
        print 'Calculating algorithm ranking...'
        
        ranking = original.getRecommendedItems(new_prefs,itemsim,str(user))

        print 'Calculating MAE for original...'
        original_MAE.append(calMAE(oranking,str(user)))

        print 'Calculating MAE for algorithm...'
        algorithm_MAE.append(calMAE(ranking,str(user)))

    print original_MAE
    print algorithm_MAE
    
    
