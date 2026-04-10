# optimizer_practice/shortest-path/solvers/astar.py

import heapq
import math
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class AStarResult:
    """A*法の実行結果"""
    distance: float
    path: list[int]
    visited_order: list[int]
    explored_count: int
    elapsed_ms: float
    found: bool


def astar(
    graph: dict[int, list[tuple[int, float]]],
    start: int,
    goal: int,
    heuristic: Callable[[int, int], float],
) -> AStarResult:
    """
    A*法による最短経路探索。

    Parameters
    ----------
    graph : dict[int, list[tuple[int, float]]]
        隣接リスト表現。graph[u] = [(v, weight), ...] 。有向グラフ。
    start : int
        始点ノードID
    goal : int
        終点ノードID
    heuristic : Callable[[int, int], float]
        heuristic(u, goal) → ノードuからゴールまでの推定距離。
        admissible（実際の距離を超えない）であること。

    Returns
    -------
    AStarResult

    Notes
    -----
    計算量: O((V + E) log V)  ※ h=0 のときダイクストラと同一
    heuristic が admissible であれば最適解を保証。
    """
    t0 = time.perf_counter()

    INF = float("inf")
    g: dict[int, float] = {node: INF for node in graph}
    g[start] = 0.0

    prev: dict[int, Optional[int]] = {node: None for node in graph}
    confirmed: set[int] = set()
    visited_order: list[int] = []

    # 優先度は f = g + h
    pq: list[tuple[float, int]] = [(heuristic(start, goal), start)]

    while pq:
        f, u = heapq.heappop(pq)

        if u in confirmed:
            continue

        confirmed.add(u)
        visited_order.append(u)

        if u == goal:
            break

        for v, weight in graph.get(u, []):
            if v in confirmed:
                continue
            new_g = g[u] + weight
            if new_g < g.get(v, INF):
                g[v] = new_g
                f_new = new_g + heuristic(v, goal)
                prev[v] = u
                heapq.heappush(pq, (f_new, v))

    elapsed_ms = (time.perf_counter() - t0) * 1000

    if g.get(goal, INF) == INF:
        return AStarResult(
            distance=INF,
            path=[],
            visited_order=visited_order,
            explored_count=len(confirmed),
            elapsed_ms=elapsed_ms,
            found=False,
        )

    path = _reconstruct_path(prev, start, goal)

    return AStarResult(
        distance=g[goal],
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
    path = []
    node: Optional[int] = goal
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    if path[0] != start:
        return []
    return path


def euclidean_heuristic(
    pos: dict[int, tuple[float, float]],
) -> Callable[[int, int], float]:
    """
    ユークリッド距離ヒューリスティクスを返すファクトリ関数。

    Parameters
    ----------
    pos : dict[int, tuple[float, float]]
        各ノードの座標 {node_id: (x, y)}

    Returns
    -------
    Callable[[int, int], float]
        heuristic(u, goal) → ユークリッド距離

    Notes
    -----
    座標系の単位とグラフの重みの単位が一致している必要がある。
    地図の重みをユークリッド距離で設定すれば admissible を満たす。
    """
    def h(u: int, goal: int) -> float:
        x1, y1 = pos[u]
        x2, y2 = pos[goal]
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return h

if __name__ == "__main__":
    # ノードに座標を付与
    pos = {
        0: (0.0, 0.0),
        1: (1.0, 0.0),
        2: (1.0, 1.0),
        3: (2.0, 0.0),
    }

    graph = {
        0: [(1, 1.0), (2, 4.0)],
        1: [(2, 1.0), (3, 2.0)],
        2: [(3, 1.0)],
        3: [],
    }

    h = euclidean_heuristic(pos)
    result = astar(graph, start=0, goal=3, heuristic=h)

    print(f"最短距離: {result.distance}")
    print(f"最短経路: {result.path}")
    print(f"確定順:   {result.visited_order}")
    print(f"探索数:   {result.explored_count}")
    print(f"計算時間: {result.elapsed_ms:.4f} ms")