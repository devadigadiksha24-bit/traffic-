# main.py
import pygame
import config
from simulation import Simulation
from controller import FixedTimeController, QLearningController, QLearningAgent

def main():
    # --- CHOOSE YOUR MODE ---
    # MODE = "FIXED"
    MODE = "AI"
    # -------------------------

    if MODE == "AI":
        # Create the AI agent
        agent = QLearningAgent(
            alpha=config.ALPHA,
            gamma=config.GAMMA,
            epsilon=config.EPSILON,
            min_epsilon=config.MIN_EPSILON,
            decay=config.EPSILON_DECAY
        )
        
        # Create the AI controller
        controller = QLearningController(
            agent=agent,
            decision_interval=config.AI_DECISION_INTERVAL,
            yellow_time=config.AI_YELLOW_TIME
        )
        
        # Note: To train the agent, you would run this `main()` function
        # many times in a loop, perhaps with visualization turned off.
        # For this example, we just run it once and watch it learn.
        
    else: # MODE == "FIXED"
        controller = FixedTimeController(
            green_time=config.FIXED_GREEN_TIME,
            yellow_time=config.FIXED_YELLOW_TIME
        )

    # Create and run the simulation
    sim = Simulation(controller, mode=MODE)
    try:
        sim.run()
    except KeyboardInterrupt:
        print("Simulation stopped.")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
