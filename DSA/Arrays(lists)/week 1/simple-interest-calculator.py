# Simple Interest Calculator

# Write a program that:
# Takes three inputs: principal amount (P), rate of interest (R), and time (T) in years.
# Calculates the Simple Interest using the formula:
# SI = (P * R * T) / 100
# Prints the result rounded to 2 decimal places.

# Example:
# Input: P = 1000, R = 5, T = 2
# Output: Simple Interest = 100.00
P = float(input("Enter Principal Amount: "))
R = float(input("Enter Rate of Interest: "))
T = float(input("Enter Time in Years: "))

SI = (P * R * T)/100
print(f"Simple Interesest : {SI :.2f}")
