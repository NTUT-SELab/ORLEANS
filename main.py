from Example.webdriver.crawljax import CrawlJax
from web_environment import WebEnvironment
from Example.action_strategy.all_valid_input import AllValidInput
from Example.server_instance.timeoff_management import TimeOffManagementServer
from Example.code_coverage.code_coverage_collector import IstanbulMiddleware

from stable_baselines import DQN
from Example.policy.custom_policy import CustomCnnPolicy

if __name__ == '__main__':
    env_index = 0
    model_dir = "./Learning_Result/"
    model_name = "DQN_Custom_policy_example"
    action_strategy = AllValidInput(env_index=env_index)
    server_instance = TimeOffManagementServer(server_port=3000 + env_index)
    webdriver = CrawlJax(crawler_id=env_index, url="http://localhost:3000/", is_wrap_element=True)
    code_coverage_collector = IstanbulMiddleware(server_port=3000 + env_index)

    env = WebEnvironment(env_index=env_index, webdriver=webdriver, action_strategy=action_strategy,
                         server_instance=server_instance, code_coverage_collector=code_coverage_collector)

    model = DQN(CustomCnnPolicy, env, verbose=1, prioritized_replay=True,
                tensorboard_log="./openai_tensorboard/" + model_name,
                learning_starts=100,
                exploration_fraction=0.97,
                exploration_final_eps=0,
                buffer_size=5000,
                target_network_update_freq=500)

    model.learn(total_timesteps=100000, log_interval=1)
    model.save(model_dir + model_name)
    model.save(model_name)
