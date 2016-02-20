from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from krpc_wrapper import Connection


class KautoPilly(App):
    connection = ObjectProperty()

    def build(self):
        self.connection = connection = Connection()
        connection.bind(
            on_connection_success=self.on_connection_success,
            on_connection_failure=self.on_connection_failure,
        )

    def connect(self, address, rpc_port, stream_port):
        self.connection.connect(
            address=address,
            rpc_port=rpc_port,
            stream_port=stream_port,
        )

    def on_connection_success(self, connection):
        root = self.root
        root.ids.atmospheric.ksp = self.connection.ksp
        root.current = 'atmospheric'

    def on_connection_failure(self, connection, message):
        popup = Popup(
            title='KSP connection error',
            content=Label(
                text=(
                    'Could not connect to address:\n\n'
                    '{}:{} (stream port: {})\n\n'.format(
                        connection.address,
                        connection.rpc_port,
                        connection.stream_port
                    ) +
                    message
                ),
                color=(1, 0, 0, 1),
                font_size=20
            ),
            size_hint=(.9, .5)
        )
        popup.open()

        # Reset connection button text
        self.root.ids.connection.dispatch('on_pre_enter')

    def on_pause(self):
        return True

    def on_stop(self):
        ksp = self.connection.ksp
        if ksp:
            ksp.close()

KautoPilly().run()
