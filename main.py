from kivy.app import App


class KautoPilly(App):
    def on_pause(self):
        return True

    def on_stop(self):
        atmospheric = self.root.ids.atmospheric
        if atmospheric.ksp:
            atmospheric.ksp.close()

KautoPilly().run()
