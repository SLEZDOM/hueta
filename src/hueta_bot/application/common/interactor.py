from typing import Callable, Generic, Optional, TypeVar


Input = TypeVar("Input")
Output = TypeVar("Output")


class Interactor(Generic[Input, Output]):
    async def __call__(
        self,
        data: Optional[Input] = None
    ) -> Output:
        raise NotImplementedError


InteractorT = TypeVar("InteractorT", bound=Interactor)
InteractorFactory = Callable[[], InteractorT]
