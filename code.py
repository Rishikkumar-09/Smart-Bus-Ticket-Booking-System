import os
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import qrcode
from PIL import Image, ImageTk
from fpdf import FPDF


class BusTicketBooking:
    def __init__(self, root):
        self.root = root
        self.root.title("Bus Ticket Booking System")
        self.root.geometry("1200x800")

        # City routes with prices
        self.city_routes = {
            "Delhi to Mumbai": 1500,
            "Delhi to Bangalore": 2000,
            "Mumbai to Bangalore": 1800,
            "Chennai to Hyderabad": 1200,
            "Hyderabad to Pune": 1000
        }

        self.seat_layout = [
            ["A1", "A2", "A3"],
            ["B1", "B2", "B3"],
            ["C1", "C2", "C3"],
            ["D1", "D2", "D3"]
        ]

        self.booked_seats = set()
        self.selected_seats = set()
        self.selected_route = None
        self.selected_date = None
        self.ticket_price = 0
        self.total_price = 0
        self.upi_id = "0987654321@axl"  # Replace with your UPI ID
        self.passenger_details = []

        self.create_route_selection()
        self.create_seat_grid()
        self.create_payment_section()

    def create_route_selection(self):
        """ Create city route and date selection with dropdown and calendar. """
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Label(frame, text="Select Route:", font=("Arial", 14)).grid(row=0, column=0, padx=5)
        self.route_var = tk.StringVar(value="Select Route")
        self.route_menu = ttk.Combobox(frame, textvariable=self.route_var, values=list(self.city_routes.keys()))
        self.route_menu.grid(row=0, column=1, padx=10)

        tk.Label(frame, text="Select Date:", font=("Arial", 14)).grid(row=0, column=2, padx=5)
        self.calendar = Calendar(frame, date_pattern="yyyy-mm-dd")
        self.calendar.grid(row=0, column=3, padx=10)

        self.select_button = tk.Button(frame, text="Confirm Route and Date", font=("Arial", 12),
                                       command=self.confirm_route)
        self.select_button.grid(row=0, column=4, padx=10)

    def confirm_route(self):
        """ Confirm the selected route and date. """
        route = self.route_var.get()
        if route not in self.city_routes:
            messagebox.showinfo("Select Route", "Please select a valid route!")
            return

        self.selected_route = route
        self.ticket_price = self.city_routes[route]
        self.selected_date = self.calendar.get_date()
        messagebox.showinfo("Route Confirmed",
                            f"Route: {self.selected_route}\nDate: {self.selected_date}\nPrice per Seat: ₹{self.ticket_price}")

    def create_seat_grid(self):
        """ Create the seat layout grid. """
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.grid(row=1, column=0, columnspan=2)

        tk.Label(frame, text="Select Seats:", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)

        self.seat_buttons = {}
        for row_idx, row in enumerate(self.seat_layout):
            for col_idx, seat_num in enumerate(row):
                button = tk.Button(frame, text=seat_num, width=8, height=2,
                                   command=lambda r=row_idx, c=col_idx: self.select_seat(r, c),
                                   relief="solid", bd=3, font=("Arial", 12), bg="green")
                button.grid(row=row_idx + 1, column=col_idx, padx=10, pady=10)
                self.seat_buttons[(row_idx, col_idx)] = button

        self.price_label = tk.Label(self.root, text="Total Price: ₹0", font=("Arial", 14))
        self.price_label.grid(row=2, column=0, columnspan=2, pady=10)

    def select_seat(self, row, col):
        """ Handle seat selection or deselection. """
        seat_number = self.seat_layout[row][col]
        button = self.seat_buttons[(row, col)]

        if seat_number in self.booked_seats:
            messagebox.showinfo("Seat Booked", f"Seat {seat_number} is already booked!")
        elif seat_number in self.selected_seats:
            self.selected_seats.remove(seat_number)
            button.config(bg="green")
        else:
            self.selected_seats.add(seat_number)
            button.config(bg="red")

        self.update_total_price()

    def update_total_price(self):
        """ Update total price based on selected seats. """
        self.total_price = len(self.selected_seats) * self.ticket_price
        self.price_label.config(text=f"Total Price: ₹{self.total_price}")

    def create_payment_section(self):
        """ Create payment section with proceed button. """
        self.proceed_button = tk.Button(self.root, text="Proceed", font=("Arial", 14),
                                        command=self.collect_passenger_details)
        self.proceed_button.grid(row=3, column=0, pady=10)

    def collect_passenger_details(self):
        """ Collect passenger details in a popup. """
        if not self.selected_seats:
            messagebox.showinfo("No Seats", "Please select at least one seat!")
            return

        self.passenger_window = tk.Toplevel(self.root)
        self.passenger_window.title("Passenger Details")
        self.passenger_window.geometry("500x600")

        tk.Label(self.passenger_window, text="Enter Passenger Details", font=("Arial", 14)).pack(pady=10)

        self.passenger_entries = []
        for i, seat in enumerate(self.selected_seats, start=1):
            frame = tk.Frame(self.passenger_window)
            frame.pack(pady=5)

            tk.Label(frame, text=f"Passenger {i} (Seat {seat}):", font=("Arial", 12)).grid(row=0, column=0, padx=5)

            name_entry = tk.Entry(frame, font=("Arial", 12))
            name_entry.grid(row=0, column=1, padx=5)

            gender_label = tk.Label(frame, text="Gender:", font=("Arial", 12))
            gender_label.grid(row=1, column=0, padx=5)

            gender_var = tk.StringVar(value="Select Gender")
            gender_menu = ttk.Combobox(frame, textvariable=gender_var, values=["Male", "Female", "Other"])
            gender_menu.grid(row=1, column=1, padx=5)

            age_label = tk.Label(frame, text="Age:", font=("Arial", 12))
            age_label.grid(row=2, column=0, padx=5)

            age_entry = tk.Entry(frame, font=("Arial", 12))
            age_entry.grid(row=2, column=1, padx=5)

            self.passenger_entries.append((name_entry, gender_var, age_entry))

        self.head_passenger_frame = tk.Frame(self.passenger_window)
        self.head_passenger_frame.pack(pady=20)

        tk.Label(self.head_passenger_frame, text="Head Passenger:", font=("Arial", 14)).grid(row=0, column=0, pady=5)
        tk.Label(self.head_passenger_frame, text="Name:", font=("Arial", 12)).grid(row=1, column=0, padx=5)
        head_name_entry = tk.Entry(self.head_passenger_frame, font=("Arial", 12))
        head_name_entry.grid(row=1, column=1, padx=5)

        tk.Label(self.head_passenger_frame, text="Mobile:", font=("Arial", 12)).grid(row=2, column=0, padx=5)
        head_mobile_entry = tk.Entry(self.head_passenger_frame, font=("Arial", 12))
        head_mobile_entry.grid(row=2, column=1, padx=5)

        tk.Label(self.head_passenger_frame, text="Email:", font=("Arial", 12)).grid(row=3, column=0, padx=5)
        head_email_entry = tk.Entry(self.head_passenger_frame, font=("Arial", 12))
        head_email_entry.grid(row=3, column=1, padx=5)

        self.head_passenger_details = (head_name_entry, head_mobile_entry, head_email_entry)

        tk.Button(self.passenger_window, text="Confirm", font=("Arial", 14), command=self.generate_upi_qr).pack(pady=20)

    def generate_upi_qr(self):
        """ Generate and display UPI QR code for payment. """
        qr_data = f"upi://pay?pa={self.upi_id}&pn=BusBooking&am={self.total_price}&cu=INR"
        qr = qrcode.make(qr_data)
        qr.save("upi_qr.png")

        qr_img = Image.open("upi_qr.png").resize((200, 200))
        qr_img = ImageTk.PhotoImage(qr_img)

        qr_window = tk.Toplevel(self.root)
        qr_window.title("QR Code Payment")
        qr_window.geometry("300x300")

        tk.Label(qr_window, image=qr_img).pack()
        tk.Button(qr_window, text="Payment Done", font=("Arial", 14), command=lambda: self.generate_ticket_pdf()).pack(
            pady=20)

        qr_window.mainloop()

    def generate_ticket_pdf(self):
        """ Generate the PDF ticket with passenger details. """
        # Define the file name and set the save path in the project folder
        save_path = os.path.join(os.getcwd(), "Bus_Ticket.pdf")

        pdf = FPDF()
        pdf.add_page()

        # Add a Unicode font (TrueType)
        font_path = os.path.join(os.getcwd(),
                                 r"replace with ur path of dejavu ttf")  # Ensure this file exists in your project directory
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", "", 12)

        pdf.cell(200, 10, txt=f"Route: {self.selected_route}", ln=True, align="L")
        pdf.cell(200, 10, txt=f"Date: {self.selected_date}", ln=True, align="L")
        pdf.cell(200, 10, txt=f"Seats: {', '.join(self.selected_seats)}", ln=True, align="L")
        pdf.cell(200, 10, txt=f"Total Price: ₹{self.total_price}", ln=True, align="L")

        pdf.ln(10)  # Line break
        pdf.cell(200, 10, txt="Passenger Details:", ln=True, align="L")
        pdf.ln(5)

        # Collecting the details of passengers
        self.passenger_details = []
        for i, (name_entry, gender_var, age_entry) in enumerate(self.passenger_entries, start=1):
            name = name_entry.get()
            gender = gender_var.get()
            age = age_entry.get()
            self.passenger_details.append((name, gender, age))

        head_name, head_mobile, head_email = [entry.get() for entry in self.head_passenger_details]

        pdf.cell(200, 10, txt=f"Head Passenger: {head_name}, Mobile: {head_mobile}, Email: {head_email}", ln=True,
                 align="L")
        pdf.ln(5)

        for i, details in enumerate(self.passenger_details, start=1):
            name, gender, age = details
            pdf.cell(200, 10, txt=f"Passenger {i}: {name}, Gender: {gender}, Age: {age}", ln=True, align="L")

        pdf.ln(10)  # Line break
        pdf.cell(200, 10, txt="Happy Journey!", ln=True, align="C")

        # Save the PDF to the specified path
        pdf.output(save_path)
        messagebox.showinfo("Ticket Generated", f"Your ticket has been saved to:\n{save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BusTicketBooking(root)
    root.mainloop()

