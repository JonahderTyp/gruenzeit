import os


def read_files_recursively(directory, file_types):
    file_contents = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(file_types):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents.append(
                        f'File: {file_path}\n\n{f.read()}\n\n{"-"*80}\n\n')
    return file_contents


def save_to_file(output_file, content_list):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(content_list)


if __name__ == "__main__":
    # directory = input("Enter the directory path: ")
    # output_file = input("Enter the output file name (with .txt extension): ")
    directory = "gruenzeit"
    output_file = "chatgpt.txt"
    file_types = ('.py', '.html')

    contents = read_files_recursively(directory, file_types)
    save_to_file(output_file, contents)

    print(f"Contents of .py and .html files have been saved to {output_file}")
