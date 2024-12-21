import datetime

class InputHandler:
    """处理用户输入的类，包括股票代码、日期范围和模型选择。"""

    def __init__(self):
        self.train_data = {}
        self.test_data = {}
        self.model_choice = None

    def validate_stock_symbol(self, symbol):
        """验证股票代码是否为非空字符串。"""
        if not symbol or not isinstance(symbol, str):
            raise ValueError("股票代码不能为空，且必须为字符串。")
        return symbol

    def validate_date(self, date_str):
        """验证日期格式是否为 YYYY-MM-DD，并转换为 datetime 对象。"""
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("日期格式无效，请输入格式为 YYYY-MM-DD 的日期。")

    def validate_date_range(self, start_date, end_date):
        """确保开始日期早于结束日期。"""
        if start_date >= end_date:
            raise ValueError("开始日期必须早于结束日期。")
        return True

    def get_stock_symbol(self, prompt="请输入股票代码（如 AAPL）："):
        """提示用户输入有效的股票代码。"""
        while True:
            try:
                stock_symbol = input(prompt)
                return self.validate_stock_symbol(stock_symbol)
            except ValueError as e:
                print(f"输入错误：{e}")
                print("请重新输入。")

    def get_date_range(self):
        """提示用户输入有效的开始日期和结束日期，并进行验证。"""
        while True:
            try:
                start_date_str = input("请输入开始日期（格式 YYYY-MM-DD）：")
                start_date = self.validate_date(start_date_str)

                end_date_str = input("请输入结束日期（格式 YYYY-MM-DD）：")
                end_date = self.validate_date(end_date_str)

                # 验证日期范围
                self.validate_date_range(start_date, end_date)

                return (
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                )
            except ValueError as e:
                print(f"输入错误：{e}")
                print("请重新输入。")

    def get_inputs(self, data_type="训练数据"):
        """获取用户输入的股票代码和日期范围，并验证合法性。"""
        print(f"请输入{data_type}的信息：")
        stock_symbol = self.get_stock_symbol(f"请输入{data_type}的股票代码（如 AAPL）：")
        start_date, end_date = self.get_date_range()
        return {"stock_symbol": stock_symbol, "start_date": start_date, "end_date": end_date}

    def get_model_choice(self):
        """提示用户选择训练模型，并验证输入合法性。"""
        while True:
            try:
                print("可用的模型选项：")
                print("1. DQN")
                print("2. PPO")
                model_choice = input("请选择训练模型（输入 1 表示 DQN，输入 2 表示 PPO）：")
                
                # 验证输入是否合法
                if model_choice == "1":
                    return "DQN"
                elif model_choice == "2":
                    return "PPO"
                else:
                    raise ValueError("输入无效，请输入数字 1 或 2。")
            except ValueError as e:
                print(f"输入错误：{e}")
                print("请重新选择模型。")

    def get_train_and_test_data_and_model(self):
        """提示用户输入训练数据、测试数据和选择的模型。"""
        self.train_data = self.get_inputs("训练数据")

        self.test_data = self.get_inputs("测试数据")

        print("\n选择训练模型：")
        self.model_choice = self.get_model_choice()

        return self.train_data, self.test_data, self.model_choice

    def validate_initial_balance(self, initial_balance):
        """验证初始余额是否为正数。"""
        if not isinstance(initial_balance, (int, float)) or initial_balance <= 0:
            raise ValueError("初始余额必须是大于 0 的数字。")
        return initial_balance

    def validate_fee_rate(self, fee_rate):
        """验证费用率是否在 [0, 1] 范围内。"""
        if not isinstance(fee_rate, (int, float)) or not (0 <= fee_rate <= 1):
            raise ValueError("费用率必须是 0 到 1 之间的数字，包括 0 和 1。")
        return fee_rate

    def validate_invest_ratio(self, invest_ratio):
        """验证投资比例是否在 (0, 1] 范围内。"""
        if not isinstance(invest_ratio, (int, float)) or not (0 < invest_ratio <= 1):
            raise ValueError("投资比例必须是 0 到 1 之间（不包括 0），且包括 1 的数字。")
        return invest_ratio

    def validate_rebalance_period(self, rebalance_period):
        """验证再平衡周期是否为正整数。"""
        if not isinstance(rebalance_period, int) or rebalance_period <= 0:
            raise ValueError("再平衡周期必须是大于 0 的整数。")
        return rebalance_period

    def validate_max_stocks(self, max_stocks):
        """验证最大持股数量是否为正整数或无限大。"""
        if not (isinstance(max_stocks, (int, float)) and (max_stocks > 0 or max_stocks == float('inf'))):
            raise ValueError("最大持股数量必须是大于 0 的整数，或使用 float('inf') 表示无限大。")
        return max_stocks

    def get_portfolio_parameters(self):
        """获取并验证投资组合参数的输入。"""
        while True:
            try:
                initial_balance = float(input("请输入初始余额（如 10000）："))
                initial_balance = self.validate_initial_balance(initial_balance)
                break
            except ValueError as e:
                print(f"初始余额输入错误：{e}")
                print("请重新输入。")

        while True:
            try:
                fee_rate = float(input("请输入费用率（如 0.01 表示 1%）："))
                fee_rate = self.validate_fee_rate(fee_rate)
                break
            except ValueError as e:
                print(f"费用率输入错误：{e}")
                print("请重新输入。")

        while True:
            try:
                invest_ratio = float(input("请输入投资比例（如 1.0 表示 100%）："))
                invest_ratio = self.validate_invest_ratio(invest_ratio)
                break
            except ValueError as e:
                print(f"投资比例输入错误：{e}")
                print("请重新输入。")

        while True:
            try:
                rebalance_period = int(input("请输入调仓周期（以天为单位，必须是正整数）："))
                rebalance_period = self.validate_rebalance_period(rebalance_period)
                break
            except ValueError as e:
                print(f"调仓周期输入错误：{e}")
                print("请重新输入。")

        while True:
            try:
                max_stocks = input("请输入最大持股数量（输入数字或 'inf' 表示无限大）：")
                max_stocks = float('inf') if max_stocks.lower() == 'inf' else int(max_stocks)
                max_stocks = self.validate_max_stocks(max_stocks)
                break
            except ValueError as e:
                print(f"最大持股数量输入错误：{e}")
                print("请重新输入。")

        return {
            "initial_balance": initial_balance,
            "fee_rate": fee_rate,
            "invest_ratio": invest_ratio,
            "rebalance_period": rebalance_period,
            "max_stocks": max_stocks
        }


# 示例调用
if __name__ == "__main__":
    handler = InputHandler()
    train_data, test_data, model_choice = handler.get_train_and_test_data_and_model()

    print("\n输入成功！")
    print(f"训练数据: 股票代码: {train_data['stock_symbol']}, 开始日期: {train_data['start_date']}, 结束日期: {train_data['end_date']}")
    print(f"测试数据: 股票代码: {test_data['stock_symbol']}, 开始日期: {test_data['start_date']}, 结束日期: {test_data['end_date']}")
    print(f"选择的训练模型: {model_choice}")
