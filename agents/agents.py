from mesa.experimental.cell_space import CellAgent, FixedAgent


class Animal(CellAgent):
    def __init__(self,
                 model,
                 energy=10.0,
                 reproduction_probability=0.1,
                 energy_from_food=5,
                 cell=None,
                 grass=False,
                 smart_movement=False,
                 movement_cost=1,
                 reproduction_energy_share=0.5
                 ):
        super().__init__(model)
        self.energy = energy
        self.reproduction_probability = reproduction_probability
        self.energy_from_food = energy_from_food
        self.cell = cell
        self.grass = grass
        self.smart_movement = smart_movement
        self.movement_cost = movement_cost
        self.reproduction_energy_share = reproduction_energy_share

    def create_offspring(self):
        offspring_energy = self.energy * self.reproduction_energy_share
        self.energy *= (1 - self.reproduction_energy_share)
        self.__class__(
            self.model,
            energy=offspring_energy,
            reproduction_probability=self.reproduction_probability,
            energy_from_food=self.energy_from_food,
            reproduction_energy_share=self.reproduction_energy_share,
            cell=self.cell,
            grass=self.grass,
            smart_movement=self.smart_movement,
        )

    def feed(self):
        pass

    def step(self):
        self.move()
        self.energy -= self.movement_cost
        self.feed()

        if self.energy <= 0:
            self.remove()
        elif self.random.random() < self.reproduction_probability:
            self.create_offspring()

    def move(self):
        pass


class Sheep(Animal):
    def feed(self):
        if self.grass:
            grass_patch = next(obj for obj in self.cell.agents if isinstance(obj, GrassPatch))
            if grass_patch.is_grown:
                self.energy += self.energy_from_food
                grass_patch.is_grown = False

    def move(self):
        if self.smart_movement:
            cells_without_wolves = self.cell.neighborhood.select(
                lambda cell: not any(isinstance(obj, Wolf) for obj in cell.agents)
            )
            if len(cells_without_wolves) == 0:
                return

            cells_with_grass = cells_without_wolves.select(
                lambda cell: any(
                    isinstance(obj, GrassPatch) and obj.is_grown for obj in cell.agents
                )
            )

            target_cells = (
                cells_with_grass if len(cells_with_grass) > 0 else cells_without_wolves
            )
            self.cell = target_cells.select_random_cell()
        else:
            self.cell = self.cell.neighborhood.select_random_cell()


class Wolf(Animal):
    def feed(self):
        sheep = [obj for obj in self.cell.agents if isinstance(obj, Sheep)]
        if sheep:
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.energy_from_food
            sheep_to_eat.remove()

    def move(self):
        if self.smart_movement:
            cells_with_sheep = self.cell.neighborhood.select(
                lambda cell: any(isinstance(obj, Sheep) for obj in cell.agents)
            )
            target_cells = (
                cells_with_sheep if len(cells_with_sheep) > 0 else self.cell.neighborhood
            )
            self.cell = target_cells.select_random_cell()
        else:
            self.cell = self.cell.neighborhood.select_random_cell()


class GrassPatch(FixedAgent):
    @property
    def is_grown(self):
        return self._is_grown

    @is_grown.setter
    def is_grown(self, is_grown: bool):
        self._is_grown = is_grown

        if not is_grown:
            self.model.simulator.schedule_event_relative(
                setattr,
                self.grass_regrowth_time,
                function_args=[self, "is_grown", True]
            )

    def __init__(self, model, countdown, cell, grass_regrowth_time):
        super().__init__(model)
        self._is_grown = countdown == 0
        self.cell = cell
        self.grass_regrowth_time = grass_regrowth_time

        if not self.is_grown:
            self.model.simulator.schedule_event_relative(
                setattr, countdown, function_args=[self, "is_grown", True]
            )


class Ground(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell
