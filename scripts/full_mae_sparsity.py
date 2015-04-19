from __future__ import division

import os
import time

import original
import algorithm
import sparsity
import genetic_som
import time

#dict of items just removed
testing_prefs = {}
#new prefs after removal
mod_prefs = {}

original_MAE = []
algorithm_MAE = []

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
    
    
if __name__ == '__main__':

    #load original prefs
    original_prefs = original.load()
    
    #get the required testing set.
    new_prefs = getTestPrefs(original_prefs, n=5)


    """
    sparsity.doFillUsingCBR(new_prefs)
    sparsity.doAverageFilling(new_prefs)
    sparsity.saveDenseMatrix(new_prefs,filename='..\\dataset\\three_dense_matrix.tab')

    
    genetic_som.MAX_CLUSTERS = 10
    genetic_som.MIN_CLUSTERS = 4
    
    genetic_som.setFilename= '../dataset/three_dense_matrix.tab'
    
    
    genetic_som.genetic(pop=20,max_evals=100,elites=4)

    #persist clusters onto files. UNVERIFIED
    genetic_som.persistClusters(genetic_som.getChromosomeList(genetic_som.final_pop),
                                filename='../dataset/three_dense_matrix.tab', folder='three',clustername='threecluster')
    
    """
    cluster = algorithm.createPrefs(folder='../five/')

    testingPrefs = getTestPrefs(original_prefs, n=5)
    
    #use the modified prefs here.
    ostart = time.time()
    oitemsim = original.calculateSimilarItems(testingPrefs, n=50)
    ostop = time.time()


    #keep track of cluster prediction details
    colist = []
    calist = []
    coMAE = []
    caMAE = []
    
    for cid in range(8):
        print "Cluster id: %d"%(cid)

        if len(colist)!= 0 and len(calist) != 0:
            coMAE.append(sum(colist)/len(colist))
            caMAE.append(sum(calist)/len(calist))
        else:
            colist = []
            calist = []
            
        clusterPrefs = cluster[cid]
    
        istart = time.time()        
        itemsim = algorithm.calculateSimilarItems(clusterPrefs, n=50)
        istop = time.time()
        
        for user in clusterPrefs:
        
            #fix missing values
            if not user:
                continue

        
            print "Cluster: %d User: %s"%(cid, user)

            rstart = time.time()
            #ranking = algorithm.getRecommendedItems(testingPrefs, clusterPrefs,itemsim,user)
            ranking = original.getRecommendedItems(testingPrefs,itemsim,user)
            rstop = time.time()

            orstart = time.time()
            oranking = original.getRecommendedItems(testingPrefs, oitemsim,user)
            orstop = time.time()

            print '**************STATS****************'
            print 'algo item sim: %d s'%(abs(istart - istop))
            print 'orig item sim: %d s'%(abs(ostart - ostop))
            print 'algo reco time: %d s'%(abs(rstart - rstop))
            print 'orig reco time: %d s'%(abs(orstart - orstop))
            print '**************END STATS************'
            
            
            original_MAE.append(getMAE(oranking,user))
            algorithm_MAE.append(getMAE(ranking,user))

            colist.append(getMAE(oranking,user))
            calist.append(getMAE(ranking,user))
            
        else:
            pass
    
    #print original_MAE
    #print algorithm_MAE

    print sum(original_MAE)/len(original_MAE)
    print sum(algorithm_MAE)/len(algorithm_MAE)

    print '##### Cluster Stats #####'
    print coMAE
    print caMAE
