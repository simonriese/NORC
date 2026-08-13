import shutil, subprocess, sys

def main():
    if not shutil.which("papi_native_avail") or not shutil.which("papi_event_chooser"):
        print("Error: PAPI tools ('papi_native_avail', 'papi_event_chooser') not found in PATH.")
        sys.exit(1)

    print("PAPI Native Counter Chooser")
    component_events = get_base_counters()
    if not component_events:
        print("No components or events found. Exiting.")
        return

    event_list = []
    all_events = {event for events in component_events.values() for event in events}
    while True:
        event = choose_next_counter(component_events,all_events)
        if event == "exit":
            break
        event_with_qualifier = choose_qualifier(event)
        if event_with_qualifier != "exit":
            event_list.append(event_with_qualifier)

    print("\n <==Chosen Counters==>")
    for event in event_list:
        print(event)

    # TODO Condense events into groups that work together
    if event_list:
        output_filename = "metrics.cfg"
        try:
            with open(output_filename, "w") as f:
                for event in event_list:
                    f.write(f"{event}\n")
            print(f"\nSuccess: Chosen counters have been saved to '{output_filename}'.")
        except IOError as e:
            print(f"\nError: Could not write to file. {e}")


def choose_next_counter(component_events: dict,all_events: list) -> str:
    output_Counter(component_events)
    while True:
        print('Choose an event, exit with "exit", or reprint list with "print')
        user_input = input("> ").strip()

        if user_input == "exit":
            return "exit"
        elif user_input == "print":
            output_Counter(component_events)
        elif user_input in all_events:
            return str(user_input)
        else:
            print("Invalid input. Please enter a valid event name from the list.")

def choose_qualifier(event: str) -> str:
    output_qualifier_info(event)
    while True:
        print(f'\nEnter qualifier for {event} (leave blank for none), "exit" to cancel, or "print" to reprint:')
        qualifier = input(f"{event}:").strip()

        if qualifier == "exit":
            return "exit"
        elif qualifier == "print":
            output_qualifier_info(event)
            continue

        test_event = f"{event}:{qualifier}" if qualifier else event

        result = subprocess.run(["papi_event_chooser", "NATIVE", test_event],capture_output=True,text=True)
        if result.returncode == 0:
            return test_event
        print(f"Invalid qualifier(s). PAPI rejected '{test_event}'.")


def output_qualifier_info(event):
    result = subprocess.run(["papi_native_avail", "-e", event], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("-"):
            lines = lines[index:]
    for line in lines:
        print(line)

def outputSimpleGrid(items, cols=4):
    if not items:
        return
    max_len = max(len(item) for item in items) + 2
    for i, item in enumerate(items):
        if i % cols == 0:
            print("  ", end="")
        print(f"{item:<{max_len}}", end="")
        if (i + 1) % cols == 0:
            print()
    print()

def output_Counter(component_events):
    for component, events in component_events.items():
        if events:
            print(component)
            outputSimpleGrid(events)
            print()

    return component_events

def get_base_counters():
    result = subprocess.run(["papi_native_avail","--noqual"],capture_output=True,text=True)
    lines = result.stdout.splitlines()
    data = []
    for index, line in enumerate(lines):
        if line.startswith("="):
            data = lines[index:]
            break
    current_component = None
    component_events = {}
    for index, line in enumerate(data):
        if line.startswith(" "):
            current_component = line.strip()
            component_events[current_component] = []

        elif line.startswith("| ") and not line.startswith("|  "):
            component_events[current_component].append(line.strip().replace("|", "").strip())
    return component_events

if __name__ == "__main__":
    main()