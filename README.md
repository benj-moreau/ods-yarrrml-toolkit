# ODS-YARRRML-Toolkit
A Python3 implementation of YARRRML Mapper and SPARQL Querying for OpenDataSoft-API data.

# Installation
First, clone the repository:

```bash
git clone https://github.com/benjimor/ods-yarrrml-toolkit.git
```

Then, assuming you already have `Python3` and `Pip` installed, install the dependencies:
> Running in a virtual environment is recommended

```bash
pip3 install -r requirements.txt
```

# Run It

## Transform an ODS API result (JSON) into RDF

Transform an ODS json api result file into an RDF (ttl) file using a YARRRML Mapping with the following command:
```bash
python3 YARRRMLMapper.py <source> <destination> <mapping>
```

example:
> Files are in root directory of this project
```bash
python3 YARRRMLMapper.py example/rap_world_data.json example/rdf_result_data.ttl example/rap_world_mapping.yml
```

## Query the resulting file using with SPARQL

Query the resulting ttl file with a SPARQL query using the following command:
```bash
python3 SPARQL.py <source> <query>
```

example:
> Files are in root directory of this project
```bash
python3 SPARQL.py example/rdf_result_data.ttl example/query.sparql
```
