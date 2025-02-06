import csv
from pathlib import Path
from os import listdir, getcwd
from os.path import isfile, join
from csv import *
from customtkinter import *
from tkinter import messagebox
from shared.tk_models import SettingPage
from shared.serial_port_controller import *

class SerialPortSetting(SettingPage):
    '''a class that implements methods and functions 
    related to connecting serial port setting to the experiments '''

    def __init__(self, preference = NONE, controller: SerialPortController = NONE):
        ''' implement the constructor of the class object,
        initializing the tab_view page with summary page'''

        super().__init__(self)

        # GUI element
        print(f"🔍 SerialPortSetting initialized with preference: {preference}")
        self.title("Serial Port")
        self.preference = None
        self.configuration_name = StringVar(value="")
        self.current_configuration_name = StringVar(value="")
        self.preference_path = None
        if isinstance(controller, SerialPortController):
            self.serial_port_controller = controller
        else:
            self.serial_port_controller = SerialPortController(self.preference)

        if os.name == 'posix':
            self.port_setting_configuration_path = os.getcwd() + "/settings/serial ports"
        else:
            self.port_setting_configuration_path = os.getcwd() + "\\settings\\serial ports"

        # setting value element
        self.serial_port = StringVar(value = "")
        self.baud_rate_var = StringVar(value="")
        self.parity_var = StringVar(value="")
        self.flow_control_var = StringVar(value="")
        self.data_bits_var = StringVar(value="")
        self.stop_bits_var = StringVar(value="")
        self.input_bype_var = StringVar(value="")

        if preference:
            if preference == "device":
                self.preference_path = os.path.join(os.getcwd(), "settings", "serial ports", "preference", "device", "preferred_config.txt")
            elif preference == "reader":
                self.preference_path = os.path.join(os.getcwd(), "settings", "serial ports", "preference", "reader", "rfid_config.txt")
            else:
                self.preference_path = None  # Fallback if no valid type

            
            if os.path.exists(self.preference_path):
                try:
                    with open(self.preference_path, "r") as file:
                        file_names = file.readlines()
                        if file_names:
                            self.confirm_setting(file_names[0].strip())
                            self.preference = file_names[0].strip()
                except Exception as e:
                    print("Error opening preference file:", e)
            else:
                print(f"Preference file {self.preference_path} not found. Using default settings.")

        else:
            self.baud_rate_var = StringVar(value="9600")
            self.parity_var = StringVar(value="None")
            self.flow_control_var = StringVar(value="None")
            self.data_bits_var = StringVar(value="Eight")
            self.stop_bits_var = StringVar(value="1")
            self.input_bype_var = StringVar(value="Binary")

        self.tab_view = CTkTabview(master=self)
        self.tab_view.grid(padx=20, pady=20, sticky = "ew")

        self.tab_view.add("Map RFID")
        self.tab_view.add("Data Collection")
        self.summary_page("Map RFID")
        self.summary_page("Data Collection")

        self.available_configuration = [file for file in listdir(self.port_setting_configuration_path)
                                        if isfile(join(self.port_setting_configuration_path, file))]

    def edit_page(self, tab: str):
        ''' page that allow user to edit/update serial port settings'''
        # top region of the page

        # pylint: disable=line-too-long
        self.configuration_region = CTkFrame(master=self.tab_view.tab(tab), corner_radius=10, border_width=2, width=400, height=200)
        self.region_title_label = CTkLabel(master = self.configuration_region, text="Configuration Selection")
        self.setting_configuration_label = CTkLabel(self.configuration_region, text="Existing Configuration", width=8, height=12)
        self.import_file = CTkOptionMenu(self.configuration_region, values=self.available_configuration, variable=self.current_configuration_name, height=12, width = 274)
        if self.preference:
                self.import_file.set(self.preference)
        self.edit_configuration_button = CTkButton(self.configuration_region, text="Edit", width=2, height=14, command=self.edit_configuration)
        
        self.set_preference_button = CTkButton(
            self.configuration_region, text="Set as Meausurement Device", width=2, height=14,
            command=lambda: self.set_preference(self.serial_port.get(), self.current_configuration_name.get())
        )
        
        self.set_rfid_button = CTkButton(
            self.configuration_region, text="Set as RFID Reader", width=2, height=14,
            command=lambda: self.set_rfid(self.serial_port.get(), self.current_configuration_name.get())
        )

        self.comfirm_button = CTkButton(self.configuration_region, text="Confirm", width=2, height=14, command=self.confirm_setting)

        self.configuration_region.grid(row=0, column=0, columnspan=5, padx=20, pady=5, sticky="ew")
        self.region_title_label.grid(row=0, column=0, padx=5, pady=3, sticky="ew")
        self.setting_configuration_label.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.import_file.grid(row=1, column=1, columnspan=2, padx=18, pady=10, sticky="ew")
        self.edit_configuration_button.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.set_preference_button.grid(row=2, column=2, padx=20, pady=15, sticky="ew")
        self.set_rfid_button.grid(row=3, column=2, padx=20, pady=15, sticky="ew")
        self.comfirm_button.grid(row=2, column=3, padx=20, pady=15, sticky="ew")

        # bottom region of the page
        self.edit_region = CTkFrame(master=self.tab_view.tab(tab), corner_radius=10, border_width=2, width=400, height=400)
        self.edit_region.grid(row=1, column=0, columnspan=5, padx=20, pady=5, sticky="ew")

        # Naming section
        self.new_configuration_label = CTkLabel(self.edit_region, text="New Configuration", width=8, height=12)
        self.new_configuration_name_label = CTkLabel(self.edit_region, text="Configuration Name", width=8, height=12)
        self.configuration_name_entry = CTkEntry(self.edit_region, textvariable=self.configuration_name)
        self.new_configuration_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.new_configuration_name_label.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.configuration_name_entry.grid(row=2, column=1, columnspan=2,padx=20, pady=5, sticky="ew")

        # port section
        available_port = []
        for port_info in self.serial_port_controller.get_available_ports():
            available_port.append(port_info[0])

        self.port_label = CTkLabel(self.edit_region, text="Port", width=8, height=12)
        self.port_menu = CTkOptionMenu(self.edit_region, height=12,
                                       values=available_port,
                                       variable=self.serial_port)
        self.port_label.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.port_menu.grid(row=3, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        # Baud rate section
        self.baud_rate_label = CTkLabel(self.edit_region, text="Baud Rate", width=8, height=12)
        self.baud_rate_menu = CTkOptionMenu(self.edit_region, height=12,
                                            values=["100", "300", "600", "1200", "2400", "4800", "9600", "19200"],
                                            variable=self.baud_rate_var)
        self.baud_rate_label.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.baud_rate_menu.grid(row=4, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        # Parity section
        self.parity_label = CTkLabel(self.edit_region, text="Parity", height=12)
        self.parity_menu = CTkOptionMenu(self.edit_region, height=12,
                                         values=["None", "Odd", "Even", "Mark", "Space"],
                                         variable=self.parity_var)
        self.parity_label.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.parity_menu.grid(row=5, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        # Flow control section
        self.flow_control_label = CTkLabel(self.edit_region, text="Flow Control", height=12)
        self.flow_control_menu = CTkOptionMenu(self.edit_region, height=12,
                                               values=["None", "Xon/Xoff", "Hardware", "Opto-RS"],
                                               variable=self.flow_control_var)
        self.flow_control_label.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.flow_control_menu.grid(row=6, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        # Data bits section
        self.data_bits_label = CTkLabel(self.edit_region, text="Data Bits", height=12)
        self.data_bits_menu = CTkOptionMenu(self.edit_region, height=12,
                                            values=["Five", "Six", "Seven", "Eight"],
                                            variable=self.data_bits_var)
        self.data_bits_label.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        self.data_bits_menu.grid(row=7, column=1, columnspan=2, padx=20, pady=5, sticky="ew")

        # Stop bit section
        self.stop_bits_label = CTkLabel(self.edit_region, text="Stop Bits", height=12)
        self.one_button = CTkRadioButton(self.edit_region, text="1", variable=self.stop_bits_var, value = "1", height=12)
        self.one_point_five_button = CTkRadioButton(self.edit_region, text="1.5", variable=self.stop_bits_var, value = "1.5", height=12)
        self.two_button = CTkRadioButton(self.edit_region, text="2", variable=self.stop_bits_var, value = "2", height=12)
        self.stop_bits_label.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        self.one_button.grid(row=8, column=1, padx=20, pady=5, sticky="ew")
        self.one_point_five_button.grid(row=8, column=2, padx=20, pady=5, sticky="ew")
        self.two_button.grid(row=9, column=1, padx=20, pady=5, sticky="ew")

        # Input byte section
        self.input_byte_label = CTkLabel(self.edit_region, text="Input Byte", height=12)
        self.binary_button = CTkRadioButton(self.edit_region, text="Binary", variable=self.input_bype_var, value = "Binary", height=12)
        self.text_button = CTkRadioButton(self.edit_region, text="Text", variable=self.input_bype_var, value = "Text", height=12)
        self.input_byte_label.grid(row=10, column=0, padx=20, pady=5, sticky="ew")
        self.binary_button.grid(row=10, column=1, padx=20, pady=5, sticky="ew")
        self.text_button.grid(row=10, column=2, padx=20, pady=5, sticky="ew")

        # button
        self.save_button = CTkButton(self.edit_region, text="Save", command=self.save, height=14)
        self.save_button.grid(row=11, column=2, padx=20, pady=5, sticky="ns")

        self.test_button = CTkButton(self.edit_region, text="Test Read", command=self.test_read, height=14)
        self.test_button.grid(row=12, column=2, padx=20, pady=5, sticky="ns")

        self.data_text = CTkLabel(self.edit_region, height=25, width=50, text="Waiting for Data...")
        self.data_text.grid(row=13, column=2, columnspan=3, padx=20, pady=3, sticky="ew")

        self.back_to_summary_button = CTkButton(self.edit_region, text="Back to Summary", command=self.go_to_summary_page, height=14)
        self.back_to_summary_button.grid(row=12, column=1, padx=20, pady=5, sticky="ns")

        self.serial_port_controller = SerialPortController(self.preference)

    def update_label(self, data):
        # Update the label with data from the test_read method
        print(data)
        self.data_text.configure(text=data)
        self.master.update_idletasks()

        #pylint: enable=line-too-long

    def summary_page(self, tab: str):
        ''' page that displays the setting of current configuration'''
        #pylint: disable=line-too-long
        self.summary_section = CTkFrame(master=self.tab_view.tab(tab), corner_radius=10, border_width=2, width=400, height=400)
        self.summary_section.grid(row=0, column=3, columnspan=8, padx=20, pady=5, sticky="ew")

        self.port_label = CTkLabel(self.summary_section, text="Port")
        self.current_port = CTkLabel(self.summary_section, text=self.serial_port.get())
        self.port_label.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        self.current_port.grid(row=0, column=2, padx=20, pady=5, sticky="ew")

        self.baud_rate_label = CTkLabel(self.summary_section, text="Baud Rate")
        self.current_baud_rate = CTkLabel(self.summary_section, text=self.baud_rate_var.get())
        self.baud_rate_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.current_baud_rate.grid(row=1, column=2, padx=20, pady=5, sticky="ew")


        self.parity_label = CTkLabel(self.summary_section, text="Parity")
        self.current_parity = CTkLabel(self.summary_section, text=self.parity_var.get())
        self.parity_label.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.current_parity.grid(row=2, column=2, padx=20, pady=5, sticky="ew")

        self.flow_control_label = CTkLabel(self.summary_section, text="Flow Control")
        self.current_flow_control = CTkLabel(self.summary_section, text=self.flow_control_var.get())
        self.flow_control_label.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.current_flow_control.grid(row=3, column=2, padx=20, pady=5, sticky="ew")


        self.data_bits_label = CTkLabel(self.summary_section, text="Data Bits")
        self.current_data_bits = CTkLabel(self.summary_section, text=self.data_bits_var.get())
        self.data_bits_label.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.current_data_bits.grid(row=4, column=2, padx=20, pady=5, sticky="ew")

        self.stop_bits_label = CTkLabel(self.summary_section, text="Stop Bits")
        self.current_stop_bits = CTkLabel(self.summary_section, text=self.stop_bits_var.get())
        self.stop_bits_label.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.current_stop_bits.grid(row=5, column=2, padx=20, pady=5, sticky="ew")

        self.input_byte_label = CTkLabel(self.summary_section, text="Input Byte")
        self.current_input_byte = CTkLabel(self.summary_section, text=self.input_bype_var.get())
        self.input_byte_label.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.current_input_byte.grid(row=6, column=2, padx=20, pady=5, sticky="ew")

        self.edit_button = CTkButton(self.summary_section, text="Edit", command=self.edit)
        self.edit_button.grid(row=8, column=2, padx=20, pady=40, sticky="ns")

        #pylint: enable=line-too-long


    def save(self):
        '''Save the current settings as a new or existing configuration.'''
        configuration_name = self.configuration_name.get().strip()
        
        if not configuration_name:
            messagebox.showerror("Error", "Configuration name cannot be empty.")
            return
        
        settings = [
            self.baud_rate_var.get(),
            self.parity_var.get(),
            self.flow_control_var.get(),
            self.data_bits_var.get(),
            self.stop_bits_var.get(),
            self.input_bype_var.get(),
            self.serial_port.get()
        ]

        settings_path = os.path.join(os.getcwd(), "settings", "serial ports", f"{configuration_name}.csv")

        try:
            with open(settings_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(settings)
            print(f"Settings saved for {configuration_name}")
            messagebox.showinfo("Success", f"Configuration '{configuration_name}' saved successfully!\n Set it as a preffered device to use it.")
        except Exception as e:
            print(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def edit(self):
        '''Function for the edit button on summary page, brings user
        to the edit page'''
        self.refresh_tabs()
        self.edit_page("Map RFID")
        self.edit_page("Data Collection")

    def go_to_summary_page(self):
        '''Refresh tabs and display the summary page'''
        self.refresh_tabs()
        self.summary_page("Map RFID")
        self.summary_page("Data Collection")
    
    def refresh_tabs(self):
        '''refreshes the page when updates are made'''
        self.tab_view.delete("Map RFID")
        self.tab_view.delete("Data Collection")
        self.tab_view.add("Map RFID")
        self.tab_view.add("Data Collection")

    def set_preference(self, port, file_name):
        '''Save a specific configuration for a given port in its own preference folder.'''
        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference", "device")
        os.makedirs(preference_dir, exist_ok=True)
        preference_path = os.path.join(preference_dir, "preferred_config.txt")
        
        try:
            with open(preference_path, "w") as file:
                file.write(file_name + "\n")
            print(f"Preference for {port} set to {file_name}")
        except Exception as e:
            print(f"Error saving preference for {port}: {e}")

    def set_rfid(self, port, file_name):
        '''Save a specific configuration for a given port in its own preference folder.'''
        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference", "reader")
        os.makedirs(preference_dir, exist_ok=True)
        preference_path = os.path.join(preference_dir, "rfid_config.txt")
        
        try:
            with open(preference_path, "w") as file:
                file.write(file_name + "\n")
            print(f"RFID Reader for {port} set to {file_name}")
        except Exception as e:
            print(f"Error saving RFID Reader for {port}: {e}")

    def confirm_setting(self, f = None):
        '''select a configuration and use it as current serial
        port setting'''
        if f:
            file_name = os.path.join(self.port_setting_configuration_path, f)
        else:
            file_name = os.path.join(self.port_setting_configuration_path, self.current_configuration_name.get())
        file = open(file_name)
        csv_reader = reader(file)
        for line in csv_reader:
            self.baud_rate_var.set(line[0])
            self.parity_var.set(line[1])
            self.flow_control_var.set(line[2])
            self.data_bits_var.set(line[3])
            self.stop_bits_var.set(line[4])
            self.input_bype_var.set(line[5])
            self.serial_port.set(line[6])
        file.close()


    def edit_configuration(self):
        '''allow user to edit existing configuration by overwriting
        the existing configuration csv file (paired with save)'''
        self.configuration_name_entry.delete(0,END)
        file_name= Path(self.current_configuration_name.get())
        self.configuration_name_entry.insert(0, file_name.with_suffix(""))
        self.confirm_setting()
        pass

    def test_read(self):
        '''Reads data from the serial port using the current settings on screen'''
        if self.serial_port_controller:
            try:
                self.serial_port_controller.retrieve_setting([self.baud_rate_var.get(), self.data_bits_var.get(),
                                                              self.parity_var.get(), self.stop_bits_var.get(),
                                                              self.flow_control_var.get()])
                self.serial_port_controller.update_setting(self.serial_port.get())
                data = self.serial_port_controller.read_data()
                print("Data read from serial port:" + str(data))
                self.update_label("Data read from serial port: " + str(data))
                return ("Data read from serial port: " + str(data))

            except Exception as e:  # pylint: disable=broad-exception-caught
                print("Error reading from serial port:", e)
                return None
        else:
            print("Serial port controller not initialized")
            return None
        

if __name__ == "__main__":
    root = CTk()
    app = SerialPortSetting()

    # TEST 1: Print Available Serial Ports
    if app.serial_port_controller:
        print("Available Serial Ports:", app.serial_port_controller.get_available_ports())
    else:
        print("ERROR: SerialPortController is not initialized!")

    # TEST 2: Set a preference for a port and retrieve it
    test_port = "COM3"  # Replace with an actual port on your system
    test_config = "test_config.csv"

    print(f"\nSetting preference for {test_port} to {test_config}...")
    app.set_preference(test_port, test_config)

    # Verify that preference is saved
    preference_path = os.path.join(os.getcwd(), "settings", "serial ports", "preference", test_port, "preferred_config.txt")
    if os.path.exists(preference_path):
        with open(preference_path, "r") as file:
            saved_config = file.read().strip()
            print(f"Retrieved Preference: {saved_config}")
            assert saved_config == test_config, "ERROR: Preference was not saved correctly!"

    # TEST 3: Save a new configuration
    test_settings = ["9600", "None", "None", "Eight", "1", "Binary", test_port]
    print("\nSaving configuration...")
    app.save("test_config", test_settings)

    # Verify that configuration is saved
    settings_path = os.path.join(os.getcwd(), "settings", "serial ports", "test_config.csv")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as file:
            saved_settings = file.read().strip()
            print(f"Saved Configuration: {saved_settings}")
            assert saved_settings == ",".join(test_settings), "ERROR: Configuration was not saved correctly!"

    print("\nAll tests passed successfully!")

    root.mainloop()

