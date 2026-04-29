# print_registers_decimal.py
import gdb

# Check if a frame exists
if gdb.selected_frame() is not None:
    # Access registers of the current frame
    for reg in gdb.selected_frame().architecture().registers():
        print(f"{reg.name()}: {gdb.parse_and_eval(reg.name()):d} (decimal)")
else:
    print("No frame selected. Please make sure the program is running and a frame is available.")

