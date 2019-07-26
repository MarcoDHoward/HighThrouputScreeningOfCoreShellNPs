import pickle

smallList =  pickle.load( open( "small.p", 'r' ) )
bigList = pickle.load( open ("big.p", 'r' ) )

print smallList
print bigList
