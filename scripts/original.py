from __future__ import division


from math import sqrt
import time

############# SIMILARITY FUNCTIONS ###############

def sim_distance(prefs,person1,person2):
    """
    Returns a distance-based similarity score for person1 and person2
    """
    
    # Get the list of shared_items
    shared={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            shared[item]=1

    # if they have no ratings in common, return 0
    if len(shared)==0: return 0
    
    # Add up the squares of all the differences
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sum_of_squares)


def sim_pearson(prefs,p1,p2):
    """
    Returns the Pearson correlation coefficient for p1 and p2
    """
    
    # Get the list of mutually rated items
    si={}

    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1

    # Find the number of elements
    n=len(si)
    # if they are no ratings in common, return 0
    if n==0: return 0

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


################ UBCF ##################

def getRecommendations(prefs,person,similarity=sim_distance):
    """
    Gets recommendations for a person by using a weighted average
    of every other user's rankings
    """
    totals={}
    simSums={}
    for other in prefs:
        # don't person to himself.
        if other==person: continue

        sim=similarity(prefs,person,other)
        # ignore scores of zero or lower
        if sim<=0: continue

        for item in prefs[other]:
            # only score movies person has not seen yet.
            if item not in prefs[person] or prefs[person][item]==0:
                # Similarity * Score
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim

                # Sum of similarities
                simSums.setdefault(item,0)
                simSums[item]+=sim
                
    # Create the normalized list
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings


################## IBCF #####################

def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            # Flip item and person
            result[item][person]=prefs[person][item]
    return result


def topMatches(prefs,person,n=5,similarity=sim_pearson):
    """
    Returns the best matches for person from the prefs dictionary.
    """
    scores=[(similarity(prefs,person,other),other) for other in prefs if other!=person]
    # Sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[0:n]

def calculateSimilarItems(prefs,n=10):
    """
    Create a dictionary of items showing which other items they
    are most similar to.
    """
    result={}
    # Invert the preference matrix to be item-centric
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        # Status updates for large datasets
        c+=1
        if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        # Find the most similar items to this one
        scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result


def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}

    print "Generating item recommendations for user: %s"%(user)
    
    try:
        # Loop over items rated by this user
        for (item,rating) in userRatings.items():
            # Loop over items similar to this one
            for (similarity,item2) in itemMatch[item]:
    
                # Ignore if this user has already rated this item
                # Note: To be modified in new algorithm.
                if item2 in userRatings: continue
                
                # Weighted sum of rating times similarity
                scores.setdefault(item2,0)
                scores[item2]+=similarity*rating
    
                # Sum of all the similarities
                totalSim.setdefault(item2,0)
                totalSim[item2]+=similarity
                
                # Divide each total score by total weighting to get an average
                try:
                    rankings=[(score/totalSim[item],item) for item,score in scores.items()]
                except ZeroDivisionError, dz:
                    print "Division by zero :( "
                    continue
    except Exception:
        print ":("
            
        # Return the rankings from highest to lowest
        rankings.sort()
        rankings.reverse()
    return rankings


################## DATA LOADING #####################

"""
100,000 ratings (1-5) from 943 users on 1682 movies. 
Each user has rated at least 20 movies.
"""

def loadMovieLens(path='../dataset'):
    # Get movie titles
    #1|Toy Story (1995)|01-Jan-1995||http://us.imdb.com/M/title-exact?Toy%20Story%20(1995)|0|0|0|1|1|1|0|0|0|0|0|0|0|0|0|0|0|0|0
    movies={}
    for line in open(path+'/u.item'):
        (id,title)=line.split('|')[0:2]
        movies[id]=title

    # Load data
    #196	242	3	881250949
    #186	302	3	891717742

    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]]=float(rating)

    return prefs


def load(path='../dataset'):
    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts)=line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movieid] = float(rating)
    return prefs

"""
def saveOriginalSim():
    f = open('../itemsim/original_sim','w')
    for item in range(ITEMS):
        f.write(str(item + 1) + '\t')
	for (i,b) in itemsim[str(item+1)]:
            f.write(str(i) + '\t' + str(b))
            if item != ITEMS:
                f.write('\t')
	f.write('\n')
    f.close()
"""

if __name__ == '__main__':
    ITEMS = 1682
    prefs = load()
    itemsim = calculateSimilarItems(prefs, n=50)
    ranking = getRecommendedItems(prefs, itemsim,'1')
    print ranking[:10]
