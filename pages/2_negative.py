# optimizer_practice/shortest-path/pages/2_negative.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import matplotlib.pyplot as plt

from graph_utils import (
    generate_negative_graph,
    generate_negative_cycle_graph,
    draw_graph,
)
from solvers.dijkstra import dijkstra
from solvers.bellman_ford import bellman_ford

st.set_page_config(page_title="Bellman-Ford", layout="wide")
st.title("⚠️ Bellman-Ford：負の重みへの対応")

# ---------------------------------------------------------------------------
# セクション1：ダイクストラの失敗 vs Bellman-Fordの正解
# ---------------------------------------------------------------------------
st.subheader("① 負の重みグラフ：Dijkstra vs Bellman-Ford")
st.markdown("""
負の重みを含むグラフでは、Dijkstraは誤った結果を返すことがあります。  
Bellman-Fordは負の重みに対応し、正しい最短経路を求めます。
""")

graph_neg, pos_neg = generate_negative_graph()
start, goal = 0, 4

result_d = dijkstra(graph_neg, start=start, goal=goal)
result_b = bellman_ford(graph_neg, start=start, goal=goal)

# メトリクス
col1, col2 = st.columns(2)
with col1:
    st.error("**Dijkstra（負の重みに非対応）**")
    st.metric("最短距離", f"{result_d.distance:.1f}")
    st.write(f"経路: {' → '.join(map(str, result_d.path))}")
with col2:
    st.success("**Bellman-Ford（負の重みに対応）**")
    st.metric("最短距離", f"{result_b.distance:.1f}")
    st.write(f"経路: {' → '.join(map(str, result_b.path))}")

# 可視化
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

draw_graph(
    graph_neg, pos_neg,
    path=result_d.path,
    visited=result_d.visited_order,
    start=start, goal=goal,
    title=f"Dijkstra（距離: {result_d.distance:.1f}）※誤り",
    show_weights=True,
    ax=ax1,
)
draw_graph(
    graph_neg, pos_neg,
    path=result_b.path,
    visited=result_b.visited_order,
    start=start, goal=goal,
    title=f"Bellman-Ford（距離: {result_b.distance:.1f}）✓正しい",
    show_weights=True,
    ax=ax2,
)

plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# ---------------------------------------------------------------------------
# セクション2：負閉路の検出
# ---------------------------------------------------------------------------
st.divider()
st.subheader("② 負閉路の検出")
st.markdown("""
負閉路（合計重みが負になる閉路）が存在すると最短距離が `-∞` に発散します。  
Bellman-Fordはこれを検出できます。
""")

graph_cycle, pos_cycle = generate_negative_cycle_graph()
result_c = bellman_ford(graph_cycle, start=0, goal=3)

if result_c.has_negative_cycle:
    st.error("⚠️ 負閉路を検出しました。最短距離は定義できません。")
else:
    st.success(f"負閉路なし。最短距離: {result_c.distance:.1f}")

fig2, ax = plt.subplots(figsize=(6, 4))
draw_graph(
    graph_cycle, pos_cycle,
    start=0, goal=3,
    title="負閉路を含むグラフ（1→2→1 で負閉路）",
    show_weights=True,
    ax=ax,
)
plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)