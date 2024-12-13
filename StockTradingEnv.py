import numpy as np
import gym
from gym import spaces

class StockTradingEnv(gym.Env):
    def __init__(self, data, initial_balance=10000):
        super(StockTradingEnv, self).__init__()
        self.data = data
        self.initial_balance = initial_balance
        self.current_step = 0
        self.done = False
        self.previous_total_value = initial_balance

        # 动作空间（买入、卖出、持有）
        self.action_space = spaces.Discrete(3)

        # 状态空间（股票价格、持仓等）
        self.observation_space = spaces.Box(
            low=0, high=np.inf, shape=(len(data.columns) + 2,)
        )
        self.reset()

    def step(self, action):
        reward = self._take_action(action)
        self.current_step += 1

        if self.current_step >= len(self.data) - 1:
            self.done = True

        return self._next_observation(), reward, self.done, {"总资产": self.previous_total_value}

    def reset(self):
        self.balance = self.initial_balance
        self.current_step = 0
        self.done = False
        self.portfolio = 0  # 当前持有的股票数量
        return self._next_observation()

    def _next_observation(self):
        obs = list(self.data.iloc[self.current_step])
        obs.append(self.balance)
        obs.append(self.portfolio)
        return np.array(obs)

    def _take_action(self, action):
        current_price = self.data.iloc[self.current_step]["Close"]

        # 执行买入或卖出动作
        if action == 0:  # 买入
            self.portfolio += self.balance / current_price
            self.balance = 0
        elif action == 1:  # 卖出
            self.balance += self.portfolio * current_price
            self.portfolio = 0

        # 计算总资产值
        total_value = self.balance + self.portfolio * current_price

        # 计算奖励
        reward = total_value - self.previous_total_value  # 奖励基于资产增长
        self.previous_total_value = total_value

        # 惩罚过度交易
        # transaction_cost = 0.001  # 交易成本（0.1%）
        # if action in [0, 1]:  # 有交易时扣除手续费
        #     reward -= transaction_cost * current_price * self.portfolio
        return reward
