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

original_MAE = []
algorithm_MAE = []
deleted_users = []

removed_prefs = {}


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

    print removed_items    
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
            
def copyDict(prefs):
    new_prefs = {}
    #hard copy to new dict mod_prefs
    for user in prefs:
        new_prefs.setdefault(user, {})
        for item in prefs[user]:
            new_prefs[user][item] = prefs[user][item]
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

if __name__ == '__main__':

    """
    Testing case study one:
    1. Remove N percent of users from data set.
    2. Process testing set.

    Original:
    Add a user to testing set and do IBCF.

    New methodolgoy:
    Add a user to testing set, then do
        usual processing
        ICBF
    """
    #load original prefs
    original_prefs = original.load()
    
    #get the required testing set.
    mod_prefs = deleteUsers(original_prefs, 0.5)

    print deleted_users
    
    for user in deleted_users:

        new_prefs = {}
        new_prefs = copyDict(mod_prefs)
        print "Length of new_prefs %d"%(len(new_prefs))
        
        org_prefs = {}
        org_prefs = copyDict(original_prefs)
        print "Length of org_prefs %d"%(len(org_prefs))
        
        #neet to remove N prefs for user before adding.
        
        print 'Adding user: %d'%(user)

        org_prefs[str(user)], removed_items = getRemovedPrefs(original_prefs[str(user)], 10)
        new_prefs[str(user)], removed_items = getRemovedPrefs(original_prefs[str(user)], 10)

        print removed_items
        
        print "Length of new_prefs %d"%(len(new_prefs))
        
        print 'Doing CBR...'
        sparsity.caseone_doFillUsingCBR(new_prefs, deleted_users)
        print 'Doing Average Filling...'
        sparsity.caseone_doAverageFilling(new_prefs, deleted_users)

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
