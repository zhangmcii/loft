from .connection import WSConnectionManager
from .presence import UserPresenceService
from .conversation import ConversationStateService


def init_ws_services(redis):
    connection = WSConnectionManager(redis)
    presence = UserPresenceService(redis)
    conversation = ConversationStateService(redis)
    return connection, presence, conversation