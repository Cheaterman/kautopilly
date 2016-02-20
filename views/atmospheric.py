from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.screenmanager import Screen


class Atmospheric(Screen):
    # Connection
    ksp = ObjectProperty(None)
    vessel = ObjectProperty(None)
    flight = ObjectProperty(None)

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
    target_roll = NumericProperty(0)
    autopilot_engaged = BooleanProperty(False)

    # Controls
    throttle = NumericProperty(.5)
    throttling = BooleanProperty(False)
    lights = BooleanProperty(False)
    gear = BooleanProperty(True)
    brakes = BooleanProperty(False)

    def on_ksp(self, screen, ksp):
        self.vessel_stream = stream = ksp.add_stream(
            getattr,
            ksp.space_center,
            'active_vessel'
        )
        self.vessel = stream()

    def on_vessel(self, screen, vessel):
        self.flight_stream = stream = self.ksp.add_stream(
            vessel.flight
        )
        self.flight = stream()

    def on_flight(self, screen, flight):
        self.setup_streams()

    def setup_streams(self):
        ksp = self.ksp
        vessel = self.vessel
        flight = self.flight
        speed_flight = vessel.flight(vessel.orbit.body.reference_frame)
        self.control = vessel.control
        self.autopilot = vessel.auto_pilot
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
        self.throttle_stream = ksp.add_stream(
            getattr,
            self.control,
            'throttle'
        )
        Clock.schedule_interval(self.update_streams, 0)
        self.autopilot.rotation_speed_multiplier = 10
        self.autopilot.max_rotation_speed = 10
        self.autopilot_engaged = False
        self.target_heading = int(flight.heading)
        self.target_pitch = int(flight.pitch)
        self.target_roll = int(flight.roll)
        self.lights = self.control.lights
        self.gear = self.control.gear
        self.brakes = self.control.brakes

    def update_streams(self, dt):
        self.vessel = self.vessel_stream()
        self.flight = self.flight_stream()
        self.altitude = self.altitude_stream()
        self.surface_altitude = self.surface_altitude_stream()
        self.speed = self.speed_stream()
        self.heading = self.heading_stream()
        self.pitch = self.pitch_stream()
        self.roll = self.roll_stream()
        self.latitude = self.latitude_stream()
        self.longitude = self.longitude_stream()
        throttle = self.throttle_stream()
        if self.throttling and throttle == self.throttle:
            self.throttling = False
        if not self.throttling:
            self.throttle = throttle

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

    def on_target_roll(self, screen, roll):
        self.autopilot.target_roll = roll

    def on_throttle(self, screen, throttle):
        self.throttling = True
        self.control.throttle = throttle

    def on_lights(self, screen, lights):
        self.control.lights = lights

    def on_gear(self, screen, gear):
        self.control.gear = gear

    def on_brakes(self, screen, brakes):
        self.control.brakes = brakes


Builder.load_file('views/atmospheric.kv')
