from tqdm import tqdm
import pandas as pd
from neo4j import GraphDatabase, exceptions

from dotenv import load_dotenv
from src.chains import create_question_generator_chain

# Connect to the Neo4j database

load_dotenv()

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self.schema = None

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters = parameters)
            return [record for record in result]

    def execute_queries(self, queries, parameters = None):
        with self._driver.session() as session:
            results = []
            for query in tqdm(queries):
                try:
                    result = session.run(query, parameters = parameters)
                    data = result.data()
                    summary = result.consume()

                    if summary.notifications:
                        print('\nWARNING')
                        results.append((None, False))
                    else:
                        print('\nQUERY CORRECTLY EXECUTED')
                        results.append((data, True))

                except exceptions.ClientError as e:
                    results.append((None, False))
                except exceptions.TransientError as e:
                    results.append((None, False))
                except exceptions.DatabaseError as e:
                    results.append((None, False))

                except Exception as e:
                    print(f"Error executing query: {query}\n{e}")
                    results.append((None, False))

            return results

    # retrieve schema
    def retrieve_schema(self):
        with self._driver.session() as session:
            schema = {}
            # Get node labels
            node_attributes = session.run('''MATCH (n)
                                             UNWIND labels(n) AS node_type
                                             WITH node_type, COLLECT(DISTINCT keys(n)) AS attribute_lists
                                             UNWIND attribute_lists AS attributes
                                             RETURN node_type, COLLECT(DISTINCT attributes) AS attribute_keys''')

            schema['node_types'] = {node_attr['node_type']: node_attr['attribute_keys'] for node_attr in node_attributes}
            # Get relationship types
            result = session.run("CALL db.relationshipTypes()")
            schema['relationship_types'] = [record['relationshipType'] for record in result]
            self.schema = schema
        return schema

    # define Schema Formatting Function
    def format_schema(self, schema):
        node_properties = schema['node_types']
        relationship_properties = schema['relationship_types']
        schema_str = "### Node Labels and Properties ###\n"
        for label, properties in node_properties.items():
            schema_str += f"{label}:\n"
            for prop in properties:
                schema_str += f"  - {prop}\n"
        schema_str += "\n### Relationship Types and Properties ###\n"
        for rel in relationship_properties:
            schema_str += f"- `{rel}`\n"
        return schema_str

    def get_central_nodes(self, schema, limit=50):
        result = {}
        for node_type in schema['node_types']:
            query = f"MATCH (n:{node_type}) RETURN n.displayName AS name, COUNT  {{(n)--() }} AS degree ORDER BY degree DESC LIMIT $limit"
            central_nodes = self.query(query, parameters={'limit': limit})
            result[node_type] = pd.DataFrame(
                [{"name": record["name"], "degree": record["degree"]} for record in central_nodes])
        return result

    # create 100 examples for validation

    def generate_questions(formatted_schema, N=100):
        gen_questions = []
        while len(gen_questions) < N:
            generator_chain = create_question_generator_chain()
            questions = generator_chain.invoke({'schema': formatted_schema, 'num_questions': 10, 'node_type': ''})
            gen_questions.extend(questions.questions)
            print(f'{len(gen_questions)} questions generated')
        with open('val_questions.pkl', 'wb') as f:
            pickle.dump(gen_questions, f)
        return gen_questions
