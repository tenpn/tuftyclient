import uselect
import sys

POLL_READ_ONLY = (
    uselect.POLLIN |
    uselect.POLLHUP |
    uselect.POLLERR
)

class SerialUSB:
    def __init__(self) -> None:
        self._listener = uselect.poll()
        self._listener.register(sys.stdin, POLL_READ_ONLY)
        self._buffer = ""
        self._complete = []
        
    def update(self) -> None:
        while self._listener.poll(0):
            new_c = str(sys.stdin.read(1))
            if new_c == "\n":
                clean_buffer = self._buffer.strip()
                if len(clean_buffer) > 0:
                    self._complete.append(self._buffer)
                self._buffer = ""
            else:
                self._buffer += new_c
                
    def pending_len(self) -> int:
        return len(self._buffer)

    def is_any(self) -> bool: 
        """
        Returns:
            true if you can pop_next()
        """
        return len(self._complete) > 0
    
    def pop_next(self):
        """returns next complete input, if is_any() is true
        """
        next = self._complete.pop(0)
        return next 
