Return a JSON string having the NL question and the corresponding Cypher translation.
The schema for the questions is fixed: 
Example: 

dict(
"questions": [
    dict(
      "nl_question": "<nl_question_1>",
      "cypher_translation": "<cypher_translation_1>"
    ),
    dict(
      "nl_question": "<nl_question_2>",
      "cypher_translation": "<cypher_translation_2>"
    ),
    dict(
      "nl_question": "<nl_question_3>",
      "cypher_translation": "<cypher_translation_3>"
    ),
    ...
    dict(
      "nl_question": "<nl_question_{num_questions}>",
      "cypher_translation": "<cypher_translation_{num_questions}>"
    )
  ]
)

IMPORTANT: keys must be "nl_questions" and "cypher_translation"! Do not use synonyms!