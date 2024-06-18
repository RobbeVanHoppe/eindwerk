import random
import time


def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


array_to_be_sorted = [random.randint(0, 1000) for _ in range(1000)]


def test_performance(rp_logger):
    arr_copy_bubble = array_to_be_sorted.copy()
    start_time_bubble = time.time()
    bubble_sort(arr_copy_bubble)
    end_time_bubble = time.time()

    arr_copy_quick = array_to_be_sorted.copy()
    start_time_quick = time.time()
    quick_sort(arr_copy_quick)
    end_time_quick = time.time()

    bubble_sort_time = end_time_bubble - start_time_bubble
    quick_sort_time = end_time_quick - start_time_quick

    rp_logger.info("Bubble Sort: %f", bubble_sort_time)
    rp_logger.info("Quick Sort: %f", quick_sort_time)

    rp_logger.info("Quick sort was %d times quicker", bubble_sort_time/quick_sort_time)
