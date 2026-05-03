from typing import TypeVar, Generic, Union, Optional, Callable, Any
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E")

@dataclass(frozen=True)
class Success(Generic[T]):
    value: T
    def is_success(self) -> bool: return True
    def is_failure(self) -> bool: return False
    def unwrap(self) -> T: return self.value
    def error(self) -> None: return None

@dataclass(frozen=True)
class Failure(Generic[E]):
    error_msg: E
    def is_success(self) -> bool: return False
    def is_failure(self) -> bool: return True
    def unwrap(self) -> None: raise ValueError(f"Called unwrap on Failure: {self.error_msg}")
    def error(self) -> E: return self.error_msg

Result = Union[Success[T], Failure[E]]

def attempt(func: Callable[..., T], *args, **kwargs) -> Result[T, str]:
    """Wraps a procedural call in a Result type to eliminate exception-based control flow."""
    try:
        return Success(func(*args, **kwargs))
    except Exception as e:
        return Failure(str(e))

async def attempt_async(func: Callable[..., Any], *args, **kwargs) -> Result[Any, str]:
    """Wraps an asynchronous call in a Result type for failure-as-data propagation."""
    try:
        return Success(await func(*args, **kwargs))
    except Exception as e:
        return Failure(str(e))
