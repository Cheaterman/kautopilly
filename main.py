from kivy.app import App


class KautoPilly(App):
    def on_pause(self):
        return True

KautoPilly().run()
