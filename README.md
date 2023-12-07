[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10290206.svg)](https://doi.org/10.5281/zenodo.10290206)

# Source Data repo for InTaVia Knowledge Graph
This repo is used for ingesting named graphs into the InTaVia Knowledge Graph (IKG).
The idea of the repository is to have a versioned source of truth that performs data validation (via SHACL) 
and creates versioning/provenance triples using GitHub actions.
Pushes to the triplestore are only done from main. Following main branch it is therefore easily possible
to recreate any previous state of the InTaVia triplestore.
This fact is also used by the versioning system of the InTaVia Knowledge Graph as new versions of a named graph in the 
IKG does not replace the old. Instead a new named graph is uploaded and provenance information is added to the 
provenance graph.

## How to contribute

To ingest your data:
- prepare your data according to [IDM-RDF](https://github.com/InTaVia/idm-rdf) and the [Shacl shapes](IKG_shacl_shapes.ttl) as a turtle file
- add the prepared ttl to the `datasets` folder
- if you are adding your data the first time, add the metadata of yor graph to the [datasets.yml](datasets.yml) file
- create a PR with these changes against main

After you created the PR a validation against the shacl constraints is performed. If your data is valid it will be merged to main and pushed to the IKG.

**For the moment please commit only one turtle file per PR**
