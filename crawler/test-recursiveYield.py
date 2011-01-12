
def faculty(k,result=1,counter=1):
    
    if counter == k:
        return result*counter
    else:
        return faculty(k,result*counter,counter+1)
    
def facultyGenerator(k,result=1,counter=1):
    
    if counter == k:
        raise StopIteration
    else:
        yield result*counter
        yield faculty(k,result*counter,counter+1)

print list(facultyGenerator(4))