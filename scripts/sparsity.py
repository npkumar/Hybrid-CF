from __future__ import division


from math import sqrt
import time

USERS = 943
ITEMS = 1682
MAX_SIM_CBR_USERS = 100 #changed for case one testing.

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
            rankings=[(score/totalSim[item],item) for item,score in scores.items()]

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

############## SPARSITY ##################

def getSimilarUserBasedRecommendations(prefs,person,num_users=10,similarity=sim_distance):
    totals={}
    simSums={}
    topSimilarUsers = topMatches(prefs,person,n=num_users)
    for (sim, userid) in topSimilarUsers:
        #print userid + '-' + str(sim)
    
        for item in prefs[userid]:
            # only score movies person has not seen yet.
            if item not in prefs[person] or prefs[person][item]==0:
                # Similarity * Score
                totals.setdefault(item,0)
                totals[item]+=prefs[userid][item]*sim

                # Sum of similarities
                simSums.setdefault(item,0)
                simSums[item]+=sim

    # Create the normalized list
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

#clustering using k-fold validation
def clustering_doFillUsingCBR(prefs):
    print "Starting CBR process..."
    for person in prefs:
        print "User : " + person
		
        recommendations = getSimilarUserBasedRecommendations(prefs, person,num_users=MAX_SIM_CBR_USERS)
        for (rating, item) in recommendations:
            prefs[person][item] = rating


def clustering_doAverageFilling(prefs):
    print "Starting Average Filling..."
    average = {}

    #Get Averages for every person
    for person in prefs:
        average.setdefault(person, 0)
        
        print "User : " + person
        count = 0
        total = 0
        for item in prefs[person]:
            total += prefs[person][item]
            count += 1
        average[person] = (total/count)

    #Assign averages to all slots per person.
    for person in prefs:
        for item in range(ITEMS):
            if (str(item+1)) not in prefs[person]:
                prefs[person][str(item+1)] = average[person]

			
	
def doFillUsingCBR(prefs):
    print "Starting CBR process..."

    for person in range(USERS):
        print "User : " + str(person+1)
        #print len(prefs[str(person+1)])
        
        recommendations = getSimilarUserBasedRecommendations(prefs, str(person+1),num_users=MAX_SIM_CBR_USERS)
        for (rating, item) in recommendations:
            prefs[str(person+1)][item] = rating

        #print len(prefs[str(person+1)])

### Modified for TEST CASE 1
def caseone_doFillUsingCBR(prefs, delusers):
    print "Starting CBR process..."

    for person in range(USERS):
        print "User : " + str(person+1)
        #print len(prefs[str(person+1)])
        if (person+1) not in delusers:
            recommendations = getSimilarUserBasedRecommendations(prefs, str(person+1),num_users=MAX_SIM_CBR_USERS)
            for (rating, item) in recommendations:
                prefs[str(person+1)][item] = rating

        

            
def doAverageFilling(prefs):
    print "Starting Average Filling..."
    average = {}

    #Get Averages for every person
    for person in range(USERS):
        average.setdefault(str(person+1), 0)
        
        print "User : " + str(person+1)
        count = 0
        total = 0
        for item in prefs[str(person+1)]:
            total += prefs[str(person+1)][item]
            count += 1
        average[str(person+1)] = (total/count)
        #print average[str(person+1)]

    #Assign averages to all slots per person.
    for person in range(USERS):
        for item in range(ITEMS):
            if (str(item+1)) not in prefs[str(person+1)]:
                prefs[str(person+1)][str(item+1)] = average[str(person+1)]

### Modified for CASE 1
def caseone_doAverageFilling(prefs,delusers):
    print "Starting Average Filling..."
    average = {}

    #Get Averages for every person
    for person in range(USERS):
        if (person+1) not in delusers:
            average.setdefault(str(person+1), 0)
        
            print "User : " + str(person+1)
            count = 0
            total = 0
            for item in prefs[str(person+1)]:
                total += prefs[str(person+1)][item]
                count += 1
            average[str(person+1)] = (total/count)
            #print average[str(person+1)]

    #Assign averages to all slots per person.
    for person in range(USERS):
        for item in range(ITEMS):
            if (person+1) not in delusers:
                if (str(item+1)) not in prefs[str(person+1)]:
                    prefs[str(person+1)][str(item+1)] = average[str(person+1)]



def saveDenseMatrix(prefs,filename='..\dataset\som_dense_matrix.tab'):
    print "Saving Dense Matrix..."

    f = open(filename,'w')

    #this section is specific to Orange SOM library API
    f.write("i" + "\t")
    for item in range(ITEMS):
        f.write("c")
        if item != ITEMS:
            f.write("\t")
    f.write("\n")

    # Actual data content from memory
    for person in prefs:
        f.write(str(person) + "\t")

        for item in range(ITEMS):
            f.write(str(round(prefs[str(person)][str(item+1)],2)))
            if item != ITEMS:
                f.write("\t")
        f.write("\n")

    f.close()
    
if __name__ == '__main__':
    
    
    load_start = time.clock()
    prefs = load()

    load_stop = time.clock()

    cbr_start = time.clock()
    doFillUsingCBR(prefs)
    cbr_stop = time.clock()

    avg_start = time.clock()
    doAverageFilling(prefs)
    avg_stop = time.clock()

    save_start = time.clock()
    saveDenseMatrix(prefs, filename)
    save_stop = time.clock()

    print time.ctime()
    print "TIme to load %f seconds."%(load_stop - load_start)
    print "TIme for CBR %f seconds."%(cbr_stop - cbr_start)
    print "TIme for AVG %f seconds."%(avg_stop - avg_start)
    print "TIme to save %f seconds."%(save_stop - save_start)


    
