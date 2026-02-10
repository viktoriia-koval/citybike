def merge_sort(items: list[float], reverse: bool = False) -> list[float]:
    if len(items) <= 1:
        return items[:]

    middle = len(items) // 2
    #print("left:", items[:middle], "right:", items[middle:])
    left = merge_sort(items[:middle], reverse=reverse)
    right = merge_sort(items[middle:], reverse=reverse)
    #print("merge:",items,"left:", left, "right:", right)
    return _merge(left, right, reverse=reverse)


def _merge(left: list[float], right: list[float], reverse: bool) -> list[float]:
    merged: list[float] = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        left_value = left[i]
        right_value = right[j]

        if reverse: #по возрастанию reverse=False
            take_left = left_value >= right_value
        else:
            take_left = left_value <= right_value

        if take_left:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    if i < len(left):
        merged.extend(left[i:])
    if j < len(right):
        merged.extend(right[j:])

    return merged


def binary_search(items: list[str], target: str) -> int:
    left = 0
    right = len(items) - 1

    while left <= right:
        mid = (left + right) // 2
        current = items[mid]

        if current == target:
            return mid
        if current < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
