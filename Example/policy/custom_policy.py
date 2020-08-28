from stable_baselines.deepq.policies import FeedForwardPolicy
import tensorflow as tf


def modified_cnn(scaled_images, **kwargs):
    """
    CNN from Nature paper.

    :param scaled_images: (TensorFlow Tensor) Image input placeholder
    :param kwargs: (dict) Extra keywords parameters for the convolutional layers of the CNN
    :return: (TensorFlow Tensor) The CNN output layer
    """

    # split input into (dom, coverage, observation)
    # dom, coverage, observation = tf.split(scaled_images, [130100, 1036, 146], 2)
    dom, coverage, observation = tf.split(scaled_images, [130100, 1036, 146], 2)

    # convert float to int
    coverage_int = tf.to_int32(coverage)
    observation_int = tf.to_int32(observation)

    # delete useless dimension
    coverage_resize = tf.squeeze(coverage_int, squeeze_dims=[1, 3])
    observation_resize = tf.squeeze(observation_int, squeeze_dims=[1, 3])

    # convert int to float
    coverage_float = tf.to_float(coverage_resize)
    observation_float = tf.to_float(observation_resize)

    layer_1 = tf.contrib.layers.conv2d(dom, 32, [1, 7], [1, 4], activation_fn=tf.nn.leaky_relu)
    layer_2 = tf.contrib.layers.conv2d(layer_1, 32, [1, 7], [1, 4], activation_fn=tf.nn.leaky_relu)
    max_pool = tf.contrib.layers.max_pool2d(layer_2, [1, 4], [1, 4])

    layer_3 = tf.contrib.layers.conv2d(max_pool, 16, [1, 7], [1, 4], activation_fn=tf.nn.leaky_relu)
    max_pool2 = tf.contrib.layers.max_pool2d(layer_3, [1, 7], [1, 7])

    layer_4 = tf.contrib.layers.conv2d(max_pool2, 4, [1, 3], 1, activation_fn=tf.nn.leaky_relu)
    max_pool3 = tf.contrib.layers.max_pool2d(layer_4, [1, 4], [1, 4])

    flattened = tf.contrib.layers.flatten(max_pool3)
    concatenation = tf.concat([flattened, coverage_float, observation_float], axis=1)
    fc1 = tf.contrib.layers.fully_connected(concatenation, 51)

    return fc1


class CustomCnnPolicy(FeedForwardPolicy):
    """
    Policy object that implements actor critic, using a CNN (the nature CNN)

    :param sess: (TensorFlow session) The current TensorFlow session
    :param ob_space: (Gym Space) The observation space of the environment
    :param ac_space: (Gym Space) The action space of the environment
    :param n_env: (int) The number of environments to run
    :param n_steps: (int) The number of steps to run for each environment
    :param n_batch: (int) The number of batch to run (n_envs * n_steps)
    :param reuse: (bool) If the policy is reusable or not
    :param _kwargs: (dict) Extra keyword arguments for the nature CNN feature extraction
    """

    def __init__(self, sess, ob_space, ac_space, n_env, n_steps, n_batch, reuse=False, **_kwargs):
        super(CustomCnnPolicy, self).__init__(sess, ob_space, ac_space, n_env, n_steps, n_batch, reuse,
                                              cnn_extractor=modified_cnn,
                                              feature_extraction="cnn", **_kwargs)
