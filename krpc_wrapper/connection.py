from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

import krpc


class Connection(EventDispatcher):
    ksp = ObjectProperty()

    def __init__(self, **kwargs):
        super(Connection, self).__init__(**kwargs)
        self.address = ''
        self.rpc_port = None
        self.stream_port = None
        self.register_event_type('on_connection_success')
        self.register_event_type('on_connection_failure')

    def on_connection_success(self):
        pass

    def on_connection_failure(self, error):
        pass

    def connect(self, address, rpc_port, stream_port):
        try:
            self.address = address
            self.rpc_port = rpc_port
            self.stream_port = stream_port

            self.ksp = krpc.connect(
                name='KautoPilly',
                address=address,
                rpc_port=rpc_port,
                stream_port=stream_port,
            )
        except krpc.error.NetworkError as e:
            self.dispatch('on_connection_failure', e.message)
        else:
            self.dispatch('on_connection_success')
