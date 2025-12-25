LeetCode-Hot100-Hunter/          # 项目根目录
│
├── app.py                       # 【核心】Streamlit 主程序入口，界面的代码全在这里
├── requirements.txt             # 【依赖】记录项目需要的库（如 streamlit, pandas 等）
├── README.md                    # 【门面】项目说明文档（非常有必要，写清楚它是干嘛的）
├── .gitignore                   # 【规范】告诉 Git 忽略哪些垃圾文件
│
├── data/                        # 【数据层】存放题目数据
│   └── problems.json            # 这里面存 Hot 100 的题目、分类、提示和做题状态
│
├── solutions/                   # 【产出层】存放你写出来的 AC 代码（最值钱的部分）
│   ├── 001_two_sum.py           # 命名建议：ID_英文题名.py
│   ├── 002_add_two_numbers.py
│   └── ...                      # 你的每一次提交都会增加一个文件
│
└── utils/                       # 【工具层】把复杂的逻辑抽离出来，保持 app.py 干净
    ├── __init__.py
    ├── data_manager.py          # 负责读取、更新 json 数据的函数
    └── git_helper.py            # 负责自动执行 git add/commit/push 的脚本