import os
import json
import glob

def extract_rephrased_questions(json_dir='.'):
    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(json_dir, '*.json'))
    
    for json_file in json_files:
        try:
            # Read the JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Create text file name (same as JSON but with .txt extension)
            txt_file = os.path.splitext(json_file)[0] + '.txt'
            
            # Open text file for writing
            with open(txt_file, 'w', encoding='utf-8') as f:
                # Sort keys to ensure numeric order
                keys = sorted(data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
                
                # Extract and write each rephrased question
                for key in keys:
                    if isinstance(data[key], dict) and "Rephrased Question(SD)" in data[key]:
                        rephrased_question = data[key]["Rephrased Question(SD)"]
                        f.write(f"{key}. {rephrased_question}\n\n")
            
            print(f"Processed {json_file} -> {txt_file}")
        
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

if __name__ == "__main__":
    # You can specify a directory path as an argument if needed
    extract_rephrased_questions()
    print("Extraction complete!")
