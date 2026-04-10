# optimizer_practice/shortest-path/solvers/dijkstra.py

import heapq
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DijkstraResult:
    """ダイクストラ法の実行結果"""
    distance: float                    # 最短距離
    path: list[int]                    # 最短経路（ノードID列）
    visited_order: list[int]           # 確定した順番（可視化用）
    explored_count: int                # 探索ノード数（A*との比較用）
    elapsed_ms: float                  # 計算時間（ミリ秒）
    found: bool                        # 経路が存在したか


def dijkstra(
    graph: dict[int, list[tuple[int, float]]],
    start: int,
    goal: int,
) -> DijkstraResult:
    """
    ダイクストラ法による最短経路探索。

    Parameters
    ----------
    graph : dict[int, list[tuple[int, float]]]
        隣接リスト表現。graph[u] = [(v, weight), ...] 。有向グラフ。
    start : int
        始点ノードID
    goal : int
        終点ノードID

    Returns
    -------
    DijkstraResult
        最短経路・距離・探索情報

    Notes
    -----
    計算量: O((V + E) log V)
    正の重みのみ対応。負の重みがある場合はBellman-Fordを使うこと。
    """
    t0 = time.perf_counter()

    # --- 初期化 ---
    INF = float("inf")
    dist: dict[int, float] = {node: INF for node in graph}
    dist[start] = 0.0

    prev: dict[int, Optional[int]] = {node: None for node in graph}

    # 確定済みノードの集合
    confirmed: set[int] = set()

    # 訪問順記録（可視化用）
    visited_order: list[int] = []

    # 優先度付きキュー：(距離, ノードID)
    # heapq は最小ヒープ。タプルの第1要素で比較される。
    pq: list[tuple[float, int]] = [(0.0, start)]

    # --- メインループ ---
    while pq:
        d, u = heapq.heappop(pq)

        # すでに確定済み（より短い経路で処理済み）ならスキップ
        # ※ heapq は要素の更新ができないため、古いエントリが残る
        #    dist[u] < d ならそのエントリは無効
        if u in confirmed:
            continue

        confirmed.add(u)
        visited_order.append(u)

        # ゴール到達で早期終了（全ノード確定まで待たなくてよい）
        if u == goal:
            break

        # --- 隣接ノードの緩和（Relaxation）---
        for v, weight in graph.get(u, []):
            if v in confirmed:
                continue
            new_dist = d + weight
            if new_dist < dist.get(v, INF):
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # --- 経路復元 ---
    if dist.get(goal, INF) == INF:
        return DijkstraResult(
            distance=INF,
            path=[],
            visited_order=visited_order,
            explored_count=len(confirmed),
            elapsed_ms=elapsed_ms,
            found=False,
        )

    path = _reconstruct_path(prev, start, goal)

    return DijkstraResult(
        distance=dist[goal],
        path=path,
        visited_order=visited_order,
        explored_count=len(confirmed),
        elapsed_ms=elapsed_ms,
        found=True,
    )


def _reconstruct_path(
    prev: dict[int, Optional[int]],
    start: int,
    goal: int,
) -> list[int]:
    """prev配列をたどって経路を復元する"""
    path = []
    node: Optional[int] = goal
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    # startから始まっていない場合は経路なし
    if path[0] != start:
        return []
    return path

if __name__ == "__main__":
    graph = {
        0: [(1, 1.0), (2, 4.0)],
        1: [(2, 1.0), (3, 2.0)],
        2: [(3, 1.0)],
        3: [],
    }

    result = dijkstra(graph, start=0, goal=3)

    print(f"最短距離: {result.distance}")        # → 3.0
    print(f"最短経路: {result.path}")            # → [0, 1, 2, 3] or [0, 1, 3]
    print(f"確定順: {result.visited_order}")     # → [0, 1, 2, 3]
    print(f"探索数: {result.explored_count}")    # → 4
    print(f"計算時間: {result.elapsed_ms:.4f} ms")