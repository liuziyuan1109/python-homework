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
stock_symbol = "AAPL"  # 这里以苹果公司股票代码示例，可替换为其他股票代码
start_date = "2019-02-01"  # 开始日期，可按需修改
end_date = "2024-09-15"  # 结束日期，可按需修改
generated_stock_data = data_generator.generate_stock_data(stock_symbol, start_date, end_date)
file_path = "generated_stock_data.csv"  # CSV文件保存路径，可按需修改
data_generator.save_data_to_csv(generated_stock_data, file_path)

# 加载数据
data = pd.read_csv('generated_stock_data.csv')  # 使用你的数据文件路径
data['Date'] = pd.to_datetime(data['Date'])

# 划分训练集和测试集
train_data = data[data['Date'] < '2024-07-10']
test_data = data[data['Date'] >= '2024-07-10']

# 定义自定义交易环境
class StockTradingEnv(gym.Env):
    def __init__(self, df, initial_balance=10000, rebalance_period=1, investment_ratio=0.1, max_shares=100, transaction_fee_ratio=0.001):
        super(StockTradingEnv, self).__init__()
        self.df = df
        self.action_space = spaces.Discrete(3)  # ['买入', '卖出', '持有']
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(6,))

        # Customizable Parameters
        self.initial_balance = initial_balance
        self.rebalance_period = rebalance_period  # How often to rebalance portfolio (in days)
        self.investment_ratio = investment_ratio  # Percentage of balance to invest
        self.max_shares = max_shares  # Max number of shares that can be held
        self.transaction_fee_ratio = transaction_fee_ratio  # Transaction fee ratio (e.g., 0.001 means 0.1%)

        # Initialize environment state
        self.reset()

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.total_asset = self.balance
        return self._next_observation()

    def _next_observation(self):
        # Observation includes: Open, High, Low, Close, Volume, Current Balance
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
        transaction_fee = 0

        # Action logic: Buy, Sell, or Hold
        if action == 0:  # Buy
            # Calculate how many shares to buy based on the investment ratio
            max_investment = self.balance * self.investment_ratio
            potential_shares = max_investment // current_price
            bought_shares = min(potential_shares, self.max_shares - self.shares_held)

            # Ensure the transaction fee is accounted for
            total_cost = bought_shares * current_price
            transaction_fee = total_cost * self.transaction_fee_ratio
            if bought_shares > 0 and self.balance >= (total_cost + transaction_fee):
                self.balance -= (total_cost + transaction_fee)
                self.shares_held += bought_shares
                traded = True

        elif action == 1:  # Sell
            if self.shares_held > 0:
                total_sale = self.shares_held * current_price
                transaction_fee = total_sale * self.transaction_fee_ratio
                self.balance += (total_sale - transaction_fee)
                self.shares_held = 0
                traded = True

        # Update total asset
        self.total_asset = self.balance + self.shares_held * current_price
        self.current_step += 1

        done = self.current_step >= len(self.df) - 1

        # Reward based on asset growth and trading
        reward = self.total_asset - self.initial_balance
        if traded:
            reward += 500  # Additional reward for trading action

        # Next observation and info
        obs = self._next_observation()

        info = {
            'total_asset': self.total_asset,
            'bought_shares': bought_shares,
            'transaction_fee': transaction_fee
        }

        return obs, reward, done, info

# Create environment with custom parameters
initial_balance = 10000  # Customize initial balance
rebalance_period = 1  # Rebalance every 5 days
investment_ratio = 0.1  # Invest 30% of available balance per trade
max_shares = 100  # Max number of shares that can be held
transaction_fee_ratio = 0.001  # Transaction fee: 0.1% of transaction value

train_env = DummyVecEnv([lambda: StockTradingEnv(train_data, initial_balance, rebalance_period, investment_ratio, max_shares, transaction_fee_ratio)])

# Train PPO model
model = PPO('MlpPolicy', train_env, verbose=1)
model.learn(total_timesteps=10000)

# Test model on test data
test_env = StockTradingEnv(test_data, initial_balance, rebalance_period, investment_ratio, max_shares, transaction_fee_ratio)
obs = test_env.reset()
d = {0: '买入', 1: '卖出', 2: '持有'}
profits = []

for i in range(len(test_data)):
    action, _states = model.predict(obs, deterministic=True)
    action = action.item()  # Extract integer action
    obs, reward, done, info = test_env.step(action)
    profits.append(info['total_asset'] - initial_balance)
    print(f"Day {i+1}: Action = {d[action]}, Total Asset = {info['total_asset']}, Bought Shares = {info['bought_shares']}, Transaction Fee = {info['transaction_fee']}")
    if done:
        break

print(f"Final Profit: {profits[-1]}")
