import numpy as np
import gym
from gym import spaces

class StockTradingEnv(gym.Env):
    def __init__(self, data, initial_balance=10000, fee_rate=0, invest_ratio=1.0, rebalance_period=2, max_stocks=float('inf')):
        super(StockTradingEnv, self).__init__()
        self.data = data
        self.initial_balance = initial_balance
        self.fee_rate = fee_rate  # 手续费率
        self.rebalance_period = rebalance_period  # 调仓周期
        self.max_stocks = max_stocks  # 最多持有股票数量

        self.current_step = 0
        self.done = False
        self.total_value = initial_balance
        self.balance = initial_balance * invest_ratio
        self.portfolio = 0
        self.last_rebalance_step = 0

        # 动作空间（买入、卖出、持有）
        self.action_space = spaces.Discrete(3)

        # 状态空间（股票价格、持仓等）
        self.observation_space = spaces.Box(
            low=0, high=np.inf, shape=(len(data.columns) + 2,)
        )
        self.reset()

    def step(self, action):
        reward = self._take_action(action)
        day = self.current_step
        self.current_step += self.rebalance_period

        if self.current_step >= len(self.data) - 1:
            self.done = True

        return self._next_observation(), reward, self.done, {"total_asset": self.total_value, "day": day}

    def reset(self):
        self.balance = self.initial_balance
        self.current_step = 0
        self.done = False
        self.portfolio = 0  # 当前持有的股票数量
        self.total_value = self.initial_balance
        self.last_rebalance_step = 0
        return self._next_observation()

    def _next_observation(self):
        obs = list(self.data.iloc[self.current_step])
        obs.append(self.balance)
        obs.append(self.portfolio)
        return np.array(obs)

    def _take_action(self, action):
        current_price = self.data.iloc[self.current_step]["Close"]
        last_balance = self.balance
        last_portfolio = self.portfolio

        # 计算可用资金和最多可购买的股票数量
        max_buyable_stocks = min(self.balance // current_price, self.max_stocks - self.portfolio)

        # 执行买入或卖出动作
        if action == 0 and max_buyable_stocks > 0:  # 买入
            buy_quantity = int(max_buyable_stocks)
            cost = buy_quantity * current_price * (1 + self.fee_rate)
            while cost > self.balance:
                buy_quantity -= 1
                cost = buy_quantity * current_price * (1 + self.fee_rate)
            self.portfolio += buy_quantity
            self.balance -= cost

        elif action == 1 and self.portfolio > 0:  # 卖出
            sell_quantity = int(self.portfolio)
            proceeds = sell_quantity * current_price * (1 - self.fee_rate)
            self.portfolio -= sell_quantity
            self.balance += proceeds

        # 计算总资产值
        total_value = self.balance + self.portfolio * current_price

        # 计算奖励
        reward = total_value - self.total_value
        self.total_value = total_value

        punish = 0

        # 惩罚不交易，鼓励交易
        if last_balance == self.balance or last_portfolio == self.portfolio:
            punish = self.initial_balance / 100
            
        # 计算奖励
        reward = total_value - self.total_value - punish # 奖励基于资产增长
        # if reward > 0:
        #     reward += total_value * 0.1
        # print(f'上次总市值：{self.total_value}，本次总市值：{total_value}')

        self.total_value = total_value

        return reward
