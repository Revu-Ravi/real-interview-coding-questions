# Array Problem 5: Rotate Array by K Positions
# Write a function that rotates a list of integers to the right by k positions, in-place (don't create a new array, and avoid slicing tricks like arr[-k:] + arr[:-k] — build it manually).

# Example:
# Input: [1, 2, 3, 4, 5, 6, 7], k = 3
# Output: [5, 6, 7, 1, 2, 3, 4]

# Input: [1, 2, 3], k = 4
# Output: [3, 1, 2]

def reverse(arr, a, b):
    while a<b:
        arr[a],arr[b]=arr[b],arr[a] #swap 
        a+=1
        b-=1

def rotate_array(arr,k):

    n = len(arr)#7
    k = k%n #3
    reverse(arr, 0, n-1)
    reverse(arr, 0, k-1)
    reverse(arr, k, n-1)
    return arr


print(rotate_array([1, 2, 3],4))