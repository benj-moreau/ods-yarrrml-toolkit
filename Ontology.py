from rdflib import Graph, RDF
import yaml
from YARRRMLMapper import parse_to_rdf_mapping
import argparse


def main(mapping, destination):
    try:
        mapping = yaml.safe_load(mapping)
        print('YARRRML Mapping Parsing: OK')
    except (yaml.parser.ParserError, yaml.scanner.ScannerError) as exception:
        print(f'YARRRML Mapping Syntax Error: {exception}')
        return
    mapping = parse_to_rdf_mapping(mapping)
    classes, properties = get_classes_properties(mapping)
    rdf_ontology = get_ontology(classes, properties)
    destination.write(rdf_ontology.serialize(format='ttl').decode('utf-8'))
    print('Ontology exported to destination file !')


def get_ontology(classes, properties):
    rdf_ontology = Graph()
    concepts = classes | properties
    for concept in concepts:
        graph = get_rdf_graph(f'{concept}')
        for s, p, o in graph.triples((concept, None, None)):
            rdf_ontology.add((s, p, o))
    return rdf_ontology


def get_rdf_graph(concept):
    rdf_graph = Graph()
    try:
        if 'schema.org' in concept:
            rdf_graph.parse(f'{concept}.ttl', format='ttl')
        else:
            rdf_graph.parse(f'{concept}', format='xml')
    except Exception as e:
        print(f'A problem occured when trying to retrieve rdf at {concept}: {e}')
    return rdf_graph


def get_classes_properties(rdf_mapping):
    properties = set()
    classes = set()
    for _, _, o in rdf_mapping.triples((None, RDF.type, None)):
        classes.add(o)
    for _, p, _ in rdf_mapping.triples((None, None, None)):
        properties.add(p)
    return classes, properties


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get ontology of the mapping file.')
    parser.add_argument('mapping', type=argparse.FileType('r'), help='yarmmml mapping file')
    parser.add_argument('destination', type=argparse.FileType('w'), help='ttl file that will contain the ontology')
    args = parser.parse_args()
    main(args.mapping, args.destination)
