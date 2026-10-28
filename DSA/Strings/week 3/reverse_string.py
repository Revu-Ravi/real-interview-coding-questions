# String Problem 1: Reverse a String

# Write a function that reverses a string without using slicing ([::-1]) and without the built-in reversed() function. Build it manually using a loop or two-pointer technique.

# Example:

# Input: "hello"
# Output: "olleh"
# Input: "Python"
# Output: "nohtyP"

def reverse_string(s):
    chars=list(s)
    l,r = 0,len(chars)-1
    while l<r:
        chars[l],chars[r]=chars[r], chars[l]
        l+=1
        r-=1
    return ''.join(chars)  
result=reverse_string("python")
print(result)