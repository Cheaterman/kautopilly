from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
)

import krpc


class AutoPilot(App):
    altitude = NumericProperty(0)
    target_heading = NumericProperty(0)
    target_pitch = NumericProperty(0)
    autopilot_engaged = BooleanProperty(False)

    def build(self):
        ksp = krpc.connect(name='Airplane autopilot')

        vessel = ksp.space_center.active_vessel
        self.control = vessel.control
        self.autopilot = vessel.auto_pilot
        self.autopilot.target_roll = 0
        self.autopilot.rotation_speed_multiplier = 10
        self.autopilot.max_rotation_speed = 10
        self.altitude_stream = ksp.add_stream(
            getattr,
            vessel.flight(),
            'mean_altitude'
        )
        Clock.schedule_interval(self.update_altitude, 0)

    def update_altitude(self, dt):
        self.altitude = self.altitude_stream()

    def on_autopilot_engaged(self, app, engaged):
        autopilot = self.autopilot
        control = self.control
        if engaged:
            autopilot.engage()
        else:
            autopilot.disengage()
            control.sas = True

    def on_target_heading(self, app, heading):
        self.autopilot.target_pitch_and_heading(self.target_pitch, heading)

    def on_target_pitch(self, app, pitch):
        self.autopilot.target_pitch_and_heading(pitch, self.target_heading)

AutoPilot().run()
