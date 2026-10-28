# arr = [12, -1, -7, 8, -15, 30, 16, 28] and an integer k = 3
# Find the minimum element in every contiguous subarray (window) of size k as you slide through the array from left to right.

def min_elements_subarray(arr,k):
    result=[]
    # 8-3+1 = 6
    for i in range(len(arr)-k+1):
        # arr[0:0+3]
        subarry = arr[i:i+k]
        result.append(min(subarry))
    return result
print(min_elements_subarray([12, -1, -7, 8, -15, 30, 16, 28],3))