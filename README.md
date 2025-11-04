# PhantomScript
PhantomScript is a concept language with an interpreter written in Python. It has limited functionality but you can make some cool stuff. Example Hello World:
``` PhantomScript
print "Hello, World!"
```

As demonstrated by the above example, the syntax does not use () for function calls. Instead, everything is keyword-based, a lot like shell commands! Indentation is not necessary, just provided for readability.

In case you couldn't tell, it's heavily inspired by Lua.

I should also probably mention that this is a concept toy language that started life as an esolang. It cannot and should not be used for real applications. There are many bugs, some known, some not. If something doesn't work, feel free to let me know but do not panic and do not be surprised.

To run a program, you can:
- Run `python3 main.py <file>`
- Run `.\main.exe <file>`
- Run like a normal Python script and enter the file to execute when prompted.

## All Commands/Syntax
### Type declarations
- Nums: just type a number as its own word. 
  - `15`
- Strings: type a string with quotes (") around it.
  - `"hi"`
- Booleans: type `Yes` or `No`, which correspond to `True` and `False` in Python.
  - `No`
- Arrays: type elements as their own words inside braces. The braces must be seperated by one space from the first and last elements. To create an array of all the ways to say "one":
  - `{ 1 1.0 "one" }`

### Object-Oriented Syntax
*The syntax for creating and copying custom objects will be here instead of the main list.*
#### Creating Objects
To create an object type, you use the `object` keyword. Example:

``` PhantomScript
object thing1
  let myVar 1
end
```

The above example creates an object `thing1` and gives it the local variable `myVar`. Right now, there is no way to access local variables from the main namespace.

To give an `object` functions, we define functions inside it. Example:

``` PhantomScript
object thing1
  function chaos
    print "I'm causing chaos!"
  end
end

thing1.chaos
```

This snippet creates an object called `thing1`, gives it a function `chaos`, and then calls the function. Functions share variables with the rest of their namespaces.

Note that in the above snippet, we didn't need to create an instance of `thing1`. This is because namespaces are real as soon as they are created with `object`. To create more than one instance of an `object`, we use the `copy` keyword. Example:

``` PhantomScript
object thing1
  function chaos
    print "I'm causing chaos!"
  end
end

thing1.chaos

copy thing1 thing2
thing2.chaos
```

This example does everything from before, but it then uses `copy` to create `thing2`, which is identical to `thing1`. This is how you instantiate classes. However, `copy` just creates a duplicate of whichever namespace you provide so you don't have to give it original `object`s. Instead, you could give it a modified `object` instance and it will copy that instead.

#### The 'this' Keyword
The `this` keyword references the current namespace and is replaced with the current namespace's name at runtime. It is used to make self-referencing `object`s copy safe. Example:

``` PhantomScript
object counter
  let count 0
  function hidden_function
    count ++
    print $count
  end

  function tick
    this.hidden_function
  end
end

copy counter tracker1
copy counter tracker2

tracker1.tick
tracker2.tick
```

Here, a `counter` `object` is created with 2 functions: one that the user will call and one the user won't. The `this` keyword is used so that the current `counter`'s `count` will go up and not the base `object`'s.

### Indices
This probably shouldn't get its own section, but I had to put it somewhere.

To get a value from an index, you can use an inline script. Example:

``` PhantomScript
let foo { "hi" "bye" }
print @$foo:0

let foo @$foo:0
print $foo
```

In the above example, the variable `foo` is created to hold an array. An inline script with the operator `0` is then used to get the first value. If you wanted the second value, you'd use the operator `1` and so on and so forth. The second block then sets foo to its first value and prints the first value of that. `foo`'s first value is `"hi"`, and the first value of `"hi"` is `"h"`, so the second block prints `"h"`.

### Commands Overview
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
- `stack`: concatenates variable with given value. Can also be used to append to an array that only uses incremented numbers as keys.
  - `stack numVar 15`
  - `stack array "value"`
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
- `break`: immediately end loop and continue after loop.
- `read <fileName> <outputVar>`: if a file exists, it gets its contents and outputs string to outputVar.
- `write <fileName> <text>`: writes a value to a file.
- `<varName> <operator> <optionalArgs>`: Do an operation on a variable. See explanation.
  - `array item "itemName" "This is the item's value"`

### Commands Explanation
- `if`: Bools are stored as either `Yes` or `No`. If the given bool is `No`, then lines are skipped indefinitely. You can exit and start executing again with `end`.
- `function`: Functions don't have their own namespaces, so **they don't support arguments**. You can put anything in a function. They are ended with `end` just like other blocks.
- `while`: While loops behave like functions in that they store a line to return to when `end` is reached. When they return to their starting line, the conditional is read again and if it is `Yes`, the loop goes again. If it is `No`, execution keeps going from the loop's start but skips the loop's contents.
- `<varName> <operator> <optionalArgs>`: Operate on a variable. Depending on a variable's type, the possible subcommands change. Example:
  ``` PhantomScript
  var foo 0
  foo ++
  print $foo
  # prints 1
  ```

  Array operators:
  - `item <key> <value>`: adds an item to the array with a given key and value
  
  Num operators:
  - `++`: adds one to variable
  - `--`: subtracts one from variable
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
Variables are stored in a `namespace` dictionary. There are four data types: `string`, `num`, `boolean` and `array`. Nums are all Python floats, so even if you set a variable to a whole number it will be stored as a decimal. Arrays can act like dictionaries or lists, but are dictionaries under the hood.


Inline scripts are processed as one word initially and then replaced with their resulting values. Because of this, they use their own type preprocessor. If you're curious, you can look in the `simplify(script)` function in the interpreter.