import zipfile
import re
import os

filename = "бриф.docx"
output_file = "brief_text.txt"

def extract_text(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml').decode('utf-8')
            text = re.sub('<[^<]+?>', ' ', xml_content)
            return text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    files = [f for f in os.listdir('.') if f.endswith('.docx')]
    print(f"Marketing DOCX files: {files}")
    # Try to find the file even if name encoding is tricky
    target = None
    for f in files:
        if "бриф" in f or "doc" in f:
            target = f
            break
            
    if target:
        print(f"Reading {target}...")
        text = extract_text(target)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print("Done.")
    else:
        print("File not found")
