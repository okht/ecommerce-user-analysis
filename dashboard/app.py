from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Analytics", layout="wide", page_icon="📊")

# ===== 自定义样式 =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

.block-container { padding: 1rem 2rem; max-width: 1200px; }
.stApp { background: #08080f; }

/* 指标卡片 */
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
}
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 18px 22px;
}
[data-testid="metric-container"] label {
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35) !important;
}

/* Tab样式 */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.02);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 24px;
    font-weight: 600;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    background: rgba(129,140,248,0.12) !important;
}

/* 隐藏Streamlit默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* selectbox */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.06);
    border-radius: 8px;
}

div[data-testid="stMarkdownContainer"] h1 {
    font-weight: 800;
    letter-spacing: -0.03em;
}
div[data-testid="stMarkdownContainer"] h3 {
    font-weight: 700;
    color: rgba(255,255,255,0.75);
}
</style>
""", unsafe_allow_html=True)

# ===== Plotly 主题 =====
COLORS = ["#818cf8", "#34d399", "#f87171", "#38bdf8", "#c084fc", "#fb923c", "#fbbf24", "#64748b"]
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.6)", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(bgcolor="rgba(8,8,15,0.95)", font_size=12, font_color="white", bordercolor="rgba(129,140,248,0.3)"),
)

# ===== 加载数据 =====
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_DIR / "retail_cleaned.csv", parse_dates=["InvoiceDate"])
    rfm = pd.read_csv(DATA_DIR / "rfm_clustered.csv", index_col="Customer ID")
    return df, rfm

df, rfm = load_data()

# ===== HEADER =====
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <div style="margin-bottom: -10px;">
        <span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em;
            background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            E-Commerce Analytics
        </span>
        <span style="font-size: 0.65rem; padding: 3px 10px; border-radius: 5px;
            background: rgba(129,140,248,0.12); color: #818cf8; font-weight: 600;
            letter-spacing: 0.05em; margin-left: 10px; vertical-align: middle;">
            RFM + K-MEANS
        </span>
    </div>
    <div style="font-size: 0.72rem; color: rgba(255,255,255,0.25); margin-top: 4px;">
        UCI Online Retail II · Dec 2009 — Dec 2011 · 5,878 Customers · 36,969 Orders
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

# ===== KPI =====
kpi_data = [
    ("CUSTOMERS", "5,878", "41个国家/地区", "#818cf8"),
    ("ORDERS", "36,969", "2年交易记录", "#34d399"),
    ("REVENUE", "£17.74M", "平均月收入 £710K", "#fbbf24"),
    ("AVG ORDER", "£480", "中位数 £299", "#f472b6"),
]
cols = st.columns(4)
for i, (label, value, sub, color) in enumerate(kpi_data):
    with cols[i]:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
            border-radius: 14px; padding: 18px 22px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -15px; right: -15px; width: 60px; height: 60px;
                border-radius: 50%; background: {color}; opacity: 0.04; filter: blur(15px);"></div>
            <div style="font-size: 0.65rem; color: rgba(255,255,255,0.3); letter-spacing: 0.1em; margin-bottom: 8px;">{label}</div>
            <div style="font-size: 1.7rem; font-weight: 800; letter-spacing: -0.03em; color: {color};
                font-family: 'JetBrains Mono', monospace;">{value}</div>
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.25); margin-top: 4px;">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["📈 销售趋势", "👥 用户分层", "💡 策略建议"])

# ---------- TAB 1: 趋势 ----------
with tab1:
    # 关键发现
    findings = [
        ("📅", "强季节性", "9-11月圣诞季销售攀升40%+"),
        ("🌍", "市场集中", "英国贡献83%收入"),
        ("📦", "商品长尾", "20%商品贡献78%收入"),
        ("👥", "用户分化", "22%用户贡献68%收入"),
    ]
    fcols = st.columns(4)
    for i, (icon, title, desc) in enumerate(findings):
        with fcols[i]:
            st.markdown(f"""
            <div style="padding: 14px 16px; border-radius: 12px; background: rgba(255,255,255,0.015);
                border: 1px solid rgba(255,255,255,0.04); height: 90px;">
                <div style="font-size: 1.1rem; margin-bottom: 6px;">{icon}</div>
                <div style="font-size: 0.8rem; font-weight: 700; color: rgba(255,255,255,0.75); margin-bottom: 3px;">{title}</div>
                <div style="font-size: 0.68rem; color: rgba(255,255,255,0.35); line-height: 1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

    # 月度趋势
    col_chart, col_ctrl = st.columns([5, 1])
    with col_ctrl:
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        metric_choice = st.radio("指标", ["收入", "订单数", "客户数"], label_visibility="collapsed")

    monthly = df.groupby(df["InvoiceDate"].dt.to_period("M")).agg(
        收入=("Revenue", "sum"),
        订单数=("Invoice", "nunique"),
        客户数=("Customer ID", "nunique")
    )
    monthly.index = monthly.index.to_timestamp()

    metric_colors = {"收入": "#818cf8", "订单数": "#34d399", "客户数": "#fbbf24"}

    with col_chart:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly.index, y=monthly[metric_choice],
            mode="lines", fill="tozeroy",
            line=dict(color=metric_colors[metric_choice], width=2.5, shape="spline"),
            fillcolor=f"rgba({int(metric_colors[metric_choice][1:3],16)},{int(metric_colors[metric_choice][3:5],16)},{int(metric_colors[metric_choice][5:7],16)},0.08)",
            hovertemplate="%{x|%Y-%m}<br>" + metric_choice + ": %{y:,.0f}<extra></extra>"
        ))
        fig.update_layout(**PLOT_LAYOUT, height=320, title=dict(text=f"月度{metric_choice}趋势", font=dict(size=14)))
        st.plotly_chart(fig, use_container_width=True)

    # 地域分布
    st.markdown("### 🌍 地域分布")
    country = df.groupby("Country")["Revenue"].sum().sort_values(ascending=True).tail(10).reset_index()
    fig_c = go.Figure(go.Bar(
        x=country["Revenue"], y=country["Country"],
        orientation="h",
        marker=dict(
            color=country["Revenue"],
            colorscale=[[0, "#38bdf8"], [0.5, "#818cf8"], [1, "#c084fc"]],
            cornerradius=4,
        ),
        hovertemplate="%{y}<br>£%{x:,.0f}<extra></extra>"
    ))
    fig_c.update_layout(**PLOT_LAYOUT, height=350, title=dict(text="Top 10 市场收入", font=dict(size=14)),
                        yaxis=dict(showgrid=False), xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)"))
    st.plotly_chart(fig_c, use_container_width=True)

# ---------- TAB 2: 用户分层 ----------
with tab2:
    col_d1, col_d2 = st.columns(2)

    seg_colors = {s: COLORS[i] for i, s in enumerate(rfm["用户标签"].unique())}

    with col_d1:
        seg_count = rfm["用户标签"].value_counts()
        fig1 = go.Figure(go.Pie(
            labels=seg_count.index, values=seg_count.values,
            hole=0.55, marker=dict(colors=[seg_colors.get(s, "#666") for s in seg_count.index]),
            textinfo="percent", textfont=dict(size=10),
            hovertemplate="%{label}<br>%{value}人 (%{percent})<extra></extra>"
        ))
        fig1.update_layout(**PLOT_LAYOUT, height=380, title=dict(text="人数分布", font=dict(size=14)),
                           showlegend=True, legend=dict(font=dict(size=12, color="rgba(255,255,255,0.7)")))
        st.plotly_chart(fig1, use_container_width=True)

    with col_d2:
        seg_rev = rfm.groupby("用户标签")["Monetary"].sum().sort_values(ascending=False)
        fig2 = go.Figure(go.Pie(
            labels=seg_rev.index, values=seg_rev.values,
            hole=0.55, marker=dict(colors=[seg_colors.get(s, "#666") for s in seg_rev.index]),
            textinfo="percent", textfont=dict(size=10),
            hovertemplate="%{label}<br>£%{value:,.0f} (%{percent})<extra></extra>"
        ))
        fig2.update_layout(**PLOT_LAYOUT, height=380, title=dict(text="收入分布", font=dict(size=14)),
                           showlegend=True, legend=dict(font=dict(size=12, color="rgba(255,255,255,0.7)")))
        st.plotly_chart(fig2, use_container_width=True)

    # 气泡图
    st.markdown("### 用户群体定位矩阵")
    seg_summary = rfm.groupby("用户标签").agg(
        平均频次=("Frequency", "mean"),
        平均消费=("Monetary", "mean"),
        人数=("Recency", "size")
    ).reset_index()

    fig3 = go.Figure()
    for _, row in seg_summary.iterrows():
        color = seg_colors.get(row["用户标签"], "#666")
        fig3.add_trace(go.Scatter(
            x=[row["平均频次"]], y=[row["平均消费"]],
            mode="markers+text",
            marker=dict(size=row["人数"] / 20, color=color, opacity=0.5, line=dict(color=color, width=1)),
            text=[row["用户标签"]],
            textposition="top center",
            textfont=dict(size=9, color="rgba(255,255,255,0.6)"),
            name=row["用户标签"],
            hovertemplate=f"{row['用户标签']}<br>人数: {row['人数']}<br>频次: {row['平均频次']:.1f}<br>消费: £{row['平均消费']:,.0f}<extra></extra>"
        ))
    fig3.update_layout(**PLOT_LAYOUT, height=480, showlegend=False,
                        xaxis_title="平均购买频次 →", yaxis_title="平均消费金额 →",
                        title=dict(text="气泡大小 = 客户人数", font=dict(size=11, color="rgba(255,255,255,0.3)")))
    st.plotly_chart(fig3, use_container_width=True)

    # 群体画像卡片
    st.markdown("### 群体画像")
    seg_detail = rfm.groupby("用户标签").agg(
        人数=("Recency", "size"),
        平均R=("Recency", "mean"),
        平均F=("Frequency", "mean"),
        平均M=("Monetary", "mean"),
        总收入=("Monetary", "sum")
    ).round(1)
    seg_detail["收入占比"] = (seg_detail["总收入"] / seg_detail["总收入"].sum() * 100).round(1)
    seg_detail = seg_detail.sort_values("总收入", ascending=False)

    card_cols = st.columns(4)
    for i, (name, row) in enumerate(seg_detail.iterrows()):
        color = seg_colors.get(name, "#666")
        with card_cols[i % 4]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
                border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;
                box-shadow: inset 0 1px 0 {color}15, 0 0 30px {color}06;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: {color};">{name}</div>
                    <div style="font-size: 0.65rem; padding: 2px 8px; border-radius: 4px;
                        background: {color}15; color: {color}; font-weight: 600;">{int(row['人数'])}</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;">
                    <div>
                        <div style="font-size: 0.55rem; color: rgba(255,255,255,0.2); letter-spacing: 0.05em;">R</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: rgba(255,255,255,0.7);">{row['平均R']:.0f}天</div>
                    </div>
                    <div>
                        <div style="font-size: 0.55rem; color: rgba(255,255,255,0.2); letter-spacing: 0.05em;">F</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: rgba(255,255,255,0.7);">{row['平均F']:.1f}次</div>
                    </div>
                    <div>
                        <div style="font-size: 0.55rem; color: rgba(255,255,255,0.2); letter-spacing: 0.05em;">M</div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: rgba(255,255,255,0.7);">£{row['平均M']:,.0f}</div>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.55rem; color: rgba(255,255,255,0.2); margin-bottom: 3px;">
                        <span>收入占比</span><span>{row['收入占比']}%</span>
                    </div>
                    <div style="width: 100%; height: 4px; background: rgba(255,255,255,0.04); border-radius: 2px;">
                        <div style="height: 100%; border-radius: 2px; background: {color}; width: {min(row['收入占比'] * 1.4, 100)}%; opacity: 0.6;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ---------- TAB 3: 策略建议 ----------
with tab3:
    # 核心原则
    st.markdown("""
    <div style="padding: 18px 24px; border-radius: 14px;
        background: linear-gradient(135deg, rgba(129,140,248,0.08), rgba(192,132,252,0.06));
        border: 1px solid rgba(129,140,248,0.12); margin-bottom: 20px;">
        <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">◆ 核心原则</div>
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5); line-height: 1.7;">
            将 <span style="color: #c4b5fd; font-weight: 700;">80%</span> 运营资源集中于 P0—P2。
            这 <span style="color: #c4b5fd; font-weight: 700;">2,502</span> 名客户覆盖了
            <span style="color: #c4b5fd; font-weight: 700;">87.9%</span> 的总收入。
        </div>
    </div>
    """, unsafe_allow_html=True)

    strategies = [
        ("P0", "🚨", "流失风险高价值", 227, "#f87171", "最高", "本周行动",
         ["启动3封递进召回邮件序列", "发放专属高额优惠券（比常规高50%）", "抽样电话回访了解流失原因"], "30天召回率", ">15%"),
        ("P1", "💎", "高价值忠诚客户", 1300, "#818cf8", "高", "本月上线",
         ["建立VIP专属权益体系", "新品提前48h开放+个性化推荐", "上线消费积分与年度回馈"], "季度留存率", ">95%"),
        ("P2", "🌱", "潜力客户", 975, "#34d399", "中高", "本月启动",
         ["消费里程碑激励（满£5K解锁VIP）", "高价值未购品类定向推荐", "限时高客单价优惠券"], "高价值转化率", ">8%"),
        ("P3", "👋", "新客户", 443, "#38bdf8", "中", "持续运营",
         ["购后7天新手引导邮件", "14天内二单享9折", "推荐低门槛高复购商品"], "30天二购率", ">25%"),
        ("P4", "💤", "沉睡客户", 1523, "#64748b", "低", "分批测试",
         ["随机20%发召回邮件测响应", "推送清仓促销与节日活动", "连续3次无响应则降频"], "激活率", ">3%"),
    ]

    for p, icon, seg, n, color, roi, urgency, actions, metric, target in strategies:
        actions_html = "".join([f'<div style="display:flex;align-items:flex-start;gap:8px;font-size:0.78rem;color:rgba(255,255,255,0.5);line-height:1.5;"><span style="color:{color};font-size:0.5rem;margin-top:5px;">●</span>{a}</div>' for a in actions])
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.018); border: 1px solid rgba(255,255,255,0.05);
            border-left: 3px solid {color}; border-radius: 14px; padding: 20px 24px; margin-bottom: 12px;
            box-shadow: inset 0 1px 0 {color}15, 0 0 30px {color}06;">
            <div style="display: grid; grid-template-columns: 60px 1fr 160px; gap: 20px; align-items: start;">
                <div style="text-align: center;">
                    <div style="font-size: 1.6rem;">{icon}</div>
                    <div style="font-size: 0.8rem; font-weight: 800; color: {color}; margin-top: 6px;
                        padding: 3px 0; border-radius: 6px; background: {color}12;
                        font-family: 'JetBrains Mono', monospace;">{p}</div>
                </div>
                <div>
                    <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 1rem; font-weight: 700;">{seg}</span>
                        <span style="font-size: 0.7rem; color: rgba(255,255,255,0.3);">{n} 人</span>
                        <span style="font-size: 0.6rem; padding: 2px 8px; border-radius: 4px;
                            background: {color}12; color: {color}; font-weight: 600;">{urgency}</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">{actions_html}</div>
                </div>
                <div style="padding: 14px 16px; border-radius: 10px; background: rgba(255,255,255,0.02);
                    border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.6rem; color: rgba(255,255,255,0.25); letter-spacing: 0.05em; margin-bottom: 6px;">核心指标</div>
                    <div style="font-size: 0.8rem; font-weight: 600; color: rgba(255,255,255,0.6); margin-bottom: 8px;">{metric}</div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 0.65rem; color: rgba(255,255,255,0.25);">目标</span>
                        <span style="font-size: 0.95rem; font-weight: 800; color: {color};
                            font-family: 'JetBrains Mono', monospace;">{target}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 6px;">
                        <span style="font-size: 0.65rem; color: rgba(255,255,255,0.25);">预期ROI</span>
                        <span style="font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.5);">{roi}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # A/B测试
    st.markdown("### 🧪 建议的 A/B 测试方案")
    ab_cols = st.columns(3)
    ab_tests = [
        ("召回邮件序列", "流失风险高价值", "#f87171", "无干预", "3封递进邮件+专属券", "30天复购率", "4周"),
        ("阶梯消费激励", "潜力客户", "#34d399", "常规促销", "累计消费里程碑奖励", "60天消费额变化", "8周"),
        ("新客二单转化", "新客户", "#38bdf8", "无干预", "14天内二单9折", "30天二购率", "4周"),
    ]
    for i, (name, tgt, color, ctrl, exp, obs, dur) in enumerate(ab_tests):
        with ab_cols[i]:
            st.markdown(f"""
            <div style="padding: 16px 18px; border-radius: 12px; background: rgba(255,255,255,0.015);
                border: 1px solid {color}15; height: 220px;">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 12px;">
                    <div style="width: 3px; height: 14px; border-radius: 2px; background: {color};"></div>
                    <div style="font-size: 0.82rem; font-weight: 700;">{name}</div>
                </div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.3); line-height: 2.0;">
                    <div style="display:flex;justify-content:space-between;"><span>对象</span><span style="color:rgba(255,255,255,0.45);">{tgt}</span></div>
                    <div style="display:flex;justify-content:space-between;"><span>对照组</span><span style="color:rgba(255,255,255,0.45);">{ctrl}</span></div>
                    <div style="display:flex;justify-content:space-between;"><span>实验组</span><span style="color:rgba(255,255,255,0.45);">{exp}</span></div>
                    <div style="display:flex;justify-content:space-between;"><span>观测</span><span style="color:{color};font-weight:600;">{obs}</span></div>
                    <div style="display:flex;justify-content:space-between;"><span>周期</span><span style="color:rgba(255,255,255,0.45);">{dur}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===== FOOTER =====
st.markdown("""
<div style="text-align: center; padding: 20px 0; margin-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.03);
    font-size: 0.65rem; color: rgba(255,255,255,0.15); letter-spacing: 0.04em;">
    E-Commerce User Behavior Analysis · UCI Online Retail II · RFM + K-Means Clustering
</div>
""", unsafe_allow_html=True)
