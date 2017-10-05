import zipfile
import cStringIO


class InMemoryZip(object):
    def __init__(self):
        self.in_memory_zip = cStringIO.StringIO()
        self.info = cStringIO.StringIO()

    def append(self, filename_in_zip, file_contents):
        '''Appends a file with name
        filename_in_zip and contents of
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a",
                             zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        # FIXME: use instead:
        # filename_in_zip = filename_in_zip.encode('utf-8')
        # and change dsodoo accordingly
        zf.writestr(
            filename_in_zip.encode('utf-8').decode('ascii', 'ignore'),
            file_contents
        )

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

    def write_info(self, lines):
        # FIXME: use instead:
        # ulines = [el.encode('utf-8') for el in lines]
        # and change dsodoo accordingly
        ulines = [
            el.encode('utf-8').decode('ascii', 'ignore') for el in lines
        ]
        self.info.writelines(ulines)

    def get_info(self):
        return self.info.getvalue()

    def close(self):
        self.in_memory_zip.close()
        self.info.close()


class VerifyZip(object):
    def __init__(self):
        pass

#     def extract_to_tmp(self, zip_path):
#         """
#         Extract content of zip file to tmp folder
#         return list of files
#         """
#         result = []
#         if os.path.isfile(zip_path):
#             filezip = ZipFile(zip_path)
#             current_tmp_folder = os.path.join(TEMP_FOLDER, DEFAULT_TOS_WORKING_PATH)
#             filezip.extractall(current_tmp_folder)
#             for name in filezip.namelist():
#                 current_file_path = os.path.join(current_tmp_folder, name)
#                 if os.path.isfile(current_file_path):
#                     result.append({
#                               'name': '%s' % (name),
#                               'path': '%s' % (current_file_path)
#                               }
#                     )
#         return result
