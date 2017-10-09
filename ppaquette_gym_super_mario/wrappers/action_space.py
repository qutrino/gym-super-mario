import gym
from gym.spaces import Discrete, MultiDiscrete
__all__ = [ 'ToDiscrete', 'ToBox' ]

def ToDiscrete():

    class ToDiscreteWrapper(gym.Wrapper):
        """
            Wrapper to convert MultiDiscrete action space to Discrete

            Only supports one config, which maps to the most logical discrete space possible
        """
        def __init__(self, env):
            super(ToDiscreteWrapper, self).__init__(env)
            mapping = {
                0: [0, 0, 0, 0, 0, 0],  # NOOP
                1: [1, 0, 0, 0, 0, 0],  # Up
                2: [0, 0, 1, 0, 0, 0],  # Down
                3: [0, 1, 0, 0, 0, 0],  # Left
                4: [0, 1, 0, 0, 1, 0],  # Left + A
                5: [0, 1, 0, 0, 0, 1],  # Left + B
                6: [0, 1, 0, 0, 1, 1],  # Left + A + B
                7: [0, 0, 0, 1, 0, 0],  # Right
                8: [0, 0, 0, 1, 1, 0],  # Right + A
                9: [0, 0, 0, 1, 0, 1],  # Right + B
                10: [0, 0, 0, 1, 1, 1],  # Right + A + B
                11: [0, 0, 0, 0, 1, 0],  # A
                12: [0, 0, 0, 0, 0, 1],  # B
                13: [0, 0, 0, 0, 1, 1],  # A + B
            }
            self.action_space = gym.spaces.multi_discrete.DiscreteToMultiDiscrete(self.action_space, mapping)
        def _step(self, action):
            return self.env._step(self.action_space(action))

    return ToDiscreteWrapper


# Adapters

class DiscreteToMultiDiscrete(Discrete):
    """
    Adapter that adapts the MultiDiscrete action space to a Discrete action space of any size
    The converted action can be retrieved by calling the adapter with the discrete action
        discrete_to_multi_discrete = DiscreteToMultiDiscrete(multi_discrete)
        discrete_action = discrete_to_multi_discrete.sample()
        multi_discrete_action = discrete_to_multi_discrete(discrete_action)
    It can be initialized using 3 configurations:
    Configuration 1) - DiscreteToMultiDiscrete(multi_discrete)                   [2nd param is empty]
        Would adapt to a Discrete action space of size (1 + nb of discrete in MultiDiscrete)
        where
            0   returns NOOP                                [  0,   0,   0, ...]
            1   returns max for the first discrete space    [max,   0,   0, ...]
            2   returns max for the second discrete space   [  0, max,   0, ...]
            etc.
    Configuration 2) - DiscreteToMultiDiscrete(multi_discrete, list_of_discrete) [2nd param is a list]
        Would adapt to a Discrete action space of size (1 + nb of items in list_of_discrete)
        e.g.
        if list_of_discrete = [0, 2]
            0   returns NOOP                                [  0,   0,   0, ...]
            1   returns max for first discrete in list      [max,   0,   0, ...]
            2   returns max for second discrete in list     [  0,   0,  max, ...]
            etc.
    Configuration 3) - DiscreteToMultiDiscrete(multi_discrete, discrete_mapping) [2nd param is a dict]
        Would adapt to a Discrete action space of size (nb_keys in discrete_mapping)
        where discrete_mapping is a dictionnary in the format { discrete_key: multi_discrete_mapping }
        e.g. for the Nintendo Game Controller [ [0,4], [0,1], [0,1] ] a possible mapping might be;
        mapping = {
            0:  [0, 0, 0],  # NOOP
            1:  [1, 0, 0],  # Up
            2:  [3, 0, 0],  # Down
            3:  [2, 0, 0],  # Right
            4:  [2, 1, 0],  # Right + A
            5:  [2, 0, 1],  # Right + B
            6:  [2, 1, 1],  # Right + A + B
            7:  [4, 0, 0],  # Left
            8:  [4, 1, 0],  # Left + A
            9:  [4, 0, 1],  # Left + B
            10: [4, 1, 1],  # Left + A + B
            11: [0, 1, 0],  # A only
            12: [0, 0, 1],  # B only,
            13: [0, 1, 1],  # A + B
        }
    """
    def __init__(self, multi_discrete, options=None):
        assert isinstance(multi_discrete, MultiDiscrete)
        self.multi_discrete = multi_discrete
        self.num_discrete_space = self.multi_discrete.num_discrete_space

        # Config 1
        if options is None:
            self.n = self.num_discrete_space + 1                # +1 for NOOP at beginning
            self.mapping = {i: [0] * self.num_discrete_space for i in range(self.n)}
            for i in range(self.num_discrete_space):
                self.mapping[i + 1][i] = self.multi_discrete.high[i]

        # Config 2
        elif isinstance(options, list):
            assert len(options) <= self.num_discrete_space
            self.n = len(options) + 1                          # +1 for NOOP at beginning
            self.mapping = {i: [0] * self.num_discrete_space for i in range(self.n)}
            for i, disc_num in enumerate(options):
                assert disc_num < self.num_discrete_space
                self.mapping[i + 1][disc_num] = self.multi_discrete.high[disc_num]

        # Config 3
        elif isinstance(options, dict):
            self.n = len(options.keys())
            self.mapping = options
            for i, key in enumerate(options.keys()):
                if i != key:
                    raise Error('DiscreteToMultiDiscrete must contain ordered keys. ' \
                                'Item {0} should have a key of "{0}", but key "{1}" found instead.'.format(i, key))
                if not self.multi_discrete.contains(options[key]):
                    raise Error('DiscreteToMultiDiscrete mapping for key {0} is ' \
                                'not contained in the underlying MultiDiscrete action space. ' \
                                'Invalid mapping: {1}'.format(key, options[key]))
        # Unknown parameter provided
        else:
            raise Error('DiscreteToMultiDiscrete - Invalid parameter provided.')

    def __call__(self, discrete_action):
        return self.mapping[discrete_action]





def ToBox():

    class ToBoxWrapper(gym.Wrapper):
        """
            Wrapper to convert MultiDiscrete action space to Box

            Only supports one config, which allows all keys to be pressed
        """
        def __init__(self, env):
            super(ToBoxWrapper, self).__init__(env)
            self.action_space = gym.spaces.multi_discrete.BoxToMultiDiscrete(self.action_space)
        def _step(self, action):
            return self.env._step(self.action_space(action))

    return ToBoxWrapper
