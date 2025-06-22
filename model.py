import math
import statistics

from mesa import Model
from agents.agents import Wolf, Sheep, GrassPatch, Ground
from mesa.datacollection import DataCollector
from mesa.experimental.cell_space import OrthogonalVonNeumannGrid
from mesa.experimental.devs import ABMSimulator


def median(values):
    if not values:
        return 0

    values = sorted(values)
    n = len(values)
    mid = n // 2
    return values[mid] if n % 2 != 0 else (values[mid - 1] + values[mid]) / 2


class WolfSheep(Model):
    description = "A model for simulating predator-prey ecosystem modelling."

    def __init__(
            self,
            width=20,
            height=20,
            initial_sheep=140,
            initial_wolves=40,
            sheep_reproduce=0.04,
            wolf_reproduce=0.05,
            sheep_gain_from_food=4,
            wolf_gain_from_food=20,
            grass_regrowth_time=30,
            simulator: ABMSimulator = None,
            grass=False,
            smart_movement=False,
            sheep_movement_cost=1,
            wolf_movement_cost=1,
            sheep_reproduction_energy_share=50,
            wolf_reproduction_energy_share=50,
            seed=None
    ):
        super().__init__(seed=seed)

        self.simulator = simulator
        self.simulator.setup(self)

        self.width = width
        self.height = height
        self.grass = grass
        self.smart_movement = smart_movement
        self.sheep_movement_cost = sheep_movement_cost
        self.wolf_movement_cost = wolf_movement_cost
        self.sheep_reproduction_energy_share = sheep_reproduction_energy_share / 100
        self.wolf_reproduction_energy_share = wolf_reproduction_energy_share / 100
        self.grid = OrthogonalVonNeumannGrid(
            [self.height, self.width],
            torus=True,
            capacity=math.inf,
            random=self.random,
        )

        reporters = {
            "Wolf": lambda m: len(m.agents_by_type[Wolf]),
            "Sheep": lambda m: len(m.agents_by_type[Sheep]),
            "Grass": (lambda grass_enabled:
                      (lambda m: len(
                          m.agents_by_type[GrassPatch].select(lambda gp: gp.is_grown)
                      ) if grass_enabled else 0)
                      )(self.grass),
            "AvgWolfEnergy": lambda m: (
                sum(w.energy for w in m.agents_by_type[Wolf]) / len(m.agents_by_type[Wolf])
                if len(m.agents_by_type[Wolf]) > 0 else 0
            ),
            "AvgSheepEnergy": lambda m: (
                sum(s.energy for s in m.agents_by_type[Sheep]) / len(m.agents_by_type[Sheep])
                if len(m.agents_by_type[Sheep]) > 0 else 0
            ),
            "MaxWolfEnergy": lambda m: (
                max([w.energy for w in m.agents_by_type[Wolf]]) if len(m.agents_by_type[Wolf]) > 0 else 0
            ),
            "MinWolfEnergy": lambda m: (
                min([w.energy for w in m.agents_by_type[Wolf]]) if len(m.agents_by_type[Wolf]) > 0 else 0
            ),
            "MaxSheepEnergy": lambda m: (
                max([s.energy for s in m.agents_by_type[Sheep]]) if len(m.agents_by_type[Sheep]) > 0 else 0
            ),
            "MinSheepEnergy": lambda m: (
                min([s.energy for s in m.agents_by_type[Sheep]]) if len(m.agents_by_type[Sheep]) > 0 else 0
            ),
            "WolfToSheepRatio": lambda m: (
                len(m.agents_by_type[Wolf]) / len(m.agents_by_type[Sheep]) if len(m.agents_by_type[Sheep]) > 0 else 0
            ),
            "MedianWolfEnergy": lambda m: (
                median([w.energy for w in m.agents_by_type[Wolf]])
            ),
            "MedianSheepEnergy": lambda m: (
                median([s.energy for s in m.agents_by_type[Sheep]])
            ),
            "SheepEnergyStdDev": lambda m: (
                statistics.stdev([s.energy for s in m.agents_by_type[Sheep]]) if len(m.agents_by_type[Sheep]) > 1 else 0
            ),
            "WolfEnergyStdDev": lambda m: (
                statistics.stdev([s.energy for s in m.agents_by_type[Wolf]]) if len(m.agents_by_type[Wolf]) > 1 else 0
            ),
        }

        self.datacollector = DataCollector(model_reporters=reporters)

        Sheep.create_agents(
            self,
            initial_sheep,
            energy=self.rng.random((initial_sheep,)) * 2 * sheep_gain_from_food,
            reproduction_probability=sheep_reproduce,
            energy_from_food=sheep_gain_from_food,
            cell=self.random.choices(self.grid.all_cells.cells, k=initial_sheep),
            grass=self.grass,
            smart_movement=self.smart_movement,
            movement_cost=self.sheep_movement_cost,
            reproduction_energy_share=self.sheep_reproduction_energy_share,
        )

        Wolf.create_agents(
            self,
            initial_wolves,
            energy=self.rng.random((initial_wolves,)) * 2 * wolf_gain_from_food,
            reproduction_probability=wolf_reproduce,
            energy_from_food=wolf_gain_from_food,
            cell=self.random.choices(self.grid.all_cells.cells, k=initial_wolves),
            grass=self.grass,
            smart_movement=self.smart_movement,
            movement_cost=self.wolf_movement_cost,
            reproduction_energy_share=self.wolf_reproduction_energy_share,
        )

        if self.grass:
            for cell in self.grid:
                is_grown = self.random.random() < 0.5
                countdown = 0 if is_grown else grass_regrowth_time
                GrassPatch(self, countdown, cell, grass_regrowth_time)
        else:
            for cell in self.grid:
                Ground(self, cell)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.agents_by_type[Sheep].do("step")
        self.agents_by_type[Wolf].do("step")
        self.datacollector.collect(self)
