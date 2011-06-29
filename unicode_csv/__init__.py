# -*- coding: utf-8 -*-
# Взято полностью с
# http://docs.python.org/library/csv.html#examples
import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def str_or_buffer(self, x):
        return (type(x) is str) or (type(x) is buffer)

    def next(self):
        row = self.reader.next()
        return [unicode(i, 'utf-8') if self.str_or_buffer(i) else unicode(i) for i in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

#
# конец вырезки из документации по Питону
#

class calc(csv.excel):
    """
    Диалект-наследник csv.excel. Но поля помещаются в кавычки во всех случаях кроме числовых
    полей с целыми числами (при вещественных в российской традиции используется запятая,
    которая здесь служит для разделения полей, поэтому не помещать в кавычки вещественные
    числа не получается), полей с датами и пустых (!) полей. Окончание строки как в UNIX.
    """
    # TODO: Может это только под Linux так, а под Windows по-другому?
    quoting = csv.QUOTE_NONNUMERIC
    lineterminator = '\n'