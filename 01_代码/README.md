# 01_代码 说明

## 文件结构与运行顺序

```
01_代码/
├── solve_all.py        # 主求解器：Q1–Q4 全流程（命令行入口）
├── make_figures.py     # 论文图表生成（读取 02_论文/files/*.json）
├── verify_tables.py    # 校验工具：论文表格 vs JSON 数据一致性
└── rerun/              # 高精度重跑脚本（论文最终数据来源，依赖 solve_all）
    ├── q2_rerun.py     # Q2：11 个体积分数 × M=2000（嵌套前缀公共随机数）
    ├── q3_rerun.py     # Q3：粗扫描 + 二分精化 × M=2000（Wilson 下界认证）
    └── q4_rerun.py     # Q4：98 配置网格 × M=200（球体镜像 bug 修复后版本）
```

## 运行顺序

```bash
# 1. 主求解器（快速全流程，结果仅作初筛）
python3 solve_all.py --mode all

# 2. 高精度重跑（论文数据以此为准，依次执行）
python3 rerun/q2_rerun.py      # → 02_论文/files/q2_probability.json
python3 rerun/q3_rerun.py      # → 02_论文/files/q3_threshold.json
python3 rerun/q4_rerun.py      # → 02_论文/files/q4_mixture_search.json

# 3. 图表生成（先 make_figures 再按需覆盖 Q2/Q3 精细版）
python3 make_figures.py

# 4. 表格一致性校验（论文定稿前运行）
python3 verify_tables.py
```

## 注意事项

- 所有输出统一写入 `02_论文/files/`（数据）与 `02_论文/figures/`（图），勿改回根目录。
- `solve_all.py` 曾存在球体–电极周期镜像 bug（靠近 X 面的球被错误接通两电极），已于 2026-08-26 修复；`rerun/q4_rerun.py` 为修复后重跑版本，旧 Q4 数据作废。
- `rerun/` 脚本通过相对路径导入同目录上级的 `solve_all.py`，请保持目录结构不变。
