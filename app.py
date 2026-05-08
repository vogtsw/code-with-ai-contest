import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/signal_samples.csv")

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

def main():
    st.title("📡 5G 信号可视化看板")
    st.markdown("欢迎来到 **'Code with AI' 极客探索赛**！")

    data = load_data()
    st.success(f"✅ 数据加载成功！共加载 {len(data)} 条5G信号记录")

    with st.sidebar:
        st.header("🔍 数据筛选")
        st.markdown("**频段筛选**")
        selected_bands = st.multiselect(
            "选择频段",
            options=data['Band'].unique().tolist(),
            default=data['Band'].unique().tolist()
        )

        st.markdown("**RSRP 强度范围**")
        min_rsrp = float(data['RSRP_dBm'].min())
        max_rsrp = float(data['RSRP_dBm'].max())
        rsrp_range = st.slider(
            "RSRP 范围 (dBm)",
            min_value=min_rsrp,
            max_value=max_rsrp,
            value=(min_rsrp, max_rsrp),
            step=1.0
        )

        st.markdown("**终端类型筛选**")
        selected_terminals = st.multiselect(
            "选择终端类型",
            options=data['TerminalType'].unique().tolist(),
            default=data['TerminalType'].unique().tolist()
        )

        st.markdown("**下载速率范围 (Mbps)**")
        min_speed = float(data['Download_Mbps'].min())
        max_speed = float(data['Download_Mbps'].max())
        speed_range = st.slider(
            "下载速率范围",
            min_value=min_speed,
            max_value=max_speed,
            value=(min_speed, max_speed),
            step=10.0
        )

    filtered_data = data[
        (data['Band'].isin(selected_bands)) &
        (data['RSRP_dBm'] >= rsrp_range[0]) &
        (data['RSRP_dBm'] <= rsrp_range[1]) &
        (data['TerminalType'].isin(selected_terminals)) &
        (data['Download_Mbps'] >= speed_range[0]) &
        (data['Download_Mbps'] <= speed_range[1])
    ]

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总记录数", len(filtered_data))
    with col2:
        st.metric("平均 RSRP", f"{filtered_data['RSRP_dBm'].mean():.2f} dBm")
    with col3:
        st.metric("平均 SINR", f"{filtered_data['SINR_dB'].mean():.2f} dB")
    with col4:
        st.metric("平均下载速率", f"{filtered_data['Download_Mbps'].mean():.2f} Mbps")

    st.markdown("### 🗺️ 信号覆盖地图")

    tab1, tab2 = st.tabs(["2D 散点地图", "3D 柱状地图"])

    with tab1:
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

        view_state = pdk.ViewState(
            latitude=filtered_data['Latitude'].mean(),
            longitude=filtered_data['Longitude'].mean(),
            zoom=12,
            pitch=0
        )

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v11',
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "RSRP: {RSRP_dBm} dBm\nSINR: {SINR_dB} dB\nBand: {Band}\n终端: {TerminalType}"}
        ))

    with tab2:
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

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v11',
            initial_view_state=view_state_3d,
            layers=[layer_3d],
            tooltip={"text": "RSRP: {RSRP_dBm} dBm\n下载: {Download_Mbps} Mbps\nBand: {Band}"}
        ))

    st.markdown("### 📊 数据统计图表")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**各频段基站数量分布**")
        band_counts = filtered_data['Band'].value_counts().reset_index()
        band_counts.columns = ['Band', 'Count']
        fig_band = px.bar(
            band_counts,
            x='Band',
            y='Count',
            color='Band',
            title="各频段基站数量",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_band.update_layout(showlegend=False)
        st.plotly_chart(fig_band, use_container_width=True)

    with chart_col2:
        st.markdown("**终端类型占比**")
        terminal_counts = filtered_data['TerminalType'].value_counts()
        fig_terminal = px.pie(
            values=terminal_counts.values,
            names=terminal_counts.index,
            title="终端类型占比",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_terminal, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📈 信号质量分析")

    analysis_col1, analysis_col2 = st.columns(2)

    with analysis_col1:
        st.markdown("**RSRP 分布直方图**")
        fig_rsrp = px.histogram(
            filtered_data,
            x='RSRP_dBm',
            nbins=30,
            title="RSRP 信号强度分布",
            color_discrete_sequence=['#3498db']
        )
        fig_rsrp.add_vline(x=-90, line_dash="dash", line_color="green", annotation_text="优秀 > -90")
        fig_rsrp.add_vline(x=-110, line_dash="dash", line_color="red", annotation_text="较差 < -110")
        st.plotly_chart(fig_rsrp, use_container_width=True)

    with analysis_col2:
        st.markdown("**SINR vs RSRP 散点图**")
        fig_scatter = px.scatter(
            filtered_data,
            x='RSRP_dBm',
            y='SINR_dB',
            color='Band',
            size='Download_Mbps',
            title="信号质量相关性分析",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 数据预览")
    st.dataframe(
        filtered_data.sort_values('RSRP_dBm', ascending=False),
        use_container_width=True,
        height=300
    )

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
    <p>🚀 Code with AI 挑战赛作品 | 5G 信号可视化看板</p>
    <p>RSRP 图例: 🟢 优秀(>-90dBm) | 🟡 良好(-90~-110dBm) | 🔴 较差(<-110dBm)</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

