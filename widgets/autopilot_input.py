from kivy.lang import Builder
from kivy.properties import (
    ObjectProperty,
    StringProperty,
)
from kivy.uix.textinput import TextInput


class AutoPilotInput(TextInput):
    target = StringProperty()
    root = ObjectProperty()

    def on_root(self, instance, value):
        if value and self.target:
            self.update_text()

    def on_target(self, instance, value):
        if value and self.root:
            self.update_text()

    def update_text(self):
        self.text = str(getattr(self.root, self.target))
        self.root.bind(**{
            self.target: lambda target, value:
                self.setter('text')(self, str(value))
        })

    def on_text(self, instance, value):
        if value:
            setattr(self.root, self.target, int(value))

    def on_text_validate(self):
        if self.root:
            self.root.autopilot_engaged = True


Builder.load_file('widgets/autopilot_input.kv')
