import os
from os import walk
from os import path
import zstandard as zstd
import argparse


class JsonValidator:

    #checks if a json is empty
    def isJsonEmpty(self,content):
        return content is None or content == '"[]"'

        

    #uses the zstandard libary to decompress the json
    def uncompressJson(self,compressed_content):
        decompressor = zstd.ZstdDecompressor()
        decompressed_content = decompressor.decompress(compressed_content)
        return decompressed_content.decode("utf-8")

    #reads a file and returns the content
    def readFile(self, path,compressed=True):
        
        if compressed:
            with open(path,"rb") as f:
                content = f.read()
                return content
        else:
            with open(path,"r",encoding="utf-8") as f:
                content = f.read()
                return content


    #walks thorugh a directory and any sub dirs ,before validatiing if they are empty. If they are empty they get removed
    def proccessEmptyJsonFromSubDir(self,path,deCompression=True,delete=True):
        jsonFileCounter = 0
        jsonEmptyCounter = 0
        for (dirpath,dirnames,filenames) in walk(path):
            for filename in filenames:
                if filename.endswith(".json"):
                    jsonFileCounter += 1
                    fullPath = os.path.join(dirpath,filename)
                    fileContent  = self.readFile(fullPath,compressed=deCompression)

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
    jValidator = JsonValidator()
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",required=True,help="The parent directory containing all the files and subfolders")
    parser.add_argument("-dc","--decompress",required=False,default=True,type=bool,help="Do the files require decompression before validation")
    parser.add_argument("--no_delete",action="store_false",dest="delete",default=True,help="Do not delete empty jsons")

    args = parser.parse_args()
    jValidator.proccessEmptyJsonFromSubDir(args.input,deCompression=args.decompress,delete=args.delete)

if __name__ == "__main__":
    main()