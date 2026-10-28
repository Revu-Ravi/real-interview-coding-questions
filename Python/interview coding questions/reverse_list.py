# Array Problem 3: Reverse an Array In-Place
# Write a function that reverses a list of integers in-place — meaning you should not create a new list or use Python's built-in .reverse() or slicing trick (arr[::-1]). Modify the original array directly using minimal extra space.

# Example:
# Input: [1, 2, 3, 4, 5]
# Output: [5, 4, 3, 2, 1]

# Input: [10, 20, 30, 40]
# Output: [40, 30, 20, 10]

# [40, 30, 20, 10]
# l=0,r=3
# [10, 30, 20, 40]
# l=1,r=2
# [10, 20, 30, 40]

def reverse_list(li):
    l,r=0,len(li)-1 #len(li)=4
    while l<r:
        li[l],li[r]=li[r],li[l]
        l+=1
        r-=1
    return li

result=reverse_list([40, 30, 20, 10])
print(result)
