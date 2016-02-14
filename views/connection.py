from kivy.lang import Builder
from kivy.properties import (
    NumericProperty,
    StringProperty,
)
from kivy.uix.screenmanager import Screen


class Connection(Screen):
    # Network info
    address = StringProperty('127.0.0.1')
    rpc_port = NumericProperty(50000)
    stream_port = NumericProperty(50001)

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)
        self.register_event_type('on_connect')

    def on_connect(self):
        pass

Builder.load_file('views/connection.kv')
