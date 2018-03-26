with open('dataset.txt', 'r') as f:
    for line in f.readlines():
           # parts = 
            english = []
            oshiwambo = []

            english,oshiwambo = line.split('------')
            print (oshiwambo)
            
