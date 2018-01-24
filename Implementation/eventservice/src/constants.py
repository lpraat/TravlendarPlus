CALENDAR_CREATED_EVENT = 'calendar_created_event'
CALENDAR_DELETED_EVENT = 'calendar_deleted_event'
PREFERENCES_DELETED_EVENT = 'preferences_deleted_event'


CALENDAR_ID_CREATED_EVENT = 'calendar_id_created_event'
CALENDAR_ID_DELETED_EVENT = 'calendar_id_deleted_event'
USER_CALENDARS_DELETED_EVENT = 'users_calendars_deleted_event'
EVENT_CREATED_EVENT = 'event_created_event'
EVENT_MODIFIED_EVENT = 'event_modified_event'
EVENT_DELETED_EVENT = 'event_deleted_event'
RECURRENCE_DELETED_EVENT = 'recurrence_deleted_event'


# For RabbitMQ
CALENDAR_EXCHANGE = 'calendar'
EVENT_EXCHANGE = 'event'
CALENDAR_CREATED = 'calendar.created'
CALENDAR_DELETED = 'calendar.deleted'
PREFERENCES_DELETED = 'calendar.preferences.deleted'


CALENDAR_ID_CREATED = 'event.calendarid.created'
CALENDAR_ID_DELETED = 'event.calendarid.deleted'
USER_CALENDARS_DELETED = 'event.usercalendars.deleted'

EVENT_CREATED = 'event.event.created'
EVENT_MODIFIED = 'event.event.modified'
EVENT_DELETED = 'event.event.deleted'

RECURRENCE_DELETED = 'event.recurrence.deleted'

EVENT = 'event.#'
EVENT_QUEUE = 'eventservice'
INSTRUCTIONS_QUEUE = 'instructionsservice'
