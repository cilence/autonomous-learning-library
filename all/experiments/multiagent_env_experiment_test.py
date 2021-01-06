import unittest
import numpy as np
import torch
from all.presets.atari import dqn
from all.presets.multiagent_atari import IndependentMultiagentAtariPreset
from all.environments import MultiagentAtariEnv
from all.experiments import MultiagentEnvExperiment
from all.logging import Writer


class MockWriter(Writer):
    def __init__(self, experiment, label, write_loss):
        self.data = {}
        self.label = label
        self.write_loss = write_loss
        self.experiment = experiment

    def add_scalar(self, key, value, step="frame"):
        if key not in self.data:
            self.data[key] = {"values": [], "steps": []}
        self.data[key]["values"].append(value)
        self.data[key]["steps"].append(self._get_step(step))

    def add_loss(self, name, value, step="frame"):
        pass

    def add_schedule(self, name, value, step="frame"):
        pass

    def add_evaluation(self, name, value, step="frame"):
        self.add_scalar("evaluation/" + name, value, self._get_step(step))

    def add_summary(self, name, mean, std, step="frame"):
        self.add_evaluation(name + "/mean", mean, step)
        self.add_evaluation(name + "/std", std, step)

    def _get_step(self, _type):
        if _type == "frame":
            return self.experiment.frame
        if _type == "episode":
            return self.experiment.episode
        return _type


class MockExperiment(MultiagentEnvExperiment):
    def _make_writer(self, agent_name, env_name, write_loss, logdir):
        self._writer = MockWriter(self, agent_name + '_' + env_name, write_loss)
        return self._writer


class TestMultiagentEnvExperiment(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        torch.manual_seed(0)
        self.env = MultiagentAtariEnv('pong_v1')
        self.env.seed(0)
        self.experiment = None

    def test_adds_default_name(self):
        experiment = MockExperiment(self.make_preset(), self.env, quiet=True)
        self.assertEqual(experiment._writer.label, "IndependentMultiagentAtariPreset_pong_v1")

    def test_adds_custom_name(self):
        experiment = MockExperiment(self.make_preset(), self.env, name='custom', quiet=True)
        self.assertEqual(experiment._writer.label, "custom_pong_v1")

    def test_writes_training_returns(self):
        experiment = MockExperiment(self.make_preset(), self.env, quiet=True)
        experiment.train(episodes=3)
        self.assertEqual(experiment._writer.data, {
            'evaluation/first_0/returns/frame': {
                'values': [-10.0, 21.0, -2.0, 10.0],
                'steps': [2716, 4314, 7766, 10708]},
            'evaluation/second_0/returns/frame': {
                'values': [10.0, -21.0, 2.0, -10.0],
                'steps': [2716, 4314, 7766, 10708]
            }
        })

    def test_writes_test_returns(self):
        experiment = MockExperiment(self.make_preset(), self.env, quiet=True)
        experiment.train(episodes=3)
        experiment._writer.data = {}
        experiment.test(episodes=3)
        self.assertEqual(experiment._writer.data, {
            'evaluation/first_0/returns/frame': {
                'steps': [2716, 4314, 7766, 10708],
                'values': [-10.0, 21.0, -2.0, 10.0]
            },
            'evaluation/second_0/returns/frame': {
                'steps': [2716, 4314, 7766, 10708],
                'values': [10.0, -21.0, 2.0, -10.0]
            }
        })

    def test_writes_loss(self):
        experiment = MockExperiment(self.make_preset(), self.env, quiet=True, write_loss=True)
        self.assertTrue(experiment._writer.write_loss)
        experiment = MockExperiment(self.make_preset(), self.env, quiet=True, write_loss=False)
        self.assertFalse(experiment._writer.write_loss)

    def make_preset(self):
        return IndependentMultiagentAtariPreset({
            agent: dqn().device('cpu').env(env).build()
            for agent, env in self.env.subenvs.items()
        })


if __name__ == "__main__":
    unittest.main()
