import re
import gc
import time
import sys
import os
import copy


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


#re.findall wasn't working so I made a much worse version
def getStrings(line):
    tracking = False
    strings = []
    current = ""
    elapsed = ""
    for i in line:
        if i == '"':
            tracking = not tracking
            if not tracking:
                elapsed += '"'
                strings.append(elapsed)
                elapsed = ""
        if tracking:
            elapsed += i
    return strings


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


def isValidDeclaration(foo):
    return isValidArray(foo) or isValidString(foo) or foo.isdecimal() or isValid(foo) or foo in ("Yes", "No")


def boo():
    if len(words) == 1:
        print()
    elif len(words) == 2:
        if not isValid(words[1]):
            return f"err InputNotValid - {type(words[1])}"
        print(words[1].value)
    elif len(words) > 2:
        return "err TooManyArgs - Expected 2"


def var():
    if not len(words) == 3:
        return "err InvalidNumberOfArgs - Expected 3"
    namespace[words[1]] = words[2]


def instantiate():
    if not len(words) == 3:
        return "err InvalidNumberOfArgs - Expected 3"
    
    old = words[1]
    new = words[2]

    if not words[1] in namespaces:
        return f"err InvalidObject - '{old}'"
    namespaces[new] = copy.deepcopy(namespaces[old])

    #copy all owned funcs
    owned = {i: j for i, j in funcs.items() if i.startswith(f"{old}.")}
    for name, index in owned.items():
        newName = name.replace(f"{old}.", f"{new}.")
        funcs[newName] = index


def readFile():
    if not len(words) == 3:
        return "err InvalidNumberOfArgs - Expected 3"
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
        return "err InvalidNumberOfArgs - Expected 3"
    if not isinstance(words[1], string):
        return f"err InvalidValueOrType - {words[1]}"
    if not isValid(words[2]):
        return f"err InvalidValueOrType - {words[2]}"
    with open(str(words[1].value), "w") as file:
        file.write(str(words[2].value))


def loc():
    if not len(words) == 2:
        return "err InvalidNumberOfArgs - Expected 2"
    if not isValid(words[1]):
        return "err InvalidValueOrType"
    locs[words[1].value] = lineNum


def conditional():
    if len(words) != 2:
        return "err InvalidNumberOfArgs - Expected 2"
    if not isinstance(words[1], boolean):
        return f"err InvalidValueOrType - {type(words[1])}"
    if words[1].value == "Yes":
        layers.append("conditional")
    else:
        layers.append("unmet")


def elseBlock():
    global elsePasses
    if len(words) > 2:
        return "err InvalidNumberOfArgs - Expected 1 or 2"
    if not elsePasses:
        layers.append("unmet")
        return
    if len(words) == 2:
        conditional()
    else:
        layers.append("else")


def whileLoop():
    global isLoop
    if len(words) != 2:
        return "err InvalidNumberOfArgs - Expected 2"
    isLoop = True
    if not isinstance(words[1], boolean):
        return f"err InvalidValue - While loops need booleans"
    if words[1].value == "Yes":
        #at end of loop, return like a function
        layers.append(lineNum - 1)
    else:
        #if not condition, treat loop like unmet if statement
        layers.append("unmet")


def breakStatement():
    global layers

    #new, better
    layers.reverse()
    for i in layers:
        if isinstance(i, int):
            index = layers.index(i)
            break
    layers.pop(index)
    layers.insert(index, "unmet")
    layers.reverse()


def endBlock():
    global lineNum
    global elsePasses
    global currentNamespace
    global namespace
    global namespaces
    global isLoop
    global namespaceHistory
    layer = layers.pop()
    if len(layers) <= 0:
        return "err EndedMain - No block to end"
    if layer == "unmet":
        elsePasses = True
    else:
        elsePasses = False

    #handle function returns
    if isinstance(layer, int):
        lineNum = layer
        if not isLoop:
            #handle return to original context
            old = namespaceHistory.pop()

            #not the greatest approach, but its 8 pm and im tired
            if len(namespaceHistory) == 0:
                namespaceHistory = [old]
            
            namespace = namespaces[namespaceHistory[-1]]
            currentNamespace = namespaceHistory[-1]
        else:
            isLoop = False
    if layer == "namespace":
        currentNamespace = "main"
        namespace = namespaces["main"]


def functionDef():
    if not len(words) >= 2:
        return "err InvalidNumberOfArgs"
    name = words[1]
    if currentNamespace != "main":
        name = f"{currentNamespace}.{name}"

    funcs[name] = lineNum

    #arguments
    if len(words) > 2:
        funcRequirements[name] = words[2::]

    layers.append("unmet")


def goto():
    global lineNum
    if not len(words) == 2:
        return "err InvalidNumberOfArgs"
    if not words[1].value in locs.keys():
        return "err InvalidPos - Set it with mark"
    lineNum = locs[words[1].value] - 1


def add():
    if len(words) < 3:
        return "err InvalidNumberOfArgs"
    var = words[1]
    val = words[2]

    if len(words) == 4:
        val = words[3]
        key = words[2]
    elif len(words) > 3:
        return "err InvalidNumberOfArgs"

    if line.split()[1].startswith("$"):
        return "err WantedVarNameNotValue - If you referenced the variable with $, delete the symbol. You want to reference the variable, not its value."
    if isinstance(namespace[var], boolean):
        return "err BooleanNotSupported"
    if not var in namespace:
        return "err InvalidValueOrType"
    if isinstance(namespace[var], array):
        arr = namespace[var]

        #generate new key
        key = max([-1]+[int(i) for i in arr.value.keys() if isinstance(i, int) or i.isdecimal()]) + 1
        
        arr.value[key] = val
        return
    if not type(namespace[var]) == type(val):
        return f"err IncompatibleTypes - {type(namespace[var])}, {type(val)}"

    #actually do thing
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
            new = string(old.replace("\n".encode("unicode_escape").decode("utf-8"), "\n")[1:-1])

            args.insert(aindex, new)
        elif arg.count('"') % 2 != 0:
            return "err UnterminatedString - InlineScript"
        elif arg in ["Yes", "No"]:
            args.pop(aindex)
            args.insert(aindex, boolean(arg == "Yes"))
    return args


#allow for operations on variables
def attribute():
    if len(words) < 2:
        return "err InvalidNumberOfArgs"
    name = words[0]
    subcommand = words[1]
    if isinstance(namespace[name], array):
        if subcommand == "item":
            namespace[name].value[words[2].value] = words[3]
    if isinstance(namespace[name], num):
        if subcommand == "++":
            namespace[name].value += 1
            return
        if subcommand == "--":
            namespace[name].value -= 1


def simplify(script):
    #simplify inline expressions/scripts
    args = script.split(":")
    if (not len(args) == 3) and not (len(args) == 2 and isValidDeclaration(args[1])):
        return "err InvalidNumberOfArgs - InlineScript"
    operator = args[1]

    args = replaceVals(args)

    #get indices of arrays, strings
    if len(args) == 2:
        key = args[1].value
        if isinstance(args[0], num):
            return "err NumsNotIndexable - InlineScript"
        if isinstance(args[0], boolean):
            return "err BooleansNotIndexable - InlineScript"
        value = args[0].value[key]
        
        #convert to appropriate language obj
        #if already language obj, leave as-is
        if isinstance(value, bool):
            value = boolean(value)
        elif isinstance(value, str):
            value = string(value)
        elif isinstance(value, float):
            value = num(value)
        return value
        

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

    problems = [i for i in args if not isValid(i)]
    if len(problems) != 0:
        return f"err InvalidValueOrType - {problems[0]}"

    return array(args)


def funcCall():
    global res
    global layers
    global lineNum
    global namespace
    global namespaces
    global kw
    global isLoop
    global currentNamespace
    global funcRequirements

    isLoop = False

    #hadle contexts
    if not "." in kw:
        #func is in main
        namespace = namespaces["main"]
        namespaceHistory.append("main")
    else:
        #func is in custom namespace
        if len(kw.split(".")) != 2:
            return "err InvalidFunctionName - Incorrect number of ownership levels"
        
        nsn = kw.split(".")[0]
        if nsn not in namespaces.keys():
            return "err InvalidNamespaceName - Undefined namespace"
        namespace = namespaces[nsn]
        namespaceHistory.append(nsn)
        currentNamespace = nsn
    
    #handle arguments
    if kw in funcRequirements:
        args = funcRequirements[kw]
        if len(words) != len(args) + 1:
            return f"err InvalidNumberOfArgs - Expected {len(args)} but got {len(words) - 1}"
        
        #args match
        #GeeksForGeeks taught me zip
        for argName, value in zip(args, words[1::]):
            namespace[argName] = value

    #move CPU
    layers.append(lineNum)
    lineNum = funcs[kw]
    res = None


def makeNS():
    global namespace
    global namespaces
    global currentNamespace
    if len(words) != 2:
        return "err InvalidNumberOfArgs"
    
    currentNamespace = words[1]
    namespaces[currentNamespace] = {}
    namespace = namespaces[currentNamespace]

    layers.append("namespace")


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

if filename == "":
    while True:
        filename = input("Please select a file to run:\n>")
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                text = file.read()
                break
        else:
            print("Invalid file name.")

text = text.split("\n") + ["exit"]

print()

lineNum = 0
layers = ["host"]
locs = {}
funcs = {}
funcRequirements = {}
elsePasses = False
isLoop = False

namespaces = {"main": {}}
namespace = namespaces["main"]
currentNamespace = "main"
namespaceHistory = ["main"]

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
       "read": readFile,
       "process": attribute,
       "object": makeNS,
       "copy": instantiate}
layerStarters = ["if", "while", "else", "function", "object"]

#iterate over file's lines to execute
while True:
    line = text[lineNum].strip()

    #preprocess literal declarations
    if line.count('"') % 2 != 0:
        error("err UnterminatedString")
        break
    if '"' in line:
        #replace spaces in strs with non-spaces
        for i in getStrings(line):
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
            elif not word[1::] in namespace.keys():
                error(f"VarNameInvalid - '{word[1::]}'")
                break
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

    #process keywords
    if kw in kws:
        res = kws[kw]()
    elif kw in funcs.keys():
        res = funcCall()
    #handle if 'this' keyword is used
    elif kw.startswith("this."):
        kw = kw.replace("this", currentNamespace)
        words.pop(0)
        words.insert(0, kw)
        if not kw in funcs.keys():
            res = f"err InvalidFunctionName - Namespace '{currentNamespace}' has no function '{kw}'"
        else:
            res = funcCall()
    elif kw in namespace:
        res = kws["process"]()

    if isinstance(res, str) and res.startswith("err"):
        error(res)
        break

    if text[lineNum] == "exit":
        break

    lineNum += 1
    if lineNum >= len(text) - 1:
        break

gc.collect()
