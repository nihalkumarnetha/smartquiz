import mysql.connector
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin@123',
    'database': 'smartquiz'
}

# Python Quiz Questions
python_questions = [
    {
        "question": "What is the correct way to create a list in Python?",
        "option_a": "list = []",
        "option_b": "list = ())",
        "option_c": "list = {}",
        "option_d": "list = ><",
        "correct_answer": "A",
        "difficulty_level": "Easy"
    },
    {
        "question": "Which of the following is a mutable data type in Python?",
        "option_a": "Tuple",
        "option_b": "String",
        "option_c": "List",
        "option_d": "Frozenset",
        "correct_answer": "C",
        "difficulty_level": "Easy"
    },
    {
        "question": "What does the 'len()' function return?",
        "option_a": "The length of an object",
        "option_b": "The type of an object",
        "option_c": "The memory address of an object",
        "option_d": "The value of an object",
        "correct_answer": "A",
        "difficulty_level": "Easy"
    },
    {
        "question": "Which keyword is used to create a function in Python?",
        "option_a": "function",
        "option_b": "def",
        "option_c": "func",
        "option_d": "define",
        "correct_answer": "B",
        "difficulty_level": "Easy"
    },
    {
        "question": "What is the output of 'print(3 ** 2)'?",
        "option_a": "6",
        "option_b": "9",
        "option_c": "5",
        "option_d": "12",
        "correct_answer": "B",
        "difficulty_level": "Easy"
    },
    {
        "question": "How do you create a dictionary in Python?",
        "option_a": "dict = {}",
        "option_b": "dict = []",
        "option_c": "dict = ()",
        "option_d": "dict = set()",
        "correct_answer": "A",
        "difficulty_level": "Medium"
    },
    {
        "question": "Which method is used to add an element to a list?",
        "option_a": "add()",
        "option_b": "append()",
        "option_c": "insert()",
        "option_d": "extend()",
        "correct_answer": "B",
        "difficulty_level": "Medium"
    },
    {
        "question": "What is the correct way to handle an exception in Python?",
        "option_a": "try-except",
        "option_b": "try-catch",
        "option_c": "catch-throw",
        "option_d": "if-else",
        "correct_answer": "A",
        "difficulty_level": "Medium"
    },
    {
        "question": "Which of the following is NOT a valid Python variable name?",
        "option_a": "my_var",
        "option_b": "2_var",
        "option_c": "_var",
        "option_d": "var_2",
        "correct_answer": "B",
        "difficulty_level": "Medium"
    },
    {
        "question": "What does 'range(5)' return?",
        "option_a": "A list from 1 to 5",
        "option_b": "A range object from 0 to 4",
        "option_c": "A list from 0 to 5",
        "option_d": "A tuple from 0 to 5",
        "correct_answer": "B",
        "difficulty_level": "Medium"
    },
    {
        "question": "Which of the following is a valid way to comment in Python?",
        "option_a": "// This is a comment",
        "option_b": "# This is a comment",
        "option_c": "<!-- This is a comment -->",
        "option_d": "/* This is a comment */",
        "correct_answer": "B",
        "difficulty_level": "Easy"
    },
    {
        "question": "What is the purpose of the 'self' parameter in a class method?",
        "option_a": "To reference the current instance of the class",
        "option_b": "To reference the class itself",
        "option_c": "To reference the parent class",
        "option_d": "To reference global variables",
        "correct_answer": "A",
        "difficulty_level": "Hard"
    },
    {
        "question": "How do you create a set in Python?",
        "option_a": "set = []",
        "option_b": "set = {}",
        "option_c": "set = set()",
        "option_d": "set = ()",
        "correct_answer": "C",
        "difficulty_level": "Medium"
    },
    {
        "question": "What is the output of 'print(\"Hello\" + \" \" + \"World\")'?",
        "option_a": "Hello World",
        "option_b": "HelloWorld",
        "option_c": "Hello + + World",
        "option_d": "Error",
        "correct_answer": "A",
        "difficulty_level": "Easy"
    },
    {
        "question": "Which method converts a string to lowercase?",
        "option_a": "lower()",
        "option_b": "toLower()",
        "option_c": "lowercase()",
        "option_d": "downcase()",
        "correct_answer": "A",
        "difficulty_level": "Easy"
    },
    {
        "question": "What is a lambda function in Python?",
        "option_a": "A function with no name that takes one argument",
        "option_b": "An anonymous function that can take multiple arguments",
        "option_c": "A function that returns a lambda expression",
        "option_d": "A type of class definition",
        "correct_answer": "B",
        "difficulty_level": "Hard"
    },
    {
        "question": "How do you check the type of a variable?",
        "option_a": "check_type()",
        "option_b": "type()",
        "option_c": "isinstance()",
        "option_d": "Both B and C",
        "correct_answer": "D",
        "difficulty_level": "Medium"
    },
    {
        "question": "What is the difference between '==' and 'is' in Python?",
        "option_a": "'==' compares values, 'is' compares identity",
        "option_b": "'is' compares values, '==' compares identity",
        "option_c": "They are the same",
        "option_d": "'is' is only for strings",
        "correct_answer": "A",
        "difficulty_level": "Hard"
    },
    {
        "question": "What does 'enumerate()' do in Python?",
        "option_a": "Converts a list to a tuple",
        "option_b": "Returns index and value pairs from an iterable",
        "option_c": "Removes duplicate elements",
        "option_d": "Sorts a list",
        "correct_answer": "B",
        "difficulty_level": "Medium"
    },
    {
        "question": "How do you import a specific function from a module?",
        "option_a": "import module.function",
        "option_b": "from module import function",
        "option_c": "import function from module",
        "option_d": "function import module",
        "correct_answer": "B",
        "difficulty_level": "Medium"
    }
]

def create_python_quiz():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 60)
        print("CREATE PYTHON QUIZ")
        print("=" * 60)
        
        # First, create a lecturer account if it doesn't exist
        lecturer_username = "lecturer_python"
        lecturer_password = generate_password_hash('123456')
        lecturer_email = "lecturer_python@gmail.com"
        
        print(f"\n[STEP 1] Checking for lecturer account...")
        cursor.execute("SELECT id FROM users WHERE username = %s AND role = 'lecturer'", (lecturer_username,))
        lecturer = cursor.fetchone()
        
        if not lecturer:
            print(f"[INFO] Creating new lecturer account: {lecturer_username}")
            cursor.execute(
                "INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)",
                (lecturer_username, lecturer_password, 'lecturer', lecturer_email)
            )
            conn.commit()
            cursor.execute("SELECT id FROM users WHERE username = %s", (lecturer_username,))
            lecturer = cursor.fetchone()
            print(f"✓ Lecturer account created with ID: {lecturer['id']}")
        else:
            print(f"✓ Lecturer account found with ID: {lecturer['id']}")
        
        lecturer_id = lecturer['id']
        
        # Create the quiz
        print(f"\n[STEP 2] Creating Python quiz...")
        quiz_title = "Python Programming Fundamentals"
        quiz_description = "A comprehensive quiz covering Python basics, data structures, functions, OOP, and advanced concepts"
        quiz_duration = 60
        
        cursor.execute(
            "INSERT INTO quizzes (title, description, created_by, duration) VALUES (%s, %s, %s, %s)",
            (quiz_title, quiz_description, lecturer_id, quiz_duration)
        )
        conn.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID() as quiz_id")
        quiz = cursor.fetchone()
        quiz_id = quiz['quiz_id']
        print(f"✓ Quiz created with ID: {quiz_id}")
        
        # Insert questions
        print(f"\n[STEP 3] Adding {len(python_questions)} questions to the quiz...")
        inserted_count = 0
        
        for i, q in enumerate(python_questions, 1):
            cursor.execute(
                "INSERT INTO questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_answer) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (quiz_id, q['question'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer'])
            )
            inserted_count += 1
            print(f"  {i}. {q['question'][:50]}... [{q['difficulty_level']}]")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("QUIZ CREATION SUMMARY")
        print("=" * 60)
        print(f"Quiz Title: {quiz_title}")
        print(f"Quiz ID: {quiz_id}")
        print(f"Lecturer: {lecturer_username} (ID: {lecturer_id})")
        print(f"Duration: {quiz_duration} minutes")
        print(f"Questions: {inserted_count}")
        print(f"Difficulty Distribution: Easy, Medium, Hard")
        print("\n✓ Python quiz created successfully!")
        print(f"\nQuiz Details:")
        print(f"  - Lecturer Login: {lecturer_username} / 123456")
        print(f"  - Quiz ID: {quiz_id}")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    create_python_quiz()
