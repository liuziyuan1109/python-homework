import random
import datetime
import csv

class DataGenerationAndManagementClass:
    def __init__(self):
        """
        初始化类，目前暂无需额外设置，保留该方法方便后续可能的扩展。
        """
        pass

    def generate_stock_data(self, stock_symbol, start_date, end_date, trend_type="random"):
        """
        生成指定股票在给定日期范围内的历史数据，包含Date, Open, High, Low, Close, Volume等列。

        参数:
            stock_symbol (str): 股票代码或者简称，用于标识股票。
            start_date (str or datetime.date): 开始日期，可以是字符串格式'YYYY-MM-DD'或者datetime.date类型。
            end_date (str or datetime.date): 结束日期，可以是字符串格式'YYYY-MM-DD'或者datetime.date类型。
            trend_type (str): 生成的趋势类型，可选值为"upward"（总体上涨）、"downward"（总体下跌）或"random"（完全随机）。

        返回:
            stock_data (list): 生成的股票历史数据，格式为[{'Date': '2021-01-01', 'Open': 100, 'High': 105, 'Low': 98, 'Close': 102, 'Volume': 1000},...]
        """
        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        stock_data = []
        current_date = start_date
        index = 1

        # 设置初始价格
        current_price = round(random.uniform(50, 150), 2)
        trend_factor = 0.05  # 用于控制总体趋势的上涨或下跌幅度

        while current_date <= end_date:
            # 根据趋势类型调整价格变化
            if trend_type == "upward":
                current_price *= (1 + trend_factor)  # 长期上涨趋势
            elif trend_type == "downward":
                current_price *= (1 - trend_factor)  # 长期下跌趋势

            # 添加每日随机波动
            daily_fluctuation = random.uniform(0.95, 1.05)
            current_price *= daily_fluctuation

            # 保证价格在合理范围
            current_price = round(current_price, 2)

            # 生成当天的价格波动
            price_fluctuation = random.uniform(0, 10)
            open_price = round(current_price, 2)
            high_price = round(open_price + price_fluctuation, 2)
            low_price = round(open_price - price_fluctuation, 2)
            close_price = round(random.uniform(low_price, high_price), 2)

            # 确保High和Low为当天的最大最小值
            high_price = max(open_price, high_price, low_price, close_price)
            low_price = min(open_price, high_price, low_price, close_price)

            # 生成随机成交量
            volume = random.randint(100, 10000)

            # 添加记录
            record = {
                'Date': current_date.strftime('%Y-%m-%d'),
                'Index': index,  # 添加序号列
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'Volume': volume
            }
            stock_data.append(record)

            # 更新日期和序号
            current_date += datetime.timedelta(days=1)
            index += 1

        return stock_data

    def save_data_to_csv(self, data, file_path):
        """
        将生成的股票数据保存到CSV文件中。

        参数:
            data (list): 要保存的股票数据，格式为[{'Date': '2021-01-01', 'Open': 100, 'High': 105, 'Low': 98, 'Close': 102, 'Volume': 1000},...]
            file_path (str): CSV文件的保存路径。

        返回:
            bool: 如果保存成功返回True，否则返回False。
        """
        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['Date', 'Index', 'Open', 'High', 'Low', 'Close', 'Volume']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for record in data:
                    writer.writerow(record)
            return True
        except:
            print("保存CSV文件时出现错误，请检查相关权限或文件路径等问题。")
            return False

if __name__ == "__main__":
    # 实例化数据生成与管理类
    data_generator = DataGenerationAndManagementClass()

    # 示例：生成某股票的历史数据并保存为CSV文件
    stock_symbol = "AAPL"  # 这里以苹果公司股票代码示例，可替换为其他股票代码
    start_date = "2022-01-01"  # 开始日期，可按需修改
    end_date = "2022-12-31"  # 结束日期，可按需修改

    # 生成总体上涨的趋势数据
    generated_stock_data = data_generator.generate_stock_data(stock_symbol, start_date, end_date, trend_type="upward")
    print(f"为股票 {stock_symbol} 生成的历史数据示例（前几条）：")
    for i in range(min(5, len(generated_stock_data))):  # 打印前5条数据示例（如果数据量足够）
        print(generated_stock_data[i])

    file_path = "generated_stock_data.csv"  # CSV文件保存路径，可按需修改
    save_success = data_generator.save_data_to_csv(generated_stock_data, file_path)
    if save_success:
        print(f"已成功将生成的股票数据保存到 {file_path} 文件中。")
    else:
        print("保存股票数据到CSV文件失败。")
