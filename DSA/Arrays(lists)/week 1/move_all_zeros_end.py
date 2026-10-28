# Array Problem 4: Move All Zeros to the End
# Write a function that takes a list of integers and moves all 0s to the end, while maintaining the relative order of the non-zero elements. Do this in-place (don't create a new array).
# Example:

# Input: [0, 1, 0, 3, 12]
# Output: [1, 3, 12, 0, 0]
# Input: [4, 0, 2, 0, 0, 9]
# Output: [4, 2, 9, 0, 0, 0]

# Things to think about:
# Notice the non-zero elements must stay in the same relative order they appeared in originally (1, 3, 12 stays in that order, just zeros pushed to the end).
# Can you do this with a single pointer that tracks "where the next non-zero element should go"?
# Try to think of a solution that only makes one pass through the array.
# Bonus challenge: Can you solve it using O(1) extra space (no new list)?

# Hint to get started: Think of it like organizing books on a shelf — you want to slide all the "real" books to the front and push the "empty slots" (zeros) to the back, without messing up the book order.

# def move_all_zeros_end(li):
#     for i in li:
#         if i == 0:
#             li.remove(0)
#             li.append(0)
#     return li

def move_all_zeros_end(li):
    j=0
    for i in range(len(li)):
        if li[i]!=0:
            li[j],li[i]=li[i],li[j]
            j+=1
    return li
l=move_all_zeros_end([0, 1, 0, 3, 12])
print(l)
