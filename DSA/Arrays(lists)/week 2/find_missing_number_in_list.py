# Array Problem 7: Find the Missing Number
# You're given an array containing n distinct numbers taken from the range 0 to n (inclusive) — so the array has n elements, but one number in the range [0, n] is missing. Find the missing number.

# Example:
# Input: [3, 0, 1]
# Output: 2
# (n = 3, range is [0,1,2,3], array has 3 elements, missing number is 2)
# Input: [0, 1]
# Output: 2
# (n = 2, range is [0,1,2], array has 2 elements, missing number is 2)
# Input: [9,6,4,2,3,5,7,0,1]
# Output: 8

# formula = n*(n+1)/2

def find_missing_number(arr):
    n=len(arr)
    n=n*(n+1)//2
    return n-sum(arr)

print(find_missing_number([9,6,4,2,3,5,7,0,1]))