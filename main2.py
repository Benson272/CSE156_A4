def run():
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
      
      
      result_to_write.append(word + "\n")


  textfile = open("gene.removed_tag.train", "w+")
  for element in result_to_write:
      textfile.write(element)
  textfile.close()      
    

  
if __name__ == "__main__":
  run()