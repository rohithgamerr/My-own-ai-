import datetime
import heapq
from enum import IntEnum
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass(order=True)
class Task:
    priority: Priority
    due_date: datetime.datetime
    id: str = field(compare=False)
    title: str = field(compare=False)
    category: str = field(compare=False)
    description: str = field(compare=False)
    reminder_offset_mins: Optional[int] = field(default=None, compare=False)
    completed: bool = field(default=False, compare=False)

    def __post_init__(self):
        # Priority is inverted for heapq (higher number = higher priority)
        # But we want Critical (4) to come first, so we store as -priority
        pass

class WorkHandler:
    def __init__(self, whatsapp_bridge: Optional[Callable] = None):
        self.tasks = []  # Priority queue
        self.all_tasks: Dict[str, Task] = {}
        self.whatsapp_bridge = whatsapp_bridge

    def add_task(self, task: Task):
        # Use negative priority for max-heap behavior with heapq
        heapq.heappush(self.tasks, (-task.priority, task.due_date, task))
        self.all_tasks[task.id] = task

    def get_next_task(self) -> Optional[Task]:
        if not self.tasks:
            return None
        return heapq.heappop(self.tasks)[2]

    def check_reminders(self):
        """Logic to trigger notifications based on relative time."""
        now = datetime.datetime.now()
        triggered = []
        for task in self.all_tasks.values():
            if task.completed or task.reminder_offset_mins is None:
                continue
            
            reminder_time = task.due_date - datetime.timedelta(minutes=task.reminder_offset_mins)
            # Trigger if we are within 1 minute of the reminder time
            if now >= reminder_time and (now - reminder_time).total_seconds() < 60:
                msg = f"REMINDER: Task '{task.title}' is due in {task.reminder_offset_mins} mins!"
                self._notify(msg)
                triggered.append(task.id)
        return triggered

    def batch_tasks(self) -> Dict[str, List[Task]]:
        """Group similar tasks into focused blocks based on category."""
        batches = {}
        for task in self.all_tasks.values():
            if task.completed:
                continue
            batches.setdefault(task.category, []).append(task)
        return batches

    def _notify(self, message: str):
        print(f"[Notification] {message}")
        if self.whatsapp_bridge:
            try:
                self.whatsapp_bridge(message)
            except Exception as e:
                print(f"WhatsApp Bridge Error: {e}")

# --- Integration Mock & Tests ---
def mock_whatsapp_bridge(msg):
    print(f"[WhatsApp Out] {msg}")

if __name__ == "__main__":
    # Initialize engine
    engine = WorkHandler(whatsapp_bridge=mock_whatsapp_bridge)

    # 1. Create Tasks with Priorities
    t1 = Task(Priority.LOW, datetime.datetime.now() + datetime.timedelta(hours=2), "1", "Clean Desk", "Admin", "Tidy up", 15)
    t2 = Task(Priority.CRITICAL, datetime.datetime.now() + datetime.timedelta(minutes=30), "2", "Fix Production Bug", "Dev", "S1 Issue", 15)
    t3 = Task(Priority.MEDIUM, datetime.datetime.now() + datetime.timedelta(hours=1), "3", "Email Client", "Admin", "Reply to query", 10)
    
    engine.add_task(t1)
    engine.add_task(t2)
    engine.add_task(t3)

    print("--- Next Priority Task ---")
    print(f"Next up: {engine.get_next_task().title}") # Should be 'Fix Production Bug'

    print("\n--- Task Batching ---")
    batches = engine.batch_tasks()
    for cat, tasks in batches.items():
        print(f"Block {cat}: {[t.title for t in tasks]}")

    print("\n--- Testing Reminders ---")
    # Force a task to be due in 15 mins for reminder test
    t_remind = Task(Priority.HIGH, datetime.datetime.now() + datetime.timedelta(minutes=15), "4", "Quick Call", "Meetings", "Sync", 15)
    engine.add_task(t_remind)
    engine.check_reminders()
