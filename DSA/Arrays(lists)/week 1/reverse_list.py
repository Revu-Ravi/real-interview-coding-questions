# Array Problem 3: Reverse an Array In-Place
# Write a function that reverses a list of integers in-place — meaning you should not create a new list or use Python's built-in .reverse() or slicing trick (arr[::-1]). Modify the original array directly using minimal extra space.

# Example:
# Input: [1, 2, 3, 4, 5]
# Output: [5, 4, 3, 2, 1]

# Input: [10, 20, 30, 40]
# Output: [40, 30, 20, 10]

# Things to think about:
# What if you had two pointers — one starting at the beginning of the array, one at the end?
# What would you do with the elements they're pointing to?
# When should the pointers stop moving? (Think about what happens when they meet or cross each other.)
# Can you solve this using O(1) extra space (i.e., without creating a second array)?

# This is your first taste of the Two Pointers technique, which is a big deal in coding interviews — you'll see it a LOT going forward.


def reverse_list(li):
    l,r=0,len(li)-1
    while l<r:
        li[l],li[r]=li[r],li[l]
        l+=1
        r-=1
    return li


# def reverse_list(li):
#     for i in range(len(li)//2):
#         temp=li[i]
#         li[i]=li[len(li)-i-1]
#         li[len(li)-i-1]=temp
#     return li
result=reverse_list([40, 30, 20, 10])
print(result)
