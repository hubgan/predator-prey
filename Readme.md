# Wolf-Sheep Predator-Prey Simulation

This project was developed as part of a course conducted at the Faculty of Computer Science, AGH University of Science and Technology (Akademia Górniczo-Hutnicza), Kraków, Poland.

This repository contains an implementation of the classic predator-prey (Wolf-Sheep) ecosystem simulation.  
The simulation is based on the [Mesa Experimental](https://github.com/projectmesa/mesa) agent-based modeling framework and demonstrates predator (wolf) and prey (sheep) population dynamics in a grid-based environment.

## Features

- **Agent-based simulation** of wolves, sheep, and grass on a 2D grid.
- **Customizable model parameters** via UI sliders and controls (e.g., initial populations, reproduction rates, energy gains, grass regrowth, movement cost, etc.).
- **Smart movement**: Optional logic for agents to avoid threats or seek food.
- **Grass regrowth**: Optionally enables a regrowing grass resource for sheep.
- **Comprehensive statistics**: Real-time plots of population sizes, energy distributions, ratios, and statistical measures.
- **Interactive visualization** using SolaraViz and Mesa Experimental.

## Model Description

- **Sheep** move across the grid, eat grass (if enabled), and reproduce probabilistically, consuming energy per movement.
- **Wolves** hunt sheep, gain energy from eating, reproduce, and also lose energy per movement.
- **Grass patches** regrow after being eaten, if the grass option is enabled.
- **Smart movement** (optional): Sheep avoid wolves, and wolves seek sheep.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [Mesa Experimental](https://github.com/projectmesa/mesa) (development version)
- Other dependencies as required in `requirements.txt` (e.g., Solara, matplotlib, etc.)

### Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Simulation

You can launch the interactive visualization with:

```bash
solara run app.py
```

## Customization

You can configure model parameters (e.g., initial populations, reproduction rates, grass regrowth time) using the sliders and controls in the app interface.
These parameters allow you to experiment with different ecosystem dynamics and observe emergent behaviors.

## Visualization

The simulation visualizes agents on a 2D grid:

- **Wolves:** Red circles
- **Sheep:** Cyan circles
- **Grass:** Green or brown squares (grown/empty)

Several real-time plots are available for:

- Population counts
- Energy levels
- Population ratios
- Additional ecosystem statistics
