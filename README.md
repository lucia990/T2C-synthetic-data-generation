# Synthetic NL ↔ Cypher Data Generation Tool

## Overview

This tool generates **synthetic natural language (NL) questions and corresponding Cypher queries** from a Neo4j graph database.  
It is designed primarily for **biological knowledge graphs**, but can be adapted for other domains.  

The tool performs the following steps:

1. Connects to a Neo4j database and retrieves its schema.  
2. Selects nodes to process (all nodes, included nodes or excluding certain nodes).  
3. Generates batches of natural language questions for each node type.  
4. Translates these questions into Cypher queries.  
5. Executes queries on Neo4j to determine which are successful.  
6. Saves successful queries for further use or analysis.  

---

## Features

- **Batch generation:** Generate multiple questions per node in each iteration.  
- **Selective node processing:** Include or exclude specific node types.  
- **Automatic saving:** Saves generated and successful queries in JSON format.  
- **Environment-based configuration:** Connection credentials are loaded from environment variables.  

---

## Installation

1. Clone the repository:

```bash
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_DIRECTORY>
```

2. Install dependencies: 
```bash
pip install -r requirements.txt
```

3. Set up environment variables
The tool requires the following environment variables:
    NEO4J_URI:	Neo4j connection URI (e.g., bolt://localhost:7687)
    NEO4J_USER:	Neo4j username
    NEO4J_PASSWORD:	Neo4j password
    GOOGLE_API_KEY:	API key for question generation (if using Google-based services)
    OLLAMA_COSY_API_KEY:  API key for cosybio ollama server usage

NOTE: Missing any required variable will raise an EnvironmentError.

## Usage

```bash
python -m results.bootstrapped_examples.py \
      --batch-size 5 \
      --iterations 10 \
      --output-dir GS_candidates \
      --include-nodes Gene Protein \
      --exclude-nodes Disease
```

where

| Argument          | Type | Default         | Description                                                    |
| ----------------- | ---- | --------------- | -------------------------------------------------------------- |
| `--batch-size`    | int  | 5               | Number of questions to generate per batch                      |
| `--iterations`    | int  | 10              | Total number of successful questions to generate per node type |
| `--output-dir`    | str  | `GS_candidates` | Directory to store generated and successful queries            |
| `--include-nodes` | list | None            | List of node types to **include** for generation               |
| `--exclude-nodes` | list | None            | List of node types to **exclude** from generation              |

Note: include-nodes and exclude-nodes are mutually exclusive.
If neither is provided, all node types from the database are processed.

## Python API

You can also use the main function programmatically:

```python
from results.bootstrapped_examples import run_generation
generated, successful = run_generation(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    num_questions_per_batch=5,
    n_iterations=100,
    output_dir="GS_candidates",
    include_nodes=["Gene", "Protein"],   # Optional
    exclude_nodes=None                    # Optional
)
```

## Internal workflow

1. Connect to Neo4j:
Establish a connection using Neo4jConnection and retrieve the database schema.

2. Node selection:
Determine which node types to process based on include_nodes or exclude_nodes.

3. Synthetic Data Generation (generate_synthetic_data):

    - Generate natural language questions with create_question_generator_chain.

    - Translate questions into Cypher with create_translator_chain.

    - Execute Cypher queries and collect successful results.

    - Repeat until N successful queries per node type are collected.

4. Data Storage:
Saves JSON files under successful_queries/<output_dir>/

## Default parameters
\| Parameter                 | Default           | Description                                      |
| ------------------------- | ----------------- | ------------------------------------------------ |
| `num_questions_per_batch` | 5                 | Number of questions generated in a single batch  |
| `n_iterations`            | 100               | Total number of successful queries per node type |
| `output_dir`              | `'GS_candidates'` | Directory where JSON output is saved             |


## Example workflow

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export GOOGLE_API_KEY="your-google-api-key"
export OLLAMA_COSY_API_KEY="your-ollama-api-key"

python generate_data.py --batch-size 10 --iterations 50
```
- Connects to Neo4j at bolt://localhost:7687. (NeDRex)

- Generates 10 questions per batch until 50 successful queries per node type.

- Stores results in successful_queries/GS_candidates/.
