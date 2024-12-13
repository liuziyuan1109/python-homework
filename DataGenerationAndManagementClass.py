import random
import datetime
import csv


class DataGenerationAndManagementClass:
    def __init__(self):
        """
        初始化类，目前暂无需额外设置，保留该方法方便后续可能的扩展。
        """
        pass

    def generate_stock_data(self, stock_symbol, start_date, end_date):
        """
        生成指定股票在给定日期范围内的历史数据，包含Date, Open, High, Low, Close, Volume等列。

        参数:
            stock_symbol (str): 股票代码或者简称，用于标识股票。
            start_date (str or datetime.date): 开始日期，可以是字符串格式'YYYY-MM-DD'或者datetime.date类型。
            end_date (str or datetime.date): 结束日期，可以是字符串格式'YYYY-MM-DD'或者datetime.date类型。

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
        while current_date <= end_date:
            open_price = round(random.uniform(50, 150), 2)
            # 先随机生成一个波动范围值
            price_fluctuation = random.uniform(0, 10)
            high_price = round(open_price + price_fluctuation, 2)
            low_price = round(open_price - price_fluctuation, 2)
            # 从Open、High、Low中确定最大值和最小值，以此来设置Close价格范围
            price_list = [open_price, high_price, low_price]
            max_price = max(price_list)
            min_price = min(price_list)
            close_price = round(random.uniform(min_price, max_price), 2)
            # 重新调整High和Low，确保它们是四个价格中的最值
            high_price = max(open_price, high_price, low_price, close_price)
            low_price = min(open_price, high_price, low_price, close_price)
            volume = random.randint(100, 10000)
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
            index += 1  # 序号递增
            current_date += datetime.timedelta(days=1)
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
                fieldnames = ['Date', 'Index','Open', 'High', 'Low', 'Close', 'Volume']
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
    start_date = "2019-02-01"  # 开始日期，可按需修改
    end_date = "2024-09-15"  # 结束日期，可按需修改
    generated_stock_data = data_generator.generate_stock_data(stock_symbol, start_date, end_date)
    print(f"为股票 {stock_symbol} 生成的历史数据示例（前几条）：")
    for i in range(min(5, len(generated_stock_data))):  # 打印前5条数据示例（如果数据量足够）
        print(generated_stock_data[i])

    file_path = "generated_stock_data.csv"  # CSV文件保存路径，可按需修改
    save_success = data_generator.save_data_to_csv(generated_stock_data, file_path)
    if save_success:
        print(f"已成功将生成的股票数据保存到 {file_path} 文件中。")
    else:
        print("保存股票数据到CSV文件失败。")