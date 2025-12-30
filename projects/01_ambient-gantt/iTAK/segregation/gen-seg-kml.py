import random
import sys

# --- SIMULATION PARAMETERS (Tune these to change the simulation) ---
GRID_SIZE = 50
DENSITY = 95
PERCENT_SIMILAR_WANTED = 40
MAX_TICKS = 100

# --- GEOSPATIAL MAPPING (Defines the Tucson area for the overlay) ---
TUCSON_BOUNDS = {
    "sw_lon": -111.00, # West
    "sw_lat": 32.19,  # South
    "ne_lon": -110.90, # East
    "ne_lat": 32.25   # North
}

# --- HELPER FUNCTION FOR GEOGRAPHIC MAPPING ---
def map_coords_to_lon_lat(x, y):
    """Maps simulation grid coordinates to longitude/latitude."""
    lon_range = TUCSON_BOUNDS["ne_lon"] - TUCSON_BOUNDS["sw_lon"]
    lat_range = TUCSON_BOUNDS["ne_lat"] - TUCSON_BOUNDS["sw_lat"]
    
    lon = TUCSON_BOUNDS["sw_lon"] + x / (GRID_SIZE - 1) * lon_range
    lat = TUCSON_BOUNDS["sw_lat"] + y / (GRID_SIZE - 1) * lat_range
    return lon, lat

# --- MODEL CLASSES (No changes) ---
class Agent:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.happy = False

    def update_happiness(self, sim):
        similar_nearby = 0
        other_nearby = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x = (self.x + dx + GRID_SIZE) % GRID_SIZE
                check_y = (self.y + dy + GRID_SIZE) % GRID_SIZE
                neighbor = sim.get_agent_at(check_x, check_y)
                if neighbor:
                    if neighbor.color == self.color:
                        similar_nearby += 1
                    else:
                        other_nearby += 1
        
        total_nearby = similar_nearby + other_nearby
        if total_nearby == 0:
            self.happy = True
            return
        percent_similar = (similar_nearby / total_nearby) * 100
        self.happy = percent_similar >= PERCENT_SIMILAR_WANTED

    def find_new_spot(self, sim):
        sim.occupied_patches[(self.x, self.y)] = None
        while True:
            new_x = random.randint(0, GRID_SIZE - 1)
            new_y = random.randint(0, GRID_SIZE - 1)
            if sim.get_agent_at(new_x, new_y) is None:
                self.x, self.y = new_x, new_y
                sim.occupied_patches[(self.x, self.y)] = self
                return

class Simulation:
    def __init__(self):
        self.agents = []
        self.occupied_patches = {}

    def get_agent_at(self, x, y):
        wrapped_x = (x + GRID_SIZE) % GRID_SIZE
        wrapped_y = (y + GRID_SIZE) % GRID_SIZE
        return self.occupied_patches.get((wrapped_x, wrapped_y))

    def setup(self):
        print("Setting up simulation...")
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                self.occupied_patches[(x, y)] = None
        all_empty_patches = list(self.occupied_patches.keys())
        num_agents = int(len(all_empty_patches) * (DENSITY / 100))
        agent_patches = random.sample(all_empty_patches, num_agents)
        for i, (x, y) in enumerate(agent_patches):
            # We will call the groups "Star Group" and "Dot Group" for clarity
            color = "Star Group" if i % 2 == 0 else "Dot Group"
            agent = Agent(x, y, color)
            self.agents.append(agent)
            self.occupied_patches[(x, y)] = agent
        for agent in self.agents:
            agent.update_happiness(self)

    def go(self):
        unhappy_agents = [agent for agent in self.agents if not agent.happy]
        if not unhappy_agents:
            return False
        random.shuffle(unhappy_agents)
        for agent in unhappy_agents:
            agent.find_new_spot(self)
        for agent in self.agents:
            agent.update_happiness(self)
        return True

    def run(self):
        print(f"Running Segregation simulation for a max of {MAX_TICKS} ticks...")
        for i in range(MAX_TICKS):
            num_unhappy = len([a for a in self.agents if not a.happy])
            percent_unhappy = (num_unhappy / len(self.agents)) * 100 if self.agents else 0
            print(f"  Tick {i+1}/{MAX_TICKS} | Unhappy Agents: {num_unhappy} ({percent_unhappy:.1f}%)")
            if not self.go():
                print("System stabilized. All agents are happy.")
                break
        print("Simulation finished.")

# --- KML GENERATION (Updated with Star and Dot styles) ---
def generate_kml(sim, filename="segregation_simulation_tucson.kml"):
    print(f"Generating KML file: {filename}...")
    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')
        f.write(f'    <name>Segregation Model - Green Star vs Red Dot</name>\n')
        f.write(f'    <description>Simulation results from {current_date}. Agent happiness requires {PERCENT_SIMILAR_WANTED}% similar neighbors.</description>\n')
        
        # --- NEW, UNAMBIGUOUS STYLES ---
        f.write('    <Style id="greenStarStyle"><IconStyle><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-stars.png</href></Icon></IconStyle></Style>\n')
        f.write('    <Style id="redDotStyle"><IconStyle><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-dot.png</href></Icon></IconStyle></Style>\n')
        
        # --- Styles for Patches (Unchanged) ---
        f.write('    <Style id="occupiedPatchStyle"><PolyStyle><color>40cccccc</color><outline>0</outline></PolyStyle></Style>\n')
        f.write('    <Style id="emptyPatchStyle"><PolyStyle><color>00ffffff</color><outline>0</outline></PolyStyle></Style>\n')

        # --- Patches Folder (Unchanged) ---
        f.write('    <Folder><name>Patches (Occupied/Empty)</name>\n')
        f.write('      <visibility>0</visibility>\n') # Hide patches by default for a cleaner look
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                lon1, lat1 = map_coords_to_lon_lat(x, y)
                lon2, lat2 = map_coords_to_lon_lat(x + 1, y + 1)
                coords = f"{lon1},{lat1},0 {lon2},{lat1},0 {lon2},{lat2},0 {lon1},{lat2},0 {lon1},{lat1},0"
                style_id = "#occupiedPatchStyle" if sim.get_agent_at(x, y) else "#emptyPatchStyle"
                f.write(f'      <Placemark><name>Patch ({x},{y})</name><styleUrl>{style_id}</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>\n')
        f.write('    </Folder>\n')

        # --- Agents Folder (Updated Logic) ---
        f.write('    <Folder><name>Agents</name>\n')
        for agent in sim.agents:
            lon, lat = map_coords_to_lon_lat(agent.x, agent.y)
            style_id = "#greenStarStyle" if agent.color == "Star Group" else "#redDotStyle"
            happiness_status = "Happy" if agent.happy else "Unhappy"
            
            f.write(f'      <Placemark>\n')
            f.write(f'        <name>{agent.color}</name>\n')
            f.write(f'        <description>Status: {happiness_status}</description>\n')
            f.write(f'        <styleUrl>{style_id}</styleUrl>\n')
            f.write(f'        <Point><coordinates>{lon},{lat},0</coordinates></Point>\n')
            f.write(f'      </Placemark>\n')
        f.write('    </Folder>\n')
        
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