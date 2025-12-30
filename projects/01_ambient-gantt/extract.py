import json

def extract_and_write_transcript(json_file_path, output_file_path):
    """
    Extracts the combined transcript from a JSON file and writes it to a text file.

    Args:
        json_file_path (str): The path to the input JSON file.
        output_file_path (str): The path to the output text file.

    Returns:
        str: A success message or an error message.
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        full_transcript = []
        if "results" in data:
            for result in data["results"]:
                if "alternatives" in result and len(result["alternatives"]) > 0:
                    # Check if 'transcript' key exists in the first alternative
                    if "transcript" in result["alternatives"][0]:
                        full_transcript.append(result["alternatives"][0]["transcript"])
                    else:
                        print(f"Warning: 'transcript' key not found in an alternative for result: {result.get('resultEndTime', 'Unknown End Time')}. Skipping this segment.")
                else:
                    print(f"Warning: No alternatives found for a result ending at {result.get('resultEndTime', 'Unknown End Time')}. Skipping this segment.")
            
            transcript_content = " ".join(full_transcript)

            with open(output_file_path, 'w') as outfile:
                outfile.write(transcript_content)
            
            if full_transcript:
                return f"Transcript successfully extracted from '{json_file_path}' and written to '{output_file_path}'."
            else:
                return f"No transcript content was extracted from '{json_file_path}'. Check the JSON structure."
        else:
            return "Error: 'results' key not found in the JSON data. No transcript could be extracted."

    except FileNotFoundError:
        return f"Error: The file '{json_file_path}' was not found. Please make sure it exists."
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON from the file '{json_file_path}'. Please ensure it's valid JSON."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- How to use the script ---
if __name__ == "__main__":
    json_input_file = "transcript.json"
    text_output_file = "transcript.txt"
    
    message = extract_and_write_transcript(json_input_file, text_output_file)
    print(message)