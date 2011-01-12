
def faculty(k,result=1,counter=1):
    
    if counter == k:
        return result*counter
    else:
        return faculty(k,result*counter,counter+1)

#crap   
def facultyGenerator(k,result=1,counter=1):
    
    if counter == k:
        yield result*counter
        raise StopIteration
    else:
        yield result
        yield facultyGenerator(k,result*counter,counter+1).next()

def count():
    yield 1
    yield 2
    yield 3
    raise StopIteration

print list(count())


#print faculty(4)
#print list(facultyGenerator(4))