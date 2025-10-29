# PhantomScript
PhantomScript is a concept language with an interpreter written in Python. It has limited functionality but you can make some cool stuff. Example Hello World:
``` PhantomScript
print "Hello, World!"
```

As demonstrated by the above example, the syntax does not use () for function calls. Instead, everything is keyword-based, a lot like shell commands! Indentation is not necessary, just provided for readability.

In case you couldn't tell, it's heavily inspired by Lua.

I should also probably mention that this is a concept toy language that started life as an esolang. It cannot and should not be used for real applications.

To run a program, you can:
- Run `python3 main.py <file>`
- Run `.\main.exe <file>`
- Run like a normal Python script and enter the file to execute when prompted.

## All Keywords/Syntax
### Overview
- `print`: prints value of any type to console.
  - `print "hello world"`
- `mark`: marks location with name.
  - `mark "nameOfPlace"`
- `goto`: goes to scrawled location.
  - `goto "nameOfPlace"`
- `var`: creates variable.
  - `var varName "varValue"`
- `let`: same as var, because I feel kind
- `$<varName>`: gets value of variable.
  - `print $varName`
- `if`: conditionals. See explanation.
  - `if Yes`
- `end`: ends current block. Used to exit conditionals.
- `stack`: concatenates variable with given value. Useful for incrementation.
  - `stack numVar 15`
- `$input`: referenced like a variable. Gets user input.
  - `print $input`
- `@<value1>:<operator>:<value2>`: inline scripts for boolean expressions.
  - `if @15:is:15`
- `exit`: end the program
- `wait`: waits for enter key to be pressed.
- `function`: define a function. See explanation.
    `function funcName`
- `while`: start a while loop. See explanation.
    - `while Yes`
- `break`: don't restart next time loop finishes. See explanation.
- `read <fileName> <outputVar>`: if a file exists, it gets its contents and outputs string to outputVar.
- `write <fileName> <text>`: writes a value to a file.

### Explanation
- `if`: Bools are stored as either `Yes` or `No`. If the given bool is `No`, then lines are skipped indefinitely. You can exit and start executing again with `end`.
- `function`: Functions don't have their own namespaces, so **they don't support arguments**. You can put anything in a function. They are ended with `end` just like other blocks.
- `while`: While loops behave like functions in that they store a line to return to when `end` is reached. When they return to their starting line, the conditional is read again and if it is `Yes`, the loop goes again. If it is `No`, execution keeps going from the loop's start but skips the loop's contents.
- `break`: This **does not** end the loop here and now. Instead, it makes the loop not return to its start the next time it completes.
- `@<value1>:<operator>:<value2>`: Inline scripts are used to do boolean operations and very simple math. The operator is used to compare the values. Operators:
  - `<`
  - `>`
  - `==`
  - `is`
  - `isnt`
  - `isn't`
  - `!=`
  - `>=`
  - `<=`
  - `+`
  - `-`
  - `/`
  - `*`
`==` and `is` do the same thing. `isn't`, `!=`, and`isnt` do the same thing. Example:
``` PhantomScript
if @15:>:10
    print "15 is greater than 10."
end
```

## How it Works
Variables are stored in a `namespace` dictionary. There are three data types: `string`, `num`, and `boolean`. Nums are all Python floats, so even if you set a variable to a whole number it will be stored as a decimal.


Inline scripts are processed as one word initially and then replaced with their resulting boolean values. Because of this, they use their own type preprocessor. If you're curious, you can look in the `simplify(script)` function in the interpreter.

