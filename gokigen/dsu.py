class DisjointSets:
    """
    A Disjoint Set Union-Find data structure.

    Attributes:
        nr_elems (int): The total number of elements.
        parent (List[int]): Pointer to the parent of each element.
        rank (List[int]): Height-based heuristic for balanced merging.
    """

    def __init__(self, nr_elems: int):
        self.nr_elems: int = nr_elems
        self.parent: list[int] = list(range(nr_elems))
        self.rank: list[int] = [0] * nr_elems
        self.history: list[tuple[int, int, bool]] = []

    def find(self, x: int) -> int:
        """
        Finds the representative (root) of the set containing x.

        Args:
            x: The element to find the root for.

        Returns:
            The root representative of the set.
        """
        rx = x
        parent = self.parent  # Local bind of attribute self.parent.

        while parent[rx] != rx:
            rx = parent[rx]
        return rx

    def same(self, a: int, b: int) -> bool:
        """
        Checks if elements a and b belong to the same disjoint set.

        Args:
            a: First element.
            b: Second element.
        Returns:

            True if a and b share the same root, False otherwise.
        """
        return self.find(a) == self.find(b)

    def union(self, a: int, b: int):
        """
        Merges the sets containing elements a and b using Union by Rank.

        Args:
            a: Element from the first set.
            b: Element from the second set.
        """
        ra = self.find(a)
        rb = self.find(b)

        # Union by rank: minimize height of tree.
        if self.rank[rb] < self.rank[ra]:
            self.history.append((rb, ra, False))
            self.parent[rb] = ra
        elif self.rank[rb] > self.rank[ra]:
            self.history.append((ra, rb, False))
            self.parent[ra] = rb
        elif self.rank[rb] == self.rank[ra]:
            self.history.append((rb, ra, True))
            self.parent[rb] = ra
            self.rank[ra] += 1

    def rollback(self):
        """Revert the last union operation."""
        if not self.history:
            return

        child, parent, rank_increased = self.history.pop()
        self.parent[child] = child
        if rank_increased:
            self.rank[parent] -= 1
