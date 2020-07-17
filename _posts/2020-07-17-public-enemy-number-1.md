---
layout: post
title:  "Public Enemy Number 1?"
categories: refactoring design
---

#### Refactoring: Duplicate Code

Duplication is one of the biggest inhibitors of change that there is in software development, if not the biggest.

It is included in the [4 Rules of Simple Design](http://wiki.c2.com/?XpSimplicityRules) as Eliminates Duplication (sometimes referred to as [Don't Repeat Yourself](http://wiki.c2.com/?DontRepeatYourself)) - FYI these rules are possibly the simplest set of guidance you can use when you develop classes, and apply fairly well to all software product development activities at different levels of abstraction.
Why is this?

I'm not sure the following will add much to the total sum of human wisdom on the subject, but I want to express it in my own way (part of that Learning to Learn thing). Ironically, in an article about duplication, a lot of what appears here is exactly that, anyway, here goes...

If a fact (piece of logic) is declared in more than one place, and is subject to change in requirements, then we are forced to change it individually in all the places that it occurs. It may not be easy to identify each instance that needs changing - there might be small variations that make a simple search and replace difficult - ranging from simple white space changes, to small variations in logic that could be parameterised.
How to not repeat yourself

As part of your TDD cycle, in the refactor step, you are going to be looking for the [Duplicate Code](https://en.wikipedia.org/wiki/Code_smell) smell.

1. Identifying duplication

- Manual Code inspection - eyeballing the code, this is viable where new code is being written, it should be possible to remove as new classes are being developed.
- Automated inspections such as Eclipse Plug-ins such as PMD with Copy and Paste Detection CPD which can identify simple copy and paste with white space differences, but simple differences such as changing variable names will throw it off the scent.

2. How to remove

- Use [Extract Method](https://refactoring.com/catalog/extractFunction.html) for simple duplication in the same class.
- Where the method exists in two subclasses within the same hierarchy, especially where they are siblings use the [Pull Up field](https://www.refactoring.com/catalog/pullUpField.html) refactoring to move into the superclass
- Where the duplication is in 2 unrelated classes, the duplication could be moved to a third class using [Extract Class](https://www.refactoring.com/catalog/extractClass.html) that the 2 classes then take a dependency on. If either class with the duplication has an existing dependency on the other, then it might make sense for the duplication to be moved to a method in the dependency. When deciding on the new home for the logic the cohesiveness of the refactored class should be considered.
- Use introduce parameter refactor to address variations that can be parameterised.

#### Some other pearls of wisdom

Here are some other views to throw into the mix, when considering the removal of duplication.

- [Rule of Three](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)) is Martin Fowler's guidance about when to remove duplication when a piece of code appears for the 3rd time. 
- In the section about tests in [Once and Only](http://c2.com/xp/OnceAndOnlyOnce.html) once the article makes the point that facts can be stated upto 3 times - once in the production code, once in the unit tests, and another time in customer tests.
- [Mark Seeman](https://blog.ploeh.dk/) makes the case in this [blog post](https://blog.ploeh.dk/2014/08/07/why-dry/) that duplication can be left in place where there is little chance of change. There is a general point that all guidance should be considered just that and applied with reference to the current context. I think that there is the consideration of the expression of intent which I think is a marginal argument, but I also think it instructive that such a simple example is used.
