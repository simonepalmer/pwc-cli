# pwc-cli (pipewire controller - command line interface)
# version: 0.1.0
# Creator: Simon E Palmer

import json
import os
import time


"""Current settings"""

def get_current_settings():
    if check_status() == True:
        current_settings = os.popen('pw-metadata -n settings').read()
        settings_list = current_settings.split("'")
        buffer_index = settings_list.index('clock.force-quantum')

        if settings_list[buffer_index+2] == str(0):
            buffer_index = settings_list.index('clock.quantum')
        buffer = settings_list[buffer_index+2]

        samples_index = settings_list.index('clock.force-rate')
        if settings_list[samples_index+2] == str(0):
            samples_index = settings_list.index('clock.rate')
        samples = settings_list[samples_index+2]

        return {
            "status": "Pipewire is RUNNING",
            "buffer": buffer,
            "samples": samples,
        }
    else:
        return {
            "status": "Pipewire is SUSPENDED",
            "buffer": "-",
            "samples": "-",
        }


def show_current_settings():
    settings = get_current_settings()

    print(f"{settings['status']}")
    text_body (
        f"buffer size: {settings['buffer']} samples",
        f"sample rate: {settings['samples']} Hz",
    )

"""Manipulating settings"""

def change_setting_value(user_input):
    setting         = user_input[0]
    value           = user_input[1]
    current_setting = get_current_settings()[setting]

    if check_status() == True:
        if len(user_input) <= 1:
            os.system("clear")

            print("NO VALUE GIVEN")
            text_body (
                f"No value given for the command '{user_input[0].lower()}'",
                f"Example: {user_input[0].lower()} <value>",
            )
            wait_for_any_key()

        else:
            if value in valid_settings[setting]:
                if value != current_setting:
                    os.system (
                        f'pw-metadata -n settings 0 clock.force-quantum {value}'
                    )
            else:
                os.system("clear")
                setting_string = ", ".join(valid_settings[setting])

                print(f"'{user_input[1]}' is not a valid buffer size!")
                text_body (
                    "Valid buffer sizes are:",
                    setting_string,
                )
                wait_for_any_key()

    else:
        print("PIPEWIRE IS SUSPENDED")
        text_body (
            f"Can't set {user_input[0]}:",
            "Pipewire service is offline",
        )
        wait_for_any_key()


"""Pipewire.service status"""

def check_status():
    if not os.popen('pw-metadata -n settings').read() == '':
        return True
    else:
        os.system("clear") # error will post in console otherwise
        return False

def enable_pipewire(user_input):
    if check_status() == False:
        os.popen("systemctl --user start pipewire.socket")

        for i in range(10):
            os.system("clear")

            print("Pipewire is STARTING")
            text_body (
                "This will take a few seconds",
                f"Loading{'.'*i}",
            )
            time.sleep(1)

        wait_for_any_key()

    else:
        os.system("clear")
        print("Pipewire is already running\n")
        wait_for_any_key()

def disable_pipewire(user_input):
    if check_status() == True:
        os.system(f'systemctl --user stop pipewire.socket')
        os.system(f'systemctl --user stop pipewire.service')
    else:
        os.system("clear")
        print("Pipewire is already suspended\n")
        wait_for_any_key()


"""Saving and loading presets"""

def save_preset(user_input):
    os.system("clear")
    print("Feature not implemented yet\n")
    wait_for_any_key()

def load_preset(user_input):
    os.system("clear")
    print("Feature not implemented yet\n")
    wait_for_any_key()


"""Manual page"""

def manual():
    os.system("clear")
    print("Manual page for pwc-cli:")
    print()
    print("Commands:")
    print()
    print("buffer       buffer <value>")
    print("                 Sets the buffer size to the chosen value")
    print("samples      sampels <value>")
    print("                 Sets the sample rate to the chosen value")
    print()
    print("enable       Enables pipewire if it's suspended")
    print("disable      Disables pipewire if it's running")
    print()
    print("help         Displays this page")
    print("exit         Exits the program")
    print()
    print("NOT YET IMPLEMENTED:")
    print()
    print("save         save <preset name>")
    print("                 Saves the current settings as a preset")
    print("load         load <preset name>")
    print("                 Loads the settings of a previously saved preset")
    print()
    wait_for_any_key()


"""Formating and interaction"""

def wait_for_any_key():
    # until a can make it "any key" it's "press ENTER"
    input("Press ENTER to continue")

def text_body(*args):
    print()
    for string in args:
        print(string)
    print()


"""List and dicts of commands & settings"""

# Valid settings

valid_settings = {
    "buffer":   ["32","64","128","256","512","1024","2048"],
    "samples":  ["44100","48000","88200","96000"],
}

# Dict of commands

commands = {
    "buffer":   change_setting_value,
    "samples":  change_setting_value,
    "enable":   enable_pipewire,
    "disable":  disable_pipewire,
    "save":     save_preset,
    "load":     load_preset,
}

# Exit commands

exit_variants = [
    "exit",
    "quit",
    ":q",
]

help_variants = [
    "help",
    "manual",
    "man",
]


def main():
    while True:
    # Clears the window and shows the current settings and prompt
        os.system("clear")
        show_current_settings()
        user_input = input("Enter command: ")
        user_input_list = user_input.split(" ")

    # Match input (in lower case) against commands
        if user_input_list[0].lower() in exit_variants:
            break

        elif user_input_list[0].lower() in help_variants:
            manual()

        elif user_input_list[0].lower() in commands:
            commands[user_input_list[0].lower()](user_input_list)

        else:
            os.system("clear")
            print("NO COMMAND")
            text_body (
                "Command could not be found",
                "Press ENTER to see list of commands",
            )
            wait_for_any_key()
            manual()

    # Clear screen on exit
    os.system("clear")

if __name__ == "__main__":
    main()


###############################################################################
# FUTURE PLANS!
#
#   1.  Implement presets saved to a json file.
#       General idea is a have a json file with dicts for all the
#       settings. I'm not yet done thinking though the details.
#       Will need the json file to sort them by name and need to
#       figure out how to check the file for conflicting names
#       and offer to overwrite it.
#
#       I will also need to figure out how to apply the settings.
#       Currently I'm thinking to loop though the dict keys and
#       call the appropriate function.
#
#
#   2.  I want to find a neat way to replace "press ENTER to continue"
#       with "press any key to continue" but for Linux this seems to not
#       be as easy as os.system("pause") like on windows.
#
#       I have come across some solutions but they require 3 different
#       imports and I would just prefer to use minimal external modules
#       and only use what I really need and avoid non-standard ones
#       at all costs to avoid dependencies
#
###############################################################################
