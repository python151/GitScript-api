class Ratio():
    def __init__(self, val1, val2):
        self.val1, self.val2 = val1, val2
    def multiply(self, ratio2):
        val1 = self.val1 * ratio2.val1
        val2 = self.val2 * ratio2.val2

        ret = Ratio(val1, val2)
        return ret
    def simplify(self):
        largestVal = self.val1
        if self.val2 > largestVal: largestVal = self.val2

        largestRatio = Ratio(self.val1, self.val2)
        for i in range(int(largestVal+1)):
            if i == 0: i = 1
            if (self.val1/i).is_integer() and (self.val2/i).is_integer():
                largestRatio = Ratio(self.val1/i, self.val2/i)
        
        return largestRatio
        