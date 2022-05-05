import sys
from main import categorize
words = {}
ngrams = {1 : {}, 2 : {}, 3 : {}}
word_counts = {}
def count_words():
  with open("gene.counts") as f:
    lines = f.readlines()
    for line in lines:
      t = line.strip().split()
      count = int(t[0])
      key = tuple(t[2:])
      if t[1] == "1-GRAM": ngrams[1][key[0]] = count
      elif t[1] == "2-GRAM": ngrams[2][key] = count
      elif t[1] == "3-GRAM": ngrams[3][key] = count
      elif t[1] == "WORDTAG":
          words[key] = count
          word_counts.setdefault(key[1], 0)
          word_counts[key[1]] += count


def convert_to_infrequent_2(categorized=None):
  result_to_write = []
  with open("gene.train") as f:
    lines = f.readlines()
    for line in lines:
      if line == "\n":
        result_to_write.append(line)
        continue

      results = line.split()

      word = results[0]
      tag = results[1]
      
      if word_counts[word] < 5:
        if categorized:
          word = categorize(word)
        else:
          word = "_RARE_"
      
      result_to_write.append(word + " " + tag + "\n")

  filename = "converted.train" if not categorized else "categorized.train"

  textfile = open(filename, "w+")
  for element in result_to_write:
      textfile.write(element)
  textfile.close()      
        

if __name__ == "__main__":
  categorized = sys.argv[1] if len(sys.argv) > 1 else False
  count_words()
  convert_to_infrequent_2(categorized)