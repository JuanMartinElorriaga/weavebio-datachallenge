from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.neo4j.operators.neo4j import Neo4jOperator
from airflow.hooks.base_hook import BaseHook
from datetime import datetime, timedelta
from py2neo import Graph, Node, Relationship
import xml.dom.minidom as minidom
from os import environ
from dotenv import load_dotenv
load_dotenv()

# Instanciate neo4j hook after configuring it in the Airflow UI
neo4j_conn = BaseHook.get_connection("neo4j_default")

# Default arguments for the DAG
default_args = {
    'owner'           : 'airflow',
    'depends_on_past' : False,
    'start_date'      : datetime(2023, 3, 18),
    'email_on_failure': False,
    'email_on_retry'  : False,
    'retries'         : 0,
    'retry_delay'     : timedelta(minutes=2),
}

def download_uniprot_xml():
    # Download file to /tmp directory using curl command
    import subprocess
    subprocess.call(['curl', '-o', '/opt/airflow/dags/Q9Y261.xml', 'https://github.com/weavebio/data-engineering-coding-challenge/blob/main/data/Q9Y261.xml'])

# Define the PythonOperator to process the UniProt XML file and store the data in Neo4j
def process_uniprot_xml():
    # Open the XML file
    with open('/opt/airflow/dags/Q9Y261.xml', 'r') as f:
        xml_str = f.read()
    # Parse the XML using minidom
    dom = minidom.parseString(xml_str)
    # Get the root element
    root = dom.documentElement

    # Iterate over the entry elements and create nodes and relationships
    entries = root.getElementsByTagName('entry')
    for entry in entries:
        # Extract information from the entry
        protein   = entry.getElementsByTagName('protein')[0]
        gene      = entry.getElementsByTagName('gene')[0]
        organism  = entry.getElementsByTagName('organism')[0]
        reference = entry.getElementsByTagName('reference')[0]

        # Create nodes for the protein, gene, organism, and reference
        protein_node   = Node('Protein', name=protein.getElementsByTagName('fullName')[0].firstChild.nodeValue)
        gene_node      = Node('Gene', name=gene.getAttribute('name'))
        organism_node  = Node('Organism', name=organism.getElementsByTagName('name')[0].firstChild.nodeValue)
        reference_node = Node('Reference', key=reference.getAttribute('key'))

        # Create relationships between the nodes
        protein_gene_rel      = Relationship(protein_node, 'FROM_GENE', gene_node)
        gene_organism_rel     = Relationship(protein_node, 'IN_ORGANISM', organism_node)
        protein_reference_rel = Relationship(protein_node, 'HAS_REFERENCE', reference_node)
        
        graph  = Graph("bolt://neo4j_host:7687", auth=("neo4j", "user_password"))
        print(f"connection to graph successfull: {graph}") 

        graph.create(protein_node)
        graph.create(gene_node)
        graph.create(organism_node)
        graph.create(reference_node)
        graph.create(protein_gene_rel)
        graph.create(gene_organism_rel)
        graph.create(protein_reference_rel)
        print(f"graphs added to model")  

# Define the PythonOperator to query the Neo4j graph database
def query_neo4j():
    # Connect to the Neo4j graph database
    graph  = Graph("bolt://neo4j_host:7687", auth=("neo4j", "user_password"))
    # Define a Cypher query to retrieve the number of Protein nodes in the graph
    cypher_query = 'MATCH (p:Protein) RETURN count(p)'

    # Execute the query using the Neo4j driver and print the result
    result = graph.run(cypher_query).evaluate()
    print(f'Number of Protein nodes: {result}')

with DAG('uniprot_neo4j_pipeline', default_args=default_args, schedule_interval=timedelta(days=1)) as dag:
    # Define the BashOperator to download the UniProt XML file
    download_op = PythonOperator(
        task_id         = 'download_file',
        python_callable = download_uniprot_xml,
    )

    # Define the PythonOperator to process the UniProt XML file
    process_op = PythonOperator(
        task_id         = 'process_uniprot_xml',
        python_callable = process_uniprot_xml
    )

    # Define the Neo4jOperator to create an index on the Protein nodes
    create_index_op = Neo4jOperator(
        task_id       = 'create_index',
        sql           = 'CREATE INDEX FOR (n:Protein) ON (n.accession)',
        neo4j_conn_id = 'neo4j_default'
    )

    # Define the PythonOperator to query the Neo4j graph database
    query_op = PythonOperator(
        task_id         = 'query_neo4j',
        python_callable = query_neo4j
    )

    # Set the dependencies between the tasks
    download_op >> process_op >> create_index_op >> query_op