# optimizer_practice/shortest-path/graph_utils.py

import math
import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

# ---------------------------------------------------------------------------
# フォント設定
# ---------------------------------------------------------------------------

def _setup_japanese_font():
    import glob
    from matplotlib import font_manager
    import matplotlib as mpl

    font_manager._load_fontmanager(try_read_cache=False)

    for font in font_manager.fontManager.ttflist:
        if 'Noto' in font.name and 'CJK' in font.name:
            mpl.rcParams['font.family'] = font.name
            mpl.rcParams['font.sans-serif'] = [font.name]
            return

    patterns = [
        '/usr/share/fonts/**/Noto*CJK*.ttc',
        '/usr/share/fonts/**/Noto*CJK*.otf',
    ]
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        if files:
            font_manager.fontManager.addfont(files[0])
            prop = font_manager.FontProperties(fname=files[0])
            mpl.rcParams['font.family'] = prop.get_name()
            mpl.rcParams['font.sans-serif'] = [prop.get_name()]
            return

    # Mac環境
    candidates = ["Hiragino Sans", "Hiragino Maru Gothic Pro"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for font in candidates:
        if font in available:
            mpl.rcParams['font.family'] = font
            return

_setup_japanese_font()


# ---------------------------------------------------------------------------
# グラフ生成
# ---------------------------------------------------------------------------

def generate_map_graph(
    n_nodes: int = 15,
    connection_radius: float = 0.35,
    seed: int = 42,
) -> tuple[dict[int, list[tuple[int, float]]], dict[int, tuple[float, float]]]:
    """
    地図風のランダムグラフを生成する。

    各ノードをランダムな座標に配置し、一定距離内のノード同士を
    無向辺で接続する。重みはユークリッド距離。

    Parameters
    ----------
    n_nodes : int
        ノード数
    connection_radius : float
        この距離以内のノード同士を接続する（座標は0〜1の範囲）
    seed : int
        乱数シード

    Returns
    -------
    graph : dict[int, list[tuple[int, float]]]
        隣接リスト（無向グラフを双方向で表現）
    pos : dict[int, tuple[float, float]]
        各ノードの座標
    """
    random.seed(seed)

    # ノードの座標をランダム生成
    pos = {i: (random.random(), random.random()) for i in range(n_nodes)}

    # 隣接リスト初期化
    graph: dict[int, list[tuple[int, float]]] = {i: [] for i in range(n_nodes)}

    # 一定距離以内のノード同士を双方向接続
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            dist = _euclidean(pos[i], pos[j])
            if dist <= connection_radius:
                graph[i].append((j, dist))
                graph[j].append((i, dist))

    return graph, pos


def generate_negative_graph() -> tuple[
    dict[int, list[tuple[int, float]]],
    dict[int, tuple[float, float]],
]:
    """
    負の重みを含む固定グラフを生成する。

    ダイクストラが誤った結果を返し、Bellman-Fordが正しく解けることを
    示すために設計されたグラフ。

    Returns
    -------
    graph : dict[int, list[tuple[int, float]]]
    pos : dict[int, tuple[float, float]]
    """
    graph = {
        0: [(1, 3.0), (2, 5.0)],
        1: [(3, 5.0)],
        2: [(1, -3.0)],
        3: [(4, 2.0)],
        4: [],
    }
    pos = {
        0: (0.0, 0.5),
        1: (0.4, 0.8),
        2: (0.4, 0.2),
        3: (0.7, 0.8),
        4: (1.0, 0.5),
    }
    return graph, pos


def generate_negative_cycle_graph() -> tuple[
    dict[int, list[tuple[int, float]]],
    dict[int, tuple[float, float]],
]:
    """
    負閉路を含むグラフを生成する。
    """
    graph = {
        0: [(1, 2.0)],
        1: [(2, -4.0)],
        2: [(3, 1.0), (1, 1.0)],  # 1→2→1 で負閉路
        3: [],
    }
    pos = {
        0: (0.0, 0.5),
        1: (0.35, 0.8),
        2: (0.65, 0.8),
        3: (1.0, 0.5),
    }
    return graph, pos


# ---------------------------------------------------------------------------
# グラフ可視化
# ---------------------------------------------------------------------------

def draw_graph(
    graph: dict[int, list[tuple[int, float]]],
    pos: dict[int, tuple[float, float]],
    path: list[int] | None = None,
    visited: list[int] | None = None,
    start: int | None = None,
    goal: int | None = None,
    title: str = "",
    show_weights: bool = True,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))

    G = nx.MultiDiGraph()
    for u in graph:
        G.add_node(u)
        for v, w in graph[u]:
            G.add_edge(u, v, weight=round(w, 3))

    # 双方向辺が存在するペアを検出（曲線にする必要がある辺）
    edge_set = {(u, v) for u, v, _ in G.edges(keys=True)}
    bidirectional = {(u, v) for (u, v) in edge_set if (v, u) in edge_set}

    path_edges = set()
    if path and len(path) >= 2:
        path_edges = {(path[i], path[i + 1]) for i in range(len(path) - 1)}

    # ノードの色
    node_colors = []
    for node in G.nodes():
        if node == start:
            node_colors.append("#2ecc71")
        elif node == goal:
            node_colors.append("#e74c3c")
        elif visited and node in visited:
            node_colors.append("#aed6f1")
        else:
            node_colors.append("#d5d8dc")

    nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color=node_colors, node_size=500)
    nx.draw_networkx_labels(G, pos=pos, ax=ax, font_size=9)

    # 辺を直線・曲線に分けて描画
    straight_edges = [(u, v) for u, v, _ in G.edges(keys=True) if (u, v) not in bidirectional]
    curved_edges = [(u, v) for u, v, _ in G.edges(keys=True) if (u, v) in bidirectional]

    def edge_colors_widths(edges):
        colors, widths = [], []
        for u, v in edges:
            if (u, v) in path_edges:
                colors.append("#e67e22")
                widths.append(3.0)
            else:
                colors.append("#bdc3c7")
                widths.append(1.0)
        return colors, widths

    if straight_edges:
        sc, sw = edge_colors_widths(straight_edges)
        nx.draw_networkx_edges(
            G, pos=pos, ax=ax,
            edgelist=straight_edges,
            edge_color=sc, width=sw,
            arrows=True, arrowsize=12,
            connectionstyle="arc3,rad=0.0",
        )

    if curved_edges:
        cc, cw = edge_colors_widths(curved_edges)
        nx.draw_networkx_edges(
            G, pos=pos, ax=ax,
            edgelist=curved_edges,
            edge_color=cc, width=cw,
            arrows=True, arrowsize=12,
            connectionstyle="arc3,rad=0.2",
        )

    if show_weights:
        # 辺ラベルは直線・曲線で分けてrad指定
        straight_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True) if (u, v) not in bidirectional}
        curved_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True) if (u, v) in bidirectional}

        if straight_labels:
            nx.draw_networkx_edge_labels(
                G, pos=pos, edge_labels=straight_labels, font_size=7, ax=ax
            )
        if curved_labels:
            nx.draw_networkx_edge_labels(
                G, pos=pos, edge_labels=curved_labels, font_size=7, ax=ax,
                label_pos=0.3,
            )

    legend = [
        mpatches.Patch(color="#2ecc71", label="Start"),
        mpatches.Patch(color="#e74c3c", label="Goal"),
        mpatches.Patch(color="#aed6f1", label="Explored"),
        mpatches.Patch(color="#e67e22", label="Shortest path"),
    ]
    ax.legend(handles=legend, loc="upper left", fontsize=7)
    ax.set_title(title, fontsize=11)
    ax.axis("off")

    return ax


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------

def _euclidean(
    p1: tuple[float, float],
    p2: tuple[float, float],
) -> float:
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def is_connected(
    graph: dict[int, list[tuple[int, float]]],
    start: int,
    goal: int,
) -> bool:
    """BFSでstartからgoalに到達可能か確認する"""
    visited = set()
    queue = [start]
    while queue:
        node = queue.pop(0)
        if node == goal:
            return True
        if node in visited:
            continue
        visited.add(node)
        for v, _ in graph.get(node, []):
            queue.append(v)
    return False