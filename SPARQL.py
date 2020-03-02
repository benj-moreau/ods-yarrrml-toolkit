from rdflib import Graph
from pyparsing import ParseException
import argparse


def main(source, query):
    rdf_graph = Graph().parse(source=source, format='ttl')
    sparql_query = query.read()
    query_result = []
    try:
        query_result = rdf_graph.query(sparql_query)
    except ParseException as exception:
        print(f'Error while trying to parse the query: {exception}')
        return
    for row in query_result:
        print_row = []
        for value in row:
            print_row.append(str(value))
        print(print_row)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query an RDF file using SPARQL.')
    parser.add_argument('source', type=argparse.FileType('r'), help='RDF source file to be queried.')
    parser.add_argument('query', type=argparse.FileType('r'), help='SPARQL Query to execute.')
    args = parser.parse_args()
    main(args.source, args.query)
