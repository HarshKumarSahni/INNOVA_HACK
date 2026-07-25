import pandas as pd
import os

def parse_syllabus_weightage(file_path: str = None) -> dict:
    """
    Parses the JEEsyllabusWeightage.xlsx file.
    Returns a dict: { "Subject": [{"topic": "...", "weightage": 0.05}, ...] }
    """
    if not file_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "JEEsyllabusWeightage.xlsx")
        
    if not os.path.exists(file_path):
        print(f"Warning: Syllabus file not found at {file_path}")
        return {}

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading syllabus excel: {e}")
        return {}
        
    result = {}
    
    # Iterate through columns in pairs
    cols = df.columns
    for i in range(0, len(cols), 2):
        if i + 1 >= len(cols):
            break
            
        subject_col = cols[i]
        weight_col = cols[i+1]
        
        # Clean subject name
        subject_name = str(subject_col).strip()
        
        topics = []
        for index, row in df.iterrows():
            topic_name = row[subject_col]
            weight = row[weight_col]
            
            if pd.isna(topic_name) or str(topic_name).strip() == "":
                continue
                
            # If weight is NaN, default to 0.01
            weight_val = float(weight) if not pd.isna(weight) else 0.01
            
            topics.append({
                "topic": str(topic_name).strip(),
                "weightage": weight_val
            })
            
        if topics:
            result[subject_name] = topics
            
    return result

def get_available_subjects(file_path: str = None) -> list:
    """Returns a list of available subjects from the excel file."""
    syllabus = parse_syllabus_weightage(file_path)
    return list(syllabus.keys())
