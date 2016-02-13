from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
)

import krpc


class AutoPilot(App):
    # Telemetry
    altitude = NumericProperty(0)
    surface_altitude = NumericProperty(0)
    speed = NumericProperty(0)
    heading = NumericProperty(90)
    pitch = NumericProperty(0)
    roll = NumericProperty(0)
    latitude = NumericProperty(0)
    longitude = NumericProperty(0)

    # Autopilot
    target_heading = NumericProperty(90)
    target_pitch = NumericProperty(0)
    autopilot_engaged = BooleanProperty(False)

    # Controls
    throttle = NumericProperty(.5)
    lights = BooleanProperty(False)
    gear = BooleanProperty(True)
    brakes = BooleanProperty(False)

    def build(self):
        Clock.schedule_once(self.krpc_init)

    def krpc_init(self, *args):
        try:
            ksp = krpc.connect(name='Kautopivy')
        except krpc.error.NetworkError as e:
            if e.message.startswith('[Errno 111]'):
                Logger.error(
                    'kRPC: Could not connect to localhost:50000. '
                    'Is kRPC server started?'
                )
                return
            raise

        vessel = ksp.space_center.active_vessel
        flight = vessel.flight()
        speed_flight = vessel.flight(vessel.orbit.body.reference_frame)
        self.control = vessel.control
        self.autopilot = vessel.auto_pilot
        self.autopilot.target_roll = 0
        self.autopilot.rotation_speed_multiplier = 10
        self.autopilot.max_rotation_speed = 10
        self.altitude_stream = ksp.add_stream(
            getattr,
            flight,
            'mean_altitude'
        )
        self.surface_altitude_stream = ksp.add_stream(
            getattr,
            flight,
            'surface_altitude'
        )
        self.speed_stream = ksp.add_stream(
            getattr,
            speed_flight,
            'speed'
        )
        self.heading_stream = ksp.add_stream(
            getattr,
            flight,
            'heading'
        )
        self.pitch_stream = ksp.add_stream(
            getattr,
            flight,
            'pitch'
        )
        self.roll_stream = ksp.add_stream(
            getattr,
            flight,
            'roll'
        )
        self.latitude_stream = ksp.add_stream(
            getattr,
            flight,
            'latitude'
        )
        self.longitude_stream = ksp.add_stream(
            getattr,
            flight,
            'longitude'
        )
        Clock.schedule_interval(self.update_streams, 0)
        self.target_pitch = int(flight.pitch)
        self.target_heading = int(flight.heading)
        self.throttle = self.control.throttle
        self.lights = self.control.lights
        self.gear = self.control.gear
        self.brakes = self.control.brakes

    def update_streams(self, dt):
        self.altitude = self.altitude_stream()
        self.surface_altitude = self.surface_altitude_stream()
        self.speed = self.speed_stream()
        self.heading = self.heading_stream()
        self.pitch = self.pitch_stream()
        self.roll = self.roll_stream()
        self.latitude = self.latitude_stream()
        self.longitude = self.longitude_stream()

    def latitude_dms(self):
        return self.to_dms(self.latitude, ('N', 'S'))

    def longitude_dms(self):
        return self.to_dms(self.longitude, ('E', 'W'))

    def to_dms(self, value, directions):
        mult = 3600 if value > 0 else -3600
        direction = directions[1 if value < 0 else 0]
        mnt, sec = divmod(value * mult, 60)
        deg, mnt = divmod(mnt, 60)
        return int(deg), int(mnt), int(sec), direction

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

    def on_throttle(self, app, throttle):
        self.control.throttle = throttle

    def on_lights(self, app, lights):
        self.control.lights = lights

    def on_gear(self, app, gear):
        self.control.gear = gear

    def on_brakes(self, app, brakes):
        self.control.brakes = brakes

AutoPilot().run()
