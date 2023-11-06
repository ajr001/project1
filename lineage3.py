import inspect
import io

class AttributeHolder:
    sep = ', '

    def __init__(self, **attrs):
        self.attrs = attrs

    def __setattr__(self, key, value):
        if inspect.currentframe().f_back.f_code.co_name == '__init__':
            object.__setattr__(self, key, value)
        else:
            self.attrs[key] = value

    def set(self, key, value):
        self.attrs[key] = value

    def __str__(self):
        attrs_str = self.sep.join([f'{k}="{v}"' for k, v in self.attrs.items()])
        return attrs_str if attrs_str else ''


class BaseGraph(AttributeHolder):
    def __init__(self, name, is_directed=False):
        super().__init__()
        self.name = name
        self.is_directed = is_directed
        self.nodes = {}
        self.edges = {}
        self.subgraphs = {}

    def graph_type(self):
        return "digraph"
    def add_node(self, name, **attrs):
        self.nodes[name] = attrs

    def add_edge(self, src, dst, **attrs):
        # src_name = src_port = src_loc = dst_name = dst_port = dst_loc = None
        # parts = src.split(':')
        # src_name = parts[0]
        # if len(parts) > 1:
        #     attrs['src_port'] = parts[1]
        # if len(parts) > 2:
        #     attrs['src_len'] = parts[2]
        # parts = dst.split(':')
        # dst_name = parts[0]
        # if len(parts) > 1:
        #     attrs['dst_port'] = parts[1]
        # if len(parts) > 2:
        #     attrs['dst_loc'] = parts[2]
        self.edges[(src, dst)] = attrs

    def add_subgraph(self, name, subgraph):
        self.subgraphs[name] = subgraph

    def __str__(self):
        ret = self.printOn().getvalue()
        return ret

    def printOn(self, stream=None):
        stream = stream or io.StringIO()
        stream.write(f'{self.graph_type()} {self.name} {{\n')
        for k,v in self.attrs.items():
            stream.write(f"   {k} = {v};")
        if self.attrs:
            stream.write("\n")
        self.print_subgraphs_on(stream)
        self.print_nodes_on(stream)
        self.print_edges_on(stream)
        stream.write('}\n')
        return stream

    def print_attributes_on(self, stream, attrs):
        if attrs:
            kvs = []
            for k, v in attrs.items():
                q = '' if v.startswith('<') else '"'
                kvs.append(f'{k}={q}{v}{q}')
            kvs = ' '.join(kvs)
            stream.write(f"[{kvs}]")

    def print_subgraphs_on(self, stream):
        for subgraph_name, subgraph in self.subgraphs.items():
            subgraph.printOn(stream)

    def print_nodes_on(self, stream):
        for name, attrs in self.nodes.items():
            stream.write(f'  {name}')
            self.print_attributes_on(stream, attrs)
            stream.write('\n')

    def print_edges_on(self, stream):
        for (src, dst), attrs in self.edges.items():
            src_with_attrs = src
            if 'src_port' in attrs:
                src_with_attrs += f':{attrs["src_port"]}'
            if 'src_loc' in attrs:
                src_with_attrs += f':{attrs["src_loc"]}'

            dst_with_attrs = dst
            if 'dst_port' in attrs:
                dst_with_attrs += f':{attrs["dst_port"]}'
            if 'dst_loc' in attrs:
                dst_with_attrs += f':{attrs["dst_loc"]}'

            stream.write(f'  {src_with_attrs} -> {dst_with_attrs}')
            attrs_copy = attrs.copy()
            attrs_copy.pop('src_port', None)
            attrs_copy.pop('dst_port', None)
            attrs_copy.pop('src_loc', None)
            attrs_copy.pop('dst_loc', None)
            self.print_attributes_on(stream, attrs_copy)
            stream.write('\n')


class Graph(BaseGraph):
    def __init__(self, name, is_directed=False):
        super().__init__(name, is_directed)

    # def __str__(self):
    #     lines = []
    #     lines.append(f'{self.graph_type} {self.name} {{')
    #     lines.append(f'  {super().__str__()}')
    #     lines.append('}')
    #     return "\n".join(lines)
    def graph_type(self):
        return "digraph"

class Subgraph(BaseGraph):
    def __init__(self, name):
        super().__init__(name)

    # def __str__(self):
    #     lines = [f'subgraph {self.name} {{']
    #     lines.append(f'  {super().__str__()}')
    #     lines.append('}')
    #     return "\n".join(lines)

    def graph_type(self):
        return "subgraph"
def demo():

    graph = Graph('G', is_directed=True)
    graph.rankdir = 'LR' #  set('rankdir', 'LR')
    c1 = Subgraph('cluster_c1')
    c1.label = 'Adapter'
    c1.labelloc = 't'
    table_a = {'shape': 'plaintext', 'label': '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD port="pone">one</TD></TR><TR><TD port="ptwo">two</TD></TR></TABLE>>'}
    table_b = {'shape': 'plaintext', 'label': '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD port="pthree">three</TD></TR><TR><TD port="pfour">four</TD></TR></TABLE>>'}
    c1.add_node('a', **table_a)
    c1.add_node('b', **table_b)
    c1.add_edge('a:pone', 'b:pthree', color='red')
    c1.add_edge('a:ptwo', 'b:pfour', color='red')
    graph.add_subgraph('c1', c1)

    c2 = Subgraph('cluster_c2')
    c2.label = 'Wrapper'
    table_c = {'shape': 'plaintext', 'label': '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD port="pfive">five</TD></TR><TR><TD port="psix">six</TD></TR></TABLE>>'}
    table_d = {'shape': 'plaintext', 'label': '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD port="pseven">seven</TD></TR><TR><TD>eight</TD></TR></TABLE>>'}
    c2.add_node('c', **table_c)
    c2.add_node('d', **table_d)
    c2.add_edge('c:pfive', 'd:pseven', color='green')
    c2.add_edge('c:psix', 'd:pseven', color='brown')
    graph.add_subgraph('c2', c2)
    graph.add_edge('b', 'c', color='blue')
    dot_string = str(graph)
    print(dot_string)

    from lineage import generate_and_open_pdf
    generate_and_open_pdf(dot_string)


if __name__ == '__main__':
    demo()
