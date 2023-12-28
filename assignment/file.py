def reverse_sorted_words(filename):
    try:
        rows = []
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                rows.append(line.strip())
        sorted_words = sorted(rows, key=lambda x: x.lower(), reverse=True)
        return sorted_words
    except FileNotFoundError as e:
        print(f"Error: File '{filename}' not found.")
        return None
    except IOError as e:
        print(f"Error: Unable to read file '{filename}': {str(e)}")
        return None

filename = 'words.txt'
sorted_words = reverse_sorted_words(filename)

if sorted_words is not None:
    print(sorted_words)
else:
    print("Error occurred during file reading.")


import re

def reformat_student_info(filename):
    rows = []
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            rows.append(line.strip())

    netid_pattern = r'([a-z]{2,3}\d{1,4})'
    name_pattern = r'[A-Z][a-zA-Z]*\s*[A-Z][a-zA-Z]*'
    major_pattern = r'\b\d{3}\b'
    gpa_pattern = r'(\d{1}+(\.\d{1,2})?)$'

    try:
        with open('studentInfoReformatted.txt', 'w', encoding='utf-8') as txtfile:
            for row in rows:
                netid = re.findall(netid_pattern, row)[0]
                name_matches = re.findall(name_pattern, row)
                name = ' '.join([re.sub(r'(?<!\s)([A-Z])', r' \1', match).strip() for match in name_matches])

                major = ' '.join(re.findall(major_pattern, row))
                if not major:
                    match = re.search(r'[A-Z][a-zA-Z]*\s*[A-Z][a-zA-Z]*(\d{3})', row)
                    if match:
                        major = ''.join(match.group(1).strip())

                gpa_matches = re.search(gpa_pattern, row)
                if gpa_matches:
                    gpa = gpa_matches.group(1)
                else:
                    raise ValueError("Invalid GPA format.")
                txtfile.write(f"{netid}, {name}, {major}, {gpa}\n")

        print("TXT file 'studentInfoReformatted.txt' created successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise NotImplementedError("Error occurred during processing.")


filename = 'studentInfo.txt'
results = reformat_student_info(filename)

def count_word(filename):
    word_counts = {}
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                words = line.strip().split()
                for word in words:
                    # Convert the word to lowercase for case-insensitive comparison
                    lowercase_word = word.lower()

                    # Update the word count
                    word_counts[lowercase_word] = word_counts.get(lowercase_word, 0) + 1

        # Print the words in alphabetical order with their occurrences
        for word in sorted(word_counts.keys()):
            print(f"{word}: {word_counts[word]}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        raise NotImplementedError("Error: File not found.")
    except IOError as e:
        print(f"Error: Unable to read file '{filename}': {str(e)}")
        raise NotImplementedError("Error: Unable to read file.")

filename = 'words2.txt'
try:
    count_word(filename)
except NotImplementedError as e:
    print(e)


def count_last_letter(words_string):
    last_letter_counts = {}
    try:
        words = words_string.split()
        for word in words:
            # Convert the word to lowercase for case-insensitive comparison
            lowercase_word = word.lower()

            # Get the last letter of the word
            last_letter = lowercase_word[-1]

            # Update the count for the last letter
            last_letter_counts[last_letter] = last_letter_counts.get(last_letter, 0) + 1

        return last_letter_counts

    except NotImplementedError as e:
        print(e)

# Example usage:
filename = 'question4.txt'
words_string = []
with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
    for line in file:
        words_string.append(line.strip())

string = ' '.join(words_string)

try:
    result = count_last_letter(string)
    print(result)
except NotImplementedError as e:
    print(e)

d = count_last_letter('apple banana orange grape cherry')
print(d)

assert len(d) == 3
assert d['a'] == 1


import numpy as np

try:
    roster = np.zeros(4, dtype={'names': ('name', 'age', 'major', 'gpa'),
                                'formats': ('U50', 'i4', 'U4', 'f8')})

    data = [('Alice', 21, 'CS', 3.8),
            ('Bob', 25, 'Math', 3.2),
            ('Carol', 18, 'Chem', 4.0),
            ('Dennis', 29, 'Phys', 3.5)]

    roster[:] = data

    # Calculate the average GPA of all students
    average_gpa = np.mean(roster['gpa'], dtype=np.float64)
    print(f"{average_gpa:.3f}")  # Adjusted precision to 3 decimal places

    # Calculate the maximum GPA of students majoring in CS
    max_gpa = np.max(roster[roster['major'] == 'CS']['gpa'])
    print(f"{max_gpa:.1f}")

    # Calculate the number of students with a GPA over 3.5
    gpa_over_35 = np.sum(roster['gpa'] > 3.5)
    print(gpa_over_35)

    # Calculate the average GPA of students who are at least 25 years old
    gpa_students_over_25 = np.mean(roster[roster['age'] >= 25]['gpa'])
    print(f"{gpa_students_over_25:.2f}")

    # Calculate the major that has the highest average GPA among students at most 22 years old
    unique_majors = np.unique(roster[roster['age'] <= 22]['major'])
    gpa_major_under_22 = max([(major, np.mean(roster[(roster['age'] <= 22) & (roster['major'] == major)]['gpa']))
                                    for major in unique_majors], key=lambda x: x[1])

    print(gpa_major_under_22[0])

except Exception as e:
    print(f"Error: {str(e)}")
    raise NotImplementedError("Error occurred during calculations.")
