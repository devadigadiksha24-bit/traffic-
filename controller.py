# controller.py
import numpy as np
import random
import config
import math

class FixedTimeController:
    """A simple controller that switches lights on a fixed timer."""
    def __init__(self, green_time, yellow_time):
        self.green_time = green_time
        self.yellow_time = yellow_time
        self.timer = self.green_time
        self.current_phase = 0  # 0 = NS_GREEN, 1 = EW_GREEN
        self.is_yellow = False

    def update(self, intersection, reward=None):
        self.timer -= 1
        
        if self.is_yellow and self.timer <= 0:
            # Yellow phase finished, switch to new green
            self.is_yellow = False
            self.current_phase = 1 - self.current_phase  # Flip phase
            self.timer = self.green_time
            if self.current_phase == 0:
                intersection.set_phase('NS_GREEN')
            else:
                intersection.set_phase('EW_GREEN')
                
        elif not self.is_yellow and self.timer <= 0:
            # Green phase finished, switch to yellow
            self.is_yellow = True
            self.timer = self.yellow_time
            if self.current_phase == 0:
                intersection.set_phase('NS_YELLOW')
            else:
                intersection.set_phase('EW_YELLOW')

class QLearningAgent:
    """The AI agent that learns using Q-learning."""
    def __init__(self, alpha, gamma, epsilon, min_epsilon, decay):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = decay
        
        # Initialize Q-table: (ns_bins, ew_bins, phase) x (actions)
        state_space = (config.MAX_QUEUE_BIN + 1, config.MAX_QUEUE_BIN + 1, config.NUM_PHASES)
        action_space = config.NUM_ACTIONS
        self.q_table = np.zeros(state_space + (action_space,))

    def get_state(self, intersection):
        """Discretizes the continuous queue lengths into bins."""
        ns_queue = len(intersection.ns_queue)
        ew_queue = len(intersection.ew_queue)
        
        ns_bin = min(math.ceil(ns_queue / config.QUEUE_BIN_SIZE), config.MAX_QUEUE_BIN)
        ew_bin = min(math.ceil(ew_queue / config.QUEUE_BIN_SIZE), config.MAX_QUEUE_BIN)
        
        phase = 0 if intersection.current_phase.startswith('NS') else 1
        
        return (int(ns_bin), int(ew_bin), int(phase))

    def choose_action(self, state):
        """Chooses an action using an epsilon-greedy policy."""
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, config.NUM_ACTIONS - 1)  # Explore
        else:
            return np.argmax(self.q_table[state])  # Exploit

    def update_q_table(self, state, action, reward, next_state):
        """Updates the Q-value for a given state-action pair."""
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        
        # Q-learning formula
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value

    def decay_epsilon(self):
        """Reduces epsilon to decrease exploration over time."""
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay

class QLearningController:
    """The controller that uses the QLearningAgent to make decisions."""
    def __init__(self, agent, decision_interval, yellow_time):
        self.agent = agent
        self.decision_interval = decision_interval
        self.yellow_time = yellow_time
        self.timer = self.decision_interval
        self.is_yellow = False
        self.last_state = None
        self.last_action = None

    def update(self, intersection, total_wait_time_reward):
        # Handle yellow light logic
        if self.is_yellow:
            self.timer -= 1
            if self.timer <= 0:
                self.is_yellow = False
                # Switch to the new green phase
                if intersection.current_phase == 'NS_YELLOW':
                    intersection.set_phase('EW_GREEN')
                else:
                    intersection.set_phase('NS_GREEN')
                # Start new decision timer
                self.timer = self.decision_interval
            return  # Do nothing else while yellow

        # Handle green light logic
        self.timer -= 1
        
        # Time to make a new decision
        if self.timer <= 0:
            current_state = self.agent.get_state(intersection)
            
            # Update Q-table based on the *last* action and the reward we just received
            if self.last_state is not None:
                self.agent.update_q_table(self.last_state, self.last_action, total_wait_time_reward, current_state)

            # Choose a new action
            action = self.agent.choose_action(current_state)
            
            # Store state and action for the next update
            self.last_state = current_state
            self.last_action = action
            
            # Execute action
            if action == 1:  # Switch phase
                self.is_yellow = True
                self.timer = self.yellow_time
                if intersection.current_phase.startswith('NS'):
                    intersection.set_phase('NS_YELLOW')
                else:
                    intersection.set_phase('EW_YELLOW')
            else:  # Keep phase
                # Do nothing, just reset timer
                self.timer = self.decision_interval
