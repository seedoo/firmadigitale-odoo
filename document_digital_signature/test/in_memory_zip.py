import zipfile
import cStringIO


class InMemoryZip(object):
    def __init__(self):
        # Create the in-memory file-like object
        self.in_memory_zip = cStringIO.StringIO()

    def append(self, filename_in_zip, file_contents):
        '''Appends a file with name
        filename_in_zip and contents of
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a",
                             zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0

        return self

    def read(self):
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writetofile(self, filename):
        '''Writes the in-memory zip to a file.'''
        f = file(filename, "w")
        f.write(self.read())
        f.close()

    def get_txt(self):
        output = cStringIO.StringIO()
        output.writelines(['First line.\n', 'Second line.\n'])
        return output.getvalue()

    def get_pdf(self):
        with open('modello.pdf') as pdf:
            return pdf.read()


if __name__ == "__main__":
    # Run a test
    imz = InMemoryZip()
    imz.append("test.txt", imz.get_txt()).\
        append("test_modello.pdf", imz.get_pdf())
    imz.writetofile("test.zip")
