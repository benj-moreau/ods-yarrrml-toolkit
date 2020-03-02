# ODS-YARRRML-Toolkit
A Python3 implementation of YARRRML Mapper and SPARQL Querying for OpenDataSoft-API data.

# Installation
First, clone the repository:

```bash
git clone https://github.com/benjimor/YARRRMLMapper.git
```

Then, assuming you already have `Python3` and `Pip` installed, install the dependencies:
> Running in a virtual environment is recommended

```bash
pip install -r requirements.txt
```

# Run It

## Transform an ODS API result (JSON) into RDF

Transform an ODS json api result file into an RDF (ttl) file using a YARRRML Mapping with the following command:
```bash
python YARRRMLMapper.py <source> <destination>.ttl <mapping>
```

example:
> Files are in root directory of this project
```bash
python YARRRMLMapper.py data.json data.ttl mapping.yml
```

## Query the resulting file using with SPARQL

Query the resulting ttl file with a SPARQL query using the following command:
```bash
python SPARQL.py <source>.ttl <query>
```

example:
> Files are in root directory of this project
```bash
python SPARQL.py data.ttl query.sparql
```