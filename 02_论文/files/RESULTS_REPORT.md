# 计算结果

## 运行环境

Python 3、NumPy、OpenPyXL、Matplotlib；随机种子 `20260823`。快速实验使用问题 2/3 每点 20 次，问题 4 初筛每点 12 次。

## 问题 1

| 组别 | 介质 A 数量 | 是否导通 | 最短路径节点数 |
|---|---:|---|---:|
| 1 | 12 | 是 | 4 |
| 2 | 49 | 是 | 4 |
| 3 | 535 | 是 | 4 |

## 问题 2

| A 体积分数 | A 数量 | 导通次数/试验次数 | 概率估计 | Wilson 95% 区间 |
|---:|---:|---:|---:|---:|
| 0.50% | 354 | 16/20 | 0.80 | [0.584, 0.919] |
| 0.60% | 424 | 18/20 | 0.90 | [0.699, 0.972] |
| 0.70% | 495 | 20/20 | 1.00 | [0.839, 1.000] |
| 1.00% | 707 | 20/20 | 1.00 | [0.839, 1.000] |

图 `figures/q2_probability.pdf` 展示概率随体积分数上升的趋势。

## 问题 3

在快速网格扫描中，0.50% 已达到点估计 0.90，因此当前仿真精度下最低填充量报告为 0.50%。由于 Wilson 下界仍低于 0.90，正式竞赛提交建议将该候选用更大样本量复核。

## 问题 4

成本公式为 `C=1.05 V_A N_A/10^9+0.05 V_B N_B/10^9`（元）。初筛中点估计满足 0.90 且成本最低的候选为：A 0.20%（141 根）、B 2.00%（597 个），点估计概率 1.00%，成本 3.0933 元。该结论来自低样本初筛，需用更大样本量复核置信下界。

## 可复现方式

```powershell
python code/solve_all.py --mode all --trials 20
```

## 2026-08-23 rerun
Q2 300 trials/point: p=(0.4367,0.5233,0.7133,0.9767), Wilson intervals in results/q2_probability.json. Q3 coarse grid first p>=0.90 at 0.80% (40 trials). Q4 lowest screened candidate is B-only 0.40%, cost 0.1994 yuan, 11/12 hits; independent confirmation remains required.

Q2 revised calibration (AXIS_CONTACT=False, EFFECTIVE_RADIUS_FACTOR=0.2), 300 trials/point: 0.50%=0.1067 [0.0766,0.1467], 0.60%=0.0967 [0.0681,0.1354], 0.70%=0.1867 [0.1466,0.2346], 1.00%=0.3567 [0.3046,0.4124].

## Six-condition rerun
Implemented strict capsule surface distance (radius factor 1.0), complete-cylinder/box intersection, physical X electrodes, finite intersection in all XYZ directions (no periodic wrap), common random prefixes across Q2 fractions, and 2000 trials/point. Q2: 0.3145, 0.4475, 0.5825, 0.8730 with Wilson intervals [0.2945,0.3352], [0.4258,0.4694], [0.5607,0.6039], [0.8577,0.8869].

���Ĳ��ö������������ĵĴ����Խ����Q2 4000�� p=(0.0748,0.2035,0.4520,0.9845)��Q3=0.87%��Q4=580A+115B��p=0.9140���ɱ�=8.9876Ԫ��
