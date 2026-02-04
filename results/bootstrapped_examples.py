import os
import json
from tqdm import tqdm
import argparse
from typing import List

from src.neo4j_connection import Neo4jConnection
from src.bootstrapping import generate_synthetic_data

from dotenv import load_dotenv
load_dotenv()


def run_generation(
    uri: str,
    user: str,
    password: str,
    num_questions_per_batch: int = 5,
    n_iterations: int = 100,
    output_dir: str = 'GS_candidates',
    include_nodes: List[str] | None = None,
    exclude_nodes: List[str] | None = None
):
    print("[DEBUG] Connecting to Neo4j...")
    conn = Neo4jConnection(uri, user, password)

    print("Retrieving schema...")
    schema = conn.retrieve_schema()
    print(f"Retrieved schema with node types: {list(schema['node_types'].keys())}")

    formatted_schema = conn.format_schema(schema)
    all_nodes = list(schema["node_types"].keys())

    if include_nodes:
        nodes = [n for n in all_nodes if n in include_nodes]
        print(f"[DEBUG] Including only nodes: {nodes}")
    elif exclude_nodes:
        nodes = [n for n in all_nodes if n not in exclude_nodes]
        print(f"Excluding nodes: {exclude_nodes}, remaining nodes: {nodes}")
    else:
        nodes = all_nodes
        print(f"Processing all nodes: {nodes}")

    generated = {}
    successful = {}

    for idx, node in enumerate(tqdm(nodes, desc="Processing nodes")):
        print(f"Starting generation for node {idx + 1}/{len(nodes)}: {node}")
        try:
            generated[node], successful[node] = generate_synthetic_data(
                conn,
                formatted_schema,
                node,
                num_questions_per_batch=num_questions_per_batch,
                N=n_iterations,
                dir_name=output_dir,
            )
            print(f"Finished generation for node: {node}")

            # Ensure output directory exists
            out_dir = os.path.join("successful_queries", output_dir)
            os.makedirs(out_dir, exist_ok=True)


        except Exception as e:
            print(f"[ERROR] Node {node} failed: {e}")

    conn.close()
    print("[DEBUG] Closed Neo4j connection")
    return generated, successful



def load_neo4j_from_env():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    missing = [k for k, v in {
        "NEO4J_URI": uri,
        "NEO4J_USER": user,
        "NEO4J_PASSWORD": password,
    }.items() if v is None]

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return uri, user, password

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate biological ↔ Cypher query pairs from a Neo4j graph"
    )

    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--output-dir", default="GS_candidates")

    parser.add_argument(
        "--include-nodes",
        nargs="*",
        help="Only generate data for these node types (default: all nodes from Neo4j)"
    )

    parser.add_argument(
        "--exclude-nodes",
        nargs="*",
        help="Exclude these node types from generation"
    )
    return parser.parse_args()

if __name__ == "__main__":

    args = parse_args()

    uri, user, password = load_neo4j_from_env()

    conn = Neo4jConnection(uri, user, password)



    run_generation(
        uri=uri,
        user=user,
        password=password,
        num_questions_per_batch=args.batch_size,
        n_iterations=args.iterations,
        output_dir=args.output_dir,
        include_nodes=args.include_nodes,
        exclude_nodes=args.exclude_nodes,
    )

    conn.close()



