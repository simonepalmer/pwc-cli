# pwc-cli (pipewire controller - command line interface)
# version: 0.5.0
# Creator: Simon E Palmer

import json
import os
import time

# Path to config file and global presets variables
PRESET_PATH = os.path.expanduser("~/.config/pwc-cli")
os.makedirs(PRESET_PATH, exist_ok=True)
PRESET_FILE = os.path.join(PRESET_PATH, ".presets.json")

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
            "buffer": f"{buffer} spls",
            "samples": f"{samples} Hz",
        }
    else:
        return {
            "status": "Pipewire is SUSPENDED",
            "buffer": "disabled",
            "samples": "disabled",
        }

def show_current_settings():
    # Get and show the current settings
    settings = get_current_settings()

    print(f"{settings['status']}")
    text_body(
        f"buffer size: {settings['buffer']}",
        f"sample rate: {settings['samples']}",
    )


"""Manipulating settings"""

def change_setting_value(user_input):
    # Check if value is valid for command and set it
    setting         = user_input[0]
    current_setting = get_current_settings()[setting]

    # Check if pipewire.service is running
    if check_status() == True:
        # Check if the input has a value
        if check_value(user_input) == True:
            value = user_input[1]
        else:
            return

        if value in valid_settings[setting]:
        # Change value if it's different from current setting
            if value != current_setting:
                os.system(
                    f'pw-metadata -n settings 0 {pw_commands[setting]} {value}'
                )
        else:
            # Give a hint of valid values if the one given is not
            setting_string = ", ".join(valid_settings[setting])
            os.system("clear")

            print(f"'{value}' is not a valid value for '{setting}'!")
            text_body(
                "Valid values are:",
                setting_string,
            )
            wait_for_key()

    else:
        print("PIPEWIRE IS SUSPENDED")
        text_body(
            f"Can't set setting:",
            "Pipewire service is offline",
        )
        wait_for_key()


"""Pipewire.service status"""

def check_status():
    # Check if pipewire is running
    if not os.popen('pw-metadata -n settings').read() == '':
        return True
    else:
        # Clear error message from console if not running
        os.system("clear")
        return False

def check_value(user_input):
    # Check if command is paired with a value
    if len(user_input) > 1:
        return True
    else:
        value_error(user_input)
        return

def enable_pipewire(user_input):
    # Enable pipewire (with laoding screen)
    if check_status() == False:
        os.popen("systemctl --user start pipewire.socket")

        # Wait for pipewire.socket to start pipewire.service
        for i in range(10):
            # Adds dots after "loading" to show that program is not frozen
            os.system("clear")
            print("Pipewire is STARTING")
            text_body(
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
    # Disable pipewire.service and pipewire.socket
    if check_status() == True:
        os.system(f'systemctl --user stop pipewire.socket')
        os.system(f'systemctl --user stop pipewire.service')
    else:
        os.system("clear")
        print("PIPEWIRE IS ALREADY SUSPENDED\n")
        wait_for_key()


"""Presets"""

def save_preset(user_input):
    os.system("clear")

    preset_data = get_current_settings()

    # Check if a name for the preset is given
    if check_value(user_input) == True:
        preset_name = user_input[1]

        # Check if file exists & load
        if not os.path.isfile(PRESET_FILE) or os.stat(PRESET_FILE).st_size == 0:
            presets = {}
        else:
            with open(PRESET_FILE, "r") as f:
                presets = json.load(f)

        # Check if preset ID already exists
        if preset_name in presets:
            if not prompt_yes_no("Preset ID already exists, overwrite it?"):
                return
    else:
        return

    if check_status() == True:

        # Add new preset
        presets[preset_name] = preset_data

        # Save updated presets
        with open(PRESET_FILE, "w") as f:
            json.dump(presets, f, indent=4)

        os.system("clear")
        print("PRESET SAVED SUCCESSFULLY!")
        text_body(
            f"Preset '{preset_name}' was saved to file:",
            f"{PRESET_FILE}",
        )
        wait_for_key()

    else:
        os.system("clear")
        print("PIPEWIRE IS SUSPENDED")
        text_body(
            f"Can't save preset '{preset_name}':",
            "Pipewire service is offline",
        )
        wait_for_key()

def load_preset(user_input):
    os.system("clear")

    # Check if a name for the preset is given
    if check_value(user_input) == True:
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
    else:
        return

    if check_status() == True:

        # Load preset values
        preset = presets[preset_name]
        buffer_value = preset["buffer"]
        samples_value = preset["samples"]

        # Change values
        change_setting_value(["buffer", buffer_value])
        change_setting_value(["samples", samples_value])

        # Display success message
        os.system("clear")
        print("PRESET LOADED SUCCESSFULLY!")
        text_body(
            f"Preset '{preset_name}' was loaded from file:",
            f"{PRESET_FILE}",
        )
        wait_for_key()

    else:
        os.system("clear")
        print("PIPEWIRE IS SUSPENDED")
        text_body(
            f"Can't load preset '{preset_name}':",
            "Pipewire service is offline",
        )
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

    # Loop though and print ID and settings for each preset
    for preset_name, preset in presets.items():
        buffer_value = preset["buffer"]
        samples_value = preset["samples"]

        print(f"{preset_name.upper()}")
        print(f"buffer={buffer_value}, samples={samples_value}")
        print()

    wait_for_key()

def remove_preset(user_input):
    os.system("clear")

    if check_value(user_input) == True:
        preset_name = user_input[1]
    else:
        return

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
    print("REMOVED SUCCESSFULLY!")
    text_body(
        f"Preset '{preset_name}' was removed from file:",
        f"{PRESET_FILE}",
    )
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
    print("remove       remove <preset name>")
    print("                 Removes the named preset")
    print("list         list")
    print("                 Lists all saved presets")
    print()
    print("Note that presets can not be saved when pipewire is suspended!")
    print()
    wait_for_key()


"""Formating and interaction"""

def wait_for_key():
    if os.name == 'posix':
        return os.system(
            "bash -c 'read -n 1 -s -r -p \"Press any key to continue...\"'"
        ) == 0
    else:
        input("Press ENTER to continue...")
        return True

def text_body(*args):
    print()
    for string in args:
        print(string)
    print()

def value_error(user_input):
    os.system("clear")
    print("NO VALUE GIVEN")
    text_body(
        f"No value given for the command '{user_input[0]}'",
        f"Example: '{user_input[0]} <value>'",
    )
    wait_for_key()

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
            text_body(
                "Command could not be found",
                "Use command 'help' to show manual page",
            )
            if prompt_yes_no("See manual page now?") == True:
                manual()

    # Clear screen on exit
    os.system("clear")


if __name__ == "__main__":
    main()


###############################################################################
#       FUTURE PLANS!
#
#   1.  I am not completely sure about the reading and writing to JSON so
#       I will come back to it at a later point and hopefully improve it
#       when I have learned more
#       and load_preset to open contents of the file. Check taken names
#       and find the selected preset respectivly
#
###############################################################################
