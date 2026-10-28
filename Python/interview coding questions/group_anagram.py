#Input: ["eat", "tea", "tan", "ate", "nat", "bat"]
#Output: [
#["ate", "eat", "tea"],
#["nat", "tan"],
#["bat"]
#] 
 
l1= ["eat", "tea", "tan", "ate", "nat", "bat"]
d1={}
for word in l1:
    k="".join(sorted(word)) 
    # print(k)
    if k not in d1:
        d1[k]=[]
        # print(k,d1.items())
    d1[k].append(word)
print(list(d1.values()))

# "defaultdict(list) automatically creates an empty list when the key doesn't exist, so I don't need to check if k not in d1."
# from collections import defaultdict

# l1 = ["eat", "tea", "tan", "ate", "nat", "bat"]

# d1 = defaultdict(list)

# for word in l1:
#     k = "".join(sorted(word))
#     d1[k].append(word)

# print(list(d1.values()))