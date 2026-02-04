Return natural language questions in a JSON array with {num_questions} questions and a unique key: "questions". 
IMPORTANT: Do not use synonyms for the key. It must be "questions"!
The schema for the questions is fixed: 
Example: 

dict(
    "questions": [
        "<question_1>",
        "<question_2>",
        "<question_3>",
        ...
        "<question_{num_questions}>"
    ]
)