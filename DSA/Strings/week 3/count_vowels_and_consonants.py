# String Problem 5: Count Vowels and Consonants
# Write a function that takes a string and counts the number of vowels and consonants in it (ignore spaces, numbers, and punctuation — only count actual letters).

# Example:
# Input: "Hello World 123!"
# Output: Vowels: 3, Consonants: 7
# Input: "Python Programming"
# Output: Vowels: 4, Consonants: 14

# Things to think about:
# What counts as a vowel? (a, e, i, o, u — and should you handle both uppercase and lowercase?)
# How do you check if a character is a letter at all (to skip spaces, digits, punctuation)? Think back to a string method you've already used in this session...
# Can you solve this in a single pass through the string, incrementing two separate counters as you go?

def count_vowels_and_consonants(s):
    vowels_set=['a', 'e', 'i', 'o', 'u']
    vowels=0
    consonants=0
    for c in s:
        if c.isalpha():
            if c.lower() in vowels_set:
                vowels+=1
            else:
                consonants+=1
    return "Vowels: {}, Consonants: {}".format(vowels,consonants) 

print(count_vowels_and_consonants("Python Programming"))