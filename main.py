import pandas as pd
from stable_baselines3 import DQN
from stable_baselines3 import PPO
from InputHandler import InputHandler
from DataGenerationAndManagementClass import DataGenerationAndManagementClass
from DQNEnv import DQNEnv
from PPOEnv import PPOEnv
from StockLogger import StockLogger
from Visualization import Visualizer

# 实例化数据生成与管理类
data_generator = DataGenerationAndManagementClass()

# 根据用户输入生成某股票的历史数据，作为训练数据和测试（回测）数据，并保存为CSV文件
handler = InputHandler()
train_data, test_data, model_choice = handler.get_train_and_test_data_and_model()
generated_stock_data = data_generator.generate_stock_data(stock_symbol=train_data['stock_symbol'],
                                                          start_date=train_data['start_date'],
                                                          end_date=train_data['end_date'])
file_path = "train_stock_data.csv"  # CSV文件保存路径，可按需修改
data_generator.save_data_to_csv(generated_stock_data, file_path)

# 回测数据
generated_stock_data = data_generator.generate_stock_data(stock_symbol=test_data['stock_symbol'],
                                                          start_date=test_data['start_date'],
                                                          end_date=test_data['end_date'])
file_path = "test_stock_data.csv"  # CSV文件保存路径，可按需修改
data_generator.save_data_to_csv(generated_stock_data, file_path)

# 加载数据
train_df = pd.read_csv('train_stock_data.csv') # 股票历史数据，包含开盘价、收盘价等
train_df = train_df.drop(columns=['Date', 'Index'])

test_df = pd.read_csv('test_stock_data.csv') # 股票历史数据，包含开盘价、收盘价等
test_df = test_df.drop(columns=['Date', 'Index'])

# 输入模型参数
parameters = handler.get_portfolio_parameters()

# 选择模型
if model_choice == 'DQN':
    # 创建训练环境和测试环境
    train_env = DQNEnv(train_df, initial_balance=parameters['initial_balance'], fee_rate=parameters['fee_rate'],
                       invest_ratio=parameters['invest_ratio'], rebalance_period=parameters['rebalance_period'],
                       max_stocks=parameters['max_stocks'])
    test_env = DQNEnv(test_df, initial_balance=parameters['initial_balance'], fee_rate=parameters['fee_rate'],
                      invest_ratio=parameters['invest_ratio'], rebalance_period=parameters['rebalance_period'],
                      max_stocks=parameters['max_stocks'])
    model = DQN("MlpPolicy",
                train_env,
                verbose=1,
                policy_kwargs={'net_arch': [64, 32, 10]},
                learning_rate=0.0001,
                exploration_fraction=0.3,
                exploration_initial_eps=0.8,
                exploration_final_eps=0.1
                )
elif model_choice == 'PPO':
    # 创建训练环境和测试环境
    train_env = PPOEnv(train_df, initial_balance=parameters['initial_balance'], fee_rate=parameters['fee_rate'],
                       invest_ratio=parameters['invest_ratio'], rebalance_period=parameters['rebalance_period'],
                       max_stocks=parameters['max_stocks'])
    test_env = PPOEnv(test_df, initial_balance=parameters['initial_balance'], fee_rate=parameters['fee_rate'],
                      invest_ratio=parameters['invest_ratio'], rebalance_period=parameters['rebalance_period'],
                      max_stocks=parameters['max_stocks'])
    model = PPO('MlpPolicy', train_env, verbose=1)

# 训练模型
model.learn(total_timesteps=50000)

# 测试智能体
model.set_env(test_env)
obs = test_env.reset()
done = False
days = []
total_asset = []
portfolios = []
while not done:
    action = model.predict(obs, deterministic=True)[0]
    obs, reward, done, info = test_env.step(action)
    days.append(info['day'])
    total_asset.append(info['total_asset'])
    portfolios.append(info['portfolio'])

prices = pd.read_csv('test_stock_data.csv')['Close'].iloc[days]
visualizer = Visualizer()
visualizer.visualize(prices, total_asset, days, initial_balance=test_env.initial_balance)
print(f"Final Profit: {(total_asset[-1] - test_env.initial_balance):.2f}")

logger = StockLogger('test_stock_data.csv')
logger.generate_log(prices, portfolios, days, total_asset, test_env.initial_balance, test_data['stock_symbol'])
logger.save_logs_to_file("stock_logs.txt")
