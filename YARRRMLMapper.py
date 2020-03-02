from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL, XSD
import yaml
import argparse

import re

url_regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


YARRRML_KEYS = {
    'mappings': ['mappings', 'mapping'],
    'predicateobjects': ['predicateobjects', 'predicateobject', 'po'],
    'predicates': ['predicates', 'predicate', 'p'],
    'objects': ['objects', 'object', 'o'],
    'value': ['value', 'v']
}

PREFIXES = {
    'rdfs:': str(RDFS),
    'rdf:': str(RDF),
    'owl:': str(OWL),
    'xsd:': str(XSD)
}

# Parser for RML YARRRML Syntax: http://rml.io/yarrrml/spec/


def main(source, destination, mapping):
    try:
        mapping = yaml.safe_load(mapping)
        print('YARRRML Parsing: OK')
    except (yaml.parser.ParserError, yaml.scanner.ScannerError) as exception:
        syntax_error = exception
        print(f'YARRRML Syntax Error: {syntax_error}')
    mapping = parse_to_rdf_mapping(mapping)
    destination.write(mapping.serialize(format='ttl').decode('utf-8'))


def parse_to_rdf_mapping(rml_mapping):
    prefixes = parse_prefixes(rml_mapping)
    resources = parse_subjects(rml_mapping, prefixes)
    rdf_semantic_mapping = parse_predicate_objects(rml_mapping, resources, prefixes)
    return rdf_semantic_mapping


def parse_prefixes(rml_mapping):
    prefixes = PREFIXES
    if 'prefixes' in rml_mapping:
        for prefix, uri in rml_mapping['prefixes'].items():
            if prefix not in prefixes:
                prefixes[prefix] = uri
    return prefixes


def parse_subjects(rml_mapping, prefixes):
    resources = {}
    for mapping_key, mapping in get_keys(rml_mapping, YARRRML_KEYS['mappings']).items():
        if 'subject' in mapping and mapping_key not in resources:
            subject = parse_uri_template(mapping['subject'], prefixes)
            resources[mapping_key] = subject
    return resources


def parse_predicate_objects(rml_mapping, resources, prefixes):
    rdf_semantic_mapping = Graph()
    for mapping_key, mapping in get_keys(rml_mapping, YARRRML_KEYS['mappings']).items():
        if mapping_key in resources:
            subject = resources[mapping_key]
            for predicate_object in get_keys(mapping, YARRRML_KEYS['predicateobjects']):
                predicate_object = uniformize_predicate_object(predicate_object)
                for predicate in predicate_object[0]:
                    predicate = parse_uri_template(predicate, prefixes)
                    for obj in predicate_object[1]:
                        rdf_semantic_mapping = parse_object(rdf_semantic_mapping,
                                                            subject,
                                                            predicate,
                                                            obj,
                                                            resources,
                                                            prefixes)
    return rdf_semantic_mapping


def parse_object(rdf_semantic_mapping, subject, predicate, obj, resources, prefixes):
    if len(obj) > 0:
        object_value = obj[0]
        uri = parse_uri_template(object_value, prefixes)
        if is_valid_uri(uri):
            # object is a URI (constant or template)
            obj = uri
        else:
            if object_value in resources:
                # object is a reference to an other resource in the mapping
                obj = resources[object_value]
            else:
                # object is a Literal (constant or reference)
                language = None
                datatype = None
                for i in range(1, len(obj)):
                    if '~lang' in obj[i]:
                        # language of the value
                        language = obj[i].replace('~lang', '')
                    else:
                        uri = parse_uri_template(obj[i], prefixes)
                        if is_valid_uri(uri):
                            # datatype of the value (URI)
                            datatype = uri
                if language:
                    obj = Literal(object_value, lang=language)
                else:
                    obj = Literal(object_value, datatype=datatype)
        rdf_semantic_mapping.add((subject, predicate, obj))
    return rdf_semantic_mapping


def parse_uri_template(template, prefixes):
    if template == 'a':
        return RDF.type
    uri_prefix = '{}:'.format(template.split(':', 1)[0])
    if uri_prefix in prefixes:
        template = template.replace(uri_prefix, prefixes[uri_prefix])
    return URIRef(template)


def uniformize_predicate_object(predicate_object):
    # returns the short uniform version:
    # [[predicate1, predicate2], [object1, object2]]
    # predicate -> URI
    # object -> [Term/URI, ?language, ?datatype]
    uniformized_predicate_object = []
    if isinstance(predicate_object, list):
        # Shorcut version using lists
        if len(predicate_object) > 1:
            if isinstance(predicate_object[0], list):
                # [[predicate1, predicate2], ...]
                uniformized_predicate_object.append(predicate_object[0])
            else:
                # [predicate1, ...]
                uniformized_predicate_object.append([predicate_object[0]])
            if isinstance(predicate_object[1], list):
                # [..., [object1, object2]]
                if predicate_object[1]:
                    if isinstance(predicate_object[1][0], list):
                        # [..., [[Term/URI, ?language, ?datatype], ...]]
                        uniformized_predicate_object.append(predicate_object[1])
                    else:
                        # [..., [Term/URI, ?language, ?datatype]]
                        obj = []
                        for element in predicate_object[1]:
                            obj.append(element)
                        uniformized_predicate_object.append([obj])
            else:
                # [..., Term/URI, ?language, ?datatype]
                obj = []
                for element in predicate_object[1:]:
                    obj.append(element)
                uniformized_predicate_object.append([obj])
    else:
        # Original version using dict
        predicates = get_keys(predicate_object, YARRRML_KEYS['predicates'])
        objects = get_keys(predicate_object, YARRRML_KEYS['objects'])
        if not predicates or not objects:
            return []
        if isinstance(predicates, list):
            uniformized_predicate_object.append(predicates)
        else:
            uniformized_predicate_object.append([predicates])
        if isinstance(objects, list):
            objs = []
            for obj in objects:
                if isinstance(obj, dict):
                    value = get_keys(obj, YARRRML_KEYS['value'] + YARRRML_KEYS['mappings'])
                    language = obj.get('language')
                    datatype = obj.get('datatype')
                    objs.append(value)
                    if language:
                        objs.append("{}~lang".format(language))
                    if datatype:
                        objs.append(datatype)
                else:
                    objs.append(obj)
            uniformized_predicate_object.append([objs])
        else:
            uniformized_predicate_object.append([objects])
    return uniformized_predicate_object


def get_keys(d, keys):
    # Get the value of the first key in keys that match a key in d
    for key in keys:
        if key in d:
            return d[key]
    return {}


def is_valid_uri(URI):
    return re.match(url_regex, URI) is not None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transform a json file into an RDF (ttl) file.')
    parser.add_argument('source', type=argparse.FileType('r'), help='json source file to be transformed')
    parser.add_argument('destination', type=argparse.FileType('w'), help='ttl file that will contain the rdf result')
    parser.add_argument('mapping', type=argparse.FileType('r'), help='yarmmml mapping file')
    args = parser.parse_args()
    main(args.source, args.destination, args.mapping)
