def min_heapify(heap, i, n):
    """Maintains the min-heap property for the heap at index i."""
    smallest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and heap[left][2] < heap[smallest][2]:  # compare by time
        smallest = left
    if right < n and heap[right][2] < heap[smallest][2]:  # compare by time
        smallest = right

    if smallest != i:
        heap[i], heap[smallest] = heap[smallest], heap[i]
        min_heapify(heap, smallest, n)

def delete_min(heap):
    """Removes the minimum (root) element from the heap."""
    n = len(heap)
    if n == 0:
        return None
    min_element = heap[0]
    heap[0] = heap[-1]
    heap.pop()
    min_heapify(heap, 0, len(heap))
    return min_element

def insert_min(heap, element):
    """Inserts a new element into the min-heap."""
    heap.append(element)
    heapify_up(heap, len(heap) - 1)

def heapify_up(heap, i):
    """Traverses an element at index i up the heap to maintain the min-heap property."""
    parent = (i - 1) // 2
    while i > 0 and heap[i][2] < heap[parent][2]:  # compare by time
        heap[i], heap[parent] = heap[parent], heap[i]
        i = parent
        parent = (i - 1) // 2
