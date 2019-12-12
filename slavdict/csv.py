import csv

class calc(csv.excel):
    """ Диалект-наследник csv.excel.  """
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\r\n'
