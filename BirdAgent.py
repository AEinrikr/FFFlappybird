import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class ForwardForwardNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(ForwardForwardNN, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.layer2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = self.layer2(x)
        return x
    def goodness(self, x):
        """Compute the goodness as the sum of squared activations."""
        return torch.sum(x**2, dim=1)
    
class Bird_Agent:
    def __init__(self, state_queue, action_queue, num_agents, input_size, hidden_size, output_size):
        self.state_queue = state_queue
        self.action_queue = action_queue
        self.num_agents = num_agents

        self.nn = ForwardForwardNN(input_size, hidden_size, output_size)
        self.optimizer = optim.Adam(self.nn.parameters(), lr=0.01)
        self_criterion = nn.MSELoss()

        self.threshold = 1.0

    def agent_task(self):
        while True:
            if not self.state_queue.empty():
                states = self.state_queue.get()
                actions = self.get_action(states)
                self.action_queue.put(actions)

    def get_action(self, states):
        """Get action based on the current state using the FF algo."""
        states = torch.tensor(states, dtype=torch.float32)
        goodness_scores = self.nn.goodness(self.nn(states))

        actions  = (goodness_scores > self.threshold).int().numpy()
        return actions
    
    def train(self, positive_states, negative_states):
        """Train the network using positive and negative states."""
        self.optimizer.zero_grad()

        pos_states = torch.tensor(positive_states, dtype =torch.float32)
        pos_goodness = self.nn.goodness(self.nn(pos_states))
        pos_loss = torch.mean((pos_goodness - self.threshold)**2)

        neg_states = torch.tensor(negative_states, dtype=torch.float32)
        neg_goodness = self.nn.goodness(self.nn(neg_states))
        neg_loss = torch.mean((neg_goodness - 0)**2)

        loss = pos_loss + neg_loss
        loss.backward()
        self.optimizer.stop()


