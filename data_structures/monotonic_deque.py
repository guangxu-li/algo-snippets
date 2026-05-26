from collections import deque
from collections.abc import Sequence


def sliding_max(nums: Sequence[int], k: int) -> list[int]:
    dq: deque[int] = deque()
    ans: list[int] = []

    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)

        if dq[0] <= i - k:
            dq.popleft()

        if i >= k - 1:
            ans.append(nums[dq[0]])

    return ans


def sliding_min(nums: Sequence[int], k: int) -> list[int]:
    dq: deque[int] = deque()
    ans: list[int] = []

    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] >= x:
            dq.pop()
        dq.append(i)

        if dq[0] <= i - k:
            dq.popleft()

        if i >= k - 1:
            ans.append(nums[dq[0]])

    return ans


def longest_valid_range(
    max_values: Sequence[int],
    min_values: Sequence[int],
    limit: int,
) -> tuple[int, int, int]:
    """
    Given two 1D arrays:
        max_values[i] = local max contribution at i
        min_values[i] = local min contribution at i

    Find longest subarray [l, r] such that:
        max(max_values[l:r+1]) - min(min_values[l:r+1]) <= limit

    Returns:
        (best_length, best_left, best_right)
    """
    max_dq: deque[int] = deque()
    min_dq: deque[int] = deque()

    left = 0
    best_len = 0
    best_left = 0
    best_right = -1

    for right in range(len(max_values)):
        while max_dq and max_values[max_dq[-1]] <= max_values[right]:
            max_dq.pop()
        max_dq.append(right)

        while min_dq and min_values[min_dq[-1]] >= min_values[right]:
            min_dq.pop()
        min_dq.append(right)

        while max_values[max_dq[0]] - min_values[min_dq[0]] > limit:
            if max_dq[0] == left:
                max_dq.popleft()
            if min_dq[0] == left:
                min_dq.popleft()
            left += 1

        cur_len = right - left + 1
        if cur_len > best_len:
            best_len = cur_len
            best_left = left
            best_right = right

    return best_len, best_left, best_right


if __name__ == "__main__":
    nums = [1, 3, 2, 5, 4]

    assert sliding_max(nums, 1) == nums
    assert sliding_min(nums, 1) == nums
    assert sliding_max(nums, 3) == [3, 5, 5]
    assert sliding_min(nums, 3) == [1, 2, 2]
    assert sliding_max(nums, len(nums)) == [5]
    assert sliding_min(nums, len(nums)) == [1]

    assert longest_valid_range([1, 3, 2], [1, 1, 2], 2) == (3, 0, 2)
    assert longest_valid_range([4, 1, 2, 3], [4, 1, 2, 3], 0) == (1, 0, 0)

    print("All tests passed.")
