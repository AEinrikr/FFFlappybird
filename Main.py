from FlappyBird import FlappyBirdGame
from BirdAgent import Bird_Agent
import threading
import queue

num_agents = 1
episodes = 2

if __name__ == "__main__":
    input_size = 8  # Number of state features
    hidden_size = 128
    output_size = 2  # Number of actions (flap or not flap)

    action_queue = queue.Queue()
    state_queue = queue.Queue()

    # Initialize the game and start the game in the main thread
    game = FlappyBirdGame(frames=120, state_queue=state_queue, action_queue=action_queue, episodes=episodes, num_agents=num_agents)
    game.start_game()

    bird = Bird_Agent(state_queue=state_queue, action_queue=action_queue, num_agents=num_agents,
                      input_size=input_size, hidden_size=hidden_size, output_size=output_size)

    def agent_task():
        bird.agent_task()

    # Start the agent logic in a separate thread
    agent_thread = threading.Thread(target=agent_task)
    agent_thread.start()

    try:
        for episode in range(episodes):
            positive_states = []
            negative_states = []

            while game.game_on():
                if not state_queue.empty():
                    states = state_queue.get()
                    for state in states:
                        if state[6] > 0:
                            positive_states.append(state)
                        else:
                            negative_states.append(state)

            if positive_states and negative_states:
                bird.train(positive_states, negative_states)

            positive_states.clear()
            negative_states.clear()

    except KeyboardInterrupt:
        pass
    finally:
        agent_thread.join()
        state_queue.close()
        action_queue.close()
