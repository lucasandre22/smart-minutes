import json

def load_json_lines_file_and_create_text(file_path, object="") -> str:
    text = ""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            text += json.loads(line)[object] + "\n\n"
    return text

if __name__ == "__main__":
    text = load_json_lines_file_and_create_text("D:\\Git\\tcc\\documents\\Emilias_podcast_99_ Anne_Lesinhovski_medium.jsonl", "content")
    f = open("demofile2.txt", "a", encoding='utf-8')
    f.write(text)
    f.close()