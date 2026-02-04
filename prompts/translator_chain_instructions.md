You will receive a list of {num_questions} natural language biomedical questions.
\n {questions}
Translate each of them in Cypher, keeping in mind that this is the schema: {schema}

A context is added to figure out the names of the entities in the database. 
Context: {context}
Use also the other information to find the appropriate entity. 
Example Query Templates:

MATCH (g:Gene)-[:GeneExpressedInTissue]->(t:Tissue)
WHERE toLower(g.displayName) CONTAINS 'genenamehere'
RETURN g.displayName AS GeneName, t.displayName AS TissueN

If available, use examples: 

{{examples}}