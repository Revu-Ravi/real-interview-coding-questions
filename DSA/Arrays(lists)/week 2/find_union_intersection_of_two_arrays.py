# Find the Union and Intersection of Two Arrays

# Given two arrays, find:

# Their union (all distinct elements present in either array)
# Their intersection (elements present in both arrays)

# Example:

# Input: arr1 = [1, 2, 3, 4, 5], arr2 = [3, 4, 5, 6, 7]
# Union: [1, 2, 3, 4, 5, 6, 7]
# Intersection: [3, 4, 5]

arr1 = [1, 2, 3, 4, 5] 
arr2 = [3, 4, 5, 6, 7]
print("Union:{} \nIntersection: {}".format(list(set(arr1)|(set(arr2))),list(set(arr1)&(set(arr2)))
))

# def union_and_intersection_of_two_arrays(arr1,arr2):
#     Union=set(arr1).union(set(arr2))
#     Intersection = set(arr1).intersection(set(arr2))
#     return list(Union), list(Intersection)


# u,i=union_and_intersection_of_two_arrays([1, 2, 3, 4, 5],[3, 4, 5, 6, 7])
# print("Union:{} \n Intersection: {}".format(u,i))
