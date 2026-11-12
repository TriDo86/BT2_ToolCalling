def two_sum(target: int, nums: list) -> tuple:
    # Return the indices of matching pairs
    missing_dict = {} # key: traversed number, value: index of it
    for i, n in enumerate(nums):
        missing_value = target - n
        if missing_value in missing_dict:
            return (missing_dict.get(missing_value), i)

        missing_dict[n] = i

    return (None, None)