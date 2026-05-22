from collections.abc import Callable

log2 = [0] * (10**5 + 1)
for i in range(2, 10**5+1):
    log2[i] = log2[i//2] + 1

class SparseTableIndex:
    def __init__(self, arr: list[int]):
        self.arr = arr
        self.n = len(arr)

        n = self.n
        m = log2[n] + 1

        st = [[0] * n for _ in range(m)]
        st[0] = list(range(n))

        for k in range(1, m):
            full = 1 << k
            half = full >> 1

            for i in range(n - full + 1):
                left = st[k - 1][i]
                right = st[k - 1][i + half]

                st[k][i] = left if arr[left] <= arr[right] else right

        self.m = m
        self.st = st

    def query_index(self, lo: int, hi: int) -> int:
        k = log2[hi - lo + 1]

        left = self.st[k][lo]
        right = self.st[k][hi - (1 << k) + 1]

        return left if self.arr[left] <= self.arr[right] else right

    def query(self, lo: int, hi: int) -> int:
        return self.arr[self.query_index(lo, hi)]

class SparseTable:
    def __init__(self, arr: list[int], op: Callable[[int, int], int] = min):
        n = len(arr)
        m = log2[n] + 1

        st = [[0] * n for _ in range(m)]
        st[0] = arr[:]

        for k in range(1, m):
            full = 1 <<k
            half = full >> 1
            for i in range(n - full + 1):
                st[k][i] = op(st[k - 1][i], st[k - 1][i + half])

        self.n = n
        self.m = m
        self.st = st
        self.op = op

    def query(self, lo: int, hi: int) -> int:
        k = log2[hi - lo + 1]
        return self.op(self.st[k][lo], self.st[k][hi - (1 << k) + 1])

    def query_nonidempotent(self, lo: int, hi: int) -> int | None:
        res = None
        length = hi - lo + 1

        for k in reversed(range(self.m)):
            if (block_size := 1 << k) <= length:
                block = self.st[k][lo]

                if res is None:
                    res = block
                else:
                    res = self.op(res, block)

                lo += block_size
                length -= block_size

        return res


if __name__ == "__main__":
    import operator
    import random
    from functools import reduce
    from math import gcd

    # Basic min tests
    arr = [1, 3, 2, 7, 9, 11]
    st = SparseTable(arr)
    assert st.query(1, 4) == 2
    assert st.query(0, 2) == 1
    assert st.query(0, 5) == 1
    assert st.query(3, 3) == 7

    # Given min tests using query_nonidempotent
    arr = [7, 2, 3, 0, 5, 10, 3, 12, 18]
    st = SparseTable(arr, op=min)
    assert st.query_nonidempotent(0, 4) == 0
    assert st.query_nonidempotent(4, 7) == 3
    assert st.query_nonidempotent(7, 8) == 12

    # Max tests
    arr = [5, 1, 9, 3, 7, 2]
    st = SparseTable(arr, op=max)
    assert st.query(0, 5) == 9
    assert st.query(1, 3) == 9
    assert st.query(3, 5) == 7
    assert st.query(4, 4) == 7

    # GCD tests
    arr = [24, 36, 48, 60, 72]
    st = SparseTable(arr, op=gcd)
    assert st.query(0, 4) == 12
    assert st.query(1, 3) == 12
    assert st.query(2, 4) == 12
    assert st.query(0, 0) == 24

    # Sum tests - must use query_nonidempotent
    arr = [7, 2, 3, 0, 5]
    st = SparseTable(arr, op=lambda a, b: a + b)
    assert st.query_nonidempotent(0, 4) == 17
    assert st.query_nonidempotent(1, 3) == 5
    assert st.query_nonidempotent(3, 4) == 5
    assert st.query_nonidempotent(2, 2) == 3

    # XOR tests - must use query_nonidempotent
    arr = [4, 1, 7, 1, 4]
    st = SparseTable(arr, op=operator.xor)
    assert st.query_nonidempotent(0, 4) == reduce(operator.xor, arr)
    assert st.query_nonidempotent(1, 3) == reduce(operator.xor, arr[1:4])
    assert st.query_nonidempotent(2, 4) == reduce(operator.xor, arr[2:5])

    # Negative numbers
    arr = [-5, -1, -10, 3, 0]
    st = SparseTable(arr, op=min)
    assert st.query(0, 4) == -10
    assert st.query(0, 1) == -5
    assert st.query(3, 4) == 0

    st = SparseTable(arr, op=max)
    assert st.query(0, 4) == 3
    assert st.query(0, 2) == -1
    assert st.query(2, 2) == -10

    # Single element
    arr = [42]
    st = SparseTable(arr)
    assert st.query(0, 0) == 42
    assert st.query_nonidempotent(0, 0) == 42

    # Exhaustive brute-force tests for min
    arr = [random.randint(-100, 100) for _ in range(50)]
    st = SparseTable(arr, op=min)

    for lo in range(len(arr)):
        for hi in range(lo, len(arr)):
            expected = min(arr[lo:hi + 1])
            assert st.query(lo, hi) == expected
            assert st.query_nonidempotent(lo, hi) == expected

    # Exhaustive brute-force tests for max
    arr = [random.randint(-100, 100) for _ in range(50)]
    st = SparseTable(arr, op=max)

    for lo in range(len(arr)):
        for hi in range(lo, len(arr)):
            expected = max(arr[lo:hi + 1])
            assert st.query(lo, hi) == expected
            assert st.query_nonidempotent(lo, hi) == expected

    # Exhaustive brute-force tests for sum
    arr = [random.randint(-100, 100) for _ in range(50)]
    st = SparseTable(arr, op=lambda a, b: a + b)

    for lo in range(len(arr)):
        for hi in range(lo, len(arr)):
            expected = sum(arr[lo:hi + 1])
            assert st.query_nonidempotent(lo, hi) == expected

    # Exhaustive brute-force tests for gcd
    arr = [random.randint(1, 100) for _ in range(50)]
    st = SparseTable(arr, op=gcd)

    for lo in range(len(arr)):
        for hi in range(lo, len(arr)):
            expected = reduce(gcd, arr[lo:hi + 1])
            assert st.query(lo, hi) == expected
            assert st.query_nonidempotent(lo, hi) == expected

    print("All tests passed!")
