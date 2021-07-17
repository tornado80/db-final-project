from linked_list import LinkedList
from logger import loading, done, error


class Vertex:
    def __init__(self, key):
        self.__key = key
        self.__outgoing_edges = LinkedList()

    @property
    def outgoing_edges(self):
        return self.__outgoing_edges

    @property
    def key(self):
        return self.__key

    def add_outgoing_edge(self, vertex):
        self.__outgoing_edges.add(vertex)


class DAG:
    def __init__(self, name: str):
        self.__vertices = {}
        self.__name = name

    @property
    def topological_order(self):
        loading(f"Calculating topological order of DAG with name: {self.__name}")
        result = []
        remaining_incoming_edges = {k: 0 for k in self.__vertices.keys()}
        nodes_without_incoming_edges = set()
        # initialization
        for vertex in self.__vertices.values():
            for neighbor in vertex.outgoing_edges:
                remaining_incoming_edges[neighbor.key] += 1
        for key, count in remaining_incoming_edges.items():
            if count == 0:
                nodes_without_incoming_edges.add(key)
        # processing
        while len(nodes_without_incoming_edges) > 0:
            key = nodes_without_incoming_edges.pop()
            result.append(key)
            for neighbor in self.__vertices[key].outgoing_edges:
                neighbor_key = neighbor.key
                remaining_incoming_edges[neighbor_key] -= 1
                if remaining_incoming_edges[neighbor_key] == 0:
                    nodes_without_incoming_edges.add(neighbor_key)
        done()
        if len(result) < len(self.__vertices):
            error("The dependency graph is not a DAG since a cycle detected")
            return None
        else:
            return result

    def add_outgoing_edge(self, k1, k2):
        for k in [k1, k2]:
            if k not in self.__vertices:
                raise KeyError(f"Vertex key not found: {k}.")
        self.__vertices[k1].add_outgoing_edge(self.__vertices[k2])

    def add_node(self, key):
        if key in self.__vertices:
            raise KeyError("Vertices with duplicate keys are not allowed.")
        self.__vertices[key] = Vertex(key)


__all__ = ["DAG"]


if __name__ == "__main__":
    g = DAG("sample")
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_outgoing_edge(1, 3)
    g.add_outgoing_edge(3, 2)
    print(g.topological_order)
