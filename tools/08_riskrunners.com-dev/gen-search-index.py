import json
import os
from bs4 import BeautifulSoup
import re

# Define the directory containing the HTML files ('.' means the current directory)
html_directory = '.'
# Define the output filename for the search index
output_filename = 'search-index.json'
# Define the file to exclude from indexing
exclude_file = '000_index.html' # Or whatever your main index file is named

# Initialize an empty list to store data from all files
all_search_data = []

# Helper function to clean text
def clean_text(text):
    # Remove leading/trailing whitespace and excess internal whitespace
    return ' '.join(text.split()).strip()

# --- Define the extraction logic as a function ---
def extract_data_from_html(html_content, source_filename):
    """Extracts specific data points from a single HTML content string."""
    soup = BeautifulSoup(html_content, 'html.parser')
    file_search_data = [] # Data specific to this file

    print(f"Processing: {source_filename}")

    # --- Extract Industries, Exposures, Event Codes ---
    sections_to_extract = {
        'industry': 'Industries',
        'exposure': 'Exposures',
        'event_code': 'Event Codes'
    }

    for section_id, section_name in sections_to_extract.items():
        header_tag = soup.find('th', id=section_id)
        if header_tag:
            table = header_tag.find_parent('table')
            if table:
                items = table.select('tbody tr td')
                for item_tag in items:
                    item_text = clean_text(item_tag.get_text())
                    if item_text:
                        file_search_data.append({
                            "title": item_text,
                            "content": f"{section_name}: {item_text}",
                            "url": f"{source_filename}#{section_id}" # Link to the section header in this file
                        })
            else:
                 print(f"  Warning: Could not find table for section with id='{section_id}' in {source_filename}")
        else:
             print(f"  Warning: Could not find section header with id='{section_id}' in {source_filename}")

    # --- Extract Wiki Summaries ---
    wiki_header = soup.find('th', id='wiki')
    if wiki_header:
        wiki_table = wiki_header.find_parent('table')
        if wiki_table:
            wiki_rows = wiki_table.select('tbody tr')
            for row in wiki_rows:
                cols = row.find_all('td')
                if len(cols) >= 2: # Expecting at least two columns
                    link_col = cols[0]
                    summary_col = cols[1] # Assuming summary is the second column

                    link_tag = link_col.find('a')
                    if link_tag:
                        url = link_tag.get('href')
                        title = clean_text(link_tag.get_text())
                        summary = clean_text(summary_col.get_text())

                        if url and title and summary:
                             file_search_data.append({
                                "title": title,
                                "content": summary,
                                # Use the external wiki URL as the primary link
                                "url": url
                                # Optional: Add source file for context if needed: "source_file": source_filename
                            })
        else:
             print(f"  Warning: Could not find Wiki table in {source_filename}.")
    else:
         print(f"  Warning: Could not find Wiki header with id='wiki' in {source_filename}.")


    # --- Extract Blue Words from Risk Factors ---
    risk_factors_header = soup.find('th', id='risk_factors')
    if risk_factors_header:
        risk_factors_table = risk_factors_header.find_parent('table')
        if risk_factors_table:
            risk_factor_rows = risk_factors_table.select('tbody tr')
            for row in risk_factor_rows:
                cell = row.find('td')
                if cell:
                    blue_phrases = cell.find_all('font', color='blue')
                    # Get the full text of the cell, removing the blue font tags for clean content
                    # Use get_text(separator=' ', strip=True) to handle nested tags better
                    full_cell_text_raw = cell.get_text(separator=' ', strip=True)
                    # Clean up potential extra whitespace introduced by get_text(separator)
                    full_cell_text = clean_text(full_cell_text_raw)


                    for blue_tag in blue_phrases:
                        blue_text = clean_text(blue_tag.get_text())
                        if blue_text:
                            file_search_data.append({
                                # Use the blue text as the title
                                "title": blue_text,
                                # Use the cleaned full cell text as content for context
                                "content": full_cell_text,
                                # Link to the Risk Factors section in this file
                                "url": f"{source_filename}#risk_factors"
                            })
        else:
             print(f"  Warning: Could not find Risk Factors table in {source_filename}.")
    else:
         print(f"  Warning: Could not find Risk Factors header with id='risk_factors' in {source_filename}.")

    return file_search_data

# --- Iterate through files and process ---
try:
    # Get list of all files in the directory
    for filename in os.listdir(html_directory):
        # Construct full path
        filepath = os.path.join(html_directory, filename)

        # Check if it's a file, ends with .html, and is not the excluded file
        if os.path.isfile(filepath) and filename.lower().endswith('.html') and filename != exclude_file:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Extract data from the current file
                file_data = extract_data_from_html(html_content, filename)
                # Add the extracted data to the main list
                all_search_data.extend(file_data)

            except Exception as e:
                print(f"  Error processing file {filename}: {e}")

except Exception as e:
    print(f"Error accessing directory {html_directory}: {e}")


# --- Write the combined data to search-index.json ---
if all_search_data:
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_search_data, f, indent=2, ensure_ascii=False)

        print(f"\nSearch index generated successfully: {output_filename}")
        print(f"Total number of items indexed from {len(os.listdir(html_directory))-1} files: {len(all_search_data)}") # Subtract 1 for the index file

    except Exception as e:
        print(f"Error writing search index file {output_filename}: {e}")
else:
    print("\nNo data extracted or no HTML files found (excluding the index). No search index file was created.")