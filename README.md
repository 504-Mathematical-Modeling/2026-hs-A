# 2026 年第七届"华数杯"大学生数学建模竞赛 A题 · 微构体中填充导电介质的仿真优化

本文件夹为华数杯练习项目，整库围绕 2026 年第七届"华数杯" A题（微构体中填充导电介质的仿真优化）展开。研究导电介质（介质 A 直圆柱体、介质 B 球体）在边长 10000nm 微构体中的导通性能与填充量的关系，求导通概率、最低填充量与最低成本填充方案。

## 目录结构

```
2026-hs-A/
├── README.md                  # 本文件：题目说明 + 练习进度
├── AGENTS.md                  # 项目指引（团队约定）
├── .gitignore
├── .vscode/settings.json      # LaTeX Workshop 配置（latexmk+xelatex 自动编译）
├── 00_题目与数据/             # 原题 PDF 与附件数据（A题.pdf、附件.xlsx 等）
├── 01_代码/                   # 建模脚本（按模块组织）
├── 02_论文/                   # 论文写作区（论文.tex + figures/ + files/）
└── 03_参考与复盘/
    ├── 参考文献/              # 题目引用的原始文献（用户手动放入）
    ├── 优秀论文/              # 参考优秀论文 PDF
    └── 资料存档/              # 通用写作规范、六大题型资料等
```

## 进度跟踪

### 2026-08-23 工作流进度

- [x] 完成题面与附件数据审计，建立周期边界连通图模型
- [x] 完成可复现 Python 求解脚本与 Monte Carlo 结果
- [x] 生成结果报告、概率曲线和技术路线图源文件
- [x] 重写 `02_论文/论文.tex` 为基于真实结果的中文论文
- [x] 安装 MiKTeX XeLaTeX 并完成论文双遍编译（生成 `02_论文/论文.pdf`）
- [x] 扩展竞赛终稿至正文约 24 页，包含 8 张图和 10 张以上表
- [ ] 安装 PDF 栅格化工具后进行逐页视觉验收

### 问题一：附件 1 三个微构体（仅介质 A）是否导通

- [ ] 读取附件.xlsx 三组分表坐标，几何建模判断介质间及介质-带电面最短距离
- [ ] 分别给出三个微构体的导通情况

### 问题二：仅介质 A 时不同体积分数的导通概率

- [ ] 体积分数 0.50%、0.60%、0.70%、1.00% 的介质 A 数量换算（四舍五入）
- [ ] 随机位置/姿态生成 + 连通性判定，蒙特卡洛求导通概率

### 问题三：导通概率 ≥ 90% 时介质 A 最低填充量

- [ ] 搜索/插值求最低体积分数（精确到两位小数）

### 问题四：同时填充 A、B 时成本最低填充量

- [ ] 成本最小化（A：1.05 元/μm³，B：0.05 元/μm³），约束导通概率 ≥ 90%
- [ ] 混合填充优化，给出最优填充量与最低成本

2026-08-23 update: solver fixed; Q2 300 trials/point, Q3 and Q4 rerun. Results: results/q2_probability.json, results/q3_threshold.json, results/q4_mixture_search.json. UTF-8 paper: 02_论文/论文.tex; compiled 25-page PDF: 02_论文/论文_new.pdf.

Q2 revised values adopted: 0.1067, 0.0967, 0.1867, 0.3567; paper rebuilt as 25-page 02_论文/论文_new.pdf.

Six-condition solver update: strict capsule distance, finite box intersection, physical X electrodes, no XYZ wrap, common random prefixes, Q2 2000 trials/point completed.

### 2026-08-26 数据复核与 Q4 修复

- [x] 全文数值一致性核查（表格 vs JSON），修复表7/附表A 的 N_A 与 Wilson 区间共 9 处
- [x] 修复 `solve_all.py` 球体-电极周期镜像 bug（靠近 X 面的球被错误接通两电极；Q1–Q3 纯 A 结果不受影响）
- [x] Q2 重跑：11 个分数点 × M=2000（公共随机数嵌套前缀方差缩减）→ `02_论文/files/q2_probability.json`
- [x] Q3 重跑：粗扫描 + 二分精化 × M=2000，认证阈值 **1.08%（765 根 A）** → `02_论文/files/q3_threshold.json`
- [x] Q4 重跑：修复后 98 配置 × M=200。点估计最优 **495A+358B（p̂=0.935，7.95 元）**；Wilson 认证最优 **495A+477B（下限 0.9231，8.15 元）**，较 765 根纯 A 省约 28% 成本 → `02_论文/files/q4_mixture_search.json`
- [x] 论文同步改写：摘要、Q3 一致性说明、Q4 候选表/成本分析/附表/核对表
- [x] 全部图表中文化（Noto Sans CJK JP），重绘 fig_q2_curve / fig_q2_ci / fig_q3_scan / fig_q4_cost / fig_q4_map
- [x] 重跑脚本归档至 `01_代码/`（q2/q3/q4_rerun.py、diag_sphere.py、verify_tables.py）
- [x] `latexmk -xelatex` 编译验证通过（旧数值残留清零）
- [x] 整理 `01_代码/`：删除 `__pycache__` 与一次性诊断脚本；高精度重跑脚本移入 `rerun/` 并修复归档时损坏的 import 头部；新增 `01_代码/README.md` 说明运行顺序
