import sys
wordtag_dict = dict()
n_gram_dict = dict()


words = {}
ngrams = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
word_counts = {}

def categorize(word):
  # words with -ase is usually gene
  # if "ase" in word or "xin" in word:
  #   return "_ASE_" 
  
  #more than one capital (usually names, or abbreviations)
  # count_upper = 0
  # for letter in word:
  #   if letter.isupper():
  #     count_upper += 1
  
  # if count_upper > 1:
  #   return "_UPPER_" 
  
  
  #letters and numbers are usually genes
  contains_letter = False
  contains_number = False
  for letter in word:
    if letter.isalpha():
      contains_letter = True
    if letter.isdigit():
      contains_number = True
  
  if contains_letter and contains_number:
    return "_ALPHA_NUMERIC_"
  
  # if word[0].isupper():
  #   return "_PROPER_"
  
  # #uncapitalized words (ususally just regular english words)
  # if word.isalpha() and word.islower():
  #   return "_LOWER_"
  
  # # single letter capital (ex. hepatitis-B)
  # if len(word) == 1 and word.isupper():
  #   return "_ONE_CAPITAL_"
  
  
  

  

  return "_RARE_"

def count_words(count_file):
  with open(count_file) as f:
    lines = f.readlines()
    for line in lines:
      t = line.strip().split()
      count = int(t[0])
      key = tuple(t[2:])
      if t[1] == "1-GRAM": ngrams[1][key[0]] = count
      elif t[1] == "2-GRAM": ngrams[2][key] = count
      elif t[1] == "3-GRAM": ngrams[3][key] = count
      elif t[1] == "4-GRAM": ngrams[4][key] = count
      elif t[1] == "WORDTAG":
          words[key] = count
          word_counts.setdefault(key[1], 0)
          word_counts[key[1]] += count
    
    
def parse_count_file(file_path):
  with open(file_path) as f:
    lines = f.readlines()
    for line in lines:
      results = line.split()
      if results[1] == "WORDTAG": #wordtag line
        count = int(results[0])
        tag = results[2]
        word = results[3]
        tup = (tag, word)
        
        # adds word to dictionary
        wordtag_dict[tup] = count
      else: #n-gram line
        count = int(results[0])
        # gets the words of the ngram
        words = tuple(results[2:])
        n_gram_dict[words] = count
  
def compute_emissions(word, tag):
  # does word exist in dictionary
  # word_exist = False
  # if ("O", word) in wordtag_dict or ("I-GENE", word) in wordtag_dict:
  #   word_exist = True
  
  # # gets count of tag being assigned to word
  # if not word_exist:
  #   count_word = wordtag_dict[(tag, "_RARE_")]
  # else:
  count_word = wordtag_dict.get((tag,word), 0)
    
  #count_total_tag = n_gram_dict[(tag,)]
  count_total_tag = ngrams[1][tag]
  return count_word / count_total_tag

#prev_tag1 is directly before tag
def compute_q(prev_tag2, prev_tag1, tag ):
  count_trigram = ngrams[3][(prev_tag2, prev_tag1, tag)]
  count_bigram = ngrams[2][(prev_tag2, prev_tag1)]
  return count_trigram / count_bigram


viterbi_tags = []
def viterbi(position, prev_tag, curr_tag, curr_word):
  if position == 0 and prev_tag == "*" and curr_tag == "*":
    return 1
  
  emission_value = compute_emissions(curr_word, curr_tag)
  
  if position == 1 or position == 2:
    possible_w = ["*"]
  else:
    possible_w = ["O", "I-GENE"]
  
  viterbi_values = [viterbi(position-1, w, prev_tag)*compute_q(w, prev_tag, curr_tag) * emission_value for w in possible_w]
  
  #get the max viterbi_values as well as the tag
  max = viterbi_values[0]
  maxIndex = 0
  for i, value in enumerate(viterbi_values):
    if value > max:
      max = value
      maxIndex = i
      
  viterbi_tags.append(possible_w[maxIndex])    
      
  return viterbi_tags


def compute_q_four(prev_tag3, prev_tag2, prev_tag1, tag ):
  count_four_gram = ngrams[4].get((prev_tag3, prev_tag2, prev_tag1, tag), 0)
  count_trigram = ngrams[3][(prev_tag3, prev_tag2, prev_tag1)]
  return count_four_gram / count_trigram

#creates dynamic 
def define_table_four(sentence):
  start_with_O = ngrams[3][("*", "*", "O")]
  start_with_GENE = ngrams[3][("*", "*", "I-GENE")]
  table = {
    (2, "*", "*", "O") : start_with_O / (start_with_O + start_with_GENE), 
    (2, "*", "*", "I-GENE") : start_with_GENE / (start_with_O + start_with_GENE)
  }
  bp = {
    
  }
  
  possible_tags_per_position = []
  possible_tags_per_position.append(["*"])
  possible_tags_per_position.append(["*"])
  for _ in range(2, len(sentence) - 1): # -1 to account for STOP
    possible_tags_per_position.append(["O", "I-GENE"])
  
  #loop from first word to last word
  for k in range(3, len(sentence) -1):
    for x in possible_tags_per_position[k-2]:
      for u in possible_tags_per_position[k-1]:
        for v in possible_tags_per_position[k]:
          viterbi_results = []
          for w in possible_tags_per_position[k-3]:
            viterbi_results.append((table[(k-1, w, x, u)] * compute_q_four(w, x, u, v) * compute_emissions(sentence[k], v), w))
            
          maximum = viterbi_results[0]
          
          for result in viterbi_results:
            if result > maximum:
              maximum = result
              
          table[(k,x, u,v)] = maximum[0]
          bp[(k,x,u,v)] = maximum[1] # gets the tag that gave max value
        
  solution_tags = ["TEMP"] * (len(sentence) - 1) # remove STOP
  
  # find the last two tags
  last_three_results = []
  for x in possible_tags_per_position[len(sentence) - 4]:
    for u in possible_tags_per_position[len(sentence) - 3]:
      for v in possible_tags_per_position[len(sentence) - 2]: # -2 is to get last word in the sentence (counting STOP)
        last_three_results.append( (table[(len(sentence) - 2, x, u, v)] * compute_q_four(x, u, v, "STOP"), x, u, v) )
      
  max_last_three = last_three_results[0]
  for result in last_three_results:
    if result > max_last_three:
      max_last_three = result
      
  #gets the two labels
  x = max_last_three[1]
  u = max_last_three[2]
  v = max_last_three[3]
  
  solution_tags[len(sentence) - 2] = v  #last word gets tag v
  solution_tags[len(sentence) - 3] = u  #second to last word gets tag u
  solution_tags[len(sentence) - 4] = x  #third to last word gets tag x
  
  for k in range(len(sentence) - 5,1,-1):
    solution_tags[k] = bp[(k+3, solution_tags[k+1], solution_tags[k+2], solution_tags[k+3])]

  return solution_tags[2:]



#creates dynamic 
def define_table(sentence):
  table = {
    (1, "*", "*") : 1
  }
  bp = {
    
  }
  
  possible_tags_per_position = []
  possible_tags_per_position.append(["*"])
  possible_tags_per_position.append(["*"])
  for _ in range(2, len(sentence) - 1): # -1 to account for STOP
    possible_tags_per_position.append(["O", "I-GENE"])
  
  #loop from first word to last word
  for k in range(2, len(sentence) -1):
    for u in possible_tags_per_position[k-1]:
      for v in possible_tags_per_position[k]:
        viterbi_results = []
        for w in possible_tags_per_position[k-2]:
          viterbi_results.append((table[(k-1, w, u)] * compute_q(w, u, v) * compute_emissions(sentence[k], v), w))
          
        maximum = viterbi_results[0]
        
        for result in viterbi_results:
          if result > maximum:
            maximum = result
            
        table[(k,u,v)] = maximum[0]
        bp[(k,u,v)] = maximum[1] # gets the tag that gave max value
        
  solution_tags = ["TEMP"] * (len(sentence) - 1) # remove STOP
  
  # find the last two tags
  last_two_results = []
  for u in possible_tags_per_position[len(sentence) - 3]:
    for v in possible_tags_per_position[len(sentence) - 2]: # -2 is to get last word in the sentence (counting STOP)
      last_two_results.append( (table[(len(sentence) - 2, u, v)] * compute_q(u, v, "STOP"), u, v) )
      
  max_last_two = last_two_results[0]
  for result in last_two_results:
    if result > max_last_two:
      max_last_two = result
      
  #gets the two labels
  v = max_last_two[2]
  u = max_last_two[1]
  solution_tags[len(sentence) - 2] = v  #last word gets tag v
  solution_tags[len(sentence) - 3] = u  #second to last word gets tag u
  
  for k in range(len(sentence) - 4,1,-1):
    solution_tags[k] = bp[(k+2, solution_tags[k+1], solution_tags[k+2])]

  return solution_tags[2:]



def baseline(count_file):
  result_to_write = []
  #read in dev file
  with open("gene.dev") as f:
    lines = f.readlines()
    for line in lines:
      if line == "\n":
        result_to_write.append(line)
        continue
      
      line = line.strip().split()
      word = line[0]
      if word_counts.get(line[0],0) < 5:
        if "categorized" in count_file:
          word = categorize(line[0])
        else:
          word = "_RARE_"
        
        
      max_emission = compute_emissions(word, "O")
      predicted_tag = "O"
      
      if compute_emissions(word,"I-GENE") > max_emission:
        predicted_tag = "I-GENE"
      
      result_to_write.append(line[0] + " " + predicted_tag + "\n")
  
  textfile = open(count_file + ".baseline", "w+")
  for element in result_to_write:
      textfile.write(element)
  textfile.close()
      

def trigram(count_file):
  result_to_write = []
  #read in dev file
  with open("gene.dev") as f:
    lines = f.readlines()
    sentences = []
    sentences_unaltered = []
    #turns lines of words into sentences
    
    curr_sentence = []
    curr_sentence_unaltered = []
    for line in lines:
      if line == "\n":
        sentences.append(curr_sentence)
        sentences_unaltered.append(curr_sentence_unaltered)
        curr_sentence = []
        curr_sentence_unaltered = []
        continue
      
      curr_sentence_unaltered.append(line.replace("\n", ""))
      
      word = line.strip()
      if word_counts.get(word,0) < 5:
        if "categorized" in count_file:
          word = categorize(line[0])
        else:
          word = "_RARE_"
      curr_sentence.append(word.replace("\n", ""))
    
    #loop through each sentence
    for i, sentence in enumerate(sentences):
      padded_sentence = ["*", "*"] + sentence + ["STOP"]
      solution_tags = define_table(padded_sentence)
      
      for item in zip(sentences_unaltered[i], solution_tags):
        result_to_write.append(" ".join(list(item)) + "\n")
      
      result_to_write.append("\n")
  
  textfile = open(count_file + ".trigram", "w+")
  for element in result_to_write:
      textfile.write(element)
  textfile.close()
    
      
    
def four_gram(count_file):
  result_to_write = []
  #read in dev file
  with open("gene.dev") as f:
    lines = f.readlines()
    sentences = []
    sentences_unaltered = []
    #turns lines of words into sentences
    
    curr_sentence = []
    curr_sentence_unaltered = []
    for line in lines:
      if line == "\n":
        sentences.append(curr_sentence)
        sentences_unaltered.append(curr_sentence_unaltered)
        curr_sentence = []
        curr_sentence_unaltered = []
        continue
      
      curr_sentence_unaltered.append(line.replace("\n", ""))
      
      word = line.strip()
      if word_counts.get(word,0) < 5:
        if "categorized" in count_file:
          word = categorize(line[0])
        else:
          word = "_RARE_"
      curr_sentence.append(word.replace("\n", ""))
    
    #loop through each sentence
    for i, sentence in enumerate(sentences):
      padded_sentence = ["*", "*"] + sentence + ["STOP"]
      solution_tags = define_table_four(padded_sentence)
      
      for item in zip(sentences_unaltered[i], solution_tags):
        result_to_write.append(" ".join(list(item)) + "\n")
      
      result_to_write.append("\n")
  
  textfile = open(count_file + ".four_gram", "w+")
  for element in result_to_write:
      textfile.write(element)
  textfile.close()  
        

if __name__ == "__main__":
  count_file = sys.argv[1]
  model = sys.argv[2]
  count_words(count_file)
  parse_count_file(count_file)

  if model == "baseline":
    baseline(count_file)
  elif model == "trigram":
    trigram(count_file)
  elif model == "4":
    four_gram(count_file)
    
  
  
  