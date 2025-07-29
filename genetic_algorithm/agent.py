import random
from typing import Union

from pydantic import BaseModel, Field

MUTATION_RATE = 0.3
NUM_WEIGHTS = 9


class GomocupAgent(BaseModel):
    name: str
    elo: int
    cmd: str


class GeneticAgent(BaseModel):
    name: str
    cmd: str
    weights: list[float] = Field(
        default_factory=lambda: [random.uniform(0, 1) for _ in range(NUM_WEIGHTS)]
    )
    # fitness set externally
    fitness: float = -1

    def mutate(self):
        """Mutate the agent's weights."""
        for i in range(len(self.weights)):
            if random.random() < MUTATION_RATE:
                # Add small random noise to the weight
                self.weights[i] += random.uniform(-0.2, 0.2)
                # Ensure weights stay within reasonable bounds [0, 1]
                self.weights[i] = max(0.0, min(1.0, self.weights[i]))


Agent = Union[GomocupAgent, GeneticAgent]
