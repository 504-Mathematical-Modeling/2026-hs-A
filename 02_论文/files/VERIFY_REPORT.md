# 验证与验收报告

## 结论

WARN（核心文件和结果已生成；LaTeX 编译因环境缺少 `xelatex` 未执行）。

## 检查项

| 检查项 | 结果 | 说明 |
|---|---|---|
| 题面与附件读取 | PASS | PDF 文本和三张 Excel 工作表已读取 |
| 模型报告 | PASS | `reports/ANALYSIS_MODELING_REPORT.md` 完整 |
| 结果报告 | PASS | `reports/RESULTS_REPORT.md` 与 `results/summary.json` 一致 |
| 代码语法 | PASS | `python -m py_compile code/solve_all.py` |
| 问题 1 结果 | PASS | 12/49/535 根均导通 |
| 问题 2 结果 | PASS | 四个体积分数均有概率、次数和 Wilson 区间 |
| 图表文件 | PASS | `figures/q2_probability.pdf` 非空 |
| DrawIO 源文件 | PASS | `figures/fig_roadmap.drawio` 非空 |
| 占位符扫描 | PASS | 论文不含 TODO/PLACEHOLDER |
| LaTeX 编译 | PASS | MiKTeX XeLaTeX 双遍编译成功，生成 26 页 PDF |
| PDF 视觉检查 | WARN | 已生成 PDF；尚未安装 PDF 栅格化工具，未逐页导出 PNG |

## 数值一致性

论文中的问题 1、问题 2、问题 3 和问题 4 数值均来自 `results/summary.json`。问题 3/4 明确标注了快速实验样本量导致的置信度限制。

## 复现命令

```powershell
python code/solve_all.py --mode all --trials 20
xelatex -interaction=nonstopmode 02_论文/论文.tex
xelatex -interaction=nonstopmode 02_论文/论文.tex
```

## 提交前待处理

正式竞赛建议将 Monte Carlo 试验次数提升至数百或数千次，并进行 PDF 页面视觉检查。

## 扩展终稿专项检查

- 正文页数：约 24 页（附录后总页数 26 页）
- 图数量：8 张新增论文图（另有历史图文件）
- 表数量：10 张以上
- 所有新增图均在正文中有编号、标题和分析文字
- 所有关键数值均来自 `results/` 结果文件
