import numpy as np
from gym import spaces
import gym

class PPOEnv(gym.Env):
    def __init__(self, df, initial_balance=10000, rebalance_period=1, invest_ratio=0.1, max_stocks=100, fee_rate=0.001):
        super(PPOEnv, self).__init__()
        self.df = df
        self.action_space = spaces.Discrete(3)  # ['买入', '卖出', '持有']
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(6,))

        # Customizable Parameters
        self.initial_balance = initial_balance
        self.rebalance_period = rebalance_period  # How often to rebalance portfolio (in days)
        self.investment_ratio = invest_ratio  # Percentage of balance to invest
        self.max_shares = max_stocks  # Max number of shares that can be held
        self.transaction_fee_ratio = fee_rate  # Transaction fee ratio (e.g., 0.001 means 0.1%)

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