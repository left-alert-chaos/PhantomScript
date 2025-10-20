import re
import gc
import time
import sys
import os


class string:
    def __init__(self, value):
        self.value = str(value)


class num:
    def __init__(self, value):
        self.value = float(value)


class boolean:
    def __init__(self, value):
        value = bool(value)
        self.value = "Yes" if value else "No"


class array:
    def __init__(self, value):
        self.value = {}
        if isinstance(value, list):
            for index, item in enumerate(value):
                self.value[index] = item
        elif isinstance(value, dict):
            self.value = value


#determine if a str is a num
def isNum(numberString):
    try:
        float(numberString)
    except:
        return False
    else:
        return True


def isValid(foo):
    if isinstance(foo, num):
        return True
    if isinstance(foo, string):
        return True
    if isinstance(foo, boolean):
        return True
    if isinstance(foo, array):
        return True
    return False


def isValidString(foo):
    return foo.startswith('"') and foo.endswith('"')


def isValidArray(foo):
    return foo.startswith("{") and foo.endswith("}")


def boo():
    if len(words) == 1:
        print()
    elif len(words) == 2:
        if not isValid(words[1]):
            return "err InputNotValid"
        print(words[1].value)
    elif len(words) > 2:
        return "err TooManyArgs"


def var():
    if not len(words) == 3:
        return "err InvalidNumberOfArgs"
    namespace[words[1]] = words[2]


def readFile():
    if not len(words) == 3:
        return "err InvalidNumberOfArgs"
    if not isinstance(words[1], string):
        return f"err InvalidValueOrType - {words[1]}"
    if isValid(words[2]):
        return f"err InvalidValueOrType - {words[2]} - Wanted a variable name not a value"
    try:
        with open(str(words[1].value), "r") as file:
            text = file.read()
    except:
        return "err InvalidFileName"
    namespace[words[2]] = string(text)


def writeFile():
    if not len(words) == 3:
        return "err InvalidNumberOfArgs"
    if not isinstance(words[1], string):
        return f"err InvalidValueOrType - {words[1]}"
    if not isValid(words[2]):
        return f"err InvalidValueOrType - {words[2]}"
    with open(str(words[1].value), "w") as file:
        file.write(str(words[2].value))


def loc():
    if not len(words) == 2:
        return "err InvalidNumberOfArgs"
    if not isValid(words[1]):
        return "err InvalidValueOrType"
    locs[words[1].value] = lineNum


def conditional():
    if len(words) != 2:
        return "err InvalidNumberOfArgs"
    if not isinstance(words[1], boolean):
        return f"err InvalidValueOrType - {type(words[1])}"
    if words[1].value == "Yes":
        layers.append("conditional")
    else:
        layers.append("unmet")


def elseBlock():
    global elsePasses
    if len(words) > 2:
        return "err InvalidNumberOfArgs"
    if not elsePasses:
        layers.append("unmet")
        return
    if len(words) == 2:
        conditional()
    else:
        layers.append("else")


def whileLoop():
    if len(words) != 2:
        return "err InvalidNumberOfArgs"
    if not isinstance(words[1], boolean):
        return f"err InvalidValue - While loops need booleans"
    if words[1].value == "Yes":
        #at end of loop, return like a function
        layers.append(lineNum - 1)
    else:
        #if not condition, move on from loop start
        layers.append("unmet")


def breakStatement():
    global shouldBreak
    shouldBreak = True


def endBlock():
    global lineNum
    global elsePasses
    global shouldBreak
    layer = layers.pop()
    if len(layers) <= 0:
        return "err EndedHost - No block to end"
    if layer == "unmet":
        elsePasses = True
    else:
        elsePasses = False

    #handle function returns
    if isinstance(layer, int) and not shouldBreak:
        lineNum = layer
        if text[lineNum] == "exit":
            return "exit"
    elif shouldBreak:
        shouldBreak = False


def functionDef():
    if not len(words) >= 2:
        return "err InvalidNumberOfArgs"
    funcs[words[1]] = lineNum
    layers.append("unmet")


def goto():
    global lineNum
    if not len(words) == 2:
        return "err InvalidNumberOfArgs"
    if not words[1].value in locs.keys():
        return "err InvalidPos - Set it with mark"
    lineNum = locs[words[1].value] - 1


def add():
    if not len(words) == 3:
        return "err InvalidNumberOfArgs"
    var = words[1]
    val = words[2]
    if line.split()[1].startswith("$"):
        return "err WantedVarNameNotValue - If you referenced the variable with $, delete it. You want to reference the variable, not its value."
    if isinstance(namespace[var], boolean):
        return "err BooleanNotSupported"
    if not var in namespace:
        return "err InvalidValueOrType"
    if not type(namespace[var]) == type(val):
        return f"err IncompatibleTypes - {type(namespace[var])}, {type(val)}"
    namespace[var].value += val.value


def error(errType):
    print(f"Error on line {lineNum + 1}. Line text:\n{line}\n\n{errType}")


def replaceVals(args):
    #type preprocessing
    for aindex, arg in enumerate(args):
        if arg.startswith("$") and arg[1::] in namespace:
            old = args.pop(aindex)
            args.insert(aindex, namespace[arg[1::]])
        elif arg.startswith("$"):
            if arg == "$input":
                args.pop(index)
                args.insert(index, string(input()))
            else:
                return f"err VarNotFound - {arg} - InlineScript"
        elif isNum(arg):
            args.pop(aindex)
            args.insert(aindex, num(arg))
        elif isValidString(arg):
            old = args.pop(aindex)

            #this line has code from StackOverFlow
            new = string(old.replacereplace("\n".encode("unicode_escape").decode("utf-8"), "\n")[1:-1])

            args.insert(aindex, new)
        elif arg.count('"') % 2 != 0:
            return "err UnterminatedString - InlineScript"
        elif arg in ["Yes", "No"]:
            args.pop(aindex)
            args.insert(aindex, boolean(arg == "Yes"))
    return args


def simplify(script):
    #simplify inline expressions/scripts
    args = script.split(":")
    if not len(args) == 3:
        return "err InvalidNumberOfArgs - InlineScript"
    operator = args[1]

    args = replaceVals(args)

    #operators
    if operator in ["==", "is"]:
        return boolean(args[0].value == args[2].value)
    if operator in ["isn't", "isnt", "!="]:
        return boolean(args[0].value != args[2].value)
    if operator == ">":
        return boolean(args[0].value > args[2].value)
    if operator == "<":
        return boolean(args[0].value < args[2].value)
    if operator == "<=":
        return boolean(args[0].value <= args[2].value)
    if operator == ">=":
        return boolean(args[0].value >= args[2].value)
    if operator == "+":
        if not type(args[0]) == type(args[2]):
            return f"err IncompatibleTypes - InlineScript"
        if isinstance(args[0], num):
            return num(args[0].value + args[2].value)
        elif isinstance(args[0], string):
            return string(args[0].value + args[2].value)
        else:
            return "err TypesNotAddable - InlineScript"
    if operator == "-":
        if (not isinstance(args[0], num)) or (not isinstance(args[2], num)):
            return "err NonNumsNotSubtractable - InlineScript"
        return num(args[0].value - args[2].value)
    if operator == "*":
        if (not isinstance(args[0], num)) or (not isinstance(args[2], num)):
            return "err NonNumsNotMultipliable - InlineScript - You cannot multiply values that aren't nums."
        return num(args[0].value * args[2].value)
    if operator == "/":
        if (not isinstance(args[0], num)) or (not isinstance(args[2], num)):
            return "err NonNumsNotDividable - InlineScript - You cannot divide values that aren't nums."
        return num(args[0].value / args[2].value)


def makeArray(rawDeclaration):
    #extract values, not trailing spaces and brackets
    args = rawDeclaration[2:-2].strip().split()
    args = replaceVals(args)

    problems = []

    #make sure no unknown values
    [problems.append(i) for i in args if not isValid(i)]
    if len(problems) != 0:
        return f"err InvalidValueOrType - {problems[0]}"

    return array(args)


#get file name
filename = ""

if len(sys.argv) == 3 and sys.argv[0].startswith("python"):
    filename = sys.argv[2]
    if not os.path.isfile(filename):
        print("Filename not valid.")
    else:
        with open(filename, "r") as target:
            text = target.read()
elif len(sys.argv) == 2 and not sys.argv[0].startswith("python"):
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Filename not valid.")
    else:
        with open(filename, "r") as target:
            text = target.read()

#i am aware that os.path.isfile exists. Please don't yell at me about this.
if filename == "":
    while True:
        filename = input("What file should we execute?\n>")
        try:
            with open(filename, "r") as target:
                text = target.read()
        except:
            print("Invalid file.")
        else:
            break

text = text.split("\n") + ["exit"]

#print("Killing -I mean executing- file...\n")
print()

lineNum = 0
layers = ["host"]
namespace = {}
locs = {}
funcs = {}
elsePasses = False
shouldBreak = False

#holds functions to handle keywords
#end is empty bc it calls in a different area than other kws and otherwise deletes too many layers
kws = {"print": boo,
       "var": var,
       "let": var,
       "mark": loc,
       "goto": goto,
       "if": conditional,
       "end": lambda: 5 + 5,
       "stack": add,
       "function": functionDef,
       "wait": input,
       "while": whileLoop,
       "break": breakStatement,
       "else": elseBlock,
       "write": writeFile,
       "read": readFile}
layerStarters = ["if", "while", "else", "function"]

#iterate over file's lines to execute
while True:
    line = text[lineNum].strip()

    #preprocess literal declarations
    if line.count('"') % 2 != 0:
        error("err UnterminatedString")
        break
    if re.search('".*"', line) is not None:
        #replace spaces in strs with non-spaces
        for i in re.findall('".*"', line):
            new = i.replace(" ", "&&&&&")
            line = line.replace(i, new)
    if re.search("{.*}", line) is not None:
        #replace spaces with non-spaces
        for i in re.findall("{.*}", line):
            new = i.replace(" ", "&&&&&")
            line = line.replace(i, new)

    words = line.split()
    #support blank lines
    if len(words) == 0 or line.startswith("#"):
        lineNum += 1
        if lineNum == len(text):
            break
        continue
    kw = words[0]

    if kw == "end":
        res = endBlock()
        if isinstance(res, str) and res.startswith("err"):
            error(res)
            break
        if res == "exit":
            break
        lineNum += 1
        continue

    if "unmet" in layers:
        lineNum += 1
        if lineNum == len(text):
            break
        if kw in layerStarters:
            layers.append("unmetLayer")
        continue

    if kw == "exit":
        break

    #convert declarations to types for easy manipulation
    line = line.replace("&&&&&", " ")
    for index, word in enumerate(words):
        if isValidString(word):
            old = words.pop(index)
            #following line has code from stackoverflow
            new = string(word.replace("&&&&&", " ").replace("""\n""".encode("unicode_escape").decode("utf-8"), "\n")[1:-1])
            words.insert(index, new)
        elif isNum(word):
            old = words.pop(index)
            new = num(float(word))
            words.insert(index, new)
        elif word in ("Yes", "No"):
            old = words.pop(index)
            words.insert(index, boolean(word == "Yes"))
        elif word.startswith("$"):
            if word == "$input":
                words.pop(index)
                words.insert(index, string(input()))
            elif not word[1::] in namespace:
                error(lineNum + 1)
            else:
                words.pop(index)
                words.insert(index, namespace[word[1::]])
        elif word.startswith("@"):
            words.pop(index)
            new = simplify(word[1::])
            if isinstance(new, str):
                error(new)
                break
            words.insert(index, new)
        elif isValidArray(word):
            words.pop(index)
            word = word.replace("&&&&&", " ")
            new = makeArray(word)

            #error
            if isinstance(new, str):
                error(new)
                break

            words.insert(index, new)

    res = "err KeywordNotFound"

    if kw in kws:
        res = kws[kw]()
    elif kw in funcs.keys():
        layers.append(lineNum)
        lineNum = funcs[kw]
        res = None

    if isinstance(res, str) and res.startswith("err"):
        error(res)
        break

    if text[lineNum] == "exit":
        break

    lineNum += 1
    if lineNum >= len(text) - 1:
        break

gc.collect()
