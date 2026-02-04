import json
import os
import time
from tqdm import tqdm

from src.chains import create_question_generator_chain, create_translator_chain

def generate_synthetic_data(neo4j_client, schema, node_type, num_questions_per_batch=5, N = 100, dir_name = f'successful'):


    generator_chain = create_question_generator_chain()
    translator_chain = create_translator_chain()

    successful_queries = []
    # list to compute statistics
    len_gen_queries = []
    len_succ_queries = []

    # Get central entities per node type
    not_formatted_schema = neo4j_client.retrieve_schema()
    central_nodes = list(neo4j_client.get_central_nodes(not_formatted_schema)[node_type].name)
    pbar = tqdm(total=N)
    while len(successful_queries) < N:
        # Generate a batch of natural language questions
        questions_batch = generator_chain.invoke({
            "schema": schema,
            "num_questions": num_questions_per_batch,
            "node_type": node_type,
            "central_entities":central_nodes
        }).questions

        # Clean questions and remove empty strings
        questions_batch = [q.strip() for q in questions_batch if q.strip()]

        # Translate batch of questions to Cypher
        cypher_queries_batch = translator_chain.invoke(
            {"context": '',
             "questions": questions_batch,
             "schema": schema,
             "num_questions": num_questions_per_batch
             }).questions

        queries = [couples['cypher_translation'] for couples in cypher_queries_batch]
        len_gen_queries.append(len(queries))
        # Step 3: Execute Cypher queries in batch
        results = neo4j_client.execute_queries(queries, parameters={'limit': 1})
        success = [res[1] for res in results]

        # Collect successful queries
        successful_queries.extend([a for a, b in zip(cypher_queries_batch, success) if b])
        num_succ_queries = len([a for a, b in zip(cypher_queries_batch, success) if b])
        len_succ_queries.append(num_succ_queries)
        pbar.update(num_succ_queries)

    # Save successful queries to a file
    try:
        os.makedirs(os.path.join(dir_name), exist_ok=True)
    except FileExistsError:
        pass
    output_file = os.path.join(dir_name, f'successful_queries_{node_type}.json')
    # Save list to compute statistics HERE
    with open(output_file, "w") as f:
        json.dump(successful_queries, f, indent=4)
    print(f"Stored {len(successful_queries)} successful NL-Cypher pairs in {output_file}.")
    time.sleep(3)
    pbar.close()

    return len_gen_queries, len_succ_queries





