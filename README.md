# YARRRMLMapper
A Python3 implementation of YARRRML Mapper

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

You can transform a json file into an RDF (ttl) file using a YARRRML Mapping with the following command:
```bash
python YARRRMLMapper.py <source> <destination>.ttl <mapping>
```

example:
> Files are in root directory (YARRRMLMapper/)
```bash
python YARRRMLMapper.py data.json data.ttl mapping.yml
```