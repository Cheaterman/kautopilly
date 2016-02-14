from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label

import krpc


class Atmospheric(Screen):
    # Network info
    address = StringProperty('127.0.0.1')
    rpc_port = NumericProperty(50000)
    stream_port = NumericProperty(50001)

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

    def __init__(self, **kwargs):
        super(Atmospheric, self).__init__(**kwargs)
        self.register_event_type('on_connection_failure')

    def on_connection_failure(self):
        pass

    def on_pre_enter(self):
        try:
            ksp = krpc.connect(
                name='KautoPilly',
                address=self.address,
                rpc_port=self.rpc_port,
                stream_port=self.stream_port,
            )
        except krpc.error.NetworkError as e:
            if e.message.startswith('[Errno 111]'):
                popup = Popup(
                    title='kRPC server connection error',
                    content=Label(
                        text=(
                            'Could not connect to address:\n\n'
                            '{}:{} (stream port: {})\n\n'.format(
                                self.address,
                                self.rpc_port,
                                self.stream_port
                            ) +
                            'Is kRPC server started?'
                        ),
                        color=(1, 0, 0, 1),
                        font_size=20
                    ),
                    size_hint=(.5, .5)
                )
                popup.open()
                self.dispatch('on_connection_failure')

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
        direction = directions[0 if value > 0 else 1]
        mnt, sec = divmod(value * mult, 60)
        deg, mnt = divmod(mnt, 60)
        return int(deg), int(mnt), int(sec), direction

    def on_autopilot_engaged(self, screen, engaged):
        autopilot = self.autopilot
        if engaged:
            autopilot.engage()
        else:
            autopilot.disengage()
            self.control.sas = True

    def on_target_heading(self, screen, heading):
        self.autopilot.target_pitch_and_heading(self.target_pitch, heading)

    def on_target_pitch(self, screen, pitch):
        self.autopilot.target_pitch_and_heading(pitch, self.target_heading)

    def on_throttle(self, screen, throttle):
        self.control.throttle = throttle

    def on_lights(self, screen, lights):
        self.control.lights = lights

    def on_gear(self, screen, gear):
        self.control.gear = gear

    def on_brakes(self, screen, brakes):
        self.control.brakes = brakes


Builder.load_file('views/atmospheric.kv')
