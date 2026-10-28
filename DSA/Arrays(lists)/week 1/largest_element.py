# Array Problem 1: Find the Largest Element in an Array
# Write a function that takes a list of integers and returns the largest element — without using Python's built-in max() function.

# Example:
# Input: [3, 7, 2, 9, 4]
# Output: 9
# Input: [-5, -1, -12, -3]
# Output: -1


def largerst_element(l1):
    largerst_element = l1[0]
    l2 = float('-inf')
    # print(l2)
    for i in l1:
        if largerst_element<i:
            # l2=largerst_element
            largerst_element=i
        elif l2<i and largerst_element!=i:
            l2=i
    return l2
result=largerst_element([-5, -5])
print(result)

# print(max(l1))

# l1.sort(reverse=True)
# print(l1[0])


