# Source Data repo for InTaVia Knhowledge Graph
This repo is used for ingesting named graphs into the InTaVia Knowledge Graph (IKG).

To ingest your data:
- prepare your data according to [IDM-RDF](https://github.com/InTaVia/idm-rdf) and the [Shacl shapes](IKG_shacl_shapes.ttl) as a turtle file
- add the prepared ttl to the `datasets` folder
- if you are adding your data the first time, add the metadata of yor graph to the [datasets.yml](datasets.yml) file
- create a PR with these changes against main

After you created the PR a validation against the shacl constraints is performed. If your data is valid it will be merged to main and pushed to the IKG.

**For the moment please commit only one turtle file per PR**