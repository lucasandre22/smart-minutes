import webvtt
vtt = webvtt.read('D:\\Git\\tcc\\backend\\transcriptions\\Reunião do Colegiado do PPGCA – 2024_09_30 13_22 BRT – Recording-pt-1.vtt')
transcript = ""

lines = []
for line in vtt:
    # Strip the newlines from the end of the text.
    # Split the string if it has a newline in the middle
    # Add the lines to an array
    lines.extend(line.text.strip().splitlines())

# Remove repeated lines
previous = None
last_person_talking = None
for line in lines:
    # Clear repeated lines or repeated speakears names
    if line == previous or (line == last_person_talking):
       continue

    # Update repeated lines
    if (line.startswith("(") and last_person_talking == None) or (line.startswith("(") and last_person_talking != line):
        last_person_talking = line

    transcript += " " + line
    previous = line

print(transcript)
with open('ppgca_.txt', 'w', encoding='utf-8') as file:
    file.write(transcript)