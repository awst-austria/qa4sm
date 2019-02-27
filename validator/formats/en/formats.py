#DATETIME_FORMAT = 'Y-m-d H:i:s e'
DATETIME_FORMAT = 'N j, Y, P e'
DATETIME_INPUT_FORMATS = [# ISO
                          '%Y-%m-%d %H:%M:%S',
                          '%Y-%m-%d %H:%M:%S.%f',
                          '%Y-%m-%d %H:%M',
                          '%Y-%m-%d',

                          # UK, Italy, France, ...
                          '%Y/%m/%d',
                          '%d/%m/%Y %H:%M:%S',
                          '%d/%m/%Y %H:%M:%S.%f',
                          '%d/%m/%Y %H:%M',
                          '%d/%m/%Y',
                          '%d/%m/%y %H:%M:%S',
                          '%d/%m/%y %H:%M:%S.%f',
                          '%d/%m/%y %H:%M',
                          '%d/%m/%y',

                          # Germany, Austria, Switzerland, ...
                          '%d.%m.%Y %H:%M:%S',
                          '%d.%m.%Y %H:%M:%S.%f',
                          '%d.%m.%Y %H:%M',
                          '%d.%m.%Y',
                          '%d.%m.%y %H:%M:%S',
                          '%d.%m.%y %H:%M:%S.%f',
                          '%d.%m.%y %H:%M',
                          '%d.%m.%y',

                          # Netherlands, ...
                          '%d-%m-%Y %H:%M:%S',
                          '%d-%m-%Y %H:%M:%S.%f',
                          '%d-%m-%Y %H:%M',
                          '%d-%m-%Y',
                          '%d-%m-%y %H:%M:%S',
                          '%d-%m-%y %H:%M:%S.%f',
                          '%d-%m-%y %H:%M',
                          '%d-%m-%y',

                          # Hungary
                          '%Y.%m.%d %H:%M:%S',
                          '%Y.%m.%d %H:%M:%S.%f',
                          '%Y.%m.%d %H:%M',
                          '%Y.%m.%d',
                          ]
