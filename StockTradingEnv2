import numpy as np
from gym import spaces
import gym

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