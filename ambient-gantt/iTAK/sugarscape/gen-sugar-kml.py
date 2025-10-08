import random
import math
import os

# --- SIMULATION PARAMETERS ---
INITIAL_POPULATION = 250
SIMULATION_TICKS = 100
# Agent Attributes
MIN_SUGAR_ENDOWMENT = 5
MAX_SUGAR_ENDOWMENT = 25
MIN_METABOLISM = 1
MAX_METABOLISM = 4
MIN_VISION = 1
MAX_VISION = 6
MIN_MAX_AGE = 60
MAX_MAX_AGE = 100

# --- GEOSPATIAL MAPPING ---
# NetLogo world dimensions from the standard Sugarscape model
GRID_SIZE = 51

# Bounding box stretching from South Tucson to Sabino Canyon
TUCSON_BOUNDS = {
    "sw_lon": -111.02, # West
    "sw_lat": 32.15,  # South (South Tucson)
    "ne_lon": -110.80, # East
    "ne_lat": 32.35   # North (Sabino Canyon)
}

# Coordinates for the two "sugar peaks"
SUGAR_PEAKS = [
    {"name": "Downtown Tucson", "lat": 32.2217, "lon": -110.9711},
    {"name": "U of Arizona", "lat": 32.2319, "lon": -110.9519}
]

# --- HELPER FUNCTIONS ---
def map_lon_lat_to_grid(lon, lat):
    """Maps longitude/latitude to the simulation grid coordinates."""
    lon_frac = (lon - TUCSON_BOUNDS["sw_lon"]) / (TUCSON_BOUNDS["ne_lon"] - TUCSON_BOUNDS["sw_lon"])
    lat_frac = (lat - TUCSON_BOUNDS["sw_lat"]) / (TUCSON_BOUNDS["ne_lat"] - TUCSON_BOUNDS["sw_lat"])
    x = int(lon_frac * (GRID_SIZE - 1))
    y = int(lat_frac * (GRID_SIZE - 1))
    return x, y

def map_grid_to_lon_lat(x, y):
    """Maps simulation grid coordinates to longitude/latitude."""
    lon_range = TUCSON_BOUNDS["ne_lon"] - TUCSON_BOUNDS["sw_lon"]
    lat_range = TUCSON_BOUNDS["ne_lat"] - TUCSON_BOUNDS["sw_lat"]
    lon = TUCSON_BOUNDS["sw_lon"] + x / (GRID_SIZE - 1) * lon_range
    lat = TUCSON_BOUNDS["sw_lat"] + y / (GRID_SIZE - 1) * lat_range
    return lon, lat

def generate_sugar_map_file():
    """Creates sugar-map.txt based on distance from Tucson landmarks."""
    print("Generating 'sugar-map.txt' for the Tucson area...")
    if os.path.exists("sugar-map.txt"):
        print("'sugar-map.txt' already exists. Skipping generation.")
        return

    peak_coords = [map_lon_lat_to_grid(p["lon"], p["lat"]) for p in SUGAR_PEAKS]
    max_dist = GRID_SIZE * 1.414 # Approx diagonal of the grid

    with open("sugar-map.txt", "w") as f:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                min_dist_to_peak = min(math.sqrt((x - px)**2 + (y - py)**2) for px, py in peak_coords)
                
                # Assign sugar level (0-4) based on proximity to a peak
                if min_dist_to_peak < GRID_SIZE * 0.1:
                    sugar_level = 4
                elif min_dist_to_peak < GRID_SIZE * 0.2:
                    sugar_level = 3
                elif min_dist_to_peak < GRID_SIZE * 0.35:
                    sugar_level = 2
                elif min_dist_to_peak < GRID_SIZE * 0.5:
                    sugar_level = 1
                else:
                    sugar_level = 0
                f.write(f"{sugar_level}\n")
    print("Generation complete.")

# --- MODEL CLASSES ---
class Patch:
    def __init__(self, x, y, max_sugar):
        self.x, self.y = x, y
        self.max_sugar = max_sugar
        self.sugar = max_sugar
        self.agent = None

    def growback(self):
        self.sugar = min(self.max_sugar, self.sugar + 1)

class Agent:
    def __init__(self, sim):
        self.sim = sim
        self.sugar = random.randint(MIN_SUGAR_ENDOWMENT, MAX_SUGAR_ENDOWMENT)
        self.metabolism = random.randint(MIN_METABOLISM, MAX_METABOLISM)
        self.vision = random.randint(MIN_VISION, MAX_VISION)
        self.age = 0
        self.max_age = random.randint(MIN_MAX_AGE, MAX_MAX_AGE)
        self.patch = None

    def place_on_empty_patch(self):
        empty_patches = [p for p in self.sim.patches.values() if not p.agent]
        if empty_patches:
            self.patch = random.choice(empty_patches)
            self.patch.agent = self

    def move(self):
        candidates = [self.patch] # Staying put is an option
        for i in range(1, self.vision + 1):
            for dx, dy in [(0, i), (0, -i), (i, 0), (-i, 0)]:
                x, y = self.patch.x + dx, self.patch.y + dy
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    target_patch = self.sim.get_patch(x, y)
                    if target_patch and not target_patch.agent:
                        candidates.append(target_patch)

        best_sugar = -1
        potential_winners = []
        for p in candidates:
            if p.sugar > best_sugar:
                best_sugar = p.sugar
                potential_winners = [p]
            elif p.sugar == best_sugar:
                potential_winners.append(p)
        
        if potential_winners:
            # Find the closest among the winners
            min_dist = float('inf')
            final_choice = self.patch
            for p in potential_winners:
                dist = math.sqrt((self.patch.x - p.x)**2 + (self.patch.y - p.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    final_choice = p
            
            # Move to the chosen patch
            self.patch.agent = None
            self.patch = final_choice
            self.patch.agent = self

    def eat(self):
        self.sugar = self.sugar - self.metabolism + self.patch.sugar
        self.patch.sugar = 0

class Simulation:
    def __init__(self):
        self.patches = {}
        self.agents = []

    def get_patch(self, x, y):
        return self.patches.get((x, y))

    def setup(self):
        print("Setting up simulation...")
        with open("sugar-map.txt", "r") as f:
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    max_sugar = int(f.readline().strip())
                    self.patches[(x, y)] = Patch(x, y, max_sugar)
        
        for _ in range(INITIAL_POPULATION):
            agent = Agent(self)
            agent.place_on_empty_patch()
            self.agents.append(agent)

    def go(self):
        for patch in self.patches.values():
            patch.growback()

        dead_agents = []
        for agent in self.agents:
            agent.move()
            agent.eat()
            agent.age += 1
            if agent.sugar <= 0 or agent.age > agent.max_age:
                dead_agents.append(agent)

        for dead_agent in dead_agents:
            dead_agent.patch.agent = None
            self.agents.remove(dead_agent)
            # Replacement ("hatch")
            new_agent = Agent(self)
            new_agent.place_on_empty_patch()
            if new_agent.patch: # Only add if there was space
                self.agents.append(new_agent)

    def run(self):
        print(f"Running Sugarscape simulation for {SIMULATION_TICKS} ticks...")
        for i in range(SIMULATION_TICKS):
            self.go()
            print(f"  Tick {i+1}/{SIMULATION_TICKS} | Population: {len(self.agents)}")
        print("Simulation finished.")

# --- KML GENERATION ---
def generate_kml(sim, filename="sugarscape_tucson.kml"):
    print(f"Generating KML file: {filename}...")
    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')
        f.write(f'    <name>Sugarscape Model - Tucson</name>\n')
        f.write(f'    <description>Results from a {SIMULATION_TICKS}-tick Sugarscape simulation.</description>\n')
        
        # Styles for Patches (shades of yellow)
        for i in range(5):
            # AABBGGRR format. Fading from bright yellow to pale yellow.
            color_hex = f"a0{i*15+150:02x}{i*15+200:02x}{i*15+240:02x}"[-8:] 
            f.write(f'    <Style id="sugarStyle_{i}"><PolyStyle><color>{color_hex}</color><outline>0</outline></PolyStyle></Style>\n')
        # Style for Agents
        f.write('    <Style id="agentStyle"><IconStyle><color>ff0000ff</color><scale>0.6</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon></IconStyle></Style>\n')

        # Patches Folder
        f.write('    <Folder><name>Sugarscape</name>\n')
        for (x, y), patch in sim.patches.items():
            lon1, lat1 = map_grid_to_lon_lat(x - 0.5, y - 0.5)
            lon2, lat2 = map_grid_to_lon_lat(x + 0.5, y + 0.5)
            coords = f"{lon1},{lat1},0 {lon2},{lat1},0 {lon2},{lat2},0 {lon1},{lat2},0 {lon1},{lat1},0"
            style_id = f"#sugarStyle_{patch.sugar}" if patch.sugar < 5 else f"#sugarStyle_4"
            f.write(f'      <Placemark><name>Patch ({x},{y})</name><styleUrl>{style_id}</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>\n')
        f.write('    </Folder>\n')

        # Agents Folder
        f.write('    <Folder><name>Agents</name>\n')
        for agent in sim.agents:
            if agent.patch:
                lon, lat = map_grid_to_lon_lat(agent.patch.x, agent.patch.y)
                f.write(f'      <Placemark>\n')
                f.write(f'        <name>Agent</name>\n')
                f.write(f'        <description>Sugar: {agent.sugar}, Vision: {agent.vision}, Metabolism: {agent.metabolism}, Age: {agent.age}</description>\n')
                f.write(f'        <styleUrl>#agentStyle</styleUrl>\n')
                f.write(f'        <Point><coordinates>{lon},{lat},0</coordinates></Point>\n')
                f.write(f'      </Placemark>\n')
        f.write('    </Folder>\n')
        
        f.write('  </Document>\n')
        f.write('</kml>\n')
    print("KML file generated successfully!")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    current_date = "October 8, 2025"
    # Step 1: Create the custom map file if it doesn't exist
    generate_sugar_map_file()
    
    # Step 2: Run the simulation
    simulation = Simulation()
    simulation.setup()
    simulation.run()
    
    # Step 3: Generate the KML output
    generate_kml(simulation)