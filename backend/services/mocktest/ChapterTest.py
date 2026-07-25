import os
import random
import pandas as pd
import textwrap
from datetime import datetime
from docx import Document
import winsound

from Generation import call_gpt, save_response, save_to_docx, check_file_access, GenerationMain
from PromptsDict import prompt_templates

TESTING = True
CHUNK_SIZE = 3
EXAM = "UGC NET"
CHAPTER_XLSX = "CS/Chapter/ChapterSyllabus.xlsx"
QUESTIONS_PATH = "CS/Chapter/ChapterQuestions.docx"
VERIFICATIONS_PATH = "CS/Chapter/ChapterVerifications.docx"
SKIPPED_PATH = "CS/Chapter/ChaptertSkipped.docx"
skipped_chunks = []

MODE_OPTIONS = {
    "1": "Full Mock Test (entire syllabus)",
    "2": "Chapter-wise Test (select specific chapters)"
}

# === MODE SELECTION ===
def choose_mode():
    print("\n🔧 Choose test generation mode:")
    for key, val in MODE_OPTIONS.items():
        print(f"{key}. {val}")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice in MODE_OPTIONS:
            return choice
        print("❌ Invalid input. Try again.")

# === LOAD CHAPTER-WISE TOPICS FROM COLUMNS ===
def load_chapterwise_topics_columnwise(filepath=CHAPTER_XLSX):
    try:
        df = pd.read_excel(filepath)
        chapters = {}
        for col in df.columns:
            chapters[col] = df[col].dropna().tolist()
        return chapters
    except Exception as e:
        print(f"❌ Failed to load chapter-wise syllabus: {e}")
        return {}

# === ASK WHICH CHAPTERS ===
def choose_chapters(chapter_topics):
    print("\n📘 Available Chapters:")
    chapters = list(chapter_topics.keys())
    for idx, name in enumerate(chapters, 1):
        print(f"{idx}. {name}")

    chosen = []
    raw = input("\n✍️ Enter chapter numbers (comma-separated, e.g., 1,3,5): ").strip()
    try:
        indices = [int(x.strip()) for x in raw.split(",")]
        for i in indices:
            if 1 <= i <= len(chapters):
                chosen.append(chapters[i - 1])
        return chosen
    except:
        print("❌ Invalid input format.")
        return []

# === RANDOMIZE QUESTION TYPES ===
def randomize_qtypes(prompt_dict, num):
    return random.sample(list(prompt_dict.keys()), num)

def verify_prompt(questions_text):
    return f"""
VERIFICATION: im gonna send you 3 questions at once
you have to check whether or not they are correct. conduct a fact check. check the factual information, whether the answer key is correct, if the solution supports the answer key, if all the options are distinct and don't have similar options, if there is any contradicting information, if there are any discrepancies
question, answer key, solution etc all should be 100% correct, if there is even a tiny fault or discrepancy, tell me
be very precise and unbiased, check very carefully
you dont need to repeat the questions and answers
just thoroughly check them if they are written correctly and then tell me for each question if it is correct or not, free of discrepancies or not. Are the answer keys correct? Are the solutions logical? Are any options misleading or repeated?
if there are any issues, tell me what and where they are, then tell me how to fix them
Example format for verifying
Question 1 - INCORRECT - ANSWER KEY MISMATCH //or whatever the problem was
Question 2 - Correct
Question 3 - INCORRECT - SIMILAR ANSWER KEYS //or whatever the problem was

Rewritten Question 1...
Rewritten Question 3...

so final format for each question:
Question <Q number> - <Correctness> - <Problem if incorrect>
<Rewritten Version of the incorrect question - whole question, answer and solution of any incorrect questions>

this is only an example, be completely unbiased in determining the correctness and incorrectness. check and recheck multiple times the correctness
Here are the questions:
{questions_text}
"""

# === GENERATE CHAPTER TEST ===
def ChapterTestMain():
    print("\n📘 Starting Chapter Test Mode...")
    chapters_data = load_chapterwise_topics_columnwise()

    if not chapters_data:
        print("❌ Aborting due to load error.")
        return

    selected_chapters = choose_chapters(chapters_data)

    if not selected_chapters:
        print("❌ No chapters selected. Aborting.")
        return

    try:
        check_file_access(QUESTIONS_PATH)
        check_file_access(VERIFICATIONS_PATH)
    except Exception as e:
        print(e)
        winsound.PlaySound("WrongBuzzer.wav", winsound.SND_FILENAME)
        return

    all_questions = []

    for chapter in selected_chapters:
        print(f"\n🧠 Generating 15 questions for chapter: {chapter}")
        topics = chapters_data[chapter]
        qtypes = randomize_qtypes(prompt_templates, num=15 // CHUNK_SIZE)

        for i in range(0, 15, CHUNK_SIZE):
            chunk_topics = topics[i:i+CHUNK_SIZE]
            if len(chunk_topics) < CHUNK_SIZE:
                print(f"⚠️ Skipping short chunk in {chapter}.")
                skipped_chunks.append(chunk_topics)
                continue
            selected_qtype = qtypes[(i // CHUNK_SIZE)]
            topics_str = "\n".join([f"{j+1}. {t}" for j, t in enumerate(chunk_topics)])
            randomized_answer_key = ', '.join(str(n) for n in random.choices(range(1, 5), k=3))
            prompt = prompt_templates[selected_qtype].format(topics=topics_str, answer_key=randomized_answer_key, num = "three", exam = EXAM)

            print(f"\nPrompt ({selected_qtype}) for {chapter}:")
            print(prompt)

            try:
                response = call_gpt(prompt, TESTING, 3)
                save_response(response)
            except Exception as e:
                print(e)
                winsound.PlaySound("WrongBuzzer.wav", winsound.SND_FILENAME)
                continue

            questions = [q.strip() for q in textwrap.dedent(response).strip().split("--Question Starting--") if q.strip()]
            if len(questions) != CHUNK_SIZE:
                print(f"⚠️ Chunk incomplete: only {len(questions)} questions.")
                skipped_chunks.append(questions)
                continue

            all_questions.extend(questions)

    # Shuffle and Save
    random.shuffle(all_questions)
    questions_text = "\n\n".join(all_questions)
    save_to_docx(questions_text, QUESTIONS_PATH)

    verified_output = ""
    for i in range(0, len(all_questions), CHUNK_SIZE):
        chunk = all_questions[i:i+CHUNK_SIZE]
        if len(chunk) < CHUNK_SIZE:
            skipped_chunks.append(chunk)
            continue
        joined_chunk = "\n\n".join(chunk)
        try:
            verified_output += call_gpt(verify_prompt(joined_chunk),TESTING, 3) + "\n\n"
        except Exception as e:
            print(e)
            winsound.PlaySound("WrongBuzzer.wav", winsound.SND_FILENAME)
            continue

    save_to_docx(verified_output.strip(), VERIFICATIONS_PATH)

    if skipped_chunks:
        print("\n📭 Skipped Chunks:")
        skipped_text = "\n\n".join(
            f"Skipped Chunk {i+1}:\n" + "\n\n".join(chunk)
            for i, chunk in enumerate(skipped_chunks)
        )
        save_to_docx(skipped_text, SKIPPED_PATH)

    print("\n✅ Chapter-wise Test completed.")
    winsound.PlaySound("CorrectHarp.wav", winsound.SND_FILENAME)

if __name__ == "__main__":
    mode = choose_mode()

    if mode == "1":
        print("\n🧪 Starting Full Mock Test Mode...")
        GenerationMain(3)

    elif mode == "2":
        ChapterTestMain()
