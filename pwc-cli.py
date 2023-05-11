# pwc-cli (pipewire controller - command line interface)
# version: 0.1.0
# Creator: Simon E Palmer

import json
import os
import time

PRESET_FILE = ".presets.json"
presets = {}

"""Current settings"""

def get_current_settings():
    # If pipewire is running, get current settings from metadata
    if check_status() == True:
        current_settings = os.popen('pw-metadata -n settings').read()
        settings_list = current_settings.split("'")

        # If there is no forced value, get default value
        buffer_index = settings_list.index('clock.force-quantum')
        if settings_list[buffer_index+2] == str(0):
            buffer_index = settings_list.index('clock.quantum')
        buffer = settings_list[buffer_index+2]

        samples_index = settings_list.index('clock.force-rate')
        if settings_list[samples_index+2] == str(0):
            samples_index = settings_list.index('clock.rate')
        samples = settings_list[samples_index+2]

        # Retrun current settings

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
        f"buffer size: {settings['buffer']} spls",
        f"sample rate: {settings['samples']} Hz",
    )


"""Manipulating settings"""

def change_setting_value(user_input):
    setting         = user_input[0]
    current_setting = get_current_settings()[setting]

    # Check if pipewire.service is running
    if check_status() == True:
        # Check if the input command has a value example: "buffer 512"
        if len(user_input) <= 1:
            os.system("clear")

            print("NO VALUE GIVEN")
            text_body (
                f"No value given for the command '{setting.lower()}'",
                f"Example: '{setting.lower()} <value>'",
            )
            wait_for_key()

        else:
            # Check if it's a valid value for the given command
            value = user_input[1]

            if value in valid_settings[setting]:
                # Change value if it's not the same as current value
                if value != current_setting:
                    os.system (
                    f'pw-metadata -n settings 0 {pw_commands[setting]} {value}'
                    )
            else:
                # Give a hint of valid values if the one given is not
                setting_string = ", ".join(valid_settings[setting])
                os.system("clear")

                print(f"'{value}' is not a valid value for '{setting}'!")
                text_body (
                    "Valid values are:",
                    setting_string,
                )
                wait_for_key()

    else:
        print("PIPEWIRE IS SUSPENDED")
        text_body (
            f"Can't set setting:",
            "Pipewire service is offline",
        )
        wait_for_key()


"""Pipewire.service status"""

def check_status():
    if not os.popen('pw-metadata -n settings').read() == '':
        return True
    else:
        # Clear error message from console if not running
        os.system("clear")
        return False

def enable_pipewire(user_input):
    if check_status() == False:
        os.popen("systemctl --user start pipewire.socket")

        # Wait for pipewire.socket to start pipewire.service
        for i in range(10):
            # Adds dots after "loading" to show that program is not frozen
            os.system("clear")
            print("Pipewire is STARTING")
            text_body (
                "This will take a few seconds",
                f"Loading{'.'*i}",
            )
            time.sleep(1)

        # Demand keypress as extra buffer for very slow systems :)
        wait_for_key()

    else:
        os.system("clear")
        print("Pipewire is already running\n")
        wait_for_key()

def disable_pipewire(user_input):
    if check_status() == True:
        os.system(f'systemctl --user stop pipewire.socket')
        os.system(f'systemctl --user stop pipewire.service')
    else:
        os.system("clear")
        print("Pipewire is already suspended\n")
        wait_for_key()


"""Presets"""

def save_preset(user_input):
    os.system("clear")

    if check_status() == True:
        # Check if a name for the preset is given
        if len(user_input) > 1:
            preset_name = user_input[1]
            preset_data = get_current_settings()

            if not os.path.isfile(PRESET_FILE) or os.stat(PRESET_FILE).st_size == 0:
                presets = {}
            else:
                with open(PRESET_FILE, "r") as f:
                    presets = json.load(f)

            # Check if preset ID already exists
            if preset_name in presets:
                if not prompt_yes_no("Preset ID already exists, overwrite it?"):
                    return

            # Add new preset
            presets[preset_name] = preset_data

            # Save updated presets
            with open(PRESET_FILE, "w") as f:
                json.dump(presets, f, indent=4)

            os.system("clear")
            print(f"Preset '{preset_name}' saved!\n")
            wait_for_key()

        else:
            os.system("clear")
            print("No preset name given!\n")
            wait_for_key()
    else:
        os.system("clear")
        print("Pipewire is suspended. Can't save preset.\n")
        wait_for_key()

def load_preset(user_input):
    os.system("clear")

    preset_name = user_input[1]

    # Load presets from file
    try:
        with open(PRESET_FILE, "r") as f:
            presets = json.load(f)
    except FileNotFoundError:
        os.system("clear")
        print("No presets found!\n")
        wait_for_key()
        return

    # Check if preset ID exists
    if preset_name not in presets:
        os.system("clear")
        print(f"Preset '{preset_name}' not found!\n")
        wait_for_key()
        return

    # Load preset values
    preset = presets[preset_name]
    buffer_value = preset["buffer"]
    samples_value = preset["samples"]

    # Change values
    change_setting_value(["buffer", buffer_value])
    change_setting_value(["samples", samples_value])

    # Display success message
    os.system("clear")
    print(f"Preset '{preset_name}' loaded successfully\n")
    wait_for_key()

def list_preset(user_input):
    try:
        with open(PRESET_FILE, "r") as f:
            presets = json.load(f)
    except FileNotFoundError:
        os.system("clear")
        print("No presets found!\n")
        wait_for_key()
        return

    os.system("clear")
    print("List of available presets:\n")

    for preset_name, preset in presets.items():
        buffer_value = preset["buffer"]
        samples_value = preset["samples"]

        print(f"{preset_name.upper()}")
        print(f"buffer={buffer_value}, samples={samples_value}")
        print()

    wait_for_key()

def remove_preset(user_input):
    os.system("clear")

    preset_name = user_input[1]

    # Load presets from file
    try:
        with open(PRESET_FILE, "r") as f:
            presets = json.load(f)
    except FileNotFoundError:
        os.system("clear")
        print("No presets found!\n")
        wait_for_key()
        return

    # Check if preset ID exists
    if preset_name not in presets:
        os.system("clear")
        print(f"Preset '{preset_name}' not found!\n")
        wait_for_key()
        return

    # Remove the preset
    presets.pop(preset_name)

    # Save the updated presets file
    with open(PRESET_FILE, "w") as f:
        json.dump(presets, f)

    # Display success message
    os.system("clear")
    print(f"Preset '{preset_name}' removed successfully\n")
    wait_for_key()


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
    print("save         save <preset name>")
    print("                 Saves the current settings as a preset")
    print("load         load <preset name>")
    print("                 Loads the settings of a previously saved preset")
    print("list         list")
    print("                 Lists all saved presets")
    print("remove       remove <preset name>")
    print("                 Removes the named preset")
    print()
    print("Note that presets can not be saved when pipewire is suspended!")
    print()
    wait_for_key()


"""Formating and interaction"""

def wait_for_key():
    input("Press ENTER to continue")

def text_body(*args):
    print()
    for string in args:
        print(string)
    print()

def prompt_yes_no(question):
    while True:
        answer = input(f"{question} (y/n): ").lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("Invalid answer. Please enter 'y' or 'n'.")

"""List and dicts of commands & settings"""

# Valid settings

valid_settings = {
    "buffer":   ["32","64","128","256","512","1024","2048"],
    "samples":  ["44100","48000","88200","96000"],
}

# Dicts of commands

commands = {
    "buffer":   change_setting_value,
    "samples":  change_setting_value,
    "enable":   enable_pipewire,
    "disable":  disable_pipewire,
    "save":     save_preset,
    "load":     load_preset,
    "list":     list_preset,
    "remove":   remove_preset,
}

pw_commands = {
    "buffer":   'clock.force-quantum',
    "samples":  'clock.force-rate',
}

# Exit commands

exit_variants = [
    "exit",
    "quit",
    ":q",
]

# Help commands

help_variants = [
    "help",
    "manual",
    "man",
]


def main():
    #Create file for presets if it doesn't exist
    if not os.path.isfile(PRESET_FILE):
        with open(PRESET_FILE, "w") as f:
            json.dump({}, f)

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
                "Use command 'help' to show manual page at any time",
            )
            if prompt_yes_no("Show manual page right away?") == True:
                manual()

    # Clear screen on exit
    os.system("clear")


if __name__ == "__main__":
    main()


###############################################################################
#       FUTURE PLANS!
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
