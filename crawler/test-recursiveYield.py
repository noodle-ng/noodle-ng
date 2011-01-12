
def faculty(k,result=1,counter=1):
    
    if counter == k:
        return result*counter
    else:
        return faculty(k,result*counter,counter+1)

# does what it should but the wrong way
def facultyGenerator(k,result=1,counter=1):
    
    yield result*counter
    
    if counter == k:        
        raise StopIteration
    else:
        # list forces generator to be evaluated
        yield list(facultyGenerator(k,result*counter,counter+1))
        

print faculty(4)
print list(facultyGenerator(4))