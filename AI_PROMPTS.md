# Agent 交互日志

**团队名称：** AI_Coders
**成员名单：** 吴冕, 戚胜宇, 安琪
**使用的 AI Coding Agent 工具：** Claude Code / SOLO AI Assistant

---

## 🤖 交互记录导出说明

本次项目通过 AI Coding Agent (Claude Code / SOLO) 辅助开发,以下是核心开发过程中的提示词和交互记录。

---

## 📋 开发过程记录

### 阶段 1: 项目初始化与数据加载

**提示词:**
> 请使用 Streamlit 框架创建一个 5G 信号可视化看板应用。应用需要:
> 1. 读取当前目录下的 `data/signal_samples.csv` 数据文件
> 2. 使用 pandas 库加载数据
> 3. 在网页顶部显示数据加载成功的提示,包括加载的记录数量
> 4. 添加缓存装饰器以提高性能
> 5. 使用 st.set_page_config 设置页面标题为"5G 信号可视化看板",布局为宽屏模式

**AI 响应:**
```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/signal_samples.csv")

st.title("📡 5G 信号可视化看板")
data = load_data()
st.success(f"✅ 数据加载成功！共加载 {len(data)} 条5G信号记录")
```

**问题修复:**
- 提示词: "pandas 版本问题,新版本需要使用 st.cache_data 而不是 st.cache"
- AI 响应: 立即修复,更新了装饰器

---

### 阶段 2: 信号地图可视化 (2D 散点图)

**提示词:**
> 在看板主区域添加一个交互式地图,使用 pydeck 库:
> 1. 使用 ScatterplotLayer 在地图上显示信号点
> 2. 经度从 Longitude 列获取,纬度从 Latitude 列获取
> 3. **关键需求**: 根据 RSRP_dBm 值设置点的颜色
>    - RSRP > -90 dBm: 绿色 [0, 255, 0]
>    - -110 < RSRP ≤ -90 dBm: 渐变色
>    - RSRP ≤ -110 dBm: 红色 [255, 0, 0]
> 4. 添加交互提示框,显示信号详细信息
> 5. 使用深色地图主题 mapbox://styles/mapbox/dark-v11

**AI 响应:**
```python
def get_rsrp_color(rsrp):
    if rsrp > -90:
        return [0, 255, 0]
    elif rsrp > -110:
        ratio = (rsrp + 110) / 20
        r = int(255 * (1 - ratio))
        g = int(255 * ratio)
        return [r, g, 0]
    else:
        return [255, 0, 0]

filtered_data['color'] = filtered_data['RSRP_dBm'].apply(get_rsrp_color)

layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_data,
    get_position='[Longitude, Latitude]',
    get_color='color',
    get_radius=100,
    radius_scale=1,
    radius_min_pixels=5,
    radius_max_pixels=20,
    pickable=True,
)
```

**迭代优化:**
- 添加了 `tooltip` 交互提示
- 调整了点的大小范围
- 添加了图例说明

---

### 阶段 3: 3D 柱状地图可视化

**提示词:**
> 在地图下方添加一个 3D 可视化视图:
> 1. 使用 pydeck 的 ColumnLayer
> 2. 柱子的高度根据 Download_Mbps (下载速率) 变化
> 3. 颜色仍然使用 RSRP 对应的颜色
> 4. 设置 pitch=45 以获得 3D 视角效果
> 5. 添加工具提示显示 RSRP 和下载速率信息

**AI 响应:**
```python
filtered_data['height'] = filtered_data['Download_Mbps'] * 2

layer_3d = pdk.Layer(
    "ColumnLayer",
    filtered_data,
    get_position='[Longitude, Latitude]',
    get_elevation='height',
    elevation_scale=5,
    radius=80,
    get_fill_color='color',
    pickable=True,
    extruded=True,
)

view_state_3d = pdk.ViewState(
    latitude=filtered_data['Latitude'].mean(),
    longitude=filtered_data['Longitude'].mean(),
    zoom=12,
    pitch=45,
    bearing=0
)
```

---

### 阶段 4: 侧边栏筛选功能

**提示词:**
> 在网页左侧添加侧边栏筛选器,实现实时数据过滤:
> 1. **频段筛选**: 使用 st.multiselect 下拉菜单选择 Band (n28, n41, n78)
> 2. **RSRP 范围**: 使用 st.slider 滑动条筛选 RSRP_dBm 的范围
> 3. **终端类型筛选**: 使用 st.multiselect 选择 TerminalType
> 4. **下载速率范围**: 使用 st.slider 筛选 Download_Mbps
> 5. 关键要求: 所有筛选器必须实时联动,地图和图表都要根据筛选条件更新

**AI 响应:**
```python
with st.sidebar:
    st.header("🔍 数据筛选")

    selected_bands = st.multiselect(
        "选择频段",
        options=data['Band'].unique().tolist(),
        default=data['Band'].unique().tolist()
    )

    rsrp_range = st.slider(
        "RSRP 范围 (dBm)",
        min_value=float(data['RSRP_dBm'].min()),
        max_value=float(data['RSRP_dBm'].max()),
        value=(float(data['RSRP_dBm'].min()), float(data['RSRP_dBm'].max())),
        step=1.0
    )

filtered_data = data[
    (data['Band'].isin(selected_bands)) &
    (data['RSRP_dBm'] >= rsrp_range[0]) &
    (data['RSRP_dBm'] <= rsrp_range[1]) &
    (data['TerminalType'].isin(selected_terminals)) &
    (data['Download_Mbps'] >= speed_range[0]) &
    (data['Download_Mbps'] <= speed_range[1])
]
```

---

### 阶段 5: 数据统计图表

**提示词:**
> 使用 plotly 库添加数据统计图表:
> 1. **左侧图表**: 柱状图显示各频段 (Band) 的基站数量分布
> 2. **右侧图表**: 饼图显示不同终端类型 (TerminalType) 的占比
> 3. 图表需要响应侧边栏的筛选变化

**AI 响应:**
```python
fig_band = px.bar(
    band_counts,
    x='Band',
    y='Count',
    color='Band',
    title="各频段基站数量",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_terminal = px.pie(
    values=terminal_counts.values,
    names=terminal_counts.index,
    title="终端类型占比",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
```

---

### 阶段 6: 高级数据分析图表

**提示词:**
> 添加更多数据分析图表以展示信号质量:
> 1. **RSRP 分布直方图**: 显示信号强度分布,添加参考线标记优秀/较差区域
> 2. **SINR vs RSRP 散点图**: 分析信噪比与信号强度的相关性,按频段着色
> 3. 在图表下方显示数据表格,支持排序

**AI 响应:**
```python
fig_rsrp = px.histogram(
    filtered_data,
    x='RSRP_dBm',
    nbins=30,
    title="RSRP 信号强度分布",
    color_discrete_sequence=['#3498db']
)
fig_rsrp.add_vline(x=-90, line_dash="dash", line_color="green")
fig_rsrp.add_vline(x=-110, line_dash="dash", line_color="red")

fig_scatter = px.scatter(
    filtered_data,
    x='RSRP_dBm',
    y='SINR_dB',
    color='Band',
    size='Download_Mbps',
    title="信号质量相关性分析"
)
```

---

### 阶段 7: 单元测试编写

**提示词:**
> 请为应用编写单元测试,使用 pytest 框架:
> 1. 测试 RSRP 颜色函数的各种边界情况
> 2. 测试数据加载功能
> 3. 测试数据筛选逻辑
> 4. 验证数据文件存在和格式正确

**AI 响应:**
```python
def test_rsrp_color_green(self):
    assert get_rsrp_color(-85) == [0, 255, 0]

def test_rsrp_color_red(self):
    assert get_rsrp_color(-115) == [255, 0, 0]

def test_filter_by_band(self):
    df = pd.read_csv("data/signal_samples.csv")
    filtered = df[df['Band'] == 'n78']
    assert all(filtered['Band'] == 'n78')
```

---

## 📊 代码演进总结

通过本次 AI 辅助开发,团队成功实现了以下功能:

1. ✅ **基础关卡** (100% 完成):
   - 数据加载与缓存
   - 2D 散点地图可视化 (RSRP 颜色编码)
   - 数据概览图表 (柱状图、饼图)

2. ✅ **进阶关卡** (100% 完成):
   - 侧边栏实时筛选联动
   - 3D 柱状地图可视化
   - 完整的单元测试覆盖
   - 工程化代码规范

3. 🎯 **AI 工具使用心得**:
   - 通过分步骤、渐进式的提示词引导 AI
   - 遇到问题时明确指出错误,AI 能够快速修正
   - 利用 AI 快速生成代码框架,人工进行细节优化
   - 整体开发效率提升显著

---

**附件日志文件名:** 无附件 (直接在文档中记录)
**简要说明:** 本日志记录了从项目初始化到完成的完整 AI 交互过程,包括需求描述、提示词、代码生成和问题修复全过程。

---

## 补充交付检查记录（2026-05-08）

### 用户补充要求

> 检查当前 GitHub 提交是否满足比赛硬核交付物；重点确认截图、README、AI_PROMPTS、requirements、tag；分析上游 reviewer 分支是否可能影响验收；缺失项直接补齐。

### Agent 实际操作记录

1. 克隆并检查 `https://github.com/vogtsw/code-with-ai-contest.git`，同时拉取上游 `https://github.com/besa-2026/code-with-ai-contest.git` 的 `main` 与 `reviewer` 分支。
2. 发现主分支已有 `app.py`、`requirements.txt`、`README.md`、`AI_PROMPTS.md` 和数据文件，但缺少 Web 应用运行截图。
3. 检查上游 `reviewer` 分支，发现其中包含 `scripts/evaluate_tags.py`，该脚本会检查 `basic-done`、`advanced-done` tag、`app.py` 以及 PROMPT/LOG/AGENT 类日志文件，说明评测很可能会按 tag 与交付物存在性进行自动筛查。
4. 使用本地虚拟环境安装依赖并执行 `python -m pytest test_app.py -v`，确认 16 个单元测试全部通过。
5. 启动 Streamlit 应用并通过浏览器自动化生成 3 张真实运行截图：
   - `screenshots/dashboard-2d-overview.png`
   - `screenshots/dashboard-3d-map.png`
   - `screenshots/dashboard-filtered-n78.png`
6. 更新 README，加入截图展示、项目结构和交付清单。
7. 修复 Streamlit 新版本关于 `use_container_width` 的弃用警告，并在筛选结果为空时给出提示，避免地图视图收到空数据。

### 透明性说明

本次补充检查与截图补齐由 OpenAI Codex coding agent 完成。本文档只记录真实发生的 AI 辅助过程，不伪造模型名称、agent 来源或不存在的交互记录。
