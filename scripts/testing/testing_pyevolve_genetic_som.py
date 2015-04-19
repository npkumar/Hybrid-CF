"""
Works only with 2.6 or earlier.
"""
try:
    import Orange
except Error:
    print 'Problem loading Orange 2.6'


try:
    from pyevolve import G1DList
    from pyevolve import GSimpleGA
except Error:
    print 'Problem loading PyEvolve 2.6 modules'
    
import random
random.seed(0)


def fitness_func(chromosome):
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
   
   
   return 1 / (1 + score)


def genetic():
    genome = G1DList.G1DList(2)
    genome.evaluator.set(fitness_func)
    genome.setParams(rangemin=2, rangemax=4)
    ga = GSimpleGA.GSimpleGA(genome)
    ga.evolve(freq_stats=10)
    print ga.bestIndividual()

