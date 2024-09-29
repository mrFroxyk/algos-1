"""Модуль кольцевого двусвязного списка"""
from typing import Self


class LinkedListItem:
    """Узел связного списка"""

    def __init__(self, data=None):
        self.data = data
        self._next_node = None
        self._prev_node = None

    @property
    def next_item(self) -> Self:
        """Следующий элемент"""
        return self._next_node

    @next_item.setter
    def next_item(self, value: Self) -> None:
        if value:
            value._prev_node = self

        self._next_node = value

    @property
    def previous_item(self) -> Self:
        """Предыдущий элемент"""
        return self._prev_node

    @previous_item.setter
    def previous_item(self, value: Self) -> None:
        if value:
            value._next_node = self

        self._prev_node = value

    def __repr__(self):
        return f"Linked List Node, data: {self.data}"


class LinkedList:
    """Связный список"""

    def __init__(self, first_item: LinkedListItem):
        self.first_item = first_item

    @property
    def last(self) -> LinkedListItem:
        """Последний элемент"""
        if len(self) == 0:
            return None

        return self.first_item.previous_item

    def append_left(self, item):
        """Добавление слева"""
        if len(self) == 0:
            self.first_item = LinkedListItem(item)
            self.first_item.next_item = self.first_item
            self.first_item.previous_item = self.first_item
            return

        new_item = LinkedListItem(item)
        new_item.previous_item = self.first_item.previous_item
        new_item.next_item = self.first_item
        self.first_item = new_item


    def append_right(self, item):
        """Добавление справа"""
        if len(self) == 0:
            self.first_item = LinkedListItem(item)
            self.first_item.next_item = self.first_item
            self.first_item.previous_item = self.first_item
            return

        new_item = LinkedListItem(item)
        self.first_item.previous_item.next_item = new_item
        self.first_item.previous_item = new_item

    def append(self, item):
        """Добавление справа"""
        return self.append_right(item)

    def remove(self, item):
        """Удаление"""
        if item not in self:
            raise ValueError("Item not found")

        cur = self.first_item
        while True:
            if cur.data == item:
                if len(self) == 1:
                    self.first_item = None
                    return

                cur.next_item.previous_item = cur.previous_item
                cur.previous_item.next_item = cur.next_item
                if cur == self.first_item:
                    self.first_item = cur.next_item
                break
            cur = cur.next_item


    def insert(self, previous_data, item):
        """Вставка справа"""
        new = LinkedListItem(item)
        cur = self.first_item
        for _ in range(len(self)):
            if cur.data == previous_data:
                new.next_item = cur.next_item
                new.previous_item = cur
                cur.next_item = new
                return
            cur = cur.next_item
        raise ValueError(f"Item {previous_data} not found in the list")

    def __len__(self):
        if not self.first_item:
            return 0

        cnt = 0
        cur = self.first_item
        while True:
            cnt += 1
            cur = cur.next_item
            if cur == self.first_item:
                break

        return cnt

    def __next__(self):
        if self._cnt >= len(self):
            raise StopIteration

        self._cnt += 1
        cur_item = self._cur
        self._cur = self._cur.next_item

        return cur_item

    def __iter__(self):
        self._cur = self.first_item
        self._cnt = 0

        return self

    def __getitem__(self, index):
        if index < 0:
            index = len(self) + index
        if index < 0 or index >= len(self):
            raise IndexError("Linked List index out of range")
        cur = self.first_item
        for _ in range(index):
            cur = cur.next_item

        return cur.data

    def __contains__(self, item):
        if not self.first_item:
            return False

        cur = self.first_item
        while True:
            if cur.data == item:
                return True
            cur = cur.next_item
            if cur == self.first_item:
                return False

    def __reversed__(self):
        if len(self) == 0:
            return []

        reversed_list = []
        last_node = self.last
        cur = last_node
        while True:
            reversed_list.append(cur.data)
            if cur == self.first_item:
                break

            cur = cur.previous_item

        return reversed_list
