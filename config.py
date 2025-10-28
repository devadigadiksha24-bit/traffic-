 # config.py
# This file contains all the configuration constants for the simulation.

# --- SCREEN & VISUALIZATION ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SIM_FPS = 60  # Frames per second for the simulation

# --- COLORS (VIBRANT LIGHT THEME OVERHAUL) ---
COLOR_SKY = (245, 245, 245)      # Very light off-white/grey for a clean background
COLOR_DARK_TEXT = (30, 30, 30)   # Near-black for maximum readability
COLOR_WHITE = (255, 255, 255)    # Pure white for lines/highlights

# Traffic Lights (High Saturation)
COLOR_RED = (255, 30, 30)        # Deep Red
COLOR_GREEN = (30, 200, 30)      # Rich Green
COLOR_YELLOW = (255, 180, 0)     # Golden Amber/Yellow

# Road & Intersection
COLOR_ROAD = (130, 140, 150)     # Darker, more prominent asphalt grey
COLOR_LINES = (255, 255, 255)    # Pure White for lane lines
COLOR_MEDIAN = (255, 240, 0)     # Super Vibrant Yellow for median
COLOR_ROAD_BORDER = (100, 100, 100) # Darker border for the road edge
COLOR_TIRE = (0, 0, 0)           # Black for wheels

# UI & Engagement
COLOR_STATS_BACKGROUND = (255, 255, 255) # White panel background
COLOR_ACCENT_UI = (0, 110, 200)          # Deep Blue accent for UI elements

# Traffic Light Casing
COLOR_CASING = (100, 100, 100)   # Dark grey casing for contrast
LIGHT_RADIUS = 10 # Slightly larger lights
LIGHT_CASING_WIDTH = 30 # Slightly wider casing

# Emergency Vehicle Colors - High Contrast
COLOR_AMBULANCE = (255, 255, 255)
COLOR_POLICE = (20, 20, 150)     # Deeper Blue for Police
COLOR_AMBULANCE_SIREN = (255, 0, 0)
COLOR_POLICE_SIREN = (0, 255, 255) # Cyan flash

# Extended palette for random normal car colors (More vibrant)
VEHICLE_COLORS = [
    (0, 150, 255),    # Sky Blue
    (255, 100, 0),    # Bright Orange
    (200, 0, 255),    # Electric Purple
    (0, 200, 100),    # Emerald Green
    (255, 0, 100),    # Hot Pink
    (255, 230, 0),    # Sunshine Yellow
    (60, 60, 60),     # Dark Charcoal
    (0, 255, 255),    # Cyan
    (180, 50, 0)      # Burnt Sienna
]

# --- SIMULATION PARAMETERS ---
# Car
CAR_WIDTH = 22 # Slightly wider cars
CAR_HEIGHT = 45 # Slightly longer cars
CAR_SPEED = 2
CAR_SPAWN_RATE = 0.03
MIN_FOLLOW_DISTANCE = 35 # Minimum gap maintained between cars (pixels)

# Ambulance (Priority)
AMBULANCE_SPEED = 3.5 # Slightly faster
AMBULANCE_SPAWN_RATE = 0.005

# Police (Priority)
POLICE_SPEED = 3.5 # Slightly faster
POLICE_SPAWN_RATE = 0.005

# --- INTERSECTION & ROAD ---
INTERSECTION_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
ROAD_WIDTH = 80  # Total width of one road (two lanes)
LANE_WIDTH = ROAD_WIDTH // 2 # Two lanes per direction
STOP_LINE_OFFSET = 50  # Where cars stop relative to the intersection center

# --- FIXED CONTROLLER SETTINGS ---
FIXED_GREEN_TIME = 180
FIXED_YELLOW_TIME = 60

# --- Q-LEARNING (AI) CONTROLLER SETTINGS ---
AI_DECISION_INTERVAL = 120
AI_YELLOW_TIME = 60

# --- Q-TABLE & AI PARAMETERS ---
QUEUE_BIN_SIZE = 5
MAX_QUEUE_BIN = 10
NUM_PHASES = 2
NUM_ACTIONS = 2

# Hyperparameters
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 1.0
EPSILON_DECAY = 0.9995
MIN_EPSILON = 0.05

REWARD_WAITING = -0.1







