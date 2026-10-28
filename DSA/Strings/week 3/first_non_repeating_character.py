# String Problem 4: First Non-Repeating Character
# Given a string, find the first character that doesn't repeat anywhere else in the string. Return the character (or indicate if none exists).

# Example:
# Input: "swiss"
# Output: "w"
# (s appears 3 times, w appears once, i appears once — but 'w' comes before 'i')
# Input: "aabbcc"
# Output: None (every character repeats)
# Input: "leetcode"
# Output: "l"
from collections import Counter
def non_repeating_character(s):
    c =Counter(s)
    for key in s:
        if c[key]==1:
            return key
    return None
print(non_repeating_character("leetcode"))

