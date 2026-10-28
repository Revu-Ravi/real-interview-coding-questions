# String Problem 6: String Compression
# Write a function that performs basic string compression using counts of repeated characters. For example, the string "aabcccccaaa" would become "a2b1c5a3". If the "compressed" string would not become smaller than the original string, return the original string.

# Example:
# Input: "aabcccccaaa"
# Output: "a2b1c5a3"
# Input: "abcdef"
# Output: "abcdef"  (compressed would be "a1b1c1d1e1f1" - longer, so return original)
# Input: "aabbcc"
# Output: "aabbcc"  (compressed would be "a2b2c2" - same length as original, so return original since it's not smaller)
def string_compression(s):
    count=0
    pc=''
    for c in s:
        if c==pc or pc == '':
            count+=1
        else:
            count=1
            pc= ''
        print(c,count)
        pc=c
    
    return 

print(string_compression("aabcccccaaa"))