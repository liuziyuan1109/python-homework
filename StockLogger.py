import pandas as pd

class StockLogger:
    def __init__(self, stock_data_file):
        self.stock_data_file = stock_data_file
        self.date_mapping = self.load_date_mapping()
        self.log_entries = []

    def load_date_mapping(self):
        """从CSV文件中加载日期和序号的对应关系"""
        data = pd.read_csv(self.stock_data_file)
        mapping = dict(enumerate(data.iloc[:, 0]))
        return mapping

    def generate_log(self, stock_price, stock_count, date_index, total_value, initial_capital, stock_name):
        """根据输入数据生成日志
        stock_price:股价的列表
        stock_count:每日行动之后持有股票数的列表
        date_index:日期序号的列表
        total_value:每日持有利益
        initial_capital:初始资金
        stock_name:股票名
        """
        # 获取具体日期
        stock = 0
        for i in range(len(stock_price)):
            stock_change = stock_count[i] - stock
            stock = stock_count[i]
            date = self.date_mapping.get(date_index[i], "未知日期")
            action = "Buy" if stock_change > 0 else "Sell"
            if stock_change == 0:
                action = "Hold"
            return_rate = ((total_value[i] / initial_capital) - 1) * 100  # 收益率（百分比）
            log_entry = (
                f"Date: {date}, "
                f"Action: {action}, "
                f"Stock: {stock_name}, "
                f"Amount: {abs(stock_change)}, "
                f"Price: {round(stock_price[i], 2)}, "
                f"Return: {round(return_rate, 2)}%"
            )
            print(log_entry)
            self.log_entries.append(log_entry)
        return 

    def save_logs_to_file(self, output_file):
        """将日志列表保存到文本文件"""
        with open(output_file, mode='w') as file:
            for log in self.log_entries:
                file.write(log + "\n")
        print(f"日志已保存到 {output_file}")

if __name__ == "__main__":
    StockLogger("test_stock_data.csv")