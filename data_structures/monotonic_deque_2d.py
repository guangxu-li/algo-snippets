from collections.abc import Sequence
from dataclasses import dataclass
import random

try:
    from data_structures.monotonic_deque import (
        longest_valid_range,
        sliding_max,
        sliding_min,
    )
except ModuleNotFoundError:
    from monotonic_deque import longest_valid_range, sliding_max, sliding_min


@dataclass(frozen=True)
class Rect:
    top: int
    left: int
    height: int
    width: int

    @property
    def area(self) -> int:
        return self.height * self.width


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*matrix)]


def sliding_max_2d(grid: Sequence[Sequence[int]], h: int, w: int) -> list[list[int]]:
    """
    Return max of every h x w submatrix.
    """
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])

    if h > rows or w > cols:
        return []

    row_max: list[list[int]] = [sliding_max(row, w) for row in grid]
    col_max: list[list[int]] = [sliding_max(col, h) for col in transpose(row_max)]

    return transpose(col_max)


def sliding_min_2d(grid: Sequence[Sequence[int]], h: int, w: int) -> list[list[int]]:
    """
    Return min of every h x w submatrix.
    """
    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])

    if h > rows or w > cols:
        return []

    row_min: list[list[int]] = [sliding_min(row, w) for row in grid]
    col_min: list[list[int]] = [sliding_min(col, h) for col in transpose(row_min)]

    return transpose(col_min)


def best_rect_fixed_width(
    grid: Sequence[Sequence[int]],
    width: int,
    limit: int,
) -> Rect | None:
    """
    Find max-area rectangle with:
        exact width = width
        variable height
        max(rect) - min(rect) <= limit
    """
    if not grid or not grid[0]:
        return None

    rows = len(grid)
    cols = len(grid[0])

    if width > cols:
        return None

    row_max = [sliding_max(row, width) for row in grid]
    row_min = [sliding_min(row, width) for row in grid]

    best: Rect | None = None

    for left in range(cols - width + 1):
        max_values = [row_max[r][left] for r in range(rows)]
        min_values = [row_min[r][left] for r in range(rows)]

        height, top, _ = longest_valid_range(max_values, min_values, limit)

        rect = Rect(top=top, left=left, height=height, width=width)

        if best is None or rect.area > best.area:
            best = rect

    return best


def best_rect_fixed_height(
    grid: Sequence[Sequence[int]],
    height: int,
    limit: int,
) -> Rect | None:
    """
    Find max-area rectangle with:
        exact height = height
        variable width
        max(rect) - min(rect) <= limit
    """
    if not grid or not grid[0]:
        return None

    rows = len(grid)

    if height > rows:
        return None

    columns = transpose(grid)

    col_max_t = [sliding_max(col, height) for col in columns]
    col_min_t = [sliding_min(col, height) for col in columns]

    col_max = transpose(col_max_t)
    col_min = transpose(col_min_t)

    best: Rect | None = None

    for top in range(rows - height + 1):
        width, left, _ = longest_valid_range(col_max[top], col_min[top], limit)

        rect = Rect(top=top, left=left, height=height, width=width)

        if best is None or rect.area > best.area:
            best = rect

    return best


def brute_max_2d(grid: Sequence[Sequence[int]], h: int, w: int) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])

    ans: list[list[int]] = []

    for r in range(rows - h + 1):
        row: list[int] = []
        for c in range(cols - w + 1):
            best = max(grid[i][j] for i in range(r, r + h) for j in range(c, c + w))
            row.append(best)
        ans.append(row)

    return ans


def brute_min_2d(grid: Sequence[Sequence[int]], h: int, w: int) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])

    ans: list[list[int]] = []

    for r in range(rows - h + 1):
        row: list[int] = []
        for c in range(cols - w + 1):
            best = min(grid[i][j] for i in range(r, r + h) for j in range(c, c + w))
            row.append(best)
        ans.append(row)

    return ans


def test_fixed_cases() -> None:
    grid = [
        [1, 3, 2, 5],
        [4, 6, 1, 2],
        [7, 2, 9, 3],
    ]

    assert brute_max_2d(grid, 2, 2) == [
        [6, 6, 5],
        [7, 9, 9],
    ]

    assert brute_min_2d(grid, 2, 2) == [
        [1, 1, 1],
        [2, 1, 1],
    ]

    grid2 = [
        [5],
    ]

    assert brute_max_2d(grid2, 1, 1) == [[5]]
    assert brute_min_2d(grid2, 1, 1) == [[5]]

    grid3 = [
        [1, 2, 3],
        [4, 5, 6],
    ]

    assert brute_max_2d(grid3, 2, 3) == [[6]]
    assert brute_min_2d(grid3, 2, 3) == [[1]]


def test_against_bruteforce() -> None:
    for _ in range(1000):
        rows = random.randint(1, 8)
        cols = random.randint(1, 8)

        grid = [[random.randint(-10, 10) for _ in range(cols)] for _ in range(rows)]

        h = random.randint(1, rows)
        w = random.randint(1, cols)

        expected_max = brute_max_2d(grid, h, w)
        expected_min = brute_min_2d(grid, h, w)

        actual_max = sliding_max_2d(grid, h, w)
        actual_min = sliding_min_2d(grid, h, w)

        assert actual_max == expected_max, (
            "max failed",
            grid,
            h,
            w,
            expected_max,
            actual_max,
        )

        assert actual_min == expected_min, (
            "min failed",
            grid,
            h,
            w,
            expected_min,
            actual_min,
        )


def run_tests() -> None:
    test_fixed_cases()
    test_against_bruteforce()
    print("All tests passed.")


if __name__ == "__main__":
    run_tests()
