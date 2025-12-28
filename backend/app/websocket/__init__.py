from .connection import WSConnectionManager
from .conversation import ConversationStateService
from .presence import UserPresenceService


def init_ws_services(redis):
    connection = WSConnectionManager(redis)
    presence = UserPresenceService(redis)
    conversation = ConversationStateService(redis)
    return connection, presence, conversation
