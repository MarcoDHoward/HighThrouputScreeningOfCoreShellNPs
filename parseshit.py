import pickle

def parseWolfram(filename):
  f = open(filename, 'r')
  data = f.readlines()
  data = [  item.replace(' ', '')  for item in data[0].strip('\n').replace('{', '(').replace( '}', ')\n').split('\n')]

  del data[-1]

  m1 = []
  m2 = []
  
  for i in range (len (data) ):
    m1.append(data[i].replace('(','').replace( ')', '' ).split(',')[0])
    m2.append(data[i].replace('(','').replace( ')', '' ).split(',')[1])
  codes = []
  for i in range (len (m1) ):
    codes.append('19%s@60%s' %(m1[i], m2[i] ) )
  return codes

  
  

pickle.dump( parseWolfram("small.txt"), open("small_corr.p", 'wb') )
pickle.dump( parseWolfram("big.txt"), open("big_corr.p", 'wb') )

print parseWolfram("small.txt")
print parseWolfram("big.txt")

