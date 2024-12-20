import matplotlib.pyplot as plt

class Visualizer():
    def __init__(self):
        pass

    def _maxProfit(self, prices, balance):
        ans = [0]
        left = 0
        right = 1
        while right < len(prices):
            if prices[right] > prices[left]:
                ans.append(prices[right] - prices[right-1] + ans[-1])   
            else:
                ans.append(ans[-1])
            left += 1
            right += 1
        for i in range(len(ans)):
            ans[i] = ans[i] * balance
        return ans

    def _avgProfit(self, prices, balance):
        ans = [0]
        left = 0
        right = 1
        num = balance / prices[0]
        while right < len(prices):
            ans.append(prices[right] - prices[right-1] + ans[-1])   
            left += 1
            right += 1
        for i in range(len(ans)):
            ans[i] = ans[i] * num
        
        return ans
    
    def visualize(self, prices, profits, show=False):
        days = len(prices)
        # 创建折线图
        plt.plot([i for i in range(days)], profits, label='profit')
        # plt.plot([i for i in range(days)], _maxProfit(prices, 10000), label='max profit')
        plt.plot([i for i in range(days)], self._avgProfit(prices, 10000), label='market trend')
        plt.grid(True)

        # 添加标题
        plt.title("Profit")

        # 添加X轴和Y轴标签
        plt.xlabel("Days")
        plt.ylabel("Profit")
        
        plt.legend()
        plt.savefig("profit.png", dpi=300)
        if show:
            plt.show()