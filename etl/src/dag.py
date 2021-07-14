from linked_list import LinkedList


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
    def __init__(self):
        self.__vertices = {}

    def topological_order(self):
        result = []
        remaining_incoming_edges = {}
        nodes_without_incoming_edges = set()
        # initialization
        for vertex in self.__vertices.values():
            for neighbor in vertex.outgoing_edges:
                key = neighbor.key
                if key not in remaining_incoming_edges:
                    remaining_incoming_edges[key] = 0
                remaining_incoming_edges[key] += 1
        for key, count in remaining_incoming_edges:
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
        return result

    def add_outgoing_edge(self, k1, k2):
        for k in [k1, k2]:
            if k not in self.__vertices:
                raise KeyError(f"Vertex key not found {k}.")
        self.__vertices[k1].add_outgoing_edge(self.__vertices[k2])

    def add_node(self, key):
        if key in self.__vertices:
            raise KeyError("Vertices with duplicate keys are not allowed.")
        self.__vertices[key] = Vertex(key)


__all__ = ["DAG"]
