def btreeToLength(tree):
    leftSide = 0
    rightSide = 0
    if(tree.left != "N"):
        leftSide = btreeToLength(tree.left)
    if(tree.right != "N"):
        rightSide = btreeToLength(tree.right)
    return leftSide+rightSide+1

def listToString(list):
    list = '[%s]' % ', '.join(
                map(str, list)).replace("'", "")
    list = list.replace(",", "")
    return list