import csv
import os
from ics import Calendar

# --- Configuration ---
# Set your input and output file names here
ICS_FILE_NAME = 'calendar.ics'
CSV_FILE_NAME = 'calendar.csv'
# ---------------------

def convert_ics_to_csv(ics_file, csv_file):
    """
    Reads an iCalendar (.ics) file and writes its events to a CSV file.
    """
    print(f"Starting conversion of '{ics_file}'...")

    # Check if the input file exists
    if not os.path.exists(ics_file):
        print(f"Error: Input file not found at '{ics_file}'")
        print("Please make sure the file is in the same directory as the script.")
        return

    try:
        # Open and read the .ics file
        with open(ics_file, 'r', encoding='utf-8') as f:
            calendar_content = f.read()
        
        # Parse the calendar content
        c = Calendar(calendar_content)
        
        print(f"Found {len(c.events)} events in the calendar.")

        # Open the .csv file for writing
        with open(csv_file, 'w', newline='', encoding='utf-8') as f_csv:
            # Define the CSV header
            fieldnames = ['Subject', 'Start Time', 'End Time', 'Description', 'Location', 'All Day']
            writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()
            
            # Iterate through each event in the calendar
            for event in c.events:
                # Write the event data as a row in the CSV
                writer.writerow({
                    'Subject': event.name or '',
                    'Start Time': event.begin.isoformat() if event.begin else '',
                    'End Time': event.end.isoformat() if event.end else '',
                    # Replace newlines in description to keep CSV formatting clean
                    'Description': (event.description or '').replace('\n', ' | '),
                    'Location': event.location or '',
                    'All Day': event.all_day
                })

        print(f"\nSuccessfully converted calendar and saved to '{csv_file}'.")

    except Exception as e:
        print(f"\nAn error occurred during conversion:")
        print(f"{e}")
        print("Please ensure the .ics file is valid and not corrupted.")

# --- Run the conversion ---
if __name__ == "__main__":
    convert_ics_to_csv(ICS_FILE_NAME, CSV_FILE_NAME)