# pwc-cli (pipewire controller - command line interface)
# version: 0.9.0
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
    if check_status():
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
    settings = get_current_settings(); print(f"{settings['status']}")
    text_body(
        f"buffer size: {settings['buffer']}",
        f"sample rate: {settings['samples']}",
    )

"""Manipulating settings"""

def change_setting_value(user_input):
    if checklist(user_input, 'value', 'valid', 'status'):
        setting = user_input[0]; value = user_input[1]
        current_setting = get_current_settings()[setting]
        if value != current_setting:
            os.system(
                f'pw-metadata -n settings 0 {pw_commands[setting]} {value}'
        )
    else:
        return

"""Enable and disable"""

def enable_pipewire(user_input):
    if not check_status():
        os.popen("systemctl --user start pipewire.socket")
        for i in range(10):
            os.system("clear")
            print("Pipewire is starting!")
            text_body(
                "This will take a few seconds",
                f"Loading{'.'*i}",
            )
            time.sleep(1)
        wait_for_key()
    else:
        os.system("clear")
        print("Pipewire is already running!\n"); wait_for_key()

def disable_pipewire(user_input):
    if check_status():
        os.system(f'systemctl --user stop pipewire.socket')
        os.system(f'systemctl --user stop pipewire.service')
    else:
        os.system("clear")
        print("Pipewire is already suspended\n"); wait_for_key()

"""Presets"""

def save_preset(user_input):
    if checklist(user_input, 'value', 'status'):
        os.system("clear")
        presets = read_presets(); preset_name = user_input[1]

        if preset_name in presets:
            if not prompt_yes_no("Preset ID already exists, overwrite it?"):
                return

        preset_data = get_current_settings()
        presets[preset_name] = preset_data
        with open(PRESET_FILE, "w") as f:
            json.dump(presets, f, indent=4)

        os.system("clear")
        print("Preset saved successfully!")
        text_body(
            f"Preset '{preset_name}' was saved to file:",
            f"{PRESET_FILE}",
        )
        wait_for_key()
    else:
        return

def load_preset(user_input):
    if checklist(user_input, 'value', 'name', 'status'):
        os.system("clear")
        presets = read_presets(); preset_name = user_input[1]
        preset = presets[preset_name]
        buffer_value = preset["buffer"]; samples_value = preset["samples"]

        change_setting_value(["buffer", buffer_value])
        change_setting_value(["samples", samples_value])

        os.system("clear")
        print("Preset loaded successfully!")
        text_body(
            f"Preset '{preset_name}' was loaded from file:",
            f"{PRESET_FILE}",
        )
        wait_for_key()
    else:
        return

def remove_preset(user_input):
    if checklist(user_input, 'value'):
        os.system("clear")
        presets = read_presets(); preset_name = user_input[1]

        if preset_name not in presets:
            name_error(preset_name); return

        presets.pop(preset_name)
        with open(PRESET_FILE, "w") as f:
            json.dump(presets, f, indent=4)

        os.system("clear")
        print("Preset removed successfully!")
        text_body(
            f"Preset '{preset_name}' was removed from file:",
            f"{PRESET_FILE}",
        )
        wait_for_key()
    else:
        return

def list_presets(user_input):
    os.system("clear")
    presets = read_presets()
    print("List of available presets:\n")
    for preset_name, setting in presets.items():
        buffer_value = setting["buffer"]; samples_value = setting["samples"]
        print(f"{preset_name.upper()}")
        print(f"buffer={buffer_value}, samples={samples_value}")
        print()

    wait_for_key()

def read_presets():
    try:
        with open(PRESET_FILE, "r") as f:
            presets = json.load(f)
            return presets
    except json.JSONDecodeError:
        return {}

"""Checks before assigning and executing"""

def check_value(user_input):
    return True if len(user_input) > 1 else False

def check_valid(user_input):
    setting = user_input[0]; value = user_input[1]
    return True if value in valid_settings[setting] else False

def check_name(user_input):
    preset_name = user_input[1]; presets = read_presets()
    return True if preset_name in presets else False

def check_status(*args):
    status = os.popen('pw-metadata -n settings').read()
    os.system('clear') # Clear error if Pipewire is suspended
    return True if 'Found "settings"' in status else False

def checklist(user_input, *args):
    for check in args:
        result = checklist_map[check](user_input)
        if result == False:
            error_map[check](user_input)
            return False

    return True

"""Error messages"""

def value_error(user_input):
    os.system("clear")
    print("No value was given!")
    text_body(
        f"No value given for the command '{user_input[0]}'",
        f"Example: '{user_input[0]} <value>'",
    )
    wait_for_key()

def valid_error(user_input):
    setting = user_input[0]; value = user_input[1]
    valid_settings_string = ", ".join(valid_settings[setting])
    os.system("clear")
    print(f"'{value}' is not a valid value for '{setting}'!")
    text_body(
        "Valid values are:",
        valid_settings_string,
    )
    wait_for_key()

def name_error(user_input):
    preset_name = user_input[0]
    os.system("clear")
    print(
        f"Preset '{preset_name.upper()}' could not be found!\n"
    )
    wait_for_key()

def status_error(*args):
    os.system("clear")
    print("Pipewire is suspended!")
    text_body(
        f"Can't set setting:",
        "Pipewire service is offline",
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
        input("Press ENTER to continue..."); return True

def prompt_yes_no(question):
    while True:
        answer = input(f"{question} (y/n): ").lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("Invalid answer. Please enter 'y' or 'n'.")

def text_body(*args):
    print()
    for string in args:
        print(string)
    print()

"""List and dicts of commands & settings"""

valid_settings = {
    "buffer"    :   ["32","64","128","256","512","1024","2048"],
    "samples"   :   ["44100","48000","88200","96000"],
}

commands = {
    "buffer"    :   change_setting_value,
    "samples"   :   change_setting_value,
    "enable"    :   enable_pipewire,
    "disable"   :   disable_pipewire,
    "save"      :   save_preset,
    "load"      :   load_preset,
    "list"      :   list_presets,
    "remove"    :   remove_preset,
}

pw_commands = {
    "buffer"    :   'clock.force-quantum',
    "samples"   :   'clock.force-rate',
}

checklist_map = {
    "value"     :   check_value,
    "valid"     :   check_valid,
    "status"    :   check_status,
    "name"      :   check_name,
}

error_map = {
    "value"     :   value_error,
    "valid"     :   valid_error,
    "status"    :   status_error,
    "name"      :   name_error,
}

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
    if not os.path.isfile(PRESET_FILE):
        with open(PRESET_FILE, "w") as f:
            json.dump({}, f)

    while True:
        os.system("clear")
        show_current_settings()
        user_input = input("Enter command: ")
        user_input_list = user_input.split(" ")

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

    os.system("clear")

if __name__ == "__main__":
    main()


###############################################################################
#
#   FUTURE PLANS!
#
#   1. Out of ideas! RIP!
#
###############################################################################
