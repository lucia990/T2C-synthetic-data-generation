Given the following knowledge graph schema {schema}, to generate {num_questions} natural language questions to query this kind of database. 
Focus on a particular node type: {node_type}
Imagine all the types of questions that can be asked by an expert in the field, e.g. clinician, biologist, doctors,...
Here follows a list of examples of real entities you can use: 
Top-50 central nodes: {central_entities}


Return just a JSON array of {num_questions} strings with an unique key: "questions".