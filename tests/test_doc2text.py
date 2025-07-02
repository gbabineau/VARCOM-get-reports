"""Unit tests for the doc2text module."""

import pytest
from docx import Document, opc
from integration_test.doc2text import extract_text_from_docx, _parse_arguments


@pytest.fixture
def create_docx_file(tmp_path):
    """Fixture to create a temporary .docx file for testing."""

    def _create_docx_file(filename, paragraphs):
        file_path = tmp_path / filename
        doc = Document()
        for paragraph in paragraphs:
            doc.add_paragraph(paragraph)
        doc.save(file_path)
        return file_path

    return _create_docx_file


def test_extract_text_from_docx_success(create_docx_file, tmp_path):
    """Test successful extraction of text from a .docx file."""
    input_file = create_docx_file(
        "test.docx", ["Hello, world!", "This is a test."]
    )
    output_file = tmp_path / "output.txt"

    extract_text_from_docx(str(input_file), str(output_file))

    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "Hello, world!\nThis is a test."


def test_extract_text_from_docx_file_not_found(tmp_path):
    """Test handling of a non-existent input file."""
    input_file = tmp_path / "non_existent.docx"
    output_file = tmp_path / "output.txt"

    with pytest.raises(opc.exceptions.PackageNotFoundError):
        extract_text_from_docx(str(input_file), str(output_file))


def test_parse_arguments(monkeypatch):
    """Test _parse_arguments with valid arguments."""
    test_args = [
        "script_name",
        "--input",
        "test.docx",
        "--output",
        "output.txt",
    ]
    monkeypatch.setattr("sys.argv", test_args)

    args = _parse_arguments()

    assert args.input == "test.docx"
    assert args.output == "output.txt"


def test_parse_arguments_missing_input(monkeypatch):
    """Test _parse_arguments when --input is missing."""
    test_args = ["script_name", "--output", "output.txt"]
    monkeypatch.setattr("sys.argv", test_args)

    with pytest.raises(SystemExit):
        _parse_arguments()


def test_parse_arguments_missing_output(monkeypatch):
    """Test _parse_arguments when --output is missing."""
    test_args = ["script_name", "--input", "test.docx"]
    monkeypatch.setattr("sys.argv", test_args)

    with pytest.raises(SystemExit):
        _parse_arguments()
