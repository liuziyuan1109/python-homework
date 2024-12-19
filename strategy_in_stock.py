import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from gym import spaces
import gym

from DataGenerationAndManagementClass import DataGenerationAndManagementClass

# 实例化数据生成与管理类
data_generator = DataGenerationAndManagementClass()

# 示例：生成某股票的历史数据并保存为CSV文件
# stock_symbol = "AAPL"  # 这里以苹果公司股票代码示例，可替换为其他股票代码
# start_date = "2019-02-01"  # 开始日期，可按需修改
# end_date = "2024-09-15"  # 结束日期，可按需修改
# generated_stock_data = data_generator.generate_stock_data(stock_symbol, start_date, end_date)
# file_path = "generated_stock_data.csv"  # CSV文件保存路径，可按需修改
# data_generator.save_data_to_csv(generated_stock_data, file_path)

# 加载数据
data = pd.read_csv('generated_stock_data.csv')  # 使用你的数据文件路径
data['Date'] = pd.to_datetime(data['Date'])

# 划分训练集和测试集
train_data = data[data['Date'] < '2024-07-10']
test_data = data[data['Date'] >= '2024-07-10']

# 定义自定义交易环境
class StockTradingEnv(gym.Env):
    def __init__(self, df):
        super(StockTradingEnv, self).__init__()
        self.df = df
        self.action_space = spaces.Discrete(3)  # ['买入', '卖出', '持有']
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(6,))
        self.current_step = 0
        self.initial_balance = 10000
        self.balance = self.initial_balance
        self.shares_held = 0
        self.total_asset = 0

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.total_asset = self.balance
        return self._next_observation()

    def _next_observation(self):
        obs = np.array([
            self.df.iloc[self.current_step]['Open'],
            self.df.iloc[self.current_step]['High'],
            self.df.iloc[self.current_step]['Low'],
            self.df.iloc[self.current_step]['Close'],
            self.df.iloc[self.current_step]['Volume'],
            self.balance
        ])
        return obs

    def step(self, action):
        current_price = self.df.iloc[self.current_step]['Close']
        bought_shares = 0
        traded = False

        if action == 0:  # Buy
            bought_shares = self.balance // current_price
            if bought_shares > 0:
                self.balance -= bought_shares * current_price
                self.shares_held += bought_shares
                traded = True
        elif action == 1:  # Sell
            if self.shares_held > 0:
                self.balance += self.shares_held * current_price
                self.shares_held = 0
                traded = True

        self.total_asset = self.balance + self.shares_held * current_price
        self.current_step += 1

        done = self.current_step >= len(self.df) - 1

        # 基于资产变化的原始奖励
        reward = self.total_asset - self.initial_balance

        # 交易次数奖励
        if traded:
            reward += 500  # 每次交易给予额外奖励

        obs = self._next_observation()

        info = {
            'total_asset': self.total_asset,
            'bought_shares': bought_shares
        }

        return obs, reward, done, info

# 创建环境
train_env = DummyVecEnv([lambda: StockTradingEnv(train_data)])

# 训练模型
model = PPO('MlpPolicy', train_env, verbose=1)
model.learn(total_timesteps=30000)

# 测试模型
test_env = StockTradingEnv(test_data)
obs = test_env.reset()
d = {0: '买入', 1: '卖出', 2: '持有'}
profits = []

for i in range(len(test_data)):
    action, _states = model.predict(obs, deterministic=True)
    action = action.item()  # 从 NumPy 数组中提取整数
    obs, reward, done, info = test_env.step(action)
    profits.append(info['total_asset'] - 10000)
    print(f"Day {i+1}: Action = {d[action]}, Total Asset = {info['total_asset']}, Bought Shares = {info['bought_shares']}")
    if done:
        break

print(f"Final Profit: {profits[-1]}")