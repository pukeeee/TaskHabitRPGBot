from .profile_kb import (
    startReplyKb,
    profileInLineKB,
    avatarNavigationKB,
    profileSettngsKB,
    editAvatarKB
)

from .task_kb import (
    todoReplyKB,
    addTaskReplyKB,
    taskListKB,
    delTasks,
    editTasks,
    completeTasksKB,
    completedTasksKB,
    delCompletedTasks,
    setTaskComplexity
)

from .habit_kb import (
    habitsReplyKB,
    addHabitReplyKB,
    habitsList,
    deleteHabits,
    editHabits,
    selectWeekdaysKB,
    todayHabits,
    setHabitComplexity
)

from .admin_kb import (
    adminKb,
    broadcastTypeKeyboard,
    checkBroadcastKeyboard
)

from .subscription_kb import (
    subscriptionKeyboard
)

__all__ = [
    # Profile keyboards
    'startReplyKb',
    'profileInLineKB',
    'avatarNavigationKB',
    'profileSettngsKB',
    'editAvatarKB',
    
    # Task keyboards
    'todoReplyKB',
    'addTaskReplyKB',
    'taskListKB',
    'delTasks',
    'editTasks',
    'completeTasksKB',
    'completedTasksKB',
    'delCompletedTasks',
    'setTaskComplexity',
    
    # Habit keyboards
    'habitsReplyKB',
    'addHabitReplyKB',
    'habitsList',
    'deleteHabits',
    'editHabits',
    'selectWeekdaysKB',
    'todayHabits',
    'setHabitComplexity',
    
    
    # Admin keyboards
    'adminKb',
    'broadcastTypeKeyboard',
    'checkBroadcastKeyboard',
    
    
    # Subscription keyboards
    'subscriptionKeyboard'
] 