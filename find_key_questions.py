import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_excel('jovana.xlsx')

print("FINDING KEY RELATIONSHIP VARIABLES")
print("="*50)

# Find education question
education_cols = [col for col in df.columns if 'obrazovan' in col.lower()]
print("EDUCATION QUESTIONS:")
for col in education_cols:
    print(f"- {col}")
    print(f"  Values: {df[col].unique()[:5]}")

# Find birth satisfaction questions
satisfaction_cols = [col for col in df.columns if any(word in col.lower() for word in ['iskustvo', 'oceni', 'zadovoljn'])]
print(f"\nBIRTH SATISFACTION QUESTIONS:")
for col in satisfaction_cols:
    print(f"- {col}")
    print(f"  Values: {df[col].unique()[:5]}")

# Find mental health related questions
mental_health_cols = [col for col in df.columns if any(word in col.lower() for word in ['tuga', 'anksioznost', 'strah', 'depresij', 'emocij', 'psiholog', 'mental'])]
print(f"\nMENTAL HEALTH QUESTIONS:")
for col in mental_health_cols:
    print(f"- {col}")
    print(f"  Values: {df[col].unique()[:3]}")

# Find desire for more children questions
desire_cols = [col for col in df.columns if any(word in col.lower() for word in ['želiš', 'planir', 'buduć', 'još', 'deca'])]
print(f"\nDESIRE FOR MORE CHILDREN QUESTIONS:")
for col in desire_cols:
    print(f"- {col}")
    print(f"  Values: {df[col].unique()[:3]}")

# Find support system questions  
support_cols = [col for col in df.columns if any(word in col.lower() for word in ['podrška', 'pomoć', 'partner', 'porodic', 'prijatelj'])]
print(f"\nSUPPORT SYSTEM QUESTIONS:")
for col in support_cols[:5]:  # Show first 5
    print(f"- {col}")
    print(f"  Values: {df[col].unique()[:3]}")

print(f"\nTOTAL COLUMNS ANALYZED: {len(df.columns)}")