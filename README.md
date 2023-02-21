# immutable-proxy

The main aim of this package is to define the class `DeepImmutableProxy` that prevents a user-defined class to be mutated to any level of depth.

`DeepImmutableProxy` takes an object as an argument and acts as a proxy to that object.
Attributes and methods can be accessed normally unless they try to mutate any object that is accessible from the wrapped object.

## Installation

This package is written in pure python. Simply install it using pip

```
pip install immutable-proxy
```


## Basic usage

```python
>>> from immutable import DeepImmutableProxy, ConstantAttributeError

```

We define a simple class:

```python
>>> class Example():
...     def __init__(self, x):
...         self.x = x
...     def __repr__(self):
...         return f'{type(self).__qualname__}({self.x!r})'

>>> example = Example(42)
>>> example.x = 0
>>> print(example)
Example(0)

```

If we wrap an object with `DeepImmutableProxy`, then this object cannot be mutated.

```python
>>> proxy = DeepImmutableProxy(Example(42))

>>> try:
...     proxy.x = 0
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Example]' object is immutable. Cannot change attribute 'x' after initialization.

>>> try:
...     del proxy.x
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Example]' object is immutable. Cannot delete attribute 'x' after initialization.

>>> print(proxy)
Example(42)

```


## Nested attributes, indirect mutation, and inheritance

The following example demonstrates a more complicated class with properties and methods that set attributes.

```python
>>> class Inner:
...     def __init__(self, x, y):
...         self.x = x
...         self.y = y
...     def __repr__(self):
...         return f'{type(self).__qualname__}({self.x!r}, {self.y!r})'
...     def set_x(self, x):
...         "Demonstrates a way to set attribute 'x'."
...         self.x = x
...     def get_x(self) -> int:
...         return self.x
...     @property
...     def y(self):
...         "Demonstrates a property to handle attribute 'y'."
...         return self.__dict__['y']
...     @y.setter
...     def y(self, value):
...         self.__dict__['y'] = value

```

The objects of this class work as expected.

```python
>>> inner = Inner(1, 2)
>>> inner.x, inner.y = -1, -2
>>> print(inner)
Inner(-1, -2)

>>> inner.set_x(3)
>>> print(inner)
Inner(3, -2)

```

Now we wrap an object of this class with `DeepImmutableProxy`.
This object cannot be mutated.

```python
>>> inner_proxy = DeepImmutableProxy(Inner(1, 2))

>>> try:
...     inner_proxy.x = -1
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'x' after initialization.

>>> try:
...     inner_proxy.y = -2
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'y' after initialization.

>>> try:
...     inner_proxy.set_x(3)
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'x' after initialization.

>>> try:
...     del inner_proxy.x
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot delete attribute 'x' after initialization.

```

We define another class whose attributes are of type `Inner`.
It also contains an attribute referring to another object that refers back to an object of this class.  The initial object cannot be modified indirectly trough this back reference.

```python 
>>> class Outer:
...     def __init__(self, a: Inner, b: Inner) -> None:
...         self.a = a
...         self.b = b
...         self.delegate = Modifier(self)
...     def __repr__(self):
...         return f'{type(self).__qualname__}({self.a!r}, {self.b!r})'
...     def set_a(self, a):
...         'Sets a.'
...         self.a = a
...     def get_a(self):
...         return self.a
...     @property
...     def b(self):
...         return self.__dict__['b']
...     @b.setter
...     def b(self, value) -> None:
...         self.__dict__['b'] = value

>>> class Modifier():
...     def __init__(self, obj):
...         self.back = obj
...     def reset(self, x):
...         self.back.x = x

>>> outer_proxy = DeepImmutableProxy(Outer(Inner(1, 2), Inner(3, 4)))

```

The object just created is wrapped with `DeepImmutableProxy`. 
This prevents mutation of attributes at all levels of depth.

```python
>>> try:
...     outer_proxy.a = Inner(-1, -2)
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Outer]' object is immutable. Cannot change attribute 'a' after initialization.

>>> try:
...     outer_proxy.b = Inner(-3, -4)
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Outer]' object is immutable. Cannot change attribute 'b' after initialization.

>>> try:
...     outer_proxy.a.x = -1
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'x' after initialization.

>>> try:
...     outer_proxy.a.y = -2
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'y' after initialization.

>>> try:
...     outer_proxy.b.x = -3
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'x' after initialization.

>>> try:
...     outer_proxy.b.y = -4
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'y' after initialization.

>>> try:
...     outer_proxy.set_a(Inner(-1, -2))
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Outer]' object is immutable. Cannot change attribute 'a' after initialization.

>>> try:
...     outer_proxy.a.set_x(-1)
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'x' after initialization.

>>> try:
...     del outer_proxy.a
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Outer]' object is immutable. Cannot delete attribute 'a' after initialization.

```

We recall that instances of `Outer` have an attribute that references an object of another class that has a reference to the first.  We show that `DeepImmutableProxy` still prevents mutation.

```python
>>> try:
...     outer_proxy.delegate.back.x = 5
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Outer]' object is immutable. Cannot change attribute 'x' after initialization.

```

Next we present an example where inheritance is involved and `super()` is used.

```python
>>> class Derived(Outer):
...     def set_a(self, a):
...         modified = Inner(2*a.x, 2*a.y)
...         super().set_a(modified)
    
>>> derived = Derived(Inner(1, 2), Inner(3, 4))
>>> derived.set_a(Inner(10, 20))
>>> print(derived)
Derived(Inner(20, 40), Inner(3, 4))

>>> derived_proxy = DeepImmutableProxy(Derived(Inner(1, 2), Inner(3, 4)))

>>> try:
...     derived_proxy.set_a(Inner(10, 20))
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Derived]' object is immutable. Cannot change attribute 'a' after initialization.

```


## Built-in types

The class `DeepImmutableProxy` works with instances of user defined classes.
For classes that are not written in *Python* there might be problems, as the introspection methods used by `DeepImmutableProxy` may not work.
This problem is solved with the class methods `DeepImmutableProxy.register_immutable`, which can be used to tell `DeepImmutableProxy` that certain class is already immutable (hence, wrapping it with `DeepImmutableProxy` has no effect), and `DeepImmutableProxy.register_proxy`, that allows a user to register a subclass of `DeepImmutableProxy` that defines an immutable proxy specific for the given type.

For example, types `int`, `float`, `str`, `bytes`, and some others, have already been registered to be immutable:

```python
>>> no_proxy = DeepImmutableProxy(3)
>>> type(no_proxy) == int
True

```

The class method `DeepImmutableProxy.get_registered_immutable` returns a list of the currently registered immutable classes:

```python
>>> [cls.__name__ for cls in DeepImmutableProxy.get_registered_immutable()] # doctest: +ELLIPSIS
['bytes', 'int', 'float', 'complex', 'str', 'NoneType', ...]

``` 

Some containers like tuples are immutable only if their content is immutable.  
Thus, when applying `DeepImmutableProxy` to a container like a tuple, we need a specific wrapper.
This wrapper is already defined in this package.

For example, the second element of the next tuple is mutable, so the resulting object is mutable.
However, when wrapped with `DeepImmutableProxy` it really becomes immutable.
This is achieved by returning a special wrapper for tuples.
The usual `DeepImmutableProxy` class does not work because attribute access for built-in types does not follow the standard Python rules.

```python
>>> mutable_tuple_proxy = DeepImmutableProxy(('immutable', ['mutable']))
>>> mutable_tuple_proxy
TupleImmutableProxy(('immutable', ['mutable']))

```

The first item of the tuple is a `str`, which is immutable, so it is returned as is.

```python
>>> mutable_tuple_proxy[0]
'immutable'

```

The second item is mutable, so it is wrapped and cannot be modified either.

```python
>>> mutable_tuple_proxy[1]
ListImmutableProxy(['mutable'])

```

This second item is of type list, so it also needs a special wrapper.
Methods that do not mutate the content can be used normally.

```python
>>> len(mutable_tuple_proxy[1]), mutable_tuple_proxy[1].index('mutable')
(1, 0)

```

However, methods that do mutate content are forbidden.

```python
>>> try:
...     mutable_tuple_proxy[1].append('another')
... except AttributeError as error:
...     print(error)
Object of type "ListImmutableProxy" does not have attribute "append".
    
```


## Copying

`DeepImmutableProxy` objects include a hook for `__copy__` and `__deepcopy__` that copies the underlying object.  The copy is mutable.

```python
>>> from copy import deepcopy

>>> copied = deepcopy(outer_proxy)
>>> print(copied)
Outer(Inner(1, 2), Inner(3, 4))

>>> copied.a.x = -1

>>> try:
...     outer_proxy.a.x = -1
... except ConstantAttributeError as error:
...     print(error)
'DeepImmutableProxy[Inner]' object is immutable. Cannot change attribute 'x' after initialization.

```

