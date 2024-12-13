from enum import Enum, auto
from typing import Dict, Any, Optional
from dataclasses import dataclass
from django.utils import timezone

class ProcessState(Enum):
    """Process state machine definition"""
    NEW = auto()         # Initial state when process is created
    READY = auto()       # Process is ready to be executed
    RUNNING = auto()     # Process is currently executing
    WAITING = auto()     # Process is waiting for external input/event
    BLOCKED = auto()     # Process is blocked on resource or dependency
    SUSPENDED = auto()   # Process execution temporarily suspended
    TERMINATED = auto()  # Process has completed execution
    ERROR = auto()       # Process encountered an error

@dataclass
class ProcessContext:
    """Process execution context with enhanced state tracking"""
    process_id: int
    state: ProcessState
    start_time: Optional[timezone.datetime] = None
    end_time: Optional[timezone.datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300  # 5 minutes default timeout
    priority: int = 0
    local_vars: Dict[str, Any] = None
    parent_context: Optional['ProcessContext'] = None

    def __post_init__(self):
        if self.local_vars is None:
            self.local_vars = {}
        if self.state == ProcessState.NEW:
            self.start_time = timezone.now()

    def transition_to(self, new_state: ProcessState, error: Optional[str] = None) -> bool:
        """
        Transition process to a new state with validation and logging
        Returns True if transition was successful
        """
        # Validate state transition
        if not self._is_valid_transition(new_state):
            return False
            
        # Update state and timestamps
        self.state = new_state
        if new_state == ProcessState.TERMINATED:
            self.end_time = timezone.now()
        elif new_state == ProcessState.ERROR:
            self.error_message = error
            self.retry_count += 1

        return True

    def _is_valid_transition(self, new_state: ProcessState) -> bool:
        """Validate if state transition is allowed"""
        # Define valid state transitions
        valid_transitions = {
            ProcessState.NEW: {ProcessState.READY},
            ProcessState.READY: {ProcessState.RUNNING, ProcessState.ERROR},
            ProcessState.RUNNING: {ProcessState.WAITING, ProcessState.BLOCKED, ProcessState.TERMINATED, ProcessState.ERROR},
            ProcessState.WAITING: {ProcessState.READY, ProcessState.ERROR},
            ProcessState.BLOCKED: {ProcessState.READY, ProcessState.ERROR},
            ProcessState.SUSPENDED: {ProcessState.READY, ProcessState.TERMINATED, ProcessState.ERROR},
            ProcessState.ERROR: {ProcessState.READY} if self.retry_count < self.max_retries else {ProcessState.TERMINATED},
            ProcessState.TERMINATED: set()  # No valid transitions from TERMINATED
        }
        
        return new_state in valid_transitions.get(self.state, set())

    def has_timed_out(self) -> bool:
        """Check if process has exceeded its timeout duration"""
        if not self.start_time or self.state == ProcessState.TERMINATED:
            return False
        elapsed = (timezone.now() - self.start_time).total_seconds()
        return elapsed > self.timeout_seconds

    def get_execution_time(self) -> Optional[float]:
        """Get total execution time in seconds"""
        if not self.start_time:
            return None
        end = self.end_time or timezone.now()
        return (end - self.start_time).total_seconds()

    def can_retry(self) -> bool:
        """Check if process can be retried after error"""
        return self.state == ProcessState.ERROR and self.retry_count < self.max_retries
