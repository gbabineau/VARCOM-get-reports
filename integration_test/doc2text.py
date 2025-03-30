""" Function to convert .docx files to very simple plain text files to test that
    expected text is in docx files. """
import argparse
from docx import Document

def extract_text_from_docx(input_file, output_file):
    """
    Extracts text from a .docx file and writes it to a specified output file.

    Args:
        input_file (str): The path to the input .docx file.
        output_file (str): The path to the output file where the extracted text will be saved.

    Returns:
        None

    Raises:
        FileNotFoundError: If the input file does not exist.
        IOError: If there is an error reading the input file or writing to the output file.

    Example:
        extract_text_from_docx("example.docx", "output.txt")
    """
    try:
        # Load the .docx file
        doc = Document(input_file)
        # Extract all text
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        # Write the text to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text successfully extracted to {output_file}")
    except (FileNotFoundError, IOError) as e:
        print(f"An error occurred: {e}")

def _parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - input (str): The input .docx filename (required).
            - output (str): The output text filename (required).
    """
    parser = argparse.ArgumentParser(
        description="Convert .docx file to plain text."
    )
    parser.add_argument("--input", required=True, help="Input .docx filename")
    parser.add_argument("--output", required=True, help="Output text filename")
    return parser.parse_args()


def main():
    """
    Main function to parse command-line arguments and extract text from a DOCX file.
    This function retrieves input and output file paths from the command-line arguments,
    then processes the input DOCX file to extract its text content and saves it to the
    specified output file.
    Command-line arguments:
        --input: Path to the input DOCX file.
        --output: Path to the output file where the extracted text will be saved.
    """

    args = _parse_arguments()

    extract_text_from_docx(args.input, args.output)

if __name__ == "__main__":
    main()