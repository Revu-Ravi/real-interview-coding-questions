
def find_duplicates(arr):
    seen=set()
    duplicates=[]
    for i in arr:
        if i in seen and i not in duplicates:
            duplicates.append(i)     
        else:
            seen.add(i)
    return duplicates   

print(find_duplicates([1,2,3,4,4,2,3,7,6,2,1,2])) #[4, 2, 3, 1]