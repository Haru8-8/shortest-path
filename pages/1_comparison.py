# optimizer_practice/shortest-path/pages/1_comparison.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import matplotlib.pyplot as plt

from graph_utils import generate_map_graph, draw_graph, is_connected
from solvers.dijkstra import dijkstra
from solvers.astar import astar, euclidean_heuristic

st.set_page_config(page_title="Dijkstra vs A*", layout="wide")
st.title("📊 Dijkstra vs A* 比較")

# ---------------------------------------------------------------------------
# サイドバー：パラメータ設定
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("グラフ設定")
    n_nodes = st.slider("ノード数", min_value=10, max_value=30, value=15)
    radius = st.slider("接続半径", min_value=0.2, max_value=0.6, value=0.35, step=0.05)
    seed = st.number_input("シード値", min_value=0, max_value=999, value=42)

    st.header("経路設定")
    start_node = st.number_input("始点ノード", min_value=0, max_value=n_nodes - 1, value=0)
    goal_node = st.number_input("終点ノード", min_value=0, max_value=n_nodes - 1, value=n_nodes - 1)

# ---------------------------------------------------------------------------
# グラフ生成
# ---------------------------------------------------------------------------
graph, pos = generate_map_graph(n_nodes=n_nodes, connection_radius=radius, seed=seed)

if start_node == goal_node:
    st.warning("始点と終点が同じです。異なるノードを選択してください。")
    st.stop()

if not is_connected(graph, start_node, goal_node):
    st.warning(f"ノード {start_node} から {goal_node} への経路が存在しません。シード値や接続半径を変更してください。")
    st.stop()

# ---------------------------------------------------------------------------
# アルゴリズム実行
# ---------------------------------------------------------------------------
result_d = dijkstra(graph, start=start_node, goal=goal_node)

h = euclidean_heuristic(pos)
result_a = astar(graph, start=start_node, goal=goal_node, heuristic=h)

# ---------------------------------------------------------------------------
# 比較メトリクス
# ---------------------------------------------------------------------------
st.subheader("比較結果")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("最短距離（Dijkstra）", f"{result_d.distance:.4f}")
    st.metric("最短距離（A*）", f"{result_a.distance:.4f}")
with col2:
    st.metric("探索ノード数（Dijkstra）", result_d.explored_count)
    st.metric("探索ノード数（A*）", result_a.explored_count,
              delta=result_a.explored_count - result_d.explored_count,
              delta_color="inverse")
with col3:
    st.metric("計算時間（Dijkstra）", f"{result_d.elapsed_ms:.4f} ms")
    st.metric("計算時間（A*）", f"{result_a.elapsed_ms:.4f} ms")

st.caption("探索ノード数のdeltaはDijkstraとの差。マイナスほどA*が効率的。")

# ---------------------------------------------------------------------------
# グラフ可視化
# ---------------------------------------------------------------------------
st.subheader("探索の可視化")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

draw_graph(
    graph, pos,
    path=result_d.path,
    visited=result_d.visited_order,
    start=start_node,
    goal=goal_node,
    title=f"Dijkstra（探索数: {result_d.explored_count}）",
    show_weights=False,
    ax=ax1,
)

draw_graph(
    graph, pos,
    path=result_a.path,
    visited=result_a.visited_order,
    start=start_node,
    goal=goal_node,
    title=f"A*（探索数: {result_a.explored_count}）",
    show_weights=False,
    ax=ax2,
)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ---------------------------------------------------------------------------
# 経路詳細
# ---------------------------------------------------------------------------
with st.expander("経路詳細"):
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Dijkstra**")
        st.write(f"経路: {' → '.join(map(str, result_d.path))}")
        st.write(f"確定順: {result_d.visited_order}")
    with c2:
        st.write("**A\***")
        st.write(f"経路: {' → '.join(map(str, result_a.path))}")
        st.write(f"確定順: {result_a.visited_order}")