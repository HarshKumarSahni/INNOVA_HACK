prompt_templates = {
    "MTF": """Match the Following type
topics - 
{topics}

difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line. create {num} - Match The Following type questions like this - very {exam} type, and very analytical.
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Match the following network types with their most appropriate characteristics:\\n1. Network Type\\tCharacteristic\\nI. LAN\\tA. Covers a metropolitan area\\nII. MAN\\tB. Intercontinental\\n...",
      "options": ["I-C, II-A, III-B, IV-D", "I-C, II-D, III-A, IV-B", "I-B, II-C, III-A, IV-D", "I-B, II-A, III-D, IV-C"],
      "correct_answer": 1, 
      "solution": "LAN: Local Area Network... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "2S": """2 statement type
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic.
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Consider the following two statements related to parsing techniques:\\nStatement I: LL(1) parsers cannot handle left-recursive grammars.\\nStatement II: LR parsers perform better...\\nIn light of the above statements, choose the correct answer from the options given below:",
      "options": ["Both Statement I and Statement II are correct", "Both Statement I and Statement II are incorrect", "Statement I is correct but Statement II is incorrect", "Statement I is incorrect but Statement II is correct"],
      "correct_answer": 1, 
      "solution": "Statement I(Correct): ... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "3S" : """3 statement type
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic.
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Which of the following statements about firewalls and intrusion detection systems are correct?\\nI. A firewall can prevent unauthorized access...\\nII. IDS can take automatic action...\\nIII. Stateful firewalls monitor...\\nWhich of the following is correct?",
      "options": ["I and II only", "I and III only", "II and III only", "All of the above"],
      "correct_answer": 2, 
      "solution": "Statement I(Correct): ... Hence, Option (2) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "4S": """4 statement type
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct.
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Which of the following statements about FCFS scheduling are correct?\\nI. FCFS scheduling can lead to convoy effect.\\nII. Average waiting time is minimum...\\nIII. FCFS scheduling is non-preemptive.\\nIV. Processes are scheduled in the order they arrive.\\nChoose the correct answer:",
      "options": ["I, II, and III only", "II and III only", "I, III, and IV only", "All of the above"],
      "correct_answer": 3, 
      "solution": "Statement I(Correct): ... Hence, Option (3) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "5S": """5 statement type
topics - 
{topics}
difficulty - *EXTREMELY* HARD, *EXTREMELY* ANALYTICAL.
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Consider the following five statements...\\nI...\\nII...\\nIII...\\nIV...\\nV...\\nWhich of the following is correct?",
      "options": ["I, II, and III only", "II and III only", "I, III, and IV only", "All of the above"],
      "correct_answer": 3, 
      "solution": "Statement I(Correct): ... Hence, Option (3) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "SL": """Single-liner scenario-based questions
topics - 
{topics}
difficulty - MODERATE
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Which of the following describes...",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 1, 
      "solution": "Explanation... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "AR": """Assertion and Reasoning questions
topics - 
{topics}
difficulty - MODERATE
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Given two statements, Assertion (A) and Reason (R)...\\nAssertion (A): ...\\nReason (R): ...",
      "options": ["Both A and R are true and R is the correct explanation of A", "Both A and R are true but R is NOT the correct explanation of A", "A is true but R is false", "A is false but R is true"],
      "correct_answer": 1, 
      "solution": "Explanation... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "CS": """Case study comprehension questions
topics - 
{topics}
difficulty - MODERATE
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Read the following case study carefully...\\nCase: ...\\nQuestion: ...",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 1, 
      "solution": "Explanation... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "CH": """Chronological ordering questions
topics - 
{topics}
difficulty - MODERATE
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Arrange the following in chronological order:\\nA...\\nB...\\nC...\\nD...\\nOptions:",
      "options": ["A, B, C, D", "B, A, D, C", "C, D, B, A", "D, C, A, B"],
      "correct_answer": 1, 
      "solution": "Explanation... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "FU": """Fill in the Blanks questions
topics - 
{topics}
difficulty - MODERATE
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "The process of ______ is known as ______.",
      "options": ["A, B", "C, D", "E, F", "G, H"],
      "correct_answer": 1, 
      "solution": "Explanation... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "MCQ": """Multiple choice questions
topics - 
{topics}
difficulty - MODERATE
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "What is the primary function of...?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 1, 
      "solution": "Explanation... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array.""",

    "NU": """Numerical answer type questions
topics - 
{topics}
difficulty - MODERATE
answer key: {answer_key}
You must output ONLY valid JSON containing the following structure:
{{
  "questions": [
    {{
      "question": "Calculate the value of...?",
      "options": ["10", "20", "30", "40"],
      "correct_answer": 1, 
      "solution": "Explanation... Hence, Option (1) is the right answer."
    }}
  ]
}}
The 'correct_answer' index should be 1-based (i.e. 1, 2, 3, or 4) matching the {answer_key} you received. Output exactly {num} questions inside the array."""
}