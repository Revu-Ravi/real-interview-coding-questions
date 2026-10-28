p='swiss'
# for i in p:
#     if p.count(i)==1:
#         print(i)
#         break;
from collections import Counter
def nrc(p):
    a = Counter(p)
    for i in p:
        if a[i] ==1:
            return i
    return None
print(nrc(p))
