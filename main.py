import os
import subprocess
import shutil

from datetime import datetime, timedelta


INPUT_FOLDER = './input'
OUTPUT_FOLDER = './output'
ERROR_FOLDER = './errors'
LOG_FILE = './errors.txt'

TIME_ZONE = 5


class DateNotFoundException(Exception):
    pass


def get_creation_time(filepath):
    cmd = f"mdls '{filepath}'"
    output = subprocess.check_output(cmd, shell=True)
    lines = output.decode("utf-8").split("\n")

    for line in lines:
        if "kMDItemContentCreationDate" in line:
            datetime_str = line.split("= ")[1]
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S +0000")

    raise DateNotFoundException(f"No EXIF date taken found for file '{filepath}'")


def check_if_file_exists_in_folder(file_name, folder):
    for file in os.listdir(folder):
        name_wo_extension = os.path.splitext(file)[0]
        if file_name == name_wo_extension:
            return True
    return False


def get_name_from_creation_time(creation_time: datetime):
    extra_seconds = 0
    while True:
        local_time = creation_time + timedelta(hours=TIME_ZONE, seconds=extra_seconds)
        name = local_time.strftime('%Y%m%d_%H%M%S')

        if not check_if_file_exists_in_folder(name, OUTPUT_FOLDER):
            return name

        extra_seconds += 1


def handle_file(file):
    print(f'Handling file "{file}"')

    creation_time = get_creation_time(file)
    new_name = get_name_from_creation_time(creation_time)

    cur_file_extension = os.path.splitext(file)[1]

    shutil.copy(file, os.path.join(OUTPUT_FOLDER, new_name) + cur_file_extension.lower())


def log_error(error: Exception):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(str(error) + '\n\n')


def convert_photo_and_video(folder: str):
    for file_name in os.listdir(folder):
        file = os.path.join(folder, file_name)

        if os.path.isdir(file):
            convert_photo_and_video(file)
        else:
            try:
                handle_file(file)
            except Exception as error:
                log_error(error)
                shutil.copy(file, os.path.join(ERROR_FOLDER, file_name))


def main():
    convert_photo_and_video(INPUT_FOLDER)


if __name__ == '__main__':
    main()
