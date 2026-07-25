from openai import OpenAI
import random
import time
import textwrap
import os
import pandas as pd
from docx import Document
from fpdf import FPDF
from services.mocktest.PromptsDict import prompt_templates
from datetime import datetime
import json
import uuid
# import winsound
from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import List
import certifi
import cloudinary
import cloudinary.uploader

# ===============================================================
# === ROBUST PATH CONFIGURATION ===
# ===============================================================

# Get the absolute path of the directory containing this script (Generation.py)
# This will be .../src/MockTestAutomation/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Get the project root directory by going up two levels from the script's directory
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# Build absolute paths to ensure files are always found
# MODEL = 'gpt-4-turbo'
MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
# SAVE_GENERATIONS_TO_DB = True
SAVE_GENERATIONS_TO_DB = True
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
# questions_per_chunk = 5 
# questions_per_chunk = 3 # change to 5 when on production level

# EXCEL_PATH = os.path.join(SCRIPT_DIR, "..", "data", "Syllabus.xlsx")
# EXCEL_PATH = os.path.join(SCRIPT_DIR, "..", "data", "UGCSyllabus.xlsx")

# Define the path to the backend/data directory
BACKEND_DATA_DIR = os.getenv(
    "BACKEND_DATA_DIR", 
    "/app/data" if os.path.exists("/app") else os.path.join(PROJECT_ROOT, "data")
)
# Create the output directories inside backend/data
OUTPUT_DIR = os.path.join(BACKEND_DATA_DIR, "generated_files")
RAW_RESPONSES_DIR = os.path.join(BACKEND_DATA_DIR, "raw_responses")

# Ensure the output directories exist at the project root
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RAW_RESPONSES_DIR, exist_ok=True)

# ===============================================================
# === MONGODB SETUP ===
# ===============================================================
try:
    MONGO_CONNECTION_STRING = os.getenv("MONGO_URI")
    if not MONGO_CONNECTION_STRING:
        print("⚠️ MONGO_URI not set. Logging disabled.")
        mongo_client = None
    else:
        # Added tlsAllowInvalidCertificates for local dev SSL issues
        mongo_client = MongoClient(
            MONGO_CONNECTION_STRING,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsCAFile=certifi.where(), # Tells the container where the SSL certs are
            tlsAllowInvalidCertificates=True,
            connectTimeoutMS=10000 
        )
        # Verify connection
        mongo_client.admin.command('ping')
        print("✅ MongoDB connection successful.")
        db = mongo_client["acetrack_finetune_db"]
        finetune_collection = db["generation_logs"]
except Exception as e:
    print(f"❌ MongoDB connection failed: {type(e).__name__} - {e}")
    mongo_client = None
# ===============================================================
if os.getenv("CLOUDINARY_URL"):
    cloudinary.config(cloudinary_url=os.getenv("CLOUDINARY_URL"))
else:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
# === TOPIC LOADING AND PROMPT GENERATION ===
# def load_all_topics(excel_path=EXCEL_PATH):
#     """Loads and shuffles topics from the specified Excel file."""
#     if not os.path.exists(excel_path):
#         raise FileNotFoundError(f"Syllabus file not found at the expected path: {excel_path}. Please ensure it exists.")
#     try:
#         df = pd.read_excel(excel_path)
#         if df.empty or len(df.columns) == 0:
#             raise ValueError("Syllabus.xlsx is empty or has no columns.")
#         topic_column = df.columns[0]
#         topics = df[topic_column].dropna().tolist()
#         random.shuffle(topics)
#         return topics
#     except Exception as e:
#         # Catch other potential pandas errors
#         raise RuntimeError(f"Failed to read or process the Excel file at {excel_path}: {e}")

def validate_topic_capacity(plan, topics_dict: dict, questions_per_chunk: int):
    """Validates topic presence (round-robin assignment handles any question count)."""
    total_topics_count = sum(len(subj_topics) for subj_topics in topics_dict.values())
    if total_topics_count == 0:
        raise ValueError("No topics selected or available for question generation.")

def build_prompt_from_template(topics_list, template_key, num_of_questions, EXAM):
    """Builds a GPT prompt from a template with the given topics."""
    topics_str = "\n".join([f"{i+1}. {topic}" for i, topic in enumerate(topics_list)])
    randomized_answer_key = ', '.join(str(n) for n in random.choices(range(1, 5), k=num_of_questions))
    template = prompt_templates.get(template_key, "")
    return template.format(topics=topics_str, answer_key=randomized_answer_key, num=num_of_questions, exam=EXAM)

def generate_all_prompts(plan, topics: dict, exam, questions_per_chunk: int):
    """Generates a list of all prompts to be sent to the GPT API using round-robin topic distribution."""
    prompts = []
    
    # 1. Shuffle topics within each subject
    shuffled_by_subj = {}
    for subj, subj_topics in topics.items():
        if subj_topics:
            shuffled_by_subj[subj] = random.sample(subj_topics, len(subj_topics))
        
    # 2. Interleave them perfectly for maximum diversity
    shuffled_topics = []
    subjects = list(shuffled_by_subj.keys())
    
    while any(shuffled_by_subj.values()):
        for subj in subjects:
            if shuffled_by_subj[subj]:
                shuffled_topics.append(shuffled_by_subj[subj].pop(0))
                
    if not shuffled_topics:
        raise ValueError("No topics available for question generation.")

    topic_index = 0
    num_topics = len(shuffled_topics)
    
    for qtype, count in plan.items():
        if count <= 0:
            continue
        num_chunks = count // questions_per_chunk
        if num_chunks == 0 and count > 0:
            num_chunks = 1
            
        for _ in range(num_chunks):
            chunk = []
            for _ in range(questions_per_chunk):
                chunk.append(shuffled_topics[topic_index % num_topics])
                topic_index += 1
            prompt = build_prompt_from_template(chunk, qtype, questions_per_chunk, exam)
            prompts.append((qtype, prompt))
            
    return prompts

# === FILE OPERATIONS ===
def save_to_docx(content, filename):
    """Saves the given content to a .docx file in the output directory."""
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        doc = Document()
        doc.add_paragraph(content)
        doc.save(path)
    except Exception as e:
        raise IOError(f"❌ Cannot access {path}. Details: {e}")
    
def save_to_pdf(content, filename):
    """Saves the given content to a .pdf file in the output directory."""
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        encoded_content = content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, txt=encoded_content)
        pdf.output(path)
    except Exception as e:
        raise IOError(f"❌ Cannot save PDF to {path}. Details: {e}")

def save_raw_response(text, folder=RAW_RESPONSES_DIR):
    """Saves the raw GPT response for debugging purposes."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_id = uuid.uuid4().hex[:6]
    # filename = f"gpt_response_{timestamp}.docx"
    filename = f"gpt_response_{timestamp}_{file_id}.pdf"
    path = os.path.join(folder, filename)
    # doc = Document()
    # doc.add_paragraph(text)
    # doc.save(path)
    # print(f"✅ Raw response saved to: {path}")
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        encoded_text = text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, txt=encoded_text)
        pdf.output(path)
        print(f"✅ Raw response saved to: {path}")
    except Exception as e:
        print(f"❌ Failed to save raw response PDF. Details: {e}")

def log_generation_to_db(system_prompt: str, user_prompt: str, response_content: str, exam_name: str, model_name: str):
    """Logs a successful prompt/response pair to MongoDB if enabled."""
    if mongo_client and SAVE_GENERATIONS_TO_DB and response_content:
        try:
            finetune_collection.insert_one({
                "system": system_prompt,
                "prompt": user_prompt,
                "response": response_content,
                "exam": exam_name,
                "model": model_name,
                "created_at": datetime.now()
            })
            print("  -> ✅ Logged generation pair to MongoDB.")
        except OperationFailure as e:
            print(f"  -> ⚠️ Failed to log to MongoDB (OperationFailure): {e.details}")
        except Exception as e:
            print(f"  -> ⚠️ Failed to log to MongoDB (General Error): {e}")
    elif not SAVE_GENERATIONS_TO_DB:
        print("  -> 🟡 Skipping MongoDB log (master flag is OFF).")

# === GPT HANDLING ===
def call_gpt(prompt, exam_name, chunks, retries=3):
    """Calls the OpenAI API with a given prompt, with retries."""
    system_prompt = f"You are a {exam_name} paper setter. You must output exclusively in valid JSON format."
    
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY") or API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    client = OpenAI(api_key=api_key)
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            response_content = response.choices[0].message.content

            return response_content, system_prompt
        
        except Exception as e:
            print(f"⚠️ GPT attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    raise RuntimeError("❌ All GPT API retries failed.")


# === CORE EXECUTION LOGIC ===
def handle_generation(prompts, exam_name, questions_per_chunk: int):
    """Handles the question generation loop, calling GPT for each prompt."""
    all_questions = []
    skipped_chunks = []
    # questions_per_chunk = 5
    max_retries_per_chunk = 3
    
    for qtype, prompt in prompts:
        print(f"Generating questions for type: {qtype}")
        generated_chunk = None
        last_failed_chunk = []
        
        for attempt in range(max_retries_per_chunk):
            try:
                print(f"  -> Attempt {attempt + 1} for {qtype}...")
                response, system_prompt_used = call_gpt(prompt, exam_name, questions_per_chunk)
                
                if not response:
                    print(f"  -> ⚠️ call_gpt returned empty response for {qtype}.")
                    last_failed_chunk = [{"error": f"--- GPT CALL RETURNED EMPTY RESPONSE --- (Type: {qtype})"}]
                    continue
                
                save_raw_response(response)

                # Parse questions from JSON
                try:
                    json_data = json.loads(response)
                    questions = json_data.get("questions", [])
                except json.JSONDecodeError:
                    print(f"  -> ⚠️ GPT returned invalid JSON for {qtype}.")
                    questions = []

                last_failed_chunk = questions if questions else [{"error": response}]
                
                # --- VALIDATION LOGIC ---
                if len(questions) >= questions_per_chunk:
                    print(f"  ✅ Success! Got {len(questions)} questions.")
                    generated_chunk = questions[:questions_per_chunk]
                    if system_prompt_used:
                         log_generation_to_db(
                             system_prompt=system_prompt_used,
                             user_prompt=prompt,
                             response_content=response,
                             exam_name=exam_name,
                             model_name=MODEL
                         )
                    break
                else:
                    print(f"  ⚠️ Validation warning: GPT returned {len(questions)} questions instead of {questions_per_chunk}.")
                    if attempt == max_retries_per_chunk - 1 and len(questions) > 0:
                        # Accept whatever we got on the final attempt
                        print(f"  ⚠️ Accepting {len(questions)} questions on final retry.")
                        generated_chunk = questions
                        break
                    time.sleep(1)

            except Exception as e:
                print(f"An error occurred during GPT call for {qtype}: {e}")
                last_failed_chunk = [f"--- ERROR IN GENERATION ---: {str(e)}"]
                if attempt < max_retries_per_chunk - 1:
                    time.sleep(2)
        
        # After the retry loop, check if we got a valid chunk
        if generated_chunk:
            all_questions.extend(generated_chunk)
        else:
            print(f"❌ Failed to generate a valid chunk for {qtype} after {max_retries_per_chunk} attempts. Skipping.")
            skipped_chunks.append(last_failed_chunk)
            
    return all_questions, skipped_chunks

def format_questions_for_pdf(questions):
    text_parts = []
    for i, q in enumerate(questions):
        if isinstance(q, str):
            text_parts.append(q)
            continue
        text = f"Q{i+1}. {q.get('question', '')}\n"
        for j, opt in enumerate(q.get('options', [])):
            text += f"   {chr(65+j)}. {opt}\n"
        text += f"\nAnswer: Option {q.get('correct_answer')}\n"
        text += f"Solution: {q.get('solution', '')}\n"
        text_parts.append(text)
    return "\n\n".join(text_parts)

# === MAIN ENTRY POINT FOR BACKEND ===
def run_generation_task(plan: dict, exam_name: str, output_format: str, questions_per_chunk: int, topics: dict):
    """Main function to be called by the FastAPI """
    try:
        print(f"Starting generation for {exam_name} with plan: {plan}")
        
        run_id = uuid.uuid4().hex[:8]
        extension = ".pdf" if output_format == 'pdf' else ".docx"
        questions_filename = f"Questions_{run_id}{extension}"
        skipped_filename = f"Skipped_{run_id}{extension}"
        
        save_function = save_to_pdf if output_format == 'pdf' else save_to_docx
        
        validate_topic_capacity(plan, topics, questions_per_chunk)
        
        prompts = generate_all_prompts(plan, topics, exam_name, questions_per_chunk)
        
        generated_questions, skipped_chunks = handle_generation(prompts, exam_name, questions_per_chunk)
        if not generated_questions and not skipped_chunks:
            raise RuntimeError("No questions were successfully generated. Check logs for API errors or response format issues.")
        
        generated_files = {}
        message = ""
        if generated_questions:
            pdf_text = format_questions_for_pdf(generated_questions)
            save_function(pdf_text, questions_filename)
            # --- CLOUDINARY UPLOAD: Questions ---
            message = f"Successfully generated {len(generated_questions)} questions."
            try:
                print(f"Uploading {questions_filename} to Cloudinary...")
                upload_questions = cloudinary.uploader.upload(
                    os.path.join(OUTPUT_DIR, questions_filename),
                    resource_type="raw",
                    public_id=f"ace-track/{questions_filename}"
                )
                generated_files["questions"] = upload_questions.get("secure_url")
            except Exception as u_err:
                print(f"⚠️ Cloudinary upload failed for questions: {u_err}")
                generated_files["questions"] = questions_filename # Fallback to filename
            
        if skipped_chunks:
            skipped_text = "\n\n".join([
                f"--- Skipped Chunk {i+1} ---:\n" + format_questions_for_pdf(chunk)
                for i, chunk in enumerate(skipped_chunks)
            ])
            save_function(skipped_text, skipped_filename)
            # --- CLOUDINARY UPLOAD: Skipped ---
            try:
                upload_skipped = cloudinary.uploader.upload(
                    os.path.join(OUTPUT_DIR, skipped_filename),
                    resource_type="raw",
                    public_id=f"ace-track/skipped_{skipped_filename}"
                )
                generated_files["skipped"] = upload_skipped.get("secure_url")
            except Exception as u_err:
                print(f"⚠️ Cloudinary upload failed for skipped chunks: {u_err}")
                generated_files["skipped"] = skipped_filename

        print("\n✅ Mock Test Generation Completed.")

        return {
            "success": True,
            "message": message,
            "files": generated_files,
            "questions": generated_questions
        }

    except Exception as e:
        error_message = f"Question generation failed: {str(e)}"
        print(f"❌ {error_message}")
        return {"success": False, "message": error_message, "files": {}, "questions": []}