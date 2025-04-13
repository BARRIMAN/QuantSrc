# QuantSrc

# 比特币量化交易模型

这是一个基于Python的比特币量化交易模型项目，旨在提供一个完整的量化交易解决方案。

## 项目结构

```
.
├── src/
│   ├── data/           # 数据获取和处理模块
│   ├── strategies/     # 交易策略模块
│   ├── backtest/       # 回测模块
│   ├── utils/          # 工具函数
│   └── config/         # 配置文件
├── requirements.txt    # 项目依赖
└── README.md          # 项目说明
```

## 环境要求

- Python 3.8+
- 依赖包见 requirements.txt

## 安装步骤

1. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用说明

1. 数据获取：
```bash
python src/data/data_fetcher.py
```

2. 运行回测：
```bash
python src/backtest/backtest_runner.py
```

3. 实盘交易（需要配置API密钥）：
```bash
python src/strategies/live_trading.py
```

## 主要功能

- 历史数据获取和处理
- 技术指标计算
- 策略回测
- 风险管理
- 实盘交易接口

## 注意事项

- 请确保在使用实盘交易功能前，充分测试策略的可靠性
- 建议先使用模拟账户进行测试
- 注意控制风险，合理设置止损

## 开发计划

- [x] 基础框架搭建
- [x] 数据获取模块
- [ ] 策略开发
- [ ] 回测系统
- [ ] 实盘接口
- [ ] 风险控制
- [ ] 性能优化

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

MIT License 
