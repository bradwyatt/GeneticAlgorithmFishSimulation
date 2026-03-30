# Genetic Algorithm Fish Simulation

This project is an adaptation of the Python-based genetic algorithm work from PyWorld by HanaAuana: https://github.com/HanaAuana/PyWorld

This project is a `pygame` simulation where a population of fish evolves over time under predator pressure. Each fish carries a 22-bit genome that controls how it moves, how large it is, how often it turns, how far ahead it can see danger in front of it, and how likely it is to react intelligently to a shark entering its vision arc.

At a high level, every generation works like this:

1. Spawn a population of fish and a fixed number of sharks in a bounded arena.
2. Let the simulation run until every fish has been eaten.
3. Use survival time as fitness.
4. Select parents probabilistically based on fitness.
5. Produce a new population with crossover, mutation, and a small elite carry-over.
6. Repeat indefinitely.

Over time, the system tends to discover fish that survive longer by evolving a useful balance of small size, lower speed, wider awareness, and better reactions.

## Setup

The project uses a modern `pygame` wheel (`2.6.1`) and runs well on current macOS / Python 3.11+ setups.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 main.py
```

If an older local environment still has `pygame==1.9.x`, reinstall:

```bash
python3 -m pip uninstall -y pygame
python3 -m pip install -r requirements.txt
```

## What The Simulation Is Optimizing

The dependent variable is survival time.

The score shown at the top of the screen is the current generation's running fitness counter. When a fish dies, it is stored alongside that score. At the end of the generation, the dead fish are ranked by score, and those results drive selection for the next generation.

The simulation is intentionally simple:

- Fish do not learn during a generation.
- Sharks do not evolve.
- The only thing that changes from generation to generation is fish DNA.
- The environment is mostly static, so selection pressure stays consistent.

That makes it easier to see how traits emerge from repeated selection rather than from hand-authored behaviors.

## Architecture

The project is small, but it has a clean separation between simulation concerns:

### Entry Point

- `main.py`

This is the runtime orchestrator. It owns:

- The `pygame` loop
- Sprite/entity classes (`Wall`, `RedFish`, `Arc`, `Shark`)
- Population creation
- Collision handling
- Generation rollover
- Rendering and HUD updates

### Genetic Algorithm

- `genetic_algorithm.py`

This module contains the evolutionary operators:

- `get_next_pop()`
- `crossover()`
- `mutate()`

It is intentionally isolated from rendering so the selection logic can be reasoned about independently from the game loop.

### Genome Representation

- `DNA.py`

This module defines the `DNA` class, which stores the bitstring for one organism. It can:

- Generate a random genome
- Return a single gene by index
- Return a human-readable grouped genotype
- Return the full genotype string for cloning / reproduction

### Shared Configuration

- `config.py`

This holds the core simulation constants:

- Screen size
- Population size
- Number of genes
- Number of elite clones
- Mutation chance

### Startup / Working Directory Bootstrapping

- `app_setup.py`

This makes sure the process is running relative to the project directory so local assets resolve correctly.

### Asset Loading

- `resources.py`

This centralizes image definitions and loads sprite assets into memory. It also includes a small case-insensitive path resolver so assets still load if filename casing differs across environments.

## Runtime Flow

The simulation loop in `main.py` can be thought of as two nested cycles:

1. A frame-by-frame game loop
2. A generation-by-generation evolution loop

### Frame Loop

Each frame:

1. Polls input and window events
2. Updates all sprite positions
3. Scrolls the water background
4. Draws the room, sprites, and HUD
5. Resolves collisions with walls and sharks
6. Increments the current fitness score

### Generation Loop

A generation ends when `RedFish.redfishes` becomes empty.

At that point the simulation:

1. Sorts the dead fish by score
2. Prints the strongest half of the population to the console
3. Computes the average score for the generation
4. Updates the high-score generation if needed
5. Builds the next generation's DNA
6. Recreates fish and arcs
7. Resets the arena and starts again

## Genetic Encoding

Each fish has exactly `22` genes stored as a binary string.

Those bits are expressed into five traits:

| Bit Range | Trait | Expression |
| --- | --- | --- |
| `0-4` | Size | `6 + int(bits, 2)` |
| `5-7` | Speed | `2 + int(bits, 2)` |
| `8-11` | Frequency of turns | `1 + int(bits, 2)` |
| `12-16` | Vision arc radius | `1 + int(bits, 2)` |
| `17-21` | Intelligence | `1 + int(bits, 2)` |

### Trait Meanings

- `Size`
  Larger fish have larger sprite bounds and interact with walls differently. Smaller fish tend to be harder targets.
- `Speed`
  Higher speed means more movement per frame, but also less stable trajectories.
- `Frequency of turns`
  This controls how often a fish picks a new random direction.
- `Vision arc radius`
  This controls how large the fish's forward eyesight arc becomes.
- `Intelligence`
  This is not planning or memory. It is simply the chance that a fish reacts when a shark enters its eyesight arc.

## How Fish Behavior Emerges

Fish behavior is partly deterministic and partly probabilistic.

Every fish:

- Has a heading
- Moves continuously according to speed and direction
- Randomly re-rolls its direction after a number of frames determined by `freq_turns`
- Bounces away from walls by being repositioned and assigned a new direction

In addition, each fish owns a paired `Arc` sprite that acts like its forward eyesight.

If a shark overlaps that arc:

1. The fish checks whether it has already registered that shark.
2. If not, it rolls a random integer from `0` to `31`.
3. If the value is less than the fish's intelligence score, it reverses direction.

That means "intelligence" is really a reaction probability, not a pathfinding system. This is important because the project demonstrates that even very simple local rules can create useful population-level adaptation.

## Selection, Crossover, and Mutation

The simulation uses a classic evolutionary pattern.

### Selection

At the end of the generation, each dead fish is paired with its survival score.

`get_next_pop()` converts those scores into weighted selection probabilities. Fitter fish are more likely to be chosen as parents, but weaker fish are not always impossible to choose. That balance keeps the search space from collapsing too quickly.

There is also a fallback for a degenerate case where all fitness values are zero: parent selection becomes uniform rather than dividing by zero.

### Crossover

For each gene position, the child inherits either parent A's bit or parent B's bit. Two children are produced at the same time, with complementary inheritance at each bit position.

This allows useful trait combinations to spread without requiring mutation to rediscover them from scratch.

### Mutation

After crossover, each gene has a `5%` chance of flipping:

- `0 -> 1`
- `1 -> 0`

Mutation prevents the simulation from getting trapped too early in a narrow part of the search space.

### Elitism

The top `2` fish from the previous generation are copied directly into the next generation as elite clones.

In the game, those elite fish are rendered with alternate sprites so they are easy to spot visually.

## Why The Evolution Trend Looks The Way It Does

The results shown in the screenshots are consistent with the mechanics of the environment:

- Small fish are harder to collide with.
- Extremely high speed is not automatically beneficial because it can create unstable movement.
- Wider eyesight arcs improve early detection.
- Higher intelligence improves the chance of reacting when danger is detected.
- Frequent turning can help fish avoid predictable paths that line them up with sharks.

Because the sharks are constant and the room geometry never changes, selection pressure repeatedly rewards trait bundles that maximize survival in that exact environment.

This is a good example of an important genetic algorithm principle: the algorithm is only as meaningful as the fitness landscape you create.

## Main Entities

### `RedFish`

Represents one evolving organism.

Responsibilities:

- Express a genome into runtime traits
- Move each frame
- React to sharks entering its forward eyesight
- Handle wall collisions
- Report its score when it dies

### `Arc`

Represents a fish's forward eyesight.

Responsibilities:

- Follow the fish with the same index
- Flip to the left/right arc sprite depending on fish direction
- Scale based on the fish's `radius_arc`

### `Shark`

Represents a non-evolving predator.

Responsibilities:

- Move through the room
- Bounce off walls
- Kill fish on collision

### `Wall`

Represents the arena bounds.

Responsibilities:

- Define the perimeter
- Provide collision targets for fish and sharks

## Console Output

At the end of each generation the program prints:

- The top 50% of the generation
- Each survivor's grouped genotype
- That fish's score
- The average score for the generation

This is useful when you want to correlate visible behavior with actual gene values instead of treating the simulation as a black box.

## Visual Notes

- Red fish are normal population members.
- Blue fish are elite clones carried over from the previous generation.
- The HUD shows current fitness, generation, highest average score, and best generation.
- A screenshot is saved briefly around score `10`, then kept only if that generation beats the previous high score average.

## Repository Layout

```text
.
├── DNA.py
├── app_setup.py
├── config.py
├── genetic_algorithm.py
├── main.py
├── resources.py
├── requirements.txt
├── Docs/
├── Fonts/
└── Sprites/
```

## Observing Fish Generations Over Time

### Generation 0 (START)

<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation0.jpeg" height="300" width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation0_score.PNG"></img>
</p>

Start of the simulation:

- The top-performing fish still have mostly random trait combinations.
- Early success is noisy because no stable strategy has emerged yet.

### Generation 48

<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation48.jpeg" height="300" width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation48_score.PNG"></img>
</p>

Compared to previous generations:

- Size tends to decrease
- Speed is very slow
- Radius arc slightly higher
- Intelligence slightly higher

### Generation 241

<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation241.jpeg" height="300" width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation241_score.PNG"></img>
</p>

Compared to previous generations:

- Size slightly increases
- Speed remains slow
- Turn frequency significantly higher
- Intelligence very high

### Generation 909 (MAX)

<p align="center">
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/Generation909.jpeg" height="300" width="400"></img>
<img src="https://github.com/bradwyatt/GeneticAlgorithmFishSimulation/blob/master/Docs/generation909_score.PNG"></img>
</p>

Compared to previous generations:

- Size extremely small
- Speed very slow
- Big radius arc
- High intelligence

## Future Directions

Some natural extensions if you want to push the experiment further:

- Evolve sharks as well as fish
- Add multiple fitness objectives
- Add obstacles or changing environments between generations
- Record per-generation metrics to CSV for plotting
- Replace the current reaction rule with a richer steering behavior

## References

- This project adapts the original Python-based genetic algorithm work from PyWorld by HanaAuana: https://github.com/HanaAuana/PyWorld
