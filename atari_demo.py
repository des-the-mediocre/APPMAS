# Copyright 2021 Andreas Nesse
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import pickle
import sys
import time

from tf_agents.environments import tf_py_environment
from evo_utils.atari_net import AtariNet
from preprocessing import suite_atari_mod as suite_atari


class AtariDemo:
    """
    Class for demoing agents.
    """

    def __init__(self,env_name,conf_path):
        def _load_config(conf_path):
            try:
                assert os.path.exists(conf_path)
            except IOError:
                print('The config file specified does not exist.')
            with open(conf_path, 'r') as f:
                conf = json.load(f)
            return conf

        self.net_conf = _load_config(conf_path)

        self.py_env = suite_atari.load(environment_name=env_name, eval_env=True)
        self.env = tf_py_environment.TFPyEnvironment(self.py_env)
        
        obs_shape = tuple(self.env.observation_spec().shape)
        action_shape = self.env.action_spec().maximum - self.env.action_spec().minimum + 1

        self.agent = AtariNet(obs_shape, action_shape, self.net_conf)


    def import_weights(self,agent_path):
        with open(agent_path, 'rb') as f:
            weights = pickle.load(f)
        self.agent.set_weights(weights)


    def run(self,epsilon):
        time_step = self.env.reset()
        score = 0.0
        while not time_step.is_last():
            action_step = self.agent.action(time_step,epsilon)
            time_step = self.env.step(action_step)
            score += time_step.reward
            self.env.render(mode='human')
            time.sleep(0.01)
        self.env.close()
        print('\nThe agent scored {:.2f}\n'.format(score[0]))


def main(env_name,agent_path,epsilon=0,conf_name='net.config'):
    """
    Run demo of loaded agent.
    """
    conf_path = os.path.join('configs',conf_name)
    demo = AtariDemo(env_name,conf_path)
    demo.import_weights(agent_path)
    demo.run(epsilon)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args)==4:
        main(args[0],args[1],float(args[2]),args[3])
    elif len(args)==3:
    	main(args[0],args[1],float(args[2]))
    else:
        main(args[0],args[1])