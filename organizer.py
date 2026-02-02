# organizer.py

# --- NEW: Module-level Docstring ---
"""
Bulk File Organizer

This script provides a command-line utility to organize files within a specified
directory into subdirectories based on their file type. It supports a dry-run
mode for previewing changes, logs all operations to a file, and allows for
custom organization rules via an external 'config.json' file.
"""

# Standard libary import
import argparse
import json
import pathlib
import shutil
import logging
import sys

# Third party import
from tqdm import tqdm

# FILE_TYPE_MAP = {
#      "Images": ['.jpeg', '.jpg', '.png', '.gif', '.svg',],
#     "Documents": ['.pdf', '.docx', '.txt', '.pptx', '.xlsx'],
#     "Audio": ['.mp3', '.wav', '.aac'],
#     "Video": ['.mp4', '.mov', '.avi', '.mkv'],
#     "Archives": ['.zip', '.rar', '.tar', '.gz'],
#     "Other" : []
# }


def load_config(config_path: pathlib.Path) -> dict:
    # --- NEW: Function Docstring ---
    """
    Loads and validates the organization rules from a JSON configuration file.

    This function attempts to open and parse the specified JSON file. It handles
    potential FileNotFoundError and json.JSONDecodeError, logging helpful
    error messages and exiting the script if the configuration is invalid or missing.

    Args:
        config_path (pathlib.Path): The path to the config.json file.

    Returns:
        dict: A dictionary containing the file type mappings.
    """
    try:

        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)
            return config_data
    except FileNotFoundError:
        logging.error(f"Configuration file not found at: {config_path}")
        logging.error(
            "Please make sure 'config.json' exists in the same directory as the script."
        )
        return 1
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing configuration file: {config_path}")
        logging.error(
            f"The file contains invalid JSON. Please check the syntax. Details: {e}"
        )
        sys.exit(1)


def process_file(
    file_path: pathlib.Path,
    source_path: pathlib.Path,
    file_type_map: dict,
    dry_run: bool,
):
    # --- NEW: Function Docstring ---
    """
    Processes a single file: determines its destination and moves it or simulates the move.

    This function is the core worker of the organization process. It finds the
    appropriate category for the file based on its extension, handles potential
    filename conflicts by renaming the file if necessary, and performs the
    actual move operation with error handling.

    Args:
        file_path (pathlib.Path): The path to the file to be processed.
        source_path (pathlib.Path): The root directory where organization is happening.
        file_type_map (dict): The dictionary of organization rules.
        dry_run (bool): If True, simulate the file move; otherwise, perform it.
    """
    file_extension = file_path.suffix.lower()

    destination_folder_name = "Other"
    for category, extensions in file_type_map.items():
        if file_extension in extensions:
            destination_folder_name = category
            break

    destination_dir = source_path / destination_folder_name

    if dry_run:
        destination_file_path = destination_dir / file_path.name
        logging.info(
            f"[DRY RUN] Would move '{file_path.name}' -> '{destination_file_path}'"
        )
    else:
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination_file_path = destination_dir / file_path.name
        counter = 1
        while destination_file_path.exists():
            logging.warning(f"Conflict: '{destination_file_path}' already exists.")
            new_filename = f"{file_path.stem} ({counter}){file_path.suffix}"
            destination_file_path = destination_dir / new_filename
            counter += 1

        try:
            shutil.move(file_path, destination_file_path)
            logging.info(f"Moved: '{file_path.name}' -> '{destination_file_path}'")
        except PermissionError as e:
            logging.error(f"Could not move '{file_path.name}'. Error: {e}")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while moving '{file_path.name}'. Error: {e}"
            )


# ... (imports and load_config function) ...


def organize_directory(source_path: pathlib.Path, dry_run: bool, file_type_map: dict):
    # --- NEW: Function Docstring ---
    """
    Orchestrates the file organization process for a given directory.

    This function serves as the main entry point for the organization logic.
    It announces the operational mode (dry run or live), discovers all files
    in the source directory, and then delegates the processing of each file
    to the process_file function.

    Args:
        source_path (pathlib.Path): The directory to be organized.
        dry_run (bool): If True, simulate without moving files.
        file_type_map (dict): A dictionary mapping folder names to file extensions.
    """

    # --- RESPONSIBILITY 1: Initial Setup & User Communication ---
    # This block announces the start of the operation and which mode is active.
    # It sets the user's expectations.
    logging.info(f"Starting to organise directory:{source_path}")
    if dry_run:
        logging.info(" --DRY RUN MODE ENABLE: No files will be moved")
    else:
        logging.warning("-- LIVE RUN MODE ENABLE : Files system changeswill be made--")

    # --- RESPONSIBILITY 2: File Discovery ---
    # This part scans the source directory and builds a list of all the files
    # that need to be processed. It separates discovery from processing.
    files_to_process = [item for item in source_path.iterdir() if item.is_file()]
    for item in tqdm(files_to_process, desc="Organizing Files"):
        # --- SUB-RESPONSIBILITY 3a: Rule Matching ---
        # This nested loop determines the correct destination folder for a single file
        # based on the configuration map.
        file_extention = item.suffix
        # print(f" Found file :{item.name}, Extention : {file_extention}")
        destination_folder_name = "Other"
        for category, extension in file_type_map.items():
            if file_extention in extension:
                destination_folder_name = category
                break

        destination_dir = source_path / destination_folder_name

        # --- SUB-RESPONSIBILITY 3b: Action (Simulation or Execution) ---
        # This is the core action block. It's a large conditional that handles
        # either the dry-run simulation or the live-run file operations. This entire
        # block is a prime candidate for its own function.
        if dry_run:
            destination_file_path = destination_dir / item.name
            logging.info(
                f"[ DRY RUN ] Would move '{item.name}' -> '{destination_file_path}' "
            )
        else:
            # All of this logic—creating the directory, resolving name conflicts,
            # and moving the file with error handling—is about processing a *single file*.
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination_file_path = destination_dir / item.name

            counter = 1
            while destination_file_path.exists():
                logging.warning(f"Conflict: '{destination_file_path}'already exists.")
                new_filename = f"{item.stem} ({counter}){item.suffix}"
                destination_file_path = destination_dir / new_filename
                counter += 1

            try:
                shutil.move(item, destination_file_path)
                logging.info(
                    f"Moved : '{item.name}' -> Destination : '{destination_file_path}'"
                )
            except (FileExistsError, PermissionError) as e:
                logging.error(f"Could not move '{item.name}'. Error: {e} ")
            except Exception as e:
                logging.error(
                    f"An unexpected error occured while moving '{item.name}'. Error : {e} "
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Organize filein a directory by its type. ",
        epilog="Example: python organizer.py /path/to/downloads",
    )
    parser.add_argument(
        "source_directory", help="The path of the directory you want to organise"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the organization without moving files.",
    )

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("organizer.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    config_file_path = pathlib.Path(__file__).parent / "config.json"
    file_type_map_from_config = load_config(config_file_path)

    source_path = pathlib.Path(args.source_directory)
    if not source_path.is_dir():
        logging.error(
            f"Error : The path '{source_path}' dose not exist or not a directory"
        )
        sys.exit(1)
    organize_directory(source_path, args.dry_run, file_type_map_from_config)
