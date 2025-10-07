import random

# --- SIMULATION PARAMETERS (Modify these to change the simulation) ---
NUM_RECYCLERS = 20
NUM_WASTEFULS = 20
MAX_STORED_ENERGY = 100
RECYCLING_WASTE_COST = 1
RESOURCE_REGENERATION_CHANCE = 50 # Value between 0-1000 (NetLogo's slider is 0-100, we use a finer grain)
SIMULATION_TICKS = 150 # How many steps the simulation will run

# --- GEOSPATIAL MAPPING (Defines the Tucson area for the overlay) ---
# NetLogo world dimensions (default is -16 to 16)
MIN_PXCOR, MAX_PXCOR = -16, 16
MIN_PYCOR, MAX_PYCOR = -16, 16
GRID_WIDTH = MAX_PXCOR - MIN_PXCOR + 1
GRID_HEIGHT = MAX_PYCOR - MIN_PYCOR + 1

# Bounding box for Tucson, AZ
TUCSON_BOUNDS = {
    "sw_lon": -111.00, # West
    "sw_lat": 32.19,  # South
    "ne_lon": -110.90, # East
    "ne_lat": 32.25   # North
}

# --- KML STYLES ---
KML_STYLES = """
    <Style id="recyclerStyle">
      <IconStyle>
        <color>ffFF0000</color> <scale>1.0</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/person.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="wastefulStyle">
      <IconStyle>
        <color>ff0000FF</color> <scale>1.0</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/person.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="newPatchStyle">
      <PolyStyle>
        <color>a000ff00</color> <outline>0</outline>
      </PolyStyle>
    </Style>
    <Style id="recycledPatchStyle">
      <PolyStyle>
        <color>a000ff96</color> <outline>0</outline>
      </PolyStyle>
    </Style>
    <Style id="wastePatchStyle">
      <PolyStyle>
        <color>a000ffff</color> <outline>0</outline>
      </PolyStyle>
    </Style>
"""

# --- HELPER FUNCTION FOR GEOGRAPHIC MAPPING ---
def map_coords(x, y):
    """Maps NetLogo pxcor/pycor to longitude/latitude."""
    lon_range = TUCSON_BOUNDS["ne_lon"] - TUCSON_BOUNDS["sw_lon"]
    lat_range = TUCSON_BOUNDS["ne_lat"] - TUCSON_BOUNDS["sw_lat"]
    
    lon = TUCSON_BOUNDS["sw_lon"] + (x - MIN_PXCOR) / (GRID_WIDTH - 1) * lon_range
    lat = TUCSON_BOUNDS["sw_lat"] + (y - MIN_PYCOR) / (GRID_HEIGHT - 1) * lat_range
    return lon, lat

# --- MODEL CLASSES ---
class Patch:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.resource_type = "new"

    def get_style_url(self):
        if self.resource_type == "new": return "#newPatchStyle"
        if self.resource_type == "recycled": return "#recycledPatchStyle"
        return "#wastePatchStyle"

class Turtle:
    def __init__(self, world):
        self.world = world
        self.x = random.randint(MIN_PXCOR, MAX_PXCOR)
        self.y = random.randint(MIN_PYCOR, MAX_PYCOR)
        self.energy = MAX_STORED_ENERGY / 2

    def move(self):
        # Simplified move: move to a random neighbor
        potential_x = self.x + random.randint(-1, 1)
        potential_y = self.y + random.randint(-1, 1)
        
        # World wrapping (torus)
        self.x = (potential_x - MIN_PXCOR) % GRID_WIDTH + MIN_PXCOR
        self.y = (potential_y - MIN_PYCOR) % GRID_HEIGHT + MIN_PYCOR
        
        self.energy -= 1

class Recycler(Turtle):
    style_url = "#recyclerStyle"

    def process_patch(self):
        patch = self.world.get_patch(self.x, self.y)
        if patch.resource_type == "new":
            if self.energy <= MAX_STORED_ENERGY - 2:
                self.energy += 2
        elif patch.resource_type == "recycled":
            if self.energy <= MAX_STORED_ENERGY - 1:
                self.energy += 1
        else: # waste
            self.energy -= RECYCLING_WASTE_COST
            patch.resource_type = "recycled"

class Wasteful(Turtle):
    style_url = "#wastefulStyle"
    
    def process_patch(self):
        patch = self.world.get_patch(self.x, self.y)
        if patch.resource_type == "new":
            if self.energy <= MAX_STORED_ENERGY - 4:
                self.energy += 4
                patch.resource_type = "waste"
        elif patch.resource_type == "recycled":
            if self.energy <= MAX_STORED_ENERGY - 2:
                self.energy += 2
                patch.resource_type = "waste"

class Simulation:
    def __init__(self):
        self.patches = {}
        self.turtles = []

    def get_patch(self, x, y):
        return self.patches.get((x, y))

    def setup(self):
        print("Setting up simulation...")
        # Create patches
        for y in range(MIN_PYCOR, MAX_PYCOR + 1):
            for x in range(MIN_PXCOR, MAX_PXCOR + 1):
                self.patches[(x, y)] = Patch(x, y)
        
        # Create agents
        self.turtles.extend([Recycler(self) for _ in range(NUM_RECYCLERS)])
        self.turtles.extend([Wasteful(self) for _ in range(NUM_WASTEFULS)])

    def go(self):
        # Process patches
        for t in self.turtles:
            t.process_patch()
            
        # Move and manage energy
        dead_turtles = []
        for t in self.turtles:
            t.move()
            if t.energy > MAX_STORED_ENERGY:
                t.energy = MAX_STORED_ENERGY
            if t.energy < 0:
                dead_turtles.append(t)
        
        # Remove dead turtles
        self.turtles = [t for t in self.turtles if t not in dead_turtles]

        # Update environment
        for patch in self.patches.values():
            if patch.resource_type == "recycled":
                if random.randint(0, 1000) < RESOURCE_REGENERATION_CHANCE:
                    patch.resource_type = "new"
            elif patch.resource_type == "waste":
                 if random.randint(0, 4) == 0 and random.randint(0, 1000) < RESOURCE_REGENERATION_CHANCE:
                    patch.resource_type = "new"
                    
    def run(self):
        print(f"Running simulation for {SIMULATION_TICKS} ticks...")
        for i in range(SIMULATION_TICKS):
            self.go()
            print(f"  Tick {i+1}/{SIMULATION_TICKS} complete. Agents remaining: {len(self.turtles)}")
        print("Simulation finished.")

# --- KML GENERATION ---
def generate_kml(sim, filename="recycling_simulation_tucson.kml"):
    print(f"Generating KML file: {filename}...")
    with open(filename, "w") as f:
        # KML Header
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')
        f.write(f'    <name>Recycling Agent Model - Tucson - {TUCSON_BOUNDS["ne_lat"]}, {TUCSON_BOUNDS["sw_lon"]}</name>\n')
        f.write(f'    <description>Simulation results from {SIMULATION_TICKS} ticks. Run on {current_date}.</description>\n')
        f.write(KML_STYLES)

        # Patches Folder
        f.write('    <Folder><name>Resource Grid</name>\n')
        patch_width = (TUCSON_BOUNDS["ne_lon"] - TUCSON_BOUNDS["sw_lon"]) / GRID_WIDTH
        patch_height = (TUCSON_BOUNDS["ne_lat"] - TUCSON_BOUNDS["sw_lat"]) / GRID_HEIGHT
        for (x, y), patch in sim.patches.items():
            sw_lon, sw_lat = map_coords(x - 0.5, y - 0.5)
            ne_lon, ne_lat = map_coords(x + 0.5, y + 0.5)
            
            coords = f"{sw_lon},{sw_lat},0 {ne_lon},{sw_lat},0 {ne_lon},{ne_lat},0 {sw_lon},{ne_lat},0 {sw_lon},{sw_lat},0"
            f.write(f'      <Placemark>\n')
            f.write(f'        <name>Patch ({x},{y})</name>\n')
            f.write(f'        <styleUrl>{patch.get_style_url()}</styleUrl>\n')
            f.write(f'        <Polygon><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates></LinearRing></outerBoundaryIs></Polygon>\n')
            f.write(f'      </Placemark>\n')
        f.write('    </Folder>\n')

        # Turtles Folder
        f.write('    <Folder><name>Agents</name>\n')
        for turtle in sim.turtles:
            lon, lat = map_coords(turtle.x, turtle.y)
            agent_type = "Recycler" if isinstance(turtle, Recycler) else "Wasteful"
            f.write(f'      <Placemark>\n')
            f.write(f'        <name>{agent_type}</name>\n')
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
    current_date = "October 7, 2025" # From context
    simulation = Simulation()
    simulation.setup()
    simulation.run()
    generate_kml(simulation)