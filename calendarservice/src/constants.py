USER_CREATED_EVENT = 'user_created_event'
USER_DELETED_EVENT = 'user_deleted_event'

CALENDAR_CREATED_EVENT = 'calendar_created_event'
CALENDAR_MODIFIED_EVENT = 'calendar_modified_event'
CALENDAR_DELETED_EVENT = 'calendar_deleted_event'

PREFERENCES_CREATED_EVENT = 'preferences_created_event'
PREFERENCES_MODIFIED_EVENT = 'preferences_modified_event'
PREFERENCES_DELETED_EVENT = 'preferences_deleted_event'

# For RabbitMQ
ACCOUNT_EXCHANGE = 'account'
CALENDAR_EXCHANGE = 'calendar'
USER_CREATED = 'user.created'
USER_DELETED = 'user.deleted'

PREFERENCES_CREATED = 'calendar.preferences.created'
PREFERENCES_MODIFIED = 'calendar.preferences.modified'
PREFERENCES_DELETED = 'calendar.preferences.deleted'

CALENDAR_CREATED = 'calendar.created'
CALENDAR_MODIFIED = 'calendar.modified'
CALENDAR_DELETED = 'calendar.deleted'

CALENDAR = 'calendar.#'
CALENDAR_QUEUE = 'calendarservice'
ACCOUNT_QUEUE = 'accountservice'
EVENT_QUEUE = 'eventservice'
INSTRUCTIONS_QUEUE = 'instructionsservice'


