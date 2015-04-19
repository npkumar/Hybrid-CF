from __future__ import division

import os
import time

############### ORIGINAL PREFS ###############

def load_original_prefs(path='../dataset'):
    print 'Loading original prefs...'
    original={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        original.setdefault(user,{})
        original[user][movieid] = float(rating)
    return original

################ NEW PREFS ####################

def createPrefs(folder='../output/'):
    """
    Loads user prefs per cluster to memory.
    >>> cluster[0]['1']['234']
    4.0
    """
    cluster = []
    
    for filename in os.listdir(folder):    

        f = open(folder + filename)
        for line in f:
            users = line.split('@')
        f.close()

        print "Preparing for cluster: " + filename
        print "Users: %d" %(len(users))
        prefs = {}

        for user in users:
            userid = user.split(',')[0]
            prefs.setdefault(userid, {})

            items = user.split(',')[1:]

            count = 1
            for item in items:
                prefs[userid][str(count)] = float(str(item).strip())
                count = count + 1
                
        cluster.append(prefs)

    return cluster


############# MODIFIED SIMILARITY FUNCTIONS ###############

def sim_distance(prefs,person1,person2):
    """
    Returns a distance-based similarity score for person1 and person2
    """
    # Add up the squares of all the differences
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sum_of_squares)


def sim_pearson(prefs,p1,p2):
    """
    Returns the Pearson correlation coefficient for p1 and p2
    """    
    # Add up all the preferences
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
    # Sum up the squares
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    # Sum up the products
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])

    # Calculate Pearson score
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))

    if den==0: return 0
    r=num/den
    return r

##################### MIBCF ###########################

def transformPrefs(prefs):
    """
    Transforms matrix.
    """
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            # Flip item and person
            result[item][person]=prefs[person][item]
    return result

def topMatches(prefs,person,n=10,similarity=sim_distance):
    """
    Returns the best matches for person from the prefs dictionary.
    After transforming prefs returns top items.
    """
    scores=[(similarity(prefs,person,other),other) for other in prefs if other!=person]
    # Sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[0:n]
    #return scores

def calculateSimilarItems(prefs,n=10):
    """
    Create a dictionary of items showing which other items they
    are most similar to.
    """
    result={}
    # Invert the preference matrix to be item-centric
    itemPrefs=transformPrefs(prefs)
    c=0

    print 'Calculating similar items..'

    for item in itemPrefs:
        # Status updates for large datasets
        c+=1
        if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        # Find the most similar items to this one
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result

def getRecommendedItems(original, prefs,itemMatch,user):

    userRatings=prefs[user] # from cluster

    originalUserRatings = original[user] # from file
    
    scores={}
    totalSim={}

    print "Calculating Recommendation for user: %s ..."%(user)
    
    # Loop over items rated by this user
    for (item,rating) in userRatings.items():
        # Loop over items similar to this one
        for (similarity,item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in originalUserRatings: continue
            
            # Weighted sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating

            # Sum of all the similarities
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity
            
            # Divide each total score by total weighting to get an average
            rankings=[(score/totalSim[item],item) for item,score in scores.items()]

            # Return the rankings from highest to lowest
            rankings.sort()
            rankings.reverse()
    return rankings



if __name__ == '__main__':
        
    original = load_original_prefs()
    cluster = createPrefs()

    # Do for second cluster
    cluster = cluster[0]

    itemsim = calculateSimilarItems(cluster, n=50)

    ranking = getRecommendedItems(original, cluster,itemsim,'1')

    print ranking[:10]
