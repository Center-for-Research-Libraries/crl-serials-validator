class MarcFileReader():
    """
    Simple iterator for text-based MARC files (mrk files).
    Basic usage with a file name:

        mfr = MarcFileReader("/path/to/file")
        for record in mfr:
            [...]

    Basic usage with a file handle:

        with open("/path/to/file", "rb") as fh:
            mfr = MarcFileReader(fh)
            for record in mfr:
                [...]

    Usage for compatibility with old-style MarcFileReader:

        mfr = MarcFileReader("/path/to/file")
        while mfr.more_records is True:
            record = mfr.get_record()

    """

    def __init__(self, marc_target, allow_unicode_failure=False):
        """
        if allow_unicode_failure is set to True, process will fail with a line cannot be decoded via utf8 or latin-1
        """
        self.allow_unicode_failure = allow_unicode_failure
        self.record = ''
        self._establish_file_handle(marc_target)
        self._find_eof()
        # The below is for the get_record method
        self.more_records = True

    def __iter__(self):
        self.record = ''
        return self

    def __next__(self):
        self._get_next_record()
        return self.record

    def _establish_file_handle(self, marc_target):
        """Set file handle. Create it if input is a file location."""
        if hasattr(marc_target, "read") and callable(marc_target.read):
            self.file_handle = marc_target
        else:
            self.file_handle = open(marc_target, "rb")

    def _find_eof(self):
        """Find the file length before iteration starts, so we know when we reach the end."""
        self.file_handle.seek(0, 2)
        self.eof = self.file_handle.tell()
        self.file_handle.seek(0)

    def _get_next_record(self):
        """Glue all lines together until we reach a blank line."""
        self.record_list = []
        while True:
            try:
                binary_line = self.file_handle.readline()
            except ValueError:
                raise StopIteration
            try:
                line_str = binary_line.decode("utf8").rstrip()
            except UnicodeDecodeError:
                try:
                    line_str = binary_line.decode("latin-1").rstrip()
                except UnicodeDecodeError:
                    if self.allow_unicode_failure is True:
                        raise Exception("Unable to process line as UTF-8 or Latin-1")
                    continue
            if not line_str:
                if not self.record_list:
                    if self.file_handle.tell() >= self.eof:
                        self.file_handle.close()
                        self.more_records = False
                        raise StopIteration
                    continue
                self.record = "\n".join(self.record_list)
                return
            self.record_list.append(line_str)

    def get_record(self):
        """
        Get the next record, if you don't want to use the class as an iterator.
        """
        record = self.__next__()
        if self.file_handle.tell() >= self.eof:
            self.more_records = False
        return record
