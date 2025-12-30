import random
import math

# --- SIMULATION PARAMETERS (Tune these to match your NetLogo model) ---
INITIAL_COWS = 50
COOPERATIVE_PROBABILITY = 0.5  # 0.0 to 1.0
METABOLISM = 1
GRASS_ENERGY = 5
REPRODUCTION_THRESHOLD = 50
REPRODUCTION_COST = 25
MAX_GRASS_HEIGHT = 10
LOW_HIGH_THRESHOLD = 5
LOW_GROWTH_CHANCE = 30  # Percent
HIGH_GROWTH_CHANCE = 80 # Percent
STRIDE_LENGTH = 1.0
SIMULATION_TICKS = 200

# --- GEOSPATIAL MAPPING (Defines the Tucson area for the overlay) ---
MIN_PXCOR, MAX_PXCOR = -16, 16
MIN_PYCOR, MAX_PYCOR = -16, 16
GRID_WIDTH = MAX_PXCOR - MIN_PXCOR + 1
GRID_HEIGHT = MAX_PYCOR - MIN_PYCOR + 1

TUCSON_BOUNDS = {
    "sw_lon": -111.00, # West
    "sw_lat": 32.19,  # South
    "ne_lon": -110.90, # East
    "ne_lat": 32.25   # North
}

# --- HELPER FUNCTIONS ---
def map_coords_to_lon_lat(x, y):
    """Maps NetLogo pxcor/pycor to longitude/latitude."""
    lon_range = TUCSON_BOUNDS["ne_lon"] - TUCSON_BOUNDS["sw_lon"]
    lat_range = TUCSON_BOUNDS["ne_lat"] - TUCSON_BOUNDS["sw_lat"]
    
    lon = TUCSON_BOUNDS["sw_lon"] + (x - MIN_PXCOR) / (GRID_WIDTH - 1) * lon_range
    lat = TUCSON_BOUNDS["sw_lat"] + (y - MIN_PYCOR) / (GRID_HEIGHT - 1) * lat_range
    return lon, lat

def scale_color_green(value, max_value):
    """Generates a KML hex color code (aabggr) for shades of green."""
    intensity = int(100 + 155 * (value / max_value))
    intensity = max(100, min(255, intensity)) # Clamp value
    return f"a000{intensity:02x}00" # a0=62% transparent

# --- MODEL CLASSES ---
class Patch:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.grass = MAX_GRASS_HEIGHT

    def grow_grass(self):
        growth_chance = HIGH_GROWTH_CHANCE if self.grass >= LOW_HIGH_THRESHOLD else LOW_GROWTH_CHANCE
        if random.random() * 100 < growth_chance:
            self.grass += 1
        if self.grass > MAX_GRASS_HEIGHT:
            self.grass = MAX_GRASS_HEIGHT

class Turtle:
    def __init__(self, x, y, world):
        self.x, self.y = x, y
        self.world = world
        self.energy = METABOLISM * 4
        self.heading = random.uniform(0, 360)

    def move(self):
        self.heading += random.uniform(-180, 180) # Simplified rt random 360 and fd
        dx = STRIDE_LENGTH * math.cos(math.radians(self.heading))
        dy = STRIDE_LENGTH * math.sin(math.radians(self.heading))
        
        self.x += dx
        self.y += dy

        # World wrapping
        if self.x > MAX_PXCOR: self.x = MIN_PXCOR
        if self.x < MIN_PXCOR: self.x = MAX_PXCOR
        if self.y > MAX_PYCOR: self.y = MIN_PYCOR
        if self.y < MIN_PYCOR: self.y = MAX_PYCOR

        self.energy -= METABOLISM

    def get_current_patch(self):
        return self.world.get_patch(round(self.x), round(self.y))

    def reproduce(self):
        if self.energy > REPRODUCTION_THRESHOLD:
            self.energy -= REPRODUCTION_COST
            return self.__class__(self.x, self.y, self.world) # Hatch 1 of the same breed
        return None

class CooperativeCow(Turtle):
    style_url = "#cooperativeCowStyle"
    breed = "Cooperative"
    
    def eat(self):
        patch = self.get_current_patch()
        if patch and patch.grass > LOW_HIGH_THRESHOLD:
            patch.grass -= 1
            self.energy += GRASS_ENERGY

class GreedyCow(Turtle):
    style_url = "#greedyCowStyle"
    breed = "Greedy"

    def eat(self):
        patch = self.get_current_patch()
        if patch and patch.grass > 0:
            patch.grass -= 1
            self.energy += GRASS_ENERGY

class Simulation:
    def __init__(self):
        self.patches = {}
        self.turtles = []

    def get_patch(self, x, y):
        # Handle wrapping for patch lookup
        x_wrapped = (x - MIN_PXCOR) % GRID_WIDTH + MIN_PXCOR
        y_wrapped = (y - MIN_PYCOR) % GRID_HEIGHT + MIN_PYCOR
        return self.patches.get((x_wrapped, y_wrapped))

    def setup(self):
        # Create patches
        for y in range(MIN_PYCOR, MAX_PYCOR + 1):
            for x in range(MIN_PXCOR, MAX_PXCOR + 1):
                self.patches[(x, y)] = Patch(x, y)
        
        # Create cows
        for _ in range(INITIAL_COWS):
            x, y = random.uniform(MIN_PXCOR, MAX_PXCOR), random.uniform(MIN_PYCOR, MAX_PYCOR)
            if random.random() < COOPERATIVE_PROBABILITY:
                self.turtles.append(CooperativeCow(x, y, self))
            else:
                self.turtles.append(GreedyCow(x, y, self))

    def go(self):
        new_turtles = []
        dead_turtles = []
        
        for t in self.turtles:
            t.move()
            t.eat()
            if t.energy < 0:
                dead_turtles.append(t)
            else:
                offspring = t.reproduce()
                if offspring:
                    new_turtles.append(offspring)

        self.turtles.extend(new_turtles)
        self.turtles = [t for t in self.turtles if t not in dead_turtles]
        
        for patch in self.patches.values():
            patch.grow_grass()
            
    def run(self):
        print(f"Running Cow Cooperation simulation for {SIMULATION_TICKS} ticks...")
        for i in range(SIMULATION_TICKS):
            self.go()
            print(f"  Tick {i+1}/{SIMULATION_TICKS} | Population: {len(self.turtles)}")
        print("Simulation finished.")

def generate_kml(sim, filename="cooperation_simulation_tucson.kml"):
    print(f"Generating KML file: {filename}...")
    with open(filename, "w") as f:
        # KML Header
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')
        f.write(f'    <name>Cow Cooperation Model - Tucson</name>\n')
        f.write(f'    <description>Simulation results from {SIMULATION_TICKS} ticks. Run on {current_date}.</description>\n')

        # --- Styles ---
        f.write('    <Style id="cooperativeCowStyle"><IconStyle><color>ff3333cc</color><scale>1.1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/cow.png</href></Icon></IconStyle></Style>\n')
        f.write('    <Style id="greedyCowStyle"><IconStyle><color>ffeeaa00</color><scale>1.1</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/cow.png</href></Icon></IconStyle></Style>\n')
        for i in range(MAX_GRASS_HEIGHT + 1):
            color_hex = scale_color_green(i, MAX_GRASS_HEIGHT)
            f.write(f'    <Style id="grassStyle_{i}"><PolyStyle><color>{color_hex}</color><outline>0</outline></PolyStyle></Style>\n')
        
        # --- Pasture Grid ---
        f.write('    <Folder><name>Pasture Grass Levels</name>\n')
        for (x, y), patch in sim.patches.items():
            sw_lon, sw_lat = map_coords_to_lon_lat(x - 0.5, y - 0.5)
            ne_lon, ne_lat = map_coords_to_lon_lat(x + 0.5, y + 0.5)
            coords = f"{sw_lon},{sw_lat},0 {ne_lon},{sw_lat},0 {ne_lon},{ne_lat},0 {sw_lon},{ne_lat},0 {sw_lon},{sw_lat},0"
            style_id = f"#grassStyle_{patch.grass}"
            f.write(f'      <Placemark><name>Grass ({x},{y})</name><styleUrl>{style_id}</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>\n')
        f.write('    </Folder>\n')

        # --- Cows ---
        f.write('    <Folder><name>Cows</name>\n')
        for turtle in sim.turtles:
            lon, lat = map_coords_to_lon_lat(turtle.x, turtle.y)
            f.write(f'      <Placemark>\n')
            f.write(f'        <name>{turtle.breed} Cow</name>\n')
            f.write(f'        <description>Energy: {int(turtle.energy)}</description>\n')
            f.write(f'        <styleUrl>{turtle.style_url}</styleUrl>\n')
            f.write(f'        <Point><coordinates>{lon},{lat},0</coordinates></Point>\n')
            f.write(f'      </Placemark>\n')
        f.write('    </Folder>\n')

        # KML Footer
        f.write('  </Document>\n')
        f.write('</kml>\n')
    print("KML file generated successfully!")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    current_date = "October 8, 2025"
    simulation = Simulation()
    simulation.setup()
    simulation.run()
    generate_kml(simulation)