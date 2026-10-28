# String Problem 2: Check if a String is a Palindrome

# Write a function that checks whether a string reads the same forwards and backwards — ignoring case and spaces (but you can assume no punctuation for now, to keep it simple).

# Example:

# Input: "madam"
# Output: True
# Input: "Nurses Run"
# Output: True
# (ignoring case and the space: "nursesrun" reversed is "nursesrun")
# Input: "hello"
# Output: False

def string_palindrom(s):
    l,r=0,len(s)-1
    while l<r:
        while l<r and not s[l].isalnum():
            l+=1
        while l<r and not s[r].isalnum():
            r-=1
        if s[l].lower() != s[r].lower():
            return False
        l+=1    
        r-=1
    return True
print(string_palindrom("Was it a car or. a cat I saw?"))