import random

from pydantic import BaseModel, Field

MUTATION_RATE = 0.1
NUM_WEIGHTS = 10


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
    fitness: int = -1

    def mutate(self):
        # Placeholder for mutation logic
        pass
