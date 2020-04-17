from Gear import Gear
from Ratio import Ratio

# Input the amount of teeth on each gear here.
A = Gear(10) 
B = Gear(20)
C = Gear(10)

def largestRatio(A, B):
    largestGear = A.teeth
    if B.teeth > largestGear: largestGear = B.teeth

    largestRatio = Ratio(A.teeth, B.teeth)
    for i in range(largestGear+1):
        if i == 0: i = 1
        if (A.teeth/i).is_integer() and (B.teeth/i).is_integer():
            largestRatio = Ratio(A.teeth/i, B.teeth/i)
    return largestRatio

AToB = largestRatio(A, B)
BToC = largestRatio(B, C)
AToC = AToB.multiply(BToC).simplify()

print("A:B", AToB.val1, ":", AToB.val2)
print("B:C", BToC.val1, ":", BToC.val2)
print("A:C", AToC.val1, ":", AToC.val2)

