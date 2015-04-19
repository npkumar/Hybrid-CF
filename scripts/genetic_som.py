from __future__ import division

import os
import random
import time
import inspyred
import Orange

rand = random.Random()
rand.seed(int(time.time()))

MIN_CLUSTERS=4
MAX_CLUSTERS=20
filename='../dataset/som_dense_matrix.tab'
final_pop = ''

def setMaxClusters(value):
    MAX_CLUSTERS = value

def setMinClusters(value):
    MIN_CLUSTERS = value

def setFilename(value):
    filename = value
    
def binaryTodecimal(candidate):
    """
    Custom
    Return b2d plus 1
    """
    return int("".join([str(c) for c in candidate]), 2) + 1

def get_map_x(x):
    """
    Three bits
    """
    return binaryTodecimal(x)

def get_map_y(y):
    """
    Three bits
    """
    return binaryTodecimal(y)

def get_topology(l):
    """
    Single bit
    """
    x = binaryTodecimal(l)
    if x == 1:
        return Orange.projection.som.RectangularTopology
    else:
        return Orange.projection.som.HexagonalTopology

def get_neighbourhood_function(l):
    """
    Two bits
    """
    x = binaryTodecimal(l)
    if x == 1:
        return Orange.projection.som.NeighbourhoodGaussian
    elif x == 2:
        return Orange.projection.som.NeighbourhoodBubble #crisp
    else:
        return Orange.projection.som.NeighbourhoodEpanechicov #cut and smoothed

def get_float_learning_rate(l):
    """
    Custom learning rate function
    Three bits
    """
    x = binaryTodecimal(l)
    val = {1:0.1,2:0.2,3:0.3,4:0.4,5:0.5,6:0.6,7:0.7,8:0.8}

    return val[x]

    """
    if x in [0,1]:
        return 0.6
    try:
        value = x / (pow(2,x) - 1)
        return round(value,1)
    except ZeroDivisionError as zero_error:
        print zero_error
    """

@inspyred.ec.generators.diversify
def generate_binary(random, args):
    """
    This function decorator is used to enforce uniqueness of candidates created by a generator.
    The decorator maintains a list of previously created candidates, and
    it ensures that new candidates are unique by checking a generated candidate against that list, regenerating if a duplicate is found.
    """
    bits = args.get('num_bits', 11)
    return [random.choice([0, 1]) for i in range(bits)]


@inspyred.ec.evaluators.evaluator
def fitness_func(chromosome, args):
    """
    Return an inspyred evaluator function based on the given function.
    This function generator takes a function that evaluates only one candidate.
    The generator handles the iteration over each candidate to be evaluated.
    """
    score = 0
    total = 0
    count = 0
    # iterate over the chromosome
    map_x=binaryTodecimal(chromosome[0:3])
    map_y=binaryTodecimal(chromosome[3:6])
    rate_learning=get_float_learning_rate(chromosome[6:9])
    neighbourhood_type=get_neighbourhood_function(chromosome[9:11])

    #topology_type=get_topology(chromosome[11:])
    topology_type=Orange.projection.som.RectangularTopology
    
    print chromosome
    print "x = %d, y = %d, learning_rate = %f, neighbourhood = %s, topology = %s"%(map_x,map_y,rate_learning,neighbourhood_type,topology_type)

    if ((map_x * map_y) < MIN_CLUSTERS) or ((map_x * map_y) > MAX_CLUSTERS):
        return 999
    
    #x3,y3,topology1,neighbourhood2,learning_rate3
    som = Orange.projection.som.SOMLearner(map_shape=(map_x, map_y),
                                          initialize=Orange.projection.som.InitializeRandom,
                                          topology=Orange.projection.som.RectangularTopology,
                                          neighbourhood=neighbourhood_type, 
                                          batch_train=True,
                                          learning_rate=rate_learning,
                                          radius_ini=4,
                                          radius_fin=2,
                                          epochs=1000)  #iterations of a training step
    try:
        map = som(Orange.data.Table(filename))

        for n in map:
            total += len(n.instances)
            count += 1

        total_average = total / count
   
        for n in map:
            score += abs(total_average - len(n.instances))
            
    except Exception as e:
        print 'Error classifing using SOM. :('
        return 1000
    
    return score

def genetic(pop=5,max_evals=5,elites=2):
    """
    http://pythonhosted.org/inspyred/reference.html#module-inspyred.ec
    class inspyred.ec.GA(random)
    This class represents a genetic algorithm which uses, by default, rank selection, n-point crossover, bit-flip mutation, and generational replacement.
    In the case of bit-flip mutation, it is expected that each candidate solution is a Sequence of binary values.
    """
    print "Basic configuration pop=%d, max_evals=%d, elites=%d"%(pop,max_evals,elites)
    print "MIN_CLUSTERS: %d"%(MIN_CLUSTERS)
    print "MAX_CLUSTERS: %d"%(MAX_CLUSTERS)
    
    ga = inspyred.ec.GA(rand)
    
    ga.observer = inspyred.ec.observers.stats_observer
    ga.terminator = inspyred.ec.terminators.evaluation_termination

    try:
        final_population = ga.evolve(evaluator=fitness_func,
                      generator=generate_binary,
                      mutation_rate=0.1, # the rate at which mutation is performed (default 0.1)
                      crossover_rate=0.6, # the rate at which crossover is performed (default 1.0)
                      num_elites=elites, #number of elites to consider (default 0)
                      max_evaluations=max_evals,
                      maximize=False,
                      pop_size=pop,
                      num_bits=11) # 3 3 3 2 (1)

        for ind in final_population:
            print(str(ind))
        
        # Sort and print the best individual, who will be at index 0.

        print "Best suggestion:"
        final_population.sort(reverse=True)
        print(final_population[0])
        final_pop = str(final_population[0])
        
    except Exception,e:
        print "Error for configuration pop=%d, max_evals=%d, elites=%d"%(pop,max_evals,elites)
    

def getChromosomeList(string):
    return list(str(string).split(' : ')[0].replace(',','').replace('[','').replace(']','').replace(' ','').strip())

def persistClusters(finalChromosome,filename='../dataset/som_dense_matrix.tab', folder='output', clustername='CLUSTER'):
    # iterate over the chromosome
    map_x=binaryTodecimal(finalChromosome[0:3])
    map_y=binaryTodecimal(finalChromosome[3:6])
    rate_learning=get_float_learning_rate(finalChromosome[6:9])
    neighbourhood_type=get_neighbourhood_function(finalChromosome[9:11])

    #topology_type=get_topology(finalChromosome[11:])
    topology_type=Orange.projection.som.RectangularTopology

    print "Setting up selected Cluster.."
    print "x = %d, y = %d, learning_rate = %f, neighbourhood = %s, topology = %s"%(map_x,map_y,rate_learning,neighbourhood_type,topology_type)
    som = Orange.projection.som.SOMLearner(map_shape=(map_x, map_y),
                                          initialize=Orange.projection.som.InitializeRandom,
                                          topology=Orange.projection.som.RectangularTopology,
                                          neighbourhood=neighbourhood_type, 
                                          batch_train=True,
                                          learning_rate=rate_learning,
                                          radius_ini=4,
                                          radius_fin=2,
                                          epochs=1000)  #iterations of a training step
    
    try:
        map = som(Orange.data.Table(filename))

        cluster_size =0
        for n in map:
            cluster_size += 1
        print "Cluster size: %d"%(cluster_size)

        if not os.path.exists('../' +folder):
            os.makedirs('../' +folder)
        
        for i in range(map_x):
            for j in range(map_y):
                output = '../' +folder+ '/' + clustername+ '_' + str(i) + str(j)
                print "Persisting CLUSTER ID: " + output
                f = open(output,'w')
                for n in map[i,j].instances:
                    f.write(str(n).replace(']','@').replace('[','').strip().replace('\'',''))
                f.close()
    except Exception as e:
        print 'Error classifing using SOM.'


#DEPRECIATED FUNC        
def dep_persistClusters(finalChromosome,filename='../dataset/som_dense_matrix.tab', clustername='CLUSTER'):
    # iterate over the chromosome
    map_x=binaryTodecimal(finalChromosome[0:3])
    map_y=binaryTodecimal(finalChromosome[3:6])
    rate_learning=get_float_learning_rate(finalChromosome[6:9])
    neighbourhood_type=get_neighbourhood_function(finalChromosome[9:11])

    #topology_type=get_topology(finalChromosome[11:])
    topology_type=Orange.projection.som.RectangularTopology

    print "Setting up selected Cluster.."
    print "x = %d, y = %d, learning_rate = %f, neighbourhood = %s, topology = %s"%(map_x,map_y,rate_learning,neighbourhood_type,topology_type)
    som = Orange.projection.som.SOMLearner(map_shape=(map_x, map_y),
                                          initialize=Orange.projection.som.InitializeRandom,
                                          topology=Orange.projection.som.RectangularTopology,
                                          neighbourhood=neighbourhood_type, 
                                          batch_train=True,
                                          learning_rate=rate_learning,
                                          radius_ini=4,
                                          radius_fin=2,
                                          epochs=1000)  #iterations of a training step
    

    try:
        map = som(Orange.data.Table(filename))

        cluster_size =0
        for n in map:
            cluster_size += 1
        print "Cluster size: %d"%(cluster_size)

        for x in range(map_x):
            for y in range(map_y):
                CLUSTER = clustername + '_' + str(x) + str(y)
                print "Persisting CLUSTER id: %s"%(CLUSTER)
                        
                for e in map[x,y].instances:
                    try:
                        f = open('../output/' + CLUSTER,"w")
                        #f.write(str(e).replace(']','\n').replace('[','').replace('\'','').strip())
                        f.write(str(e).strip())
                        f.close()
                    except Exception as e:
                        print "Error during file handling " + CLUSTER + " :" + e
                        
    except Exception as e:
        print 'Error classifing using SOM.'

    
if __name__ == '__main__':
    
    start = time.clock()
    genetic()
    stop = time.clock()
    print "Total time: %d"%(stop - start)
