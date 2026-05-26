from collections.abc import Callable
from typing import Any

# Segment trees with point updates and range queries over a generic
# associative operation. For range-add updates + range-sum queries with lazy
# propagation, see `segment_tree_lazy.py`.
#
# Indexing convention used in this file:
#   - The *user-facing* array indices are 0-indexed, i.e. valid positions are
#     [0, n - 1]. The same algorithms work for 1-indexed inputs [1, n] by
#     swapping the root range from (0, n - 1) to (1, n); both conventions are
#     equivalent and you only need to stay consistent between build and query.
#   - The *internal tree nodes* are always 1-indexed (root = 1, children at
#     2 * node and 2 * node + 1) for the recursive variants, which is the
#     standard layout. The iterative variant uses a different layout (leaves
#     at [n, 2n), parent at i // 2).


class SegmentTreeRecursive:
    """Recursive segment tree with point updates and range queries.

    Uses an array of size 4n. The combining operation must be associative;
    `identity` must satisfy op(identity, x) == op(x, identity) == x.
    """

    def __init__(
        self,
        arr: list[int],
        op: Callable[[Any, Any], Any] = lambda a, b: a + b,
        identity: Any = 0,
    ):
        self.n = len(arr)
        self.op = op
        self.identity = identity
        self.tree = [identity] * (4 * max(self.n, 1))

        if self.n > 0:
            self._build(1, 0, self.n - 1, arr)

    def _build(self, node: int, lo: int, hi: int, arr: list[int]) -> None:
        if lo == hi:
            self.tree[node] = arr[lo]
            return

        mid = (lo + hi) >> 1
        self._build(2 * node, lo, mid, arr)
        self._build(2 * node + 1, mid + 1, hi, arr)
        self.tree[node] = self.op(self.tree[2 * node], self.tree[2 * node + 1])

    def update(self, i: int, val: int) -> None:
        self._update(1, 0, self.n - 1, i, val)

    def _update(self, node: int, lo: int, hi: int, i: int, val: int) -> None:
        if lo == hi:
            self.tree[node] = val
            return

        mid = (lo + hi) >> 1
        if i <= mid:
            self._update(2 * node, lo, mid, i, val)
        else:
            self._update(2 * node + 1, mid + 1, hi, i, val)

        self.tree[node] = self.op(self.tree[2 * node], self.tree[2 * node + 1])

    # inclusive: [l, r]
    def query(self, l: int, r: int) -> Any:
        if l > r:
            return self.identity
        return self._query(1, 0, self.n - 1, l, r)

    def _query(self, node: int, lo: int, hi: int, l: int, r: int) -> Any:
        if r < lo or hi < l:
            return self.identity
        if l <= lo and hi <= r:
            return self.tree[node]

        mid = (lo + hi) >> 1
        return self.op(
            self._query(2 * node, lo, mid, l, r),
            self._query(2 * node + 1, mid + 1, hi, l, r),
        )


class SegmentTreeIterative:
    """Iterative bottom-up segment tree with point updates and range queries.

    Uses an array of size 2n: leaves live at positions [n, 2n) and parents at
    i // 2. Works for any n (not only powers of two). The operation must be
    associative; non-commutative ops are supported by keeping separate
    left/right accumulators during the query.
    """

    def __init__(
        self,
        arr: list[int],
        op: Callable[[Any, Any], Any] = lambda a, b: a + b,
        identity: Any = 0,
    ):
        self.n = len(arr)
        self.op = op
        self.identity = identity
        self.tree = [identity] * (2 * max(self.n, 1))

        for i, val in enumerate(arr):
            self.tree[self.n + i] = val
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = op(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, i: int, val: int) -> None:
        i += self.n
        self.tree[i] = val
        i >>= 1
        while i > 0:
            self.tree[i] = self.op(self.tree[2 * i], self.tree[2 * i + 1])
            i >>= 1

    # inclusive: [l, r]
    def query(self, l: int, r: int) -> Any:
        if l > r:
            return self.identity

        res_l = self.identity
        res_r = self.identity
        l += self.n
        r += self.n + 1  # convert to half-open [l, r)

        while l < r:
            if l & 1:
                res_l = self.op(res_l, self.tree[l])
                l += 1
            if r & 1:
                r -= 1
                res_r = self.op(self.tree[r], res_r)
            l >>= 1
            r >>= 1

        return self.op(res_l, res_r)


if __name__ == "__main__":
    import math
    import operator
    import random
    from functools import reduce
    from math import gcd

    # ---------------- SegmentTreeRecursive ----------------

    arr = [1, 3, 2, 7, 9, 11]
    st = SegmentTreeRecursive(arr)
    assert st.query(0, 5) == sum(arr)
    assert st.query(1, 4) == sum(arr[1:5])
    assert st.query(3, 3) == 7
    assert st.query(2, 1) == 0  # empty range -> identity

    st.update(3, 0)
    arr[3] = 0
    assert st.query(0, 5) == sum(arr)
    assert st.query(2, 4) == sum(arr[2:5])

    arr = [5, 1, 9, 3, 7, 2]
    st = SegmentTreeRecursive(arr, op=min, identity=math.inf)
    assert st.query(0, 5) == 1
    assert st.query(2, 5) == 2
    assert st.query(4, 4) == 7

    st = SegmentTreeRecursive(arr, op=max, identity=-math.inf)
    assert st.query(0, 5) == 9
    assert st.query(3, 5) == 7

    arr = [24, 36, 48, 60, 72]
    st = SegmentTreeRecursive(arr, op=gcd, identity=0)
    assert st.query(0, 4) == 12
    assert st.query(0, 0) == 24

    arr = [4, 1, 7, 1, 4]
    st = SegmentTreeRecursive(arr, op=operator.xor, identity=0)
    assert st.query(0, 4) == reduce(operator.xor, arr)
    assert st.query(1, 3) == reduce(operator.xor, arr[1:4])

    # ---------------- SegmentTreeIterative ----------------

    arr = [1, 3, 2, 7, 9, 11]
    st = SegmentTreeIterative(arr)
    assert st.query(0, 5) == sum(arr)
    assert st.query(1, 4) == sum(arr[1:5])
    assert st.query(3, 3) == 7
    assert st.query(5, 3) == 0  # empty

    st.update(3, 0)
    arr[3] = 0
    assert st.query(0, 5) == sum(arr)

    # ---------------- Brute-force cross-checks ----------------

    random.seed(0)
    base = [random.randint(-100, 100) for _ in range(50)]

    rec = SegmentTreeRecursive(base[:])
    itr = SegmentTreeIterative(base[:])

    for _ in range(200):
        if random.random() < 0.3:
            idx = random.randrange(len(base))
            val = random.randint(-100, 100)
            base[idx] = val
            rec.update(idx, val)
            itr.update(idx, val)
        else:
            lo = random.randrange(len(base))
            hi = random.randrange(lo, len(base))
            expected = sum(base[lo : hi + 1])
            assert rec.query(lo, hi) == expected
            assert itr.query(lo, hi) == expected

    base = [random.randint(-100, 100) for _ in range(40)]
    itr_min = SegmentTreeIterative(base[:], op=min, identity=math.inf)
    rec_min = SegmentTreeRecursive(base[:], op=min, identity=math.inf)
    for lo in range(len(base)):
        for hi in range(lo, len(base)):
            expected = min(base[lo : hi + 1])
            assert itr_min.query(lo, hi) == expected
            assert rec_min.query(lo, hi) == expected

    print("All tests passed.")
