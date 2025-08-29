import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('jovana.xlsx')

print("SURVEY ANALYSIS")
print("="*50)

# Categorize questions by type
categorical_questions = []
rating_questions = []
yes_no_questions = []
numerical_questions = []
text_questions = []

for i, col in enumerate(df.columns[1:], 1):  # Skip timestamp
    unique_values = df[col].nunique()
    sample_values = df[col].dropna().unique()[:5]
    
    question_type = "Unknown"
    
    # Check for rating scales
    if any("1 =" in str(val) and "5 =" in str(val) for val in sample_values):
        rating_questions.append((i, col, unique_values, sample_values))
        question_type = "Rating Scale"
    # Check for yes/no questions
    elif unique_values <= 3 and any(val in ['Da', 'Ne'] for val in sample_values if pd.notna(val)):
        yes_no_questions.append((i, col, unique_values, sample_values))
        question_type = "Yes/No"
    # Check for categorical with reasonable number of categories
    elif unique_values <= 10:
        categorical_questions.append((i, col, unique_values, sample_values))
        question_type = "Categorical"
    # High number of unique values - likely text or numerical
    else:
        text_questions.append((i, col, unique_values, sample_values))
        question_type = "Text/Open-ended"
    
    print(f"Q{i}: {question_type} ({unique_values} unique values)")

print(f"\nSUMMARY:")
print(f"- Categorical questions: {len(categorical_questions)}")
print(f"- Rating scale questions: {len(rating_questions)}")  
print(f"- Yes/No questions: {len(yes_no_questions)}")
print(f"- Text/Open-ended questions: {len(text_questions)}")

print(f"\nRATING SCALE QUESTIONS:")
for i, (q_num, question, unique_count, samples) in enumerate(rating_questions[:5]):
    print(f"{q_num}. {question}")
    print(f"   Sample values: {samples}")

print(f"\nCATEGORICAL QUESTIONS (first 10):")
for i, (q_num, question, unique_count, samples) in enumerate(categorical_questions[:10]):
    print(f"{q_num}. {question}")
    print(f"   Values: {samples}")
    print()