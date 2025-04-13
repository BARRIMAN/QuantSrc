import pandas as pd

file_path = 'ETHBTC_1d_2017_2025_data_cleaned.csv'

# 1. 读取 CSV
df = pd.read_csv(file_path)

# 2. 将 'Open time' 从毫秒级时间戳转换为可读日期时间
# df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')

# 3. 按日期进行排序
df.sort_values(by='Open time', inplace=True)

# 4. 确认是否有重复日期：检查并去重
before_count = len(df)
df.drop_duplicates(subset='Open time', keep='first', inplace=True)
after_count = len(df)
if before_count != after_count:
    print(f"去掉了 {before_count - after_count} 行重复日期数据")

# 5. 检查是否存在缺失值
nan_rows = df[df.isnull().any(axis=1)]
if not nan_rows.empty:
    print("以下行存在 NaN 值：")
    print(nan_rows)

    # 按列进行前向填充
    df.fillna(method='ffill', inplace=True)
    print("\n已对 NaN 进行前向填充（forward fill）。")
else:
    print("没有检测到 NaN 值。")

# 6. 检查结果
print("\n处理后的 DataFrame 概况：")
print(df.info())
print(df.head())

# 如需保存处理完的数据，可执行
df.to_csv('ETHBTC_1d_2017_2025_cleaned.csv', index=False)
