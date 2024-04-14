import json

def parse_lines(lines):
    chapters = []
    chapter = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            if chapter:
                chapters.append(chapter)
                chapter = {}
            chapter['chapter'] = int(line)
        elif '-->' in line:
            times = line.split(' --> ')
            chapter['start_time'] = times[0]
            chapter['end_time'] = times[1]
        else:
            chapter['content'] = line
    if chapter:
        chapters.append(chapter)
    return chapters

def main():
    with open('D:\\Git\\tcc\\documents\\Emilias_podcast_99_ Anne_Lesinhovski_medium.srt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    chapters = parse_lines(lines)
    
    with open('Emilias_podcast_99_ Anne_Lesinhovski_medium.json', 'w', encoding='utf-8') as outfile:
        for chapter in chapters:
            json.dump(chapter, outfile, ensure_ascii=False)
            outfile.write('\n')


if __name__ == "__main__":
    main()
