"""Shared quiz content for the Lab 2 Section 3 study app.

Two matched-difficulty, 5-question general-knowledge quiz sets with
different content (so returning participants can't rely on already
knowing the answers). Quiz set 1 is always used in session 1; quiz set
2 is always used in session 2, for every participant -- the CONDITION
(A vs B) assigned to each session is what varies per participant, via
CONDITION_SEQUENCE in main.py ("AB", "BA", "AA", or "BB").
"""

QUESTION_SETS = {
    1: [
        {
            "id": "set1_q1",
            "question": "What is the name of our planet?",
            "answer": "Earth",
            "explanation": "Earth is the third planet from the Sun and the only one known to support life.",
        },
        {
            "id": "set1_q2",
            "question": "How many days are there in a week?",
            "answer": "Seven",
            "explanation": "A week has seven days, Monday through Sunday.",
        },
        {
            "id": "set1_q3",
            "question": "What color do you get when you mix blue and yellow?",
            "answer": "Green",
            "explanation": "Blue and yellow are primary colors that combine to make green.",
        },
        {
            "id": "set1_q4",
            "question": "What is the largest ocean on Earth?",
            "answer": "The Pacific Ocean",
            "explanation": "The Pacific Ocean covers about a third of the Earth's surface.",
        },
        {
            "id": "set1_q5",
            "question": "How many legs does a spider have?",
            "answer": "Eight",
            "explanation": "Spiders are arachnids, and all arachnids have eight legs.",
        },
    ],
    2: [
        {
            "id": "set2_q1",
            "question": "What is the capital of France?",
            "answer": "Paris",
            "explanation": "Paris has been the capital of France for centuries.",
        },
        {
            "id": "set2_q2",
            "question": "How many continents are there on Earth?",
            "answer": "Seven",
            "explanation": "The seven continents are Africa, Antarctica, Asia, Australia, Europe, North America, and South America.",
        },
        {
            "id": "set2_q3",
            "question": "What gas do plants absorb from the air?",
            "answer": "Carbon dioxide",
            "explanation": "Plants use carbon dioxide during photosynthesis to produce energy.",
        },
        {
            "id": "set2_q4",
            "question": "What is the tallest mountain in the world?",
            "answer": "Mount Everest",
            "explanation": "Mount Everest stands about 8,849 meters tall in the Himalayas.",
        },
        {
            "id": "set2_q5",
            "question": "How many colors are there in a rainbow?",
            "answer": "Seven",
            "explanation": "A rainbow has seven colors: red, orange, yellow, green, blue, indigo, and violet.",
        },
    ],
}

CORRECT_FEEDBACK_TEXT = "Bingo! That is correct!"


def incorrect_feedback_text(item):
    return f"Uh oh, that is incorrect. The correct answer is {item['answer']}. {item['explanation']}"
