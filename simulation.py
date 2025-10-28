 # simulation.py
import pygame
import random
import config
from collections import deque
import math

class TrafficLight:
    """Represents a single traffic light (Red, Yellow, Green)."""
    def __init__(self):
        self.state = 'red'  # 'red', 'yellow', 'green'
        self.colors = {
            'red': config.COLOR_RED,
            'yellow': config.COLOR_YELLOW,
            'green': config.COLOR_GREEN
        }
        self.timer = 0 

    def draw(self, surface, x, y):
        radius = config.LIGHT_RADIUS
        casing_width = config.LIGHT_CASING_WIDTH
        
        # 1. Draw Casing (Vertical rectangle to hold the lights) - Rounded Corners
        casing_height = radius * 6 + 25 
        casing_rect = pygame.Rect(x - casing_width // 2, y - radius * 3 - 10, casing_width, casing_height)
        # Use a slight shadow for depth
        pygame.draw.rect(surface, (150, 150, 150), casing_rect.move(2, 2), border_radius=5)
        pygame.draw.rect(surface, config.COLOR_CASING, casing_rect, border_radius=5)
        
        # Color for unlit lights (darker version of the casing)
        UNLIT_COLOR = (100, 100, 100) 
        
        # 2. Draw Lights (Top: Red, Middle: Yellow, Bottom: Green)
        
        # Red Light
        red_y = y - radius * 2
        # If lit, use the vibrant color, otherwise use the unlit color with a border
        color = self.colors['red'] if self.state == 'red' else UNLIT_COLOR
        pygame.draw.circle(surface, color, (x, red_y), radius)
        if self.state != 'red': pygame.draw.circle(surface, config.COLOR_DARK_TEXT, (x, red_y), radius, 1) # Outline

        # Yellow Light
        yellow_y = y 
        color = self.colors['yellow'] if self.state == 'yellow' else UNLIT_COLOR
        pygame.draw.circle(surface, color, (x, yellow_y), radius)
        if self.state != 'yellow': pygame.draw.circle(surface, config.COLOR_DARK_TEXT, (x, yellow_y), radius, 1) # Outline

        # Green Light
        green_y = y + radius * 2
        color = self.colors['green'] if self.state == 'green' else UNLIT_COLOR
        pygame.draw.circle(surface, color, (x, green_y), radius)
        if self.state != 'green': pygame.draw.circle(surface, config.COLOR_DARK_TEXT, (x, green_y), radius, 1) # Outline
        
        # 3. Draw Timer (Dark text on light casing)
        if self.timer > 0:
            time_sec = math.ceil(self.timer / config.SIM_FPS)
            font = pygame.font.SysFont('Arial', 14, bold=True)
            text_surface = font.render(f"{int(time_sec)}", True, config.COLOR_DARK_TEXT)
            
            # Position the text below the casing
            text_x = x - text_surface.get_width() // 2
            text_y = y + radius * 3 + 10 
            surface.blit(text_surface, (text_x, text_y))


class Vehicle:
    """Represents a single vehicle (car, police, or ambulance) in the simulation."""
    def __init__(self, path, vehicle_type='Car'):
        self.path = path  # 'NS' or 'EW'
        self.type = vehicle_type
        self.is_emergency = self.type in ['Ambulance', 'Police']

        # Determine dimensions, speed, and color based on type
        if self.type == 'Ambulance':
            self.width, self.height = config.CAR_WIDTH, config.CAR_HEIGHT
            self.speed = config.AMBULANCE_SPEED
            self.color = config.COLOR_AMBULANCE
            self.siren_color = config.COLOR_AMBULANCE_SIREN
        elif self.type == 'Police':
            self.width, self.height = config.CAR_WIDTH, config.CAR_HEIGHT
            self.speed = config.POLICE_SPEED
            self.color = config.COLOR_POLICE
            self.siren_color = config.COLOR_POLICE_SIREN
        else: # Car (or any other non-emergency vehicle)
            self.width, self.height = config.CAR_WIDTH, config.CAR_HEIGHT
            self.speed = config.CAR_SPEED
            self.color = random.choice(config.VEHICLE_COLORS)

        # Handle rotation for path
        if path == 'EW':
            self.width, self.height = self.height, self.width 

        # Set initial position and stop line
        if path == 'NS':
            self.x = config.INTERSECTION_POS[0] - config.LANE_WIDTH / 2 - self.width / 2
            self.y = 0 - self.height
            self.stop_pos = config.INTERSECTION_POS[1] - config.STOP_LINE_OFFSET
        else:  # 'EW'
            self.x = 0 - self.width
            self.y = config.INTERSECTION_POS[1] - config.LANE_WIDTH / 2 - self.height / 2
            self.stop_pos = config.INTERSECTION_POS[0] - config.STOP_LINE_OFFSET

        self.wait_time = 0
        self.is_waiting = False
        self.is_moving = False

    def update(self, is_light_green, cars_in_front):
        """Moves the vehicle or makes it wait."""
        
        self.is_waiting = False
        self.is_moving = True
        
        is_at_stop_line = False
        car_in_front_stopping = False

        # 1. Check for red light stop position
        if self.path == 'NS':
            if self.y < self.stop_pos and (self.y + self.height + self.speed) >= self.stop_pos:
                is_at_stop_line = True
        else: # 'EW'
            if self.x < self.stop_pos and (self.x + self.width + self.speed) >= self.stop_pos:
                is_at_stop_line = True

        # 2. Check for car in front stop
        if cars_in_front:
            car_front = cars_in_front[0]
            required_gap = config.MIN_FOLLOW_DISTANCE
            
            if self.path == 'NS':
                distance = car_front.y - (self.y + self.height)
            else: # EW
                distance = car_front.x - (self.x + self.width)
            
            if distance < required_gap + self.speed: 
                car_in_front_stopping = True
        
        
        # 3. Determine if we should stop
        should_stop = False
        
        # Emergency vehicles run the red light IF they are the first car in queue.
        if self.is_emergency and is_at_stop_line and not is_light_green and not cars_in_front:
            pass 
        elif is_at_stop_line and not is_light_green:
            should_stop = True 
        elif car_in_front_stopping:
            should_stop = True 

        # 4. Apply movement
        if should_stop:
            self.is_moving = False
            self.is_waiting = True
            
            # Ensure car stops exactly at the stop line, or behind the car in front
            if is_at_stop_line and not is_light_green:
                 if self.path == 'NS':
                    self.y = self.stop_pos - self.height
                 else:
                    self.x = self.stop_pos - self.width
            elif car_in_front_stopping:
                # Stop directly behind the car in front
                if self.path == 'NS':
                    self.y = car_front.y - self.height - config.MIN_FOLLOW_DISTANCE
                else:
                    self.x = car_front.x - self.width - config.MIN_FOLLOW_DISTANCE
        else:
            self.is_waiting = False
            self.is_moving = True
            if self.path == 'NS':
                self.y += self.speed
            else:
                self.x += self.speed

        # 5. Update wait time
        if self.is_waiting:
            self.wait_time += 1
        else:
            self.wait_time = 0


    def draw(self, surface, frame_count):
        
        if self.path == 'NS':
            body_w, body_h = self.width, self.height
        else:
            body_w, body_h = self.width, self.height

        body_rect = pygame.Rect(self.x, self.y, body_w, body_h)
        
        # 1. Vehicle Body with Shadow Effect (more appealing/3D)
        shadow_offset = 2
        pygame.draw.rect(surface, (100, 100, 100), body_rect.move(shadow_offset, shadow_offset), border_radius=5)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=5)
        
        # 2. Cabin/Roof (using a lighter shade of the body color for contrast)
        color_r, color_g, color_b = self.color
        cabin_color = (min(255, color_r + 30), min(255, color_g + 30), min(255, color_b + 30))
        if self.is_emergency: cabin_color = (200, 200, 200) # Fixed light grey for emergency

        if self.path == 'NS':
            roof_rect = (self.x + 2, self.y + 10, body_w - 4, 15)
        else:
            roof_rect = (self.x + 10, self.y + 2, 15, body_h - 4) # FIXED: Ensuring parenthesis is closed on this logical line
        pygame.draw.rect(surface, cabin_color, roof_rect, border_radius=2)
        
        # 3. Wheels (small, black rectangles)
        if self.path == 'NS':
            wheels = [(self.x + 3, self.y + 5, 4, 8), (self.x + body_w - 7, self.y + 5, 4, 8), 
                      (self.x + 3, self.y + body_h - 13, 4, 8), (self.x + body_w - 7, self.y + body_h - 13, 4, 8)]
        else:
            wheels = [(self.x + 5, self.y + 3, 8, 4), (self.x + 5, self.y + body_h - 7, 8, 4), 
                      (self.x + body_w - 13, self.y + 3, 8, 4), (self.x + body_w - 13, self.y + body_h - 7, 8, 4)]
        for wheel in wheels:
             pygame.draw.rect(surface, config.COLOR_TIRE, wheel, border_radius=1)


        # 4. Emergency Vehicle Details & Flashing Sirens
        if self.is_emergency:
            
            # Siren Flashing Effect (pop of color)
            siren_left_color = config.COLOR_AMBULANCE_SIREN if self.type == 'Ambulance' else (255, 0, 0)
            siren_right_color = config.COLOR_AMBULANCE_SIREN if self.type == 'Ambulance' else config.COLOR_POLICE_SIREN
            
            # Simple alternating flash (15 frames left, 15 frames right)
            is_left_flash = frame_count % 30 < 15
            
            flash_color = siren_left_color if is_left_flash else siren_right_color
            
            if self.path == 'NS':
                # Light bar on top
                light_rect = (self.x + body_w // 2 - 5, self.y, 10, 3)
                pygame.draw.rect(surface, flash_color, light_rect, border_radius=1)
                pygame.draw.rect(surface, config.COLOR_DARK_TEXT, light_rect, 1, border_radius=1) # Casing
            else:
                # Light bar on front (right side of the vehicle body)
                light_rect = (self.x + body_w - 3, self.y + body_h // 2 - 5, 3, 10)
                pygame.draw.rect(surface, flash_color, light_rect, border_radius=1)
                pygame.draw.rect(surface, config.COLOR_DARK_TEXT, light_rect, 1, border_radius=1) # Casing


        # 5. UI/UX: Movement Indicator (Vibrant Arrow)
        if self.is_moving and not self.is_emergency:
            arrow_color = config.COLOR_ACCENT_UI # Use the new vibrant UI accent color
            arrow_size = 5
            
            if self.path == 'NS':
                # Arrow points down (traveling North to South is Y+)
                points = [(self.x + body_w // 2, self.y + body_h), 
                          (self.x + body_w // 2 - arrow_size, self.y + body_h - arrow_size * 2), 
                          (self.x + body_w // 2 + arrow_size, self.y + body_h - arrow_size * 2)]
            else:
                # Arrow points right (traveling West to East is X+)
                points = [(self.x + body_w, self.y + body_h // 2), 
                          (self.x + body_w - arrow_size * 2, self.y + body_h // 2 - arrow_size), 
                          (self.x + body_w - arrow_size * 2, self.y + body_h // 2 + arrow_size)]
            pygame.draw.polygon(surface, arrow_color, points)

        # 6. UI/UX: Waiting Highlight (Pop of color for waiting)
        if self.is_waiting:
            # Draw a thick yellow outline to signify it's stationary and waiting
            pygame.draw.rect(surface, config.COLOR_YELLOW, body_rect, 3, border_radius=5)


class Intersection:
    """Manages the traffic lights and vehicle queues."""
    def __init__(self):
        self.ns_light = TrafficLight()
        self.ew_light = TrafficLight()
        self.ns_queue = deque()
        self.ew_queue = deque()
        self.set_phase('NS_GREEN')  # Start with NS green
        self.current_phase = 'NS_GREEN'
        
        self.center_x = config.INTERSECTION_POS[0]
        self.center_y = config.INTERSECTION_POS[1]

    def set_phase(self, phase):
        """Sets the state of the traffic lights based on the phase."""
        self.current_phase = phase
        if phase == 'NS_GREEN':
            self.ns_light.state = 'green'
            self.ew_light.state = 'red'
        elif phase == 'NS_YELLOW':
            self.ns_light.state = 'yellow'
            self.ew_light.state = 'red'
        elif phase == 'EW_GREEN':
            self.ns_light.state = 'red'
            self.ew_light.state = 'green'
        elif phase == 'EW_YELLOW':
            self.ns_light.state = 'red' 
            self.ew_light.state = 'yellow'

    def _draw_road(self, surface):
        """Draws the intersection and road markings with high visibility."""
        road_half = config.ROAD_WIDTH
        ns_road_x = self.center_x - road_half
        ns_road_y = 0
        ew_road_x = 0
        ew_road_y = self.center_y - road_half
        
        ns_road = (ns_road_x, ns_road_y, config.ROAD_WIDTH * 2, config.SCREEN_HEIGHT)
        ew_road = (ew_road_x, ew_road_y, config.SCREEN_WIDTH, config.ROAD_WIDTH * 2)
        
        # Draw roads (overlapping rects creates the intersection block)
        pygame.draw.rect(surface, config.COLOR_ROAD, ns_road)
        pygame.draw.rect(surface, config.COLOR_ROAD, ew_road)
        
        # Draw NS Median Line (Dashed Vibrant Yellow) - Thicker Line
        start_y = 0
        while start_y < config.SCREEN_HEIGHT:
            pygame.draw.line(surface, config.COLOR_MEDIAN, 
                             (self.center_x, start_y), 
                             (self.center_x, start_y + 20), 3) # Increased thickness
            start_y += 40
            
        # Draw EW Median Line (Dashed Vibrant Yellow) - Thicker Line
        start_x = 0
        while start_x < config.SCREEN_WIDTH:
            pygame.draw.line(surface, config.COLOR_MEDIAN, 
                             (start_x, self.center_y), 
                             (start_x + 20, self.center_y), 3) # Increased thickness
            start_x += 40
            
        # Draw Lane Lines (Dashed White) - NS - Thicker Line
        ns_lane1_x = self.center_x - config.LANE_WIDTH
        start_y = 0
        while start_y < config.SCREEN_HEIGHT:
            pygame.draw.line(surface, config.COLOR_LINES, 
                             (ns_lane1_x, start_y), 
                             (ns_lane1_x, start_y + 15), 2) # Increased thickness
            start_y += 30
        
        # Draw Lane Lines (Dashed White) - EW - Thicker Line
        ew_lane1_y = self.center_y - config.LANE_WIDTH
        start_x = 0
        while start_x < config.SCREEN_WIDTH:
            pygame.draw.line(surface, config.COLOR_LINES, 
                             (start_x, ew_lane1_y), 
                             (start_x + 15, ew_lane1_y), 2) # Increased thickness
            start_x += 30

        # Draw Stop Lines (Thick White/Highly Visible)
        stop_ns_y = self.center_y - config.STOP_LINE_OFFSET
        stop_ew_x = self.center_x - config.STOP_LINE_OFFSET
        
        # NS Stop Line (for NS vehicles)
        pygame.draw.line(surface, config.COLOR_WHITE, 
                         (self.center_x - config.LANE_WIDTH, stop_ns_y), 
                         (self.center_x, stop_ns_y), 8) # Thicker line
        
        # EW Stop Line (for EW vehicles)
        pygame.draw.line(surface, config.COLOR_WHITE, 
                         (stop_ew_x, self.center_y - config.LANE_WIDTH), 
                         (stop_ew_x, self.center_y), 8) # Thicker line

    def draw(self, surface, controller_timer=0):
        self._draw_road(surface)

        # Traffic light positions (outside the road/near the stop line)
        stop_ns_y = self.center_y - config.STOP_LINE_OFFSET
        
        # NS light: on the left side of the NS lane, near the stop line
        light_ns_x = self.center_x - config.LANE_WIDTH - config.ROAD_WIDTH // 2 - 15 
        light_ns_y = stop_ns_y - 25 
        
        # EW light: above the EW lane, near the stop line (for visual completeness)
        stop_ew_x = self.center_x - config.STOP_LINE_OFFSET
        light_ew_x = stop_ew_x - 25
        light_ew_y = self.center_y - config.LANE_WIDTH - config.ROAD_WIDTH // 2 - 15 
        
        # Draw both lights
        self.ns_light.timer = controller_timer
        self.ns_light.draw(surface, light_ns_x, light_ns_y)
        
        # NOTE: Drawing EW light is only for visual feedback, not functional in the 2-phase controller logic
        # For a cleaner look, the EW light will be drawn below the NS light.
        self.ew_light.timer = controller_timer 
        self.ew_light.draw(surface, light_ew_x, light_ew_y)


class Simulation:
    """The main class that runs the entire simulation."""
    def __init__(self, controller, mode):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(f"UrbanFlow - {mode} Mode")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 30, bold=True)
        
        self.controller = controller
        self.intersection = Intersection()
        self.vehicles = []
        self.running = True
        self.total_wait_time = 0
        self.cars_passed = 0
        self.frame_count = 0
        self.emergency_vehicles_present = []


    def _spawn_vehicle(self):
        """Randomly spawns new vehicles, including a chance for an ambulance/police."""
        path = random.choice(['NS', 'EW'])
        
        # 1. Spawn Emergency Vehicles (Ambulance/Police)
        if len(self.emergency_vehicles_present) == 0:
            if random.random() < config.AMBULANCE_SPAWN_RATE:
                self.vehicles.append(Vehicle(path, vehicle_type='Ambulance'))
            elif random.random() < config.POLICE_SPAWN_RATE:
                self.vehicles.append(Vehicle(path, vehicle_type='Police'))
        
        # 2. Spawn Regular Cars
        if random.random() < config.CAR_SPAWN_RATE:
            self.vehicles.append(Vehicle(path, vehicle_type='Car'))


    def _update_vehicles(self):
        """Updates all vehicles, manages queues, and calculates rewards."""
        self.intersection.ns_queue.clear()
        self.intersection.ew_queue.clear()
        self.emergency_vehicles_present = [] 
        
        current_total_wait = 0
        cars_to_remove = []

        # Sort cars: NS by y (ascending), EW by x (ascending)
        ns_cars = sorted([v for v in self.vehicles if v.path == 'NS'], key=lambda v: v.y)
        ew_cars = sorted([v for v in self.vehicles if v.path == 'EW'], key=lambda v: v.x)
        
        all_cars = ns_cars + ew_cars
        
        for car in all_cars:
            if car.is_emergency:
                self.emergency_vehicles_present.append(car.type)

            cars_in_front = []
            if car.path == 'NS':
                is_green = self.intersection.ns_light.state == 'green'
                idx = ns_cars.index(car)
                cars_in_front = ns_cars[idx + 1:] 
            else: # EW
                is_green = self.intersection.ew_light.state == 'green'
                idx = ew_cars.index(car)
                cars_in_front = ew_cars[idx + 1:]

            car.update(is_green, cars_in_front)
            
            if car.is_waiting:
                current_total_wait += car.wait_time
                if car.path == 'NS':
                    self.intersection.ns_queue.append(car)
                else:
                    self.intersection.ew_queue.append(car)
            
            # Remove cars that are off-screen
            if (car.path == 'NS' and car.y > config.SCREEN_HEIGHT) or \
               (car.path == 'EW' and car.x > config.SCREEN_WIDTH):
                cars_to_remove.append(car)
                
                self.total_wait_time += car.wait_time 
                self.cars_passed += 1 

        for car in cars_to_remove:
            self.vehicles.remove(car)
            
        return -current_total_wait


    def _draw_stats_panel(self):
        """Draws a dedicated, modern panel for simulation statistics."""
        # Panel dimensions (Top Right)
        panel_x = config.SCREEN_WIDTH - 280
        panel_y = 20
        panel_width = 260
        panel_height = 280
        
        # 1. Draw Background (White with subtle shadow)
        shadow_offset = 5
        pygame.draw.rect(self.screen, (200, 200, 200), 
                         (panel_x + shadow_offset, panel_y + shadow_offset, panel_width, panel_height), 
                         border_radius=10)
        pygame.draw.rect(self.screen, config.COLOR_STATS_BACKGROUND, 
                         (panel_x, panel_y, panel_width, panel_height), 
                         border_radius=10)
        # Border in the accent color
        pygame.draw.rect(self.screen, config.COLOR_ACCENT_UI, 
                         (panel_x, panel_y, panel_width, panel_height), 3, 
                         border_radius=10)
        
        # 2. Title (Bold and Accent Colored)
        title_surface = self.title_font.render("TRAFFIC SIMULATOR", True, config.COLOR_ACCENT_UI)
        self.screen.blit(title_surface, (panel_x + 10, panel_y + 10))
        
        # Separator
        pygame.draw.line(self.screen, config.COLOR_ACCENT_UI, 
                         (panel_x + 5, panel_y + 45), 
                         (panel_x + panel_width - 5, panel_y + 45), 2)

        # 3. Stats Data
        avg_wait = (self.total_wait_time / self.cars_passed / config.SIM_FPS) if self.cars_passed > 0 else 0
        
        stats_data = [
            ("Current Phase:", self.intersection.current_phase, config.COLOR_ACCENT_UI),
            ("NS Queue Length:", len(self.intersection.ns_queue), config.COLOR_RED if len(self.intersection.ns_queue) > 5 else config.COLOR_DARK_TEXT),
            ("EW Queue Length:", len(self.intersection.ew_queue), config.COLOR_RED if len(self.intersection.ew_queue) > 5 else config.COLOR_DARK_TEXT),
            ("Cars Passed:", self.cars_passed, config.COLOR_DARK_TEXT),
            ("Avg Wait Time:", f"{avg_wait:.2f} s", config.COLOR_GREEN),
        ]
        
        if hasattr(self.controller, 'agent'): # If AI mode
             stats_data.append(("AI Epsilon:", f"{self.controller.agent.epsilon:.4f}", config.COLOR_YELLOW))

        # Draw stats lines
        y_offset_start = panel_y + 55
        for i, (label, value, color) in enumerate(stats_data):
            label_font = pygame.font.SysFont('Arial', 18, bold=True)
            value_font = pygame.font.SysFont('Arial', 18)
            
            label_surface = label_font.render(label, True, config.COLOR_DARK_TEXT) 
            value_surface = value_font.render(str(value), True, color)
            
            y_offset = y_offset_start + i * 30
            self.screen.blit(label_surface, (panel_x + 10, y_offset))
            self.screen.blit(value_surface, (panel_x + panel_width - 10 - value_surface.get_width(), y_offset))

        # 4. Emergency Alert (More prominent flash)
        if len(self.emergency_vehicles_present) > 0:
            
            alert_color = config.COLOR_RED if self.frame_count % 30 < 15 else config.COLOR_DARK_TEXT # Flashing
            vehicles_list = ", ".join(self.emergency_vehicles_present)
            alert_text = f"🚨 {vehicles_list.upper()} INCOMING! 🚨"
            
            alert_surface = self.font.render(alert_text, True, alert_color)
            
            # Position the alert box at the bottom of the panel
            alert_box_width = panel_width - 20
            alert_box_height = alert_surface.get_height() + 10
            alert_box_x = panel_x + 10
            alert_box_y = panel_y + panel_height - alert_box_height - 10
            
            # Draw a box with a red border
            pygame.draw.rect(self.screen, config.COLOR_WHITE, (alert_box_x, alert_box_y, alert_box_width, alert_box_height), border_radius=4)
            pygame.draw.rect(self.screen, config.COLOR_RED, (alert_box_x, alert_box_y, alert_box_width, alert_box_height), 2, border_radius=4)
            
            # Center the text
            text_x = alert_box_x + alert_box_width // 2 - alert_surface.get_width() // 2
            text_y = alert_box_y + 5
            self.screen.blit(alert_surface, (text_x, text_y))


    def _draw(self):
        """Draws the entire simulation state."""
        self.screen.fill(config.COLOR_SKY) 
        timer = getattr(self.controller, 'timer', 0)
        self.intersection.draw(self.screen, controller_timer=timer)
        
        for car in self.vehicles:
            car.draw(self.screen, self.frame_count)
            
        self._draw_stats_panel()
            
        pygame.display.flip()

    def run(self):
        """The main simulation loop."""
        while self.running:
            self.clock.tick(config.SIM_FPS)
            self.frame_count += 1
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

            # 1. Update vehicles and get reward
            reward = self._update_vehicles()
            
            # 2. Update controller (AI or Fixed)
            self.controller.update(self.intersection, reward)
            
            # 3. Spawn new vehicles
            self._spawn_vehicle()
            
            # 4. Draw everything
            self._draw()
            
        if hasattr(self.controller, 'agent'):
            self.controller.agent.decay_epsilon()
            
        pygame.quit()


















