from .profile_kb import (
    startReplyKb,
    regRase,
    regSex,
    regClass,
    profileInLineKB,
    avatarNavigationKB
)

from .task_kb import (
    todoReplyKB,
    addTaskReplyKB,
    taskListKB,
    delTasks,
    editTasks,
    completeTasks
)

from .habit_kb import (
    habitsReplyKB,
    addHabitReplyKB,
    habitsList,
    deleteHabits,
    editHabits,
    selectWeekdaysKB,
    todayHabits
)

__all__ = [
    # Profile keyboards
    'startReplyKb',
    'regRase',
    'regSex',
    'regClass',
    'profileInLineKB',
    'avatarNavigationKB',
    
    # Task keyboards
    'todoReplyKB',
    'addTaskReplyKB',
    'taskListKB',
    'delTasks',
    'editTasks',
    'completeTasks',
    
    # Habit keyboards
    'habitsReplyKB',
    'addHabitReplyKB',
    'habitsList',
    'deleteHabits',
    'editHabits',
    'selectWeekdaysKB',
    'todayHabits'
] 