import unittest
import torch
from all.environments import MultiagentPettingZooEnv
from pettingzoo.mpe import simple_world_comm_v2


class MultiagentPettingZooEnvTest(unittest.TestCase):
    def test_init(self):
        MultiagentPettingZooEnv(simple_world_comm_v2.env(), device='cpu')

    def test_variable_spaces(self):
        env = MultiagentPettingZooEnv(simple_world_comm_v2.env(), device='cpu')
        state = env.reset()
        # tests that action spaces work
        for agent in env.agents:
            state = env.last()
            self.assertTrue(env.observation_spaces[agent].contains(state['observation'].cpu().detach().numpy()))
            env.step(env.action_spaces[env.agent_selection].sample())


if __name__ == "__main__":
    unittest.main()
