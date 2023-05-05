# module that generates a provenance graph from a given ttl file and pushes it to a triple store
import datetime
import os
import subprocess
from SPARQLWrapper import SPARQLWrapper, JSON
import click
from rdflib import PROV, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
import requests
import yaml


@click.command()
@click.option("--file", required=True, help="Turtle File to ingest in the IKG")
@click.option(
    "--config", default="datasets.yml", help="Path of the configuration Yaml to use."
)
@click.option("--provenance_graph", default="http://www.provenance.intavia.eu")
@click.option("--triplestore", default=None)
def ingest_file_in_ikg(file: str, config: str, provenance_graph: str, triplestore: str):
    if triplestore is None:
        triplestore = os.environ.get("INTAVIA_TRIPLESTORE")
    sparql = SPARQLWrapper(triplestore)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)
    if not triplestore.startswith("http://127.0.0.1:8080"):
        sparql.setHTTPAuth("BASIC")
        sparql.setCredentials(
            user=os.environ.get("SPARQL_USER"), passwd=os.environ.get("SPARQL_PASSWORD")
        )
    with open(config, "r") as conf:
        conf = yaml.safe_load(conf)
        d_set = None
        for dataset in conf["datasets"]:
            if f'datasets/{dataset["file"]}' == file:
                print("Found dataset")
                d_set = dataset
                break
        if d_set is None:
            raise Exception("Dataset not found")
        else:
            ng = URIRef(
                f"{d_set['namespace']}{'' if d_set['namespace'].endswith('/') else '/'}{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
            )
            ng_ds_root = URIRef(
                f"{d_set['namespace']}{'' if d_set['namespace'].endswith('/') else '/'}"
            )
            g = Graph()
            ns_intavia = Namespace("http://www.intavia.eu/prov#")
            g.bind("intavia-prov", ns_intavia)
            g.add((ng, RDF.type, PROV.Collection))
            g.add((ng, RDF.type, ns_intavia.Dataset))
            g.add((ng, ns_intavia.dataset_for, ng_ds_root))
            g.add((ng, ns_intavia.latest_version_for, ng_ds_root))
            g.add((ng_ds_root, RDFS.label, Literal(d_set["name"])))
            g.add(
                (
                    ng,
                    ns_intavia.valid_from,
                    Literal(
                        datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        datatype=XSD.dateTime,
                    ),
                )
            )
            g.serialize(destination="provenance_graph.ttl")
            sparql_insert_valid_until = f"""
            # insert valid until statement for previous version
            INSERT {{
                GRAPH <{provenance_graph}> {{
                    ?dataset <{ns_intavia}valid_until> "{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}"^^<http://www.w3.org/2001/XMLSchema#dateTime>
                    }}
                    }}
                    WHERE {{
                        GRAPH <{provenance_graph}> {{?dataset <{ns_intavia}latest_version_for> <{ng_ds_root}> .
                                    FILTER NOT EXISTS {{ ?dataset <{ns_intavia}valid_until> ?date }}
                        }}
                    }}
                    """
            sparql.setQuery(sparql_insert_valid_until)
            sparql.query()
            sparql_query_delete = f"""
            # delete latest statement from dataset root
            DELETE  {{
                GRAPH <{provenance_graph}> {{?dataset <http://www.intavia.eu/prov#latest_version_for> <{ng_ds_root}>}}
            }}
            WHERE {{
                GRAPH <{provenance_graph}> {{?dataset <http://www.intavia.eu/prov#latest_version_for> <{ng_ds_root}>}}
            }}
            """
            sparql.setQuery(sparql_query_delete)
            sparql.query()
            data = open("provenance_graph.ttl", "rb").read()
            headers = {
                "Content-Type": "application/x-turtle",
            }
            params = {"context-uri": provenance_graph}
            upload = requests.post(
                triplestore,
                data=data,
                headers=headers,
                params=params,
                auth=requests.auth.HTTPBasicAuth(
                    os.environ.get("SPARQL_USER"), os.environ.get("SPARQL_PASSWORD")
                ),
            )
            params = {"context-uri": ng}
            data = open(f"datasets/{d_set['file']}", "rb").read()
            upload = requests.post(
                triplestore,
                data=data,
                headers=headers,
                params=params,
                auth=requests.auth.HTTPBasicAuth(
                    os.environ.get("SPARQL_USER"), os.environ.get("SPARQL_PASSWORD")
                ),
            )


if __name__ == "__main__":
    ingest_file_in_ikg()
