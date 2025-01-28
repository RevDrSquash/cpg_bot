import os
import re
import pandas as pd

from difflib import SequenceMatcher

def extract_project_id(input_string):
    """
    Splits an input string into two parts based on a regex pattern that matches
    four digits followed by a '-' at the start of the string.

    Args:
        input_string (str): The input string to be processed.

    Returns:
        tuple: A tuple containing two strings:
               - The first string is the four digits if a match is found, otherwise an empty string.
               - The second string is the part of the input string after the '-' if a match is found, otherwise the entire input string.
    """
    # Define the regex pattern
    pattern = r"^(\d{4}) - (.+)$"
    
    # Search for the pattern in the input string
    match = re.match(pattern, input_string)
    
    if match:
        # Extract the four digits and the part after the '-'
        return match.group(1), match.group(2)
    else:
        # Return empty string and the full input string if no match is found
        return "", input_string

def extract_project_date(input_string):
    """
    Splits an input string into two parts based on a regex pattern that matches
    a date followed by a '-' at the start of the string.

    Args:
        input_string (str): The input string to be processed.

    Returns:
        tuple: A tuple containing two strings:
               - The first string is the date if a match is found, otherwise an empty string.
               - The second string is the part of the input string after the '-' if a match is found, otherwise the entire input string.
    """
    # Define the regex pattern
    pattern = r"^(\d{4}-\d{2}-\d{2}) - (.+)$"
    
    # Search for the pattern in the input string
    match = re.match(pattern, input_string)
    
    if match:
        # Extract the four digits and the part after the '-'
        return match.group(1), match.group(2)
    else:
        # Return empty string and the full input string if no match is found
        return "", input_string

def list_files_by_subdirectory(directory_path):
    """
    Returns a dictionary where the keys are subdirectories immediately under the given directory path,
    and the values are lists of the files under each subdirectory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        dict: A dictionary with subdirectories as keys and lists of files under each subdirectory as values.
              If the provided directory path does not exist or contains no subdirectories, returns an empty dictionary.
    """
    result = {}
    
    try:
        # List all entries in the given directory
        entries = os.listdir(directory_path)
        
        for entry in entries:
            entry_path = os.path.join(directory_path, entry)
            
            # Check if the entry is a subdirectory
            if not os.path.isdir(entry_path):
                continue
                
            result[entry] = []
            # List files in the subdirectory
            for __ , __ , files in os.walk(entry_path):
                result[entry] += files

        return result

    except FileNotFoundError:
        print(f"Error: The directory '{directory_path}' does not exist.")
        return {}
    except PermissionError:
        print(f"Error: Permission denied to access the directory '{directory_path}'.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

def filter_dataframe_by_similarity(df, column, target_strings, threshold=0.8):
    """
    Filters a Pandas DataFrame by checking the similarity of a column's values to a list of target strings.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        column (str): The name of the column to compare.
        target_strings (list): A list of target strings to compare against.
        threshold (float): The similarity ratio threshold (0 to 1).

    Returns:
        pd.DataFrame: A filtered DataFrame containing only rows with similarity above the threshold
                      for at least one target string.
    """
    def is_similar_to_any(value, targets, threshold):
        """
        Checks if the value is similar to any of the target strings.

        Args:
            value (str): The value to compare.
            targets (list): The list of target strings.
            threshold (float): The similarity ratio threshold.

        Returns:
            bool: True if the value is similar to at least one target string, False otherwise.
        """
        for target in targets:
            if SequenceMatcher(None, value, target).ratio() >= threshold:
                return True
        return False

    # Apply the similarity check and filter rows
    filtered_df = df[df[column].apply(lambda x: is_similar_to_any(x, target_strings, threshold))]

    return filtered_df

if __name__ == "__main__":
    root = "C:\\Users\\trist\\OneDrive - Sturgess Solutions\\CPG Archive"
    output = "C:\\Users\\trist\\OneDrive - Sturgess Solutions\\projects.csv"

    project_list = []

    entries = os.listdir(root)
    for entry in entries:
        entry_path = os.path.join(root, entry)
            
        # Check if the entry is a subdirectory
        if not os.path.isdir(entry_path):
            continue
        
        subdir_files = list_files_by_subdirectory(entry_path)
        
        for subdir in subdir_files:
            project_id, project_name = extract_project_id(subdir)
            project_date, project_name = extract_project_date(project_name)
            project_list.append( (project_name, project_id, entry, " ".join(subdir_files[subdir])) )

    df = pd.DataFrame.from_records(project_list, columns=['Project Name', 'Project ID', 'Year', 'Files'])
    # df.to_csv(output, index=False)

    df = pd.read_csv('E:\\dev\\cpg_bot\\cpg_bot\\data\\projects.csv', dtype={'Project Name': str, 'Project ID': str, 'Year': str, 'Files': str}, keep_default_na=False)

    # print( df[ df['Year'] == '2023' ] )
    # print( df[ df['Project Name'] == 'Kamloops Health Centre' ] )

    test_names = ["City of Burnaby Archive Strategy", "Kamloops Health Centre"]

    df = filter_dataframe_by_similarity( df, 'Project Name', test_names )
    print(df)

    # print( df[ df['Project Name'].isin(test_names) ].to_json(index=False, orient="records") )
    # [[ 'Project Name', 'Project ID', 'Year' ]]
