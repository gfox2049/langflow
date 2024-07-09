import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Coroutine, List

if TYPE_CHECKING:
    from langflow.graph.graph.base import Graph
    from langflow.graph.vertex.base import Vertex


class RunnableVerticesManager:
    def __init__(self):
        self.run_map = defaultdict(list)  # Tracks successors of each vertex
        self.run_predecessors = defaultdict(set)  # Tracks predecessors for each vertex
        self.vertices_to_run = set()  # Set of vertices that are ready to run
        self.vertices_being_run = set()  # Set of vertices that are currently running

    def to_dict(self) -> dict:
        return {
            "run_map": self.run_map,
            "run_predecessors": self.run_predecessors,
            "vertices_to_run": self.vertices_to_run,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunnableVerticesManager":
        instance = cls()
        instance.run_map = data["run_map"]
        instance.run_predecessors = data["run_predecessors"]
        instance.vertices_to_run = data["vertices_to_run"]
        return instance

    def __getstate__(self) -> object:
        return {
            "run_map": self.run_map,
            "run_predecessors": self.run_predecessors,
            "vertices_to_run": self.vertices_to_run,
        }

    def __setstate__(self, state: dict) -> None:
        self.run_map = state["run_map"]
        self.run_predecessors = state["run_predecessors"]
        self.vertices_to_run = state["vertices_to_run"]

    def update_run_state(self, run_predecessors: dict, vertices_to_run: set):
        self.run_predecessors.update(run_predecessors)
        self.vertices_to_run.update(vertices_to_run)
        self.build_run_map(self.run_predecessors, self.vertices_to_run)

    def is_vertex_runnable(self, vertex_id: str, inactivated_vertices: set[str], activated_vertices: set[str]) -> bool:
        """Determines if a vertex is runnable."""

        if not activated_vertices:
            # check vertices_to_run
            should_run = vertex_id in self.vertices_to_run
        else:
            # check run_predecessors
            should_run = vertex_id in activated_vertices
        return (
            vertex_id not in self.vertices_being_run
            and not self.run_predecessors.get(vertex_id)
            and vertex_id not in inactivated_vertices
            and should_run
        )

    def find_runnable_predecessors_for_successors(
        self, vertex_id: str, inactivated_vertices: set[str], activated_vertices: set[str]
    ) -> List[str]:
        """Finds runnable predecessors for the successors of a given vertex."""
        runnable_vertices = []
        visited = set()

        def find_runnable_predecessors(predecessor_id: str):
            if predecessor_id in visited:
                return
            visited.add(predecessor_id)
            if self.is_vertex_runnable(predecessor_id, inactivated_vertices, activated_vertices):
                runnable_vertices.append(predecessor_id)
            else:
                for pred_pred_id in self.run_predecessors.get(predecessor_id, []):
                    find_runnable_predecessors(pred_pred_id)

        for successor_id in self.run_map.get(vertex_id, []):
            for predecessor_id in self.run_predecessors.get(successor_id, []):
                find_runnable_predecessors(predecessor_id)

        return runnable_vertices

    def remove_from_predecessors(self, vertex_id: str):
        """Removes a vertex from the predecessor list of its successors."""
        predecessors = self.run_map.get(vertex_id, [])
        for predecessor in predecessors:
            if vertex_id in self.run_predecessors[predecessor]:
                self.run_predecessors[predecessor].remove(vertex_id)

    def build_run_map(self, predecessor_map, vertices_to_run):
        """Builds a map of vertices and their runnable successors."""
        self.run_map = defaultdict(list)
        for vertex_id, predecessors in predecessor_map.items():
            for predecessor in predecessors:
                self.run_map[predecessor].append(vertex_id)
        self.run_predecessors = predecessor_map.copy()
        self.vertices_to_run = vertices_to_run

    def update_vertex_run_state(self, vertex_id: str, is_runnable: bool):
        """Updates the runnable state of a vertex."""
        if is_runnable:
            self.vertices_to_run.add(vertex_id)
        else:
            self.vertices_to_run.discard(vertex_id)
            self.vertices_being_run.discard(vertex_id)

    async def get_next_runnable_vertices(
        self,
        lock: asyncio.Lock,
        set_cache_coro: Callable[["Graph", asyncio.Lock], Coroutine],
        graph: "Graph",
        vertex: "Vertex",
        cache: bool = True,
    ) -> List[str]:
        """
        Retrieves the next runnable vertices in the graph for a given vertex.

        Args:
            lock (asyncio.Lock): The lock object to be used for synchronization.
            set_cache_coro (Callable): The coroutine function to set the cache.
            graph (Graph): The graph object containing the vertices.
            vertex (Vertex): The vertex object for which the next runnable vertices are to be retrieved.
            cache (bool, optional): A flag to indicate if the cache should be updated. Defaults to True.

        Returns:
            list: A list of IDs of the next runnable vertices.

        """
        async with lock:
            self.remove_vertex_from_runnables(vertex.id)
            direct_successors_ready = [
                v
                for v in vertex.successors_ids
                if self.is_vertex_runnable(v, graph.inactivated_vertices, graph.activated_vertices)
            ]
            if not direct_successors_ready:
                # No direct successors ready, look for runnable predecessors of successors
                next_runnable_vertices = self.find_runnable_predecessors_for_successors(
                    vertex.id, graph.inactivated_vertices, graph.activated_vertices
                )
            else:
                next_runnable_vertices = direct_successors_ready

            for v_id in set(next_runnable_vertices):  # Use set to avoid duplicates
                if vertex.id == v_id:
                    next_runnable_vertices.remove(v_id)
                else:
                    self.add_to_vertices_being_run(v_id)
            if cache:
                await set_cache_coro(data=graph, lock=lock)  # type: ignore
        return next_runnable_vertices

    def remove_vertex_from_runnables(self, v_id):
        self.update_vertex_run_state(v_id, is_runnable=False)
        self.remove_from_predecessors(v_id)

    def add_to_vertices_being_run(self, v_id):
        self.vertices_being_run.add(v_id)

    @staticmethod
    def get_top_level_vertices(graph, vertices_ids):
        """
        Retrieves the top-level vertices from the given graph based on the provided vertex IDs.

        Args:
            graph (Graph): The graph object containing the vertices.
            vertices_ids (list): A list of vertex IDs.

        Returns:
            list: A list of top-level vertex IDs.

        """
        top_level_vertices = []
        for vertex_id in vertices_ids:
            vertex = graph.get_vertex(vertex_id)
            if vertex.parent_is_top_level:
                top_level_vertices.append(vertex.parent_node_id)
            else:
                top_level_vertices.append(vertex_id)
        return top_level_vertices
