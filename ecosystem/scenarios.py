import json
import random
from typing import Dict, List

class Biome:
    def __init__(self, name: str, resources: Dict[str, int]):
        self.name = name
        self.resources = resources

class Scenario:
    def __init__(self, name: str, biomes: List[Biome]):
        self.name = name
        self.biomes = biomes

    def get_biome(self, name: str) -> Biome:
        for biome in self.biomes:
            if biome.name == name:
                return biome
        return None

class Ecosystem:
    def __init__(self):
        self.scenarios = []
        self.biomes = []

    def add_biome(self, biome: Biome):
        self.biomes.append(biome)

    def add_scenario(self, scenario: Scenario):
        self.scenarios.append(scenario)

    def get_scenario(self, name: str) -> Scenario:
        for scenario in self.scenarios:
            if scenario.name == name:
                return scenario
        return None

# Define biomes
desert_biome = Biome("Desert", {"water": 10, "food": 20})
forest_biome = Biome("Forest", {"water": 50, "food": 80})
ocean_biome = Biome("Ocean", {"water": 100, "food": 50})
tundra_biome = Biome("Tundra", {"water": 20, "food": 30})
volcanic_biome = Biome("Volcanic", {"water": 30, "food": 40})

# Create ecosystem
ecosystem = Ecosystem()
ecosystem.add_biome(desert_biome)
ecosystem.add_biome(forest_biome)
ecosystem.add_biome(ocean_biome)
ecosystem.add_biome(tundra_biome)
ecosystem.add_biome(volcanic_biome)

# Define scenarios
scenario1 = Scenario("Scenario 1", [desert_biome, forest_biome])
scenario2 = Scenario("Scenario 2", [ocean_biome, tundra_biome])
scenario3 = Scenario("Scenario 3", [volcanic_biome, desert_biome])

ecosystem.add_scenario(scenario1)
ecosystem.add_scenario(scenario2)
ecosystem.add_scenario(scenario3)

# Environmental events
def drought(biome: Biome):
    biome.resources["water"] -= 10

def abundance(biome: Biome):
    biome.resources["food"] += 20

def storm(biome: Biome):
    biome.resources["water"] += 30

# Configurable scenario files (YAML/JSON)
import yaml

def load_scenario_from_yaml(file_path: str) -> Scenario:
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        scenario = Scenario(data["name"], [])
        for biome_data in data["biomes"]:
            biome = Biome(biome_data["name"], biome_data["resources"])
            scenario.biomes.append(biome)
        return scenario

# Example usage
scenario = load_scenario_from_yaml("scenario.yaml")
print(scenario.name)
for biome in scenario.biomes:
    print(biome.name, biome.resources)