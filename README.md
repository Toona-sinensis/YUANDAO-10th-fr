# 原道十周年 频响曲线数据 / Frequency Response Data

从公开频响曲线图数字化的 **原道十周年**（平头耳塞）频率响应数据，可直接导入
REW、AutoEQ、VituixCAD、squig.link 等工具。

Digitized frequency response data for the **Yuandao 10th Anniversary** earbud,
ready to import into REW, AutoEQ, VituixCAD or squig.link.

---

## 数据来源 / Source

| 项目 | 内容 |
|---|---|
| 产品 | 原道十周年（平头塞） |
| 原始出处 | 哔哩哔哩 UP主 **油兔几** |
| 视频 | [原道 十周年 详细测试 \| 想了想，祝您马年大吉吧 \| 频响曲线、平头横评](https://www.bilibili.com/video/BV1d7XCB5EHP) |
| 原始图表 | [`source/chart.png`](source/chart.png)（原道十周年 vs 正品 MX500） |

**本仓库的数据是本人从上述视频中的频响曲线图逐像素数字化的结果，并非原始测量文件。**
原始测量与图表版权归原 UP主所有；如果你需要权威数据，请以原始视频为准。

This data was digitized by hand (per-pixel) from the chart in the source video.
It is not the original measurement file. The measurement and chart remain the
property of the original creator.

---

## 文件说明 / Files

```
data/
  Yuandao-10th_1-24oct.csv     1/24 倍频程，239 点（推荐使用）
  Yuandao-10th_raw.csv         像素级原始分辨率，1309 点（未平滑）
  Yuandao-10th_normalized.csv  以 1 kHz 归零
  Yuandao-10th.frd             REW / ARTA / VituixCAD 导入格式
  Yuandao-10th_REW.txt         REW 文本导入（制表符分隔）
plots/
  Yuandao-10th_response.png    曲线总览（绝对 SPL + 归一化两个视图）
verification/
  Yuandao-10th_extraction_check.png   提取轨迹叠加在原图上的验证图
source/
  chart.png                    原始曲线图
digitize.py                    数字化脚本，可复现全部数据
```

### CSV 格式

两列，带表头，逗号分隔：

```csv
frequency,spl
20.00,71.16
20.59,72.06
21.19,73.14
```

请按纯文本导入，不要对首行做数值解析。

---

## 主要数据特征 / Highlights

绝对值按图中刻度（绝对 SPL 视图）：

- **低频**：20 Hz 处 71 dB，向中频单调爬升，100 Hz 约 100 dB
- **中频**：200 Hz – 1 kHz 缓升至约 107 dB
- **高频峰**：1.5 kHz 达 108 dB（全频最高），5 kHz 有 106 dB 的小峰
- **滚降**：6 kHz 后开始下降，8 kHz 96 dB，10 kHz 96 dB
- **极高频**：12 kHz 约 91 dB，13 kHz 附近有窄谷，14 kHz 回升至 94 dB，19.5 kHz 落至 80 dB

这是典型的平头塞形态：低频滚降明显、中频平直、高频有峰后转陡降。

---

## 精度说明 / Accuracy

- **坐标标定**：图内 36 条竖网格线与 11 条横网格线用最小二乘拟合，
  残差 x 轴 0.33 px、y 轴 0.47 px（x 轴 20 Hz–19.5 kHz 对数，y 轴 65–115 dB 线性）
- **提取方式**：按颜色掩膜分离黑色实测曲线，按列连续性追踪，剔除图例与标题文字干扰
- **精度估计**：受曲线线宽与抗锯齿影响，约 **±0.2 dB**
- **Y 轴含义**：图中纵轴是相对显示刻度，**不是校准后的绝对声压级**；引用时请注明归一化基准
- **相位**：原图无相位信息，`.frd` 文件中相位列全部填 0

### 关于曲线重叠区

图中黑线与对比曲线（MX500）在部分频段几乎重合，对比曲线不透明地覆盖在黑线之上，
该处像素上不留黑线痕迹。本数据中以下区间为两端插值，非逐像素测得：

| 区间 | 宽度 | 说明 |
|---|---|---|
| 约 658–755 Hz | 30 px | 与对比曲线重合，插值跨过 |
| 约 922–1096 Hz | 34 px | 与对比曲线重合，插值跨过 |

这两段曲线都接近水平（约 106.5–107 dB），插值误差估计在 0.2 dB 以内。
另有约 206–212 Hz 一处极短插值（5 px），可忽略。

### 多源交叉验证

该型号共找到三张对比图，分别与不同产品对比（紫色「老原道」、蓝色「水月雨NB塞」、
青色「MX500」）。三张图独立数字化后，以 1 kHz 归一逐点比较：

| 对比 | 归一化差异 RMS | 极值 |
|---|---|---|
| 紫线版 vs 蓝线版 | 0.09 dB | ±0.45 dB |
| 青线版 vs 蓝线版 | 0.04 dB | ±0.29 dB |

三者在同一形状上收敛，说明数字化结果可靠。本仓库采用青线（MX500 对比）版本，
因为该版本对比曲线为青色，与黑色曲线的颜色分离度最好。

### 频响范围

该图横轴右端标注为 **19.5 kHz**，因此数据上限约 19.3 kHz，**没有 20 kHz 的端点**。
如果你的工具要求完整覆盖到 20 kHz，请按既有滚降趋势自行外推。

---

## 复现 / Reproduce

```bash
pip install pillow numpy
python digitize.py 24oct > data/Yuandao-10th_1-24oct.csv
python digitize.py raw   > data/Yuandao-10th_raw.csv
```

脚本从 `source/chart.png` 读取图像，把 CSV 输出到标准输出，由 shell 重定向写入，
自身不打开任何文件用于写入。已确认重跑结果与仓库中的数据逐点一致。

---

## 许可证 / License

- **数字化脚本与仓库整理工作**：[MIT](LICENSE)（代码部分）
- **曲线数据本身**：建议按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
  使用，转载或二次发布时请注明原始测量来源（UP主 油兔几）与本仓库

---

## 免责声明 / Disclaimer

本数据仅供个人学习、EQ 调试与技术交流使用。数字化的过程不可避免地引入误差，
不适合作为产品验收、退换货或商业宣传的依据。
