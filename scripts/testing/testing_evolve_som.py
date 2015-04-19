import random
import time
import inspyred
import Orange

rand = random.Random()
rand.seed(int(time.time()))


def generate_binary(random, args):
    bits = args.get('num_bits', 8)
    return [random.choice([0, 1]) for i in range(bits)]

def evaluate_binary(candidate, args):
    return int("".join([str(c) for c in candidate]), 2)

@inspyred.ec.generators.diversify
def generate_numbers(random, args):
    """
    This function decorator is used to enforce uniqueness of candidates created by a generator. The decorator maintains a list of previously created candidates, and
    it ensures that new candidates are unique by checking a generated candidate against that list, regenerating if a duplicate is found.
    """
    bits = 2
    return [random.choice([2,3,4,5]) for i in range(bits)]

@inspyred.ec.evaluators.evaluator
def fitness_func(chromosome,args):
   score = 0
   total = 0
   count = 0
   # iterate over the chromosome
   x,y = chromosome[0],chromosome[1]

   print "x=" + str(x) + "y=" + str(y)
   
   som = Orange.projection.som.SOMLearner(map_shape=(x, y), initialize=Orange.projection.som.InitializeRandom,topology=Orange.projection.som.RectangularTopology,neighbourhood=Orange.projection.som.NeighbourhoodGaussian,learning_rate=0.1)
   try:
       map = som(Orange.data.Table("../dataset/som_dense_matrix.tsv"))
   except Error:
       print 'Error classifing using SOM.'

   for n in map:
       total += len(n.instances)
       count += 1

   total_average = total / count
   
   for n in map:
       score += abs(total_average - len(n.instances))
   
   
   return score


def genetic():


    """
    http://pythonhosted.org/inspyred/reference.html#module-inspyred.ec
    class inspyred.ec.GA(random)
    This class represents a genetic algorithm which uses, by default, rank selection, n-point crossover, bit-flip mutation, and generational replacement.
    In the case of bit-flip mutation, it is expected that each candidate solution is a Sequence of binary values.
    """
    ga = inspyred.ec.GA(rand)
    
    ga.observer = inspyred.ec.observers.stats_observer
    ga.terminator = inspyred.ec.terminators.evaluation_termination

    final_pop = ga.evolve(evaluator=fitness_func,
                      generator=generate_numbers,
                      mutation_rate=0.1, # the rate at which mutation is performed (default 0.1)
                      crossover_rate=0.6, # the rate at which crossover is performed (default 1.0)
                      num_elites=2, #number of elites to consider (default 0)
                      max_evaluations=15,
                      maximize=False,
                      pop_size=5,
                      num_bits=2)

    for ind in final_pop:
        print(str(ind))
        
    # Sort and print the best individual, who will be at index 0.

    print "Best suggestion:"
    final_pop.sort(reverse=True)
    print(final_pop[0])

    
