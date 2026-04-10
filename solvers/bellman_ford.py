# optimizer_practice/shortest-path/solvers/bellman_ford.py

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class BellmanFordResult:
    """Bellman-Ford法の実行結果"""
    distance: float
    path: list[int]
    visited_order: list[int]   # 各イテレーションで更新されたノード（可視化用）
    explored_count: int        # 総緩和試行回数
    elapsed_ms: float
    found: bool
    has_negative_cycle: bool   # 負閉路の有無


def bellman_ford(
    graph: dict[int, list[tuple[int, float]]],
    start: int,
    goal: int,
) -> BellmanFordResult:
    """
    Bellman-Ford法による最短経路探索。

    Parameters
    ----------
    graph : dict[int, list[tuple[int, float]]]
        隣接リスト表現。graph[u] = [(v, weight), ...] 。有向グラフ。
        負の重みを含んでもよい。
    start : int
        始点ノードID
    goal : int
        終点ノードID

    Returns
    -------
    BellmanFordResult

    Notes
    -----
    計算量: O(V * E)
    負の重みに対応。負閉路が存在する場合は has_negative_cycle=True を返す。
    """
    t0 = time.perf_counter()

    nodes = list(graph.keys())
    V = len(nodes)
    INF = float("inf")

    dist: dict[int, float] = {node: INF for node in nodes}
    dist[start] = 0.0
    prev: dict[int, Optional[int]] = {node: None for node in nodes}

    # 可視化用：各イテレーションで更新されたノードを記録
    visited_order: list[int] = []
    explored_count = 0

    # --- V-1 回の全辺緩和 ---
    for _ in range(V - 1):
        updated = False
        for u in nodes:
            if dist[u] == INF:
                continue  # startから未到達なら緩和不要
            for v, weight in graph.get(u, []):
                explored_count += 1
                new_dist = dist[u] + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    updated = True
                    if v not in visited_order:
                        visited_order.append(v)

        # 1イテレーションで更新がなければ早期終了
        if not updated:
            break

    # --- 負閉路チェック（V回目の緩和）---
    has_negative_cycle = False
    for u in nodes:
        if dist[u] == INF:
            continue
        for v, weight in graph.get(u, []):
            if dist[u] + weight < dist[v]:
                has_negative_cycle = True
                break
        if has_negative_cycle:
            break

    elapsed_ms = (time.perf_counter() - t0) * 1000

    if has_negative_cycle:
        return BellmanFordResult(
            distance=-INF,
            path=[],
            visited_order=visited_order,
            explored_count=explored_count,
            elapsed_ms=elapsed_ms,
            found=False,
            has_negative_cycle=True,
        )

    if dist.get(goal, INF) == INF:
        return BellmanFordResult(
            distance=INF,
            path=[],
            visited_order=visited_order,
            explored_count=explored_count,
            elapsed_ms=elapsed_ms,
            found=False,
            has_negative_cycle=False,
        )

    path = _reconstruct_path(prev, start, goal)

    return BellmanFordResult(
        distance=dist[goal],
        path=path,
        visited_order=visited_order,
        explored_count=explored_count,
        elapsed_ms=elapsed_ms,
        found=True,
        has_negative_cycle=False,
    )


def _reconstruct_path(
    prev: dict[int, Optional[int]],
    start: int,
    goal: int,
) -> list[int]:
    path = []
    node: Optional[int] = goal
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    if path[0] != start:
        return []
    return path

if __name__ == "__main__":
    # ① 負の重みあり・正常ケース
    graph_neg = {
        0: [(1, 3.0), (2, 5.0)],
        1: [(3, 5.0)],
        2: [(1, -3.0)],
        3: [],
    }

    result = bellman_ford(graph_neg, start=0, goal=3)
    print(f"① 最短距離: {result.distance}")   # → 2.0
    print(f"   最短経路: {result.path}")       # → [0, 2, 1, 3]

    # ② ダイクストラが失敗するケース（同グラフでダイクストラを試す）
    from dijkstra import dijkstra
    result_d = dijkstra(graph_neg, start=0, goal=3)
    print(f"② ダイクストラ: {result_d.distance}")  # → 3.0（誤った答え）
    print(f"   最短経路: {result_d.path}")           # → [0, 1, 3]（誤り）

    # ③ 負閉路あり
    graph_cycle = {
        0: [(1, 1.0)],
        1: [(2, -3.0)],
        2: [(1, 1.0)],   # 1→2→1 で -2 ずつ減り続ける
        3: [],
    }
    result_c = bellman_ford(graph_cycle, start=0, goal=3)
    print(f"③ 負閉路: {result_c.has_negative_cycle}")  # → True