midfreq_backtest/  
│  
├── data/                  # 存放原始CSV或历史行情数据  
├── strategies/            # 各类交易策略模块（价格行为模块也放这里）  
│   ├── base.py            # 抽象策略类  
│   └── price_action.py    # 价格行为策略 
├── core/                  # 回测引擎主体  
│   ├── engine.py  
│   ├── portfolio.py  
│   └── order.py  
├── utils/                 # 工具函数，如数据加载、可视化  
│   ├── data_loader.py  
│   └── visual.py  
├── run_backtest.py        # 回测主脚本  
└── config.py              # 配置文件（可切换策略、参数等）  
