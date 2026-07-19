"""
JSON Validator for ZSSK Data Collection.

Validates and removes empty JSON files from the data collection directory.
"""
import os
from os import walk
from os import path
import zstandard as zstd
import argparse


class JsonValidator:
    """
    Validates and cleans up compressed JSON files.
    
    Provides methods to check if JSON content is empty, decompress
    zstandard-compressed files, and remove empty files from disk.
    """

    def isJsonEmpty(self, content):
        """
        Check if JSON content is empty.
        
        Args:
            content: JSON string to check.
        
        Returns:
            bool: True if content is None or empty array '[]'.
        """
        return content is None or content == '"[]"'

    def uncompressJson(self, compressed_content):
        """
        Decompress zstandard-compressed JSON content.
        
        Args:
            compressed_content (bytes): Compressed data.
        
        Returns:
            str: Decompressed JSON string.
        """
        decompressor = zstd.ZstdDecompressor()
        decompressed_content = decompressor.decompress(compressed_content)
        return decompressed_content.decode("utf-8")

    def readFile(self, path, compressed=True):
        """
        Read a file from disk.
        
        Args:
            path (str): Path to the file.
            compressed (bool): If True, read in binary mode; otherwise read as text.
        
        Returns:
            bytes or str: File content.
        """
        if compressed:
            with open(path, "rb") as f:
                content = f.read()
                return content
        else:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                return content

    def proccessEmptyJsonFromSubDir(self, path, deCompression=True, delete=True):
        """
        Walk through a directory and validate/remove empty JSON files.
        
        Args:
            path (str): Parent directory to process.
            deCompression (bool): Decompress files before validation. Default: True.
            delete (bool): Remove empty files. Default: True.
        """
        jsonFileCounter = 0
        jsonEmptyCounter = 0
        for (dirpath, dirnames, filenames) in walk(path):
            for filename in filenames:
                if filename.endswith(".json"):
                    jsonFileCounter += 1
                    fullPath = os.path.join(dirpath, filename)
                    fileContent = self.readFile(fullPath, compressed=deCompression)

                    if deCompression:
                        fileContent = self.uncompressJson(compressed_content=fileContent)
                    if self.isJsonEmpty(fileContent):
                        jsonEmptyCounter += 1
                        print(f"{fullPath} was found to be empty!")

                        if delete:
                            os.remove(fullPath)
                            print(f"Removed {filename}")
                        else:
                            print(f"Would have removed {filename} but deletion is disabled")
        print(f"In total {jsonEmptyCounter}/{jsonFileCounter} were found to be empty!")

def main():
    """
    Command-line entry point for JSON validation.
    
    Parses arguments and runs the validator on the specified directory.
    """
    jValidator = JsonValidator()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="The parent directory containing all the files and subfolders")
    parser.add_argument("-dc", "--decompress", required=False, default=True, type=bool, help="Do the files require decompression before validation")
    parser.add_argument("--no_delete", action="store_false", dest="delete", default=True, help="Do not delete empty jsons")

    args = parser.parse_args()
    jValidator.proccessEmptyJsonFromSubDir(args.input, deCompression=args.decompress, delete=args.delete)

if __name__ == "__main__":
    main()
