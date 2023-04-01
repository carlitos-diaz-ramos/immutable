import asyncio

from immutable import DeepImmutableProxy as DIP


class Example():
    def __init__(self, x: int) -> None:
        self.x = x
    async def coro(self) -> int:
        await asyncio.sleep(0.1)
        return self.x
    def make(self) -> int:
        return Maker(self).do()
    def run(self) -> int:
        return asyncio.run(coroutine())

class Maker():
    def __init__(self, example: Example) -> None:
        self.example = example
    def do(self) -> int:
        return asyncio.run(coroutine())

async def coroutine() -> int:
    await asyncio.sleep(0.1)
    return 13
    

def test_run_coroutine_in_class() -> None:
    example = Example(42)
    assert asyncio.run(example.coro()) == 42
    proxy: DIP[Example] = DIP(Example(42))
    assert asyncio.run(proxy.coro()) == 42

def test_run_coroutine() -> None:
    result = asyncio.run(coroutine())
    assert result == 13

def test_async_delegate_to_coroutine() -> None:
    '''
    We test asyncio.run inside a method.  This is not pointless because, after
    patching super(), there is a problem with the _socket class: a 
    member_descriptor checks the type of an attribute and we have to 
    circumvent this descriptor.
    Remove the ismemberdescriptor check in _ClassProxy.__getattribute__ to see
    what happens.
    '''
    example = Example(42)
    assert example.run() == 13
    proxy: DIP[Example] = DIP(Example(42))
    assert proxy.run() == 13

def test_async_delegated_to_other_class() -> None:
    example = Example(42)
    assert example.make() == 13
    proxy: DIP[Example] = DIP(Example(42))
    assert proxy.make() == 13
