# optimizer_practice/shortest-path/app.py

import streamlit as st

st.set_page_config(
    page_title="最短経路アルゴリズム比較",
    page_icon="🗺️",
    layout="wide",
)

st.title("🗺️ 最短経路アルゴリズム比較")
st.markdown("""
重み付き有向グラフ上での最短経路探索アルゴリズムを比較・可視化します。

| ページ | 内容 |
|---|---|
| **Dijkstra vs A\*** | 正の重みグラフで探索ノード数・計算時間を比較 |
| **Bellman-Ford** | 負の重みグラフでダイクストラの失敗とBellman-Fordの正しい結果を比較 |
""")

st.divider()
st.subheader("手法の使い分け")
st.markdown("""
| 手法 | 重みの条件 | 最適性 | 計算量 | 特徴 |
|---|---|---|---|---|
| Dijkstra | 非負のみ | ✅ | O((V+E) log V) | 高速・実用的 |
| A* | 非負のみ | ✅ | O((V+E) log V) | ヒューリスティクスで探索削減 |
| Bellman-Ford | 負の重みも可 | ✅ | O(VE) | 負閉路検出も可能 |
""")