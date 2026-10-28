# String Problem 3: Check if Two Strings are Anagrams
# Write a function that checks whether two strings are anagrams of each other — meaning they contain exactly the same characters with the same frequencies, just possibly in a different order.

# Example:
# Input: s1 = "listen", s2 = "silent"
# Output: True
# Input: s1 = "hello", s2 = "world"
# Output: False
# Input: s1 = "Dormitory", s2 = "Dirty Room"
# Output: True  (ignoring case and spaces)
from collections import Counter

def two_strings_are_anagram(s1,s2):
    s1="".join(sorted(c.lower() for c in s1 if c.isalnum()))
    s2="".join(sorted(c.lower() for c in s2 if c.isalnum()))
    return Counter(s1) == Counter(s2)

print(two_strings_are_anagram("Dormitory","Dirty Room"))