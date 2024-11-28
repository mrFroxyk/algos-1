"""Sort algorithm module. Can be used in CLI. Uses argparse.
"""

import argparse
import copy
import click
import json
import os
from collections.abc import Callable

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


def my_sort(array: list, reverse: bool = False, animate: bool = False) -> list:
    """Sorts array. Uses TimSort algorithm. Modifies array

    Args:
        array (list): list of elements
        reverse (bool, optional): sort in descending order. Defaults to False.
        animate (bool, optional): animate sort. Defaults to False.

    Returns:
        list: sorted list

    """

    def _validate():
        if not isinstance(array, list):
            raise TypeError("array is not a list")

        if not isinstance(reverse, bool):
            raise TypeError("reverse is not a boolean")

        if not isinstance(animate, bool):
            raise TypeError("animate is not a boolean")

    _validate()

    if len(array) == 0:
        if animate:
            return my_anim(
                [
                    array,
                ],
            )
        return array

    timsort = TimSort(reverse, animate)
    if animate:
        anim_list = [
            copy.deepcopy(array),
        ]
        for arr in timsort.sort(array):
            anim_list.append(copy.deepcopy(arr))
        my_anim(anim_list)
    else:
        for _ in timsort.sort(array):
            pass
    return array


def my_anim(anim_list: list[list]) -> None:
    """Run matplotlib animation of TimSort sortion algorithm.

    Args:
        anim_list (list[list]): list of lists.
            Each list - deepcopy of target array.
            Each list contains elements of 1 step of sortion.

    Returns:
        None

    """

    def animate(frame):
        """Animation func used in FuncAnim

        Args:
            frame (list): list in anim_list

        Returns:
            None: None

        """
        plt.clf()

        x = range(len(frame))
        y = frame

        plt.bar(x, y)
        # plt.title(f"Frame = {i}")
        return ()

    fig, _ = plt.subplots()

    anim = FuncAnimation(  # pylint: disable=W0612
        fig=fig,
        func=animate,
        frames=iter(anim_list),
        interval=10,
        repeat=False,
        cache_frame_data=False,
    )
    plt.show(block=True)  # block=True чтобы передавать контроль обратно в CLI



class TimSort:
    """TimSort algorithm class"""

    MIN_MERGE = 16

    def __init__(
        self,
        reverse: bool = False,
        animate: bool = False,
        key: Callable | None = None,
        cmp: Callable | None = None,
    ):
        self._reverse = reverse
        self._animate = animate
        self._key = key

        self._cmp = cmp
        if cmp is None:
            self._cmp = self.increasing
            if reverse:
                self._cmp = self.decreasing

    def sort(self, arr: list):
        """Iterative Timsort function to sort the array[0...n-1] (similar to merge sort)

        Args:
            arr (list): list to sort

        Returns:
            list: sorted list

        Yields:
            list: step of sorting. Contain target list elements

        """
        n = len(arr)
        min_run = self.calc_min_run(n)

        # Sort individual subarrays of size RUN
        for start in range(0, n, min_run):
            end = min(start + min_run - 1, n - 1)
            for _ in self.insertion_sort(arr, start, end):
                if self._animate:
                    yield arr

        # Start merging from size RUN (or 32). It will merge
        # to form size 64, then 128, 256 and so on ....
        size = min_run
        while size < n:

            # Pick starting point of left sub array. We
            # are going to merge arr[left..left+size-1]
            # and arr[left+size, left+2*size-1]
            # After every merge, we increase left by 2*size
            for left in range(0, n, 2 * size):

                # Find ending point of left sub array
                # mid+1 is starting point of right sub array
                mid = min(n - 1, left + size - 1)
                right = min((left + 2 * size - 1), (n - 1))

                # Merge sub array arr[left.....mid] &
                # arr[mid+1....right]
                if mid < right:
                    for arr in self.merge(arr, left, mid, right):
                        if self._animate:
                            yield arr

            size = 2 * size
        return arr

    def calc_min_run(self, n: int) -> int:
        """Returns the minimum length of a
            run from 23 - 64 so that
            the len(array)/minrun is less than or
            equal to a power of 2.
            e.g. 1=>1, ..., 63=>63, 64=>32, 65=>33,
            ..., 127=>64, 128=>32, ...

        Args:
            n (int): len of list

        Returns:
            int: minimum length of run

        """
        r = 0
        while n >= self.MIN_MERGE:
            r |= n & 1
            n >>= 1
        return n + r

    def insertion_sort(self, arr: list, left: int, right: int):
        """One step of insertion sort algorithm. Modifies arr

        Args:
            arr (list): list of elements
            left (int): left element
            right (int): right element

        Yields:
            list: step of sortion

        """
        for i in range(left + 1, right + 1):
            j = i
            while j > left and self._cmp(arr[j], arr[j - 1]):
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
                j -= 1
                if self._animate:
                    yield arr

    def merge(self, arr: list, l: int, m: int, r: int):
        """Merge sortion algorithm.

        Args:
            arr (list): list of elements
            l (int): left end element
            m (int): mid element
            r (int): right element

        Yields:
            list: step of sortion

        """
        # original array is broken in two parts
        # left and right array
        len1, len2 = m - l + 1, r - m
        left, right = [], []
        for i in range(len1):
            left.append(arr[l + i])
        for i in range(len2):
            right.append(arr[m + 1 + i])

        i, j, k = 0, 0, l

        # after comparing, we merge those two array
        # in larger sub array
        while i < len1 and j < len2:
            if self._cmp(left[i], right[j]):
                arr[k] = left[i]
                i += 1
                if self._animate:
                    yield arr
            else:
                arr[k] = right[j]
                j += 1
                if self._animate:
                    yield arr
            k += 1

        # Copy remaining elements of left, if any
        while i < len1:
            arr[k] = left[i]
            k += 1
            i += 1
            if self._animate:
                yield arr

        # Copy remaining element of right, if any
        while j < len2:
            arr[k] = right[j]
            k += 1
            j += 1
            if self._animate:
                yield arr

    @staticmethod
    def increasing(a, b) -> bool:
        """Compare a and b in increasing order.

        Args:
            a (_type_): Any that supports comparsions
            b (_type_): Any that supports comparsions

        Returns:
            bool: result of comparsion

        """
        return a < b

    @staticmethod
    def decreasing(a, b) -> bool:
        """Compare a and b in decreasing order.

        Args:
            a (_type_): Any that supports comparsions
            b (_type_): Any that supports comparsions

        Returns:
            bool: result of comparsion

        """
        return a > b


@click.command()
@click.option(
    "-f",
    "--file-path",
    help="Load data from file of .json format",
    type=click.Path(exists=True)
)
@click.option(
    "-arr",
    "--array",
    help="List of elements separated by space to sort. Must be of the same type.",
    type=str,  # Строка для ввода данных
)
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    help="Reverse the order of the elements",
)
@click.option(
    "-anm",
    "--animate",
    is_flag=True,
    help="Show animation or not",
)
def main(file_path: str, array: str, reverse: bool, animate: bool) -> None:
    """Entry point function."""
    if file_path:
        with open(file_path, encoding="utf-8") as file:
            array = json.load(file)
    elif array:
        array = [int(x) for x in array.split()]  # Преобразуем строку в список целых чисел

    print(f"Before sort: {array}")
    print(f"Reverse flag: {reverse}\n")
    my_sort(array, reverse, animate)
    print(f"After sort: {array}")

if __name__ == "__main__":
    main()