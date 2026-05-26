# Lazy-propagation segment trees for range-add updates + range-sum queries.
#
# Indexing convention:
#   - The *user-facing* array indices are 0-indexed, i.e. valid positions are
#     [0, n - 1]. The same algorithms work for 1-indexed inputs [1, n] by
#     swapping the recursive variant's root range from (0, n - 1) to (1, n).
#   - The *internal tree nodes* are 1-indexed (root = 1, children at 2 * node
#     and 2 * node + 1) for both variants.


class SegmentTreeLazy:
    """Recursive segment tree with lazy propagation.

    Supports range-add updates and range-sum queries. The same skeleton can be
    adapted to other (update, query) pairs by changing how `lazy` composes and
    how it applies to the node aggregate.
    """

    def __init__(self, arr: list[int]):
        self.n = len(arr)
        size = 4 * max(self.n, 1)
        self.tree = [0] * size
        self.lazy = [0] * size

        if self.n > 0:
            self._build(1, 0, self.n - 1, arr)

    def _build(self, node: int, lo: int, hi: int, arr: list[int]) -> None:
        if lo == hi:
            self.tree[node] = arr[lo]
            return

        mid = (lo + hi) >> 1
        self._build(2 * node, lo, mid, arr)
        self._build(2 * node + 1, mid + 1, hi, arr)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _apply(self, node: int, lo: int, hi: int, delta: int) -> None:
        self.tree[node] += delta * (hi - lo + 1)
        self.lazy[node] += delta

    def _push(self, node: int, lo: int, hi: int) -> None:
        if self.lazy[node] == 0:
            return

        mid = (lo + hi) >> 1
        self._apply(2 * node, lo, mid, self.lazy[node])
        self._apply(2 * node + 1, mid + 1, hi, self.lazy[node])
        self.lazy[node] = 0

    # inclusive: [l, r]
    def update_range(self, l: int, r: int, delta: int) -> None:
        if l > r:
            return
        self._update(1, 0, self.n - 1, l, r, delta)

    def _update(self, node: int, lo: int, hi: int, l: int, r: int, delta: int) -> None:
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            self._apply(node, lo, hi, delta)
            return

        self._push(node, lo, hi)
        mid = (lo + hi) >> 1
        self._update(2 * node, lo, mid, l, r, delta)
        self._update(2 * node + 1, mid + 1, hi, l, r, delta)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    # inclusive: [l, r]
    def query_range(self, l: int, r: int) -> int:
        if l > r:
            return 0
        return self._query(1, 0, self.n - 1, l, r)

    def _query(self, node: int, lo: int, hi: int, l: int, r: int) -> int:
        if r < lo or hi < l:
            return 0
        if l <= lo and hi <= r:
            return self.tree[node]

        self._push(node, lo, hi)
        mid = (lo + hi) >> 1
        return self._query(2 * node, lo, mid, l, r) + self._query(
            2 * node + 1, mid + 1, hi, l, r
        )

    def query_point(self, i: int) -> int:
        return self.query_range(i, i)


class SegmentTreeLazyIterative:
    """Iterative segment tree with lazy propagation (range-add + range-sum).

    The input length `n` is padded up to the next power of two `size`, so each
    internal node `i` covers exactly `size >> (floor_log2(i))` leaves. The tree
    layout is the same as the iterative point-update tree: leaves at
    [size, 2*size), parents at i // 2. Padding leaves [size + n, 2*size) hold
    0, so they never contribute to sums even though some apply/push operations
    touch nodes whose subtrees include them.

    Each op (update_range / query_range) follows three passes along the two
    boundary paths from the root down to the leaves at `l + size` and
    `r + size`: push pending lazy down, apply changes to fully-covered nodes
    (or accumulate them for queries), then pull aggregates back up. AtCoder
    Library's `lazy_segtree` is the standard reference.
    """

    def __init__(self, arr: list[int]):
        self.n = len(arr)

        size = 1
        while size < self.n:
            size <<= 1

        self.size = size
        self.log = size.bit_length() - 1
        self.tree = [0] * (2 * size)
        self.lazy = [0] * (2 * size)

        self.tree[size:size+self.n] = arr
        for i in reversed(range(1, size)):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def _apply(self, node: int, delta: int) -> None:
        # subtree-leaf count = size >> depth, where depth = log2(node) = node.bit_length() - 1
        # node's range = size // 2^depth
        self.tree[node] += delta * (self.size >> (node.bit_length() - 1))
        self.lazy[node] += delta

    def _push(self, node: int) -> None:
        if self.lazy[node]:
            self._apply(2 * node, self.lazy[node])
            self._apply(2 * node + 1, self.lazy[node])
            self.lazy[node] = 0

    def _pull(self, node: int) -> None:
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _push_path(self, l: int, r: int) -> None:
        for s in reversed(range(1, self.log + 1)):
            if l % (1 << s):
                self._push(l >> s)
            if r % (1 << s):
                self._push((r - 1) >> s)

    def _pull_path(self, l: int, r: int) -> None:
        for s in range(1, self.log + 1):
            if l % (1 << s):
                self._pull(l >> s)
            if r % (1 << s):
                self._pull((r - 1) >> s)

    # inclusive: [l, r]
    def update_range(self, l: int, r: int, delta: int) -> None:
        if l > r:
            return

        l += self.size
        r += self.size + 1  # half-open

        self._push_path(l, r)

        l2, r2 = l, r
        while l2 < r2:
            if l2 & 1:
                self._apply(l2, delta)
                l2 += 1
            if r2 & 1:
                r2 -= 1
                self._apply(r2, delta)
            l2 >>= 1
            r2 >>= 1

        self._pull_path(l, r)

    # inclusive: [l, r]
    def query_range(self, l: int, r: int) -> int:
        if l > r:
            return 0

        l += self.size
        r += self.size + 1

        self._push_path(l, r)

        res = 0
        while l < r:
            if l & 1:
                res += self.tree[l]
                l += 1
            if r & 1:
                r -= 1
                res += self.tree[r]
            l >>= 1
            r >>= 1
        return res

    def query_point(self, i: int) -> int:
        return self.query_range(i, i)


if __name__ == "__main__":
    import random

    # ---------------- SegmentTreeLazy ----------------

    arr = [1, 2, 3, 4, 5]
    lz = SegmentTreeLazy(arr)
    assert lz.query_range(0, 4) == sum(arr)
    assert lz.query_range(1, 3) == sum(arr[1:4])
    assert lz.query_point(2) == arr[2]

    lz.update_range(1, 3, 10)
    for i in range(1, 4):
        arr[i] += 10
    assert lz.query_range(0, 4) == sum(arr)
    assert lz.query_range(1, 3) == sum(arr[1:4])
    assert lz.query_point(2) == arr[2]

    lz.update_range(0, 4, -2)
    arr = [v - 2 for v in arr]
    assert lz.query_range(0, 4) == sum(arr)
    assert lz.query_point(0) == arr[0]
    assert lz.query_point(4) == arr[4]

    empty = SegmentTreeLazy([0] * 5)
    empty.update_range(0, 2, 3)
    empty.update_range(2, 4, 5)
    assert empty.query_point(0) == 3
    assert empty.query_point(2) == 8
    assert empty.query_point(4) == 5
    assert empty.query_range(0, 4) == 24
    assert empty.query_range(1, 3) == 16

    # ---------------- SegmentTreeLazyIterative ----------------

    arr = [1, 2, 3, 4, 5]
    lzi = SegmentTreeLazyIterative(arr)
    assert lzi.query_range(0, 4) == sum(arr)
    assert lzi.query_range(1, 3) == sum(arr[1:4])
    assert lzi.query_point(2) == arr[2]
    assert lzi.query_range(3, 1) == 0  # empty

    lzi.update_range(1, 3, 10)
    for i in range(1, 4):
        arr[i] += 10
    assert lzi.query_range(0, 4) == sum(arr)
    assert lzi.query_range(1, 3) == sum(arr[1:4])
    assert lzi.query_point(2) == arr[2]

    lzi.update_range(0, 4, -2)
    arr = [v - 2 for v in arr]
    assert lzi.query_range(0, 4) == sum(arr)
    assert lzi.query_point(0) == arr[0]
    assert lzi.query_point(4) == arr[4]

    empty = SegmentTreeLazyIterative([0] * 5)
    empty.update_range(0, 2, 3)
    empty.update_range(2, 4, 5)
    assert empty.query_point(0) == 3
    assert empty.query_point(2) == 8
    assert empty.query_point(4) == 5
    assert empty.query_range(0, 4) == 24
    assert empty.query_range(1, 3) == 16

    # single-element edge case
    single = SegmentTreeLazyIterative([7])
    assert single.query_point(0) == 7
    single.update_range(0, 0, 3)
    assert single.query_point(0) == 10
    assert single.query_range(0, 0) == 10

    # power-of-two length (no padding) edge case
    pow2 = SegmentTreeLazyIterative([1, 2, 3, 4])
    pow2.update_range(0, 3, 5)
    assert pow2.query_range(0, 3) == sum([6, 7, 8, 9])
    assert pow2.query_point(2) == 8

    # ---------------- Brute-force cross-checks ----------------

    random.seed(0)

    base = [random.randint(-100, 100) for _ in range(50)]
    lz = SegmentTreeLazy(base[:])
    for _ in range(300):
        if random.random() < 0.5:
            lo = random.randrange(len(base))
            hi = random.randrange(lo, len(base))
            delta = random.randint(-50, 50)
            for i in range(lo, hi + 1):
                base[i] += delta
            lz.update_range(lo, hi, delta)
        else:
            lo = random.randrange(len(base))
            hi = random.randrange(lo, len(base))
            assert lz.query_range(lo, hi) == sum(base[lo : hi + 1])

    # cross-check recursive vs iterative on varied sizes
    for n in (1, 2, 3, 5, 8, 13, 16, 31, 64):
        base = [random.randint(-100, 100) for _ in range(n)]
        rec_lazy = SegmentTreeLazy(base[:])
        itr_lazy = SegmentTreeLazyIterative(base[:])
        ref = base[:]

        for _ in range(500):
            if random.random() < 0.5:
                lo = random.randrange(n)
                hi = random.randrange(lo, n)
                delta = random.randint(-50, 50)
                for i in range(lo, hi + 1):
                    ref[i] += delta
                rec_lazy.update_range(lo, hi, delta)
                itr_lazy.update_range(lo, hi, delta)
            else:
                lo = random.randrange(n)
                hi = random.randrange(lo, n)
                expected = sum(ref[lo : hi + 1])
                assert rec_lazy.query_range(lo, hi) == expected
                assert itr_lazy.query_range(lo, hi) == expected

    print("All tests passed.")
