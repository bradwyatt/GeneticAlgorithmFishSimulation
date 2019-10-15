# Genetic Algorithm Fish Simulation

The goal (dependent variable) is for the population of red fish to evolve by developing traits that will help them survive for a longer period of time before being eaten by sharks.

- The strongest 50% of each fish population mate, while the weakest are eliminated from the gene pool.  The blue fish are the top 2 fish from the previous generation.

- The variables I created includes field of vision (the arc each fish can ‘see’ a shark), size, speed, intelligence (does the fish move away from a shark as it enters the arc), and frequency of turns.

As a result, The fish last longer before being eaten as time goes on.

## Observing Fish Generations Over Time

### Generation 0
<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation0.jpeg" height="300", width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation0_score.PNG"></img>
</p>
Start of the simulation: 

- The Top 50% output (to the left) was produced after the red fish were all eaten by sharks 
- The red fish with the highest scores have very random traits

### Generation 48
<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation48.jpeg" height="300", width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation48_score.PNG"></img>
</p>
Compared to previous generations:

- Size tends to decrease
- Speed is very slow
- Radius arc slightly higher
- Intelligence slightly higher

### Generation 241
<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation241.jpeg" height="300", width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation241_score.PNG"></img>
</p>
Compared to previous generations:

- Size slightly increases
- Speed remains slow
- Turn frequency significantly higher
- Intelligence very high

### Generation 909 (MAX)
<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation909.jpeg" height="300", width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation909_score.PNG"></img>
</p>
Compared to previous generations:

- Size extremely small
- Speed very slow
- Big radius arc
- High intelligence

## References
Genetic Algorithm code was from https://github.com/HanaAuana/PyWorld (initiation of DNA in objects)
