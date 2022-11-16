# coding: utf-8
from code_table import SingleEnglishCode
from input_method_config import BasicConfig
import pygame
import os

# Note: https://stackoverflow.com/questions/31555665/get-inputs-without-focus-in-python-pygame/71722948
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
pygame.init()


class XBoxHandler:
    LR_AXIS = (0, 1, 2, 3)

    def __init__(self):
        self.joy = None
        self.binding = False

    def refresh(self, joysticks, name="Xbox 360 Controller"):
        if self.binding:
            return
        for joy in joysticks.values():
            if joy.get_name() == name:
                self.joy = joy
                self.binding = True
                return
        self.binding = False

    def handle_trigger(self, events, callback):
        for e in events:
            if e.type == pygame.JOYBUTTONDOWN:
                # get axis state
                lx, ly = self.joy.get_axis(0), self.joy.get_axis(1)
                rx, ry = self.joy.get_axis(3), self.joy.get_axis(4)
                callback(lx, ly, rx, ry)


def unittest():
    bc = BasicConfig(SingleEnglishCode)
    h = XBoxHandler()

    pygame.event.set_grab(True)  # Keeps the cursor within the pygame window

    # Set the width and height of the screen (width, height), and name the window.
    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("Joystick example")

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.
    joysticks = {}

    done = False
    while not done:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        events = pygame.event.get()
        # print(events)
        for event in events:
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")

        h.refresh(joysticks)

        if h.binding:
            h.handle_trigger(events)

        # Limit to 30 frames per second.
        clock.tick(30)


if __name__ == '__main__':
    unittest()
    # h.get_joystick('1')
