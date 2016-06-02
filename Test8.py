import MoteinoPY as moteinopy


MoteinoStructs = {
    'GreenDude': "int Command;" + "byte Lights[7];" + "byte Temperature;",
    'SplitFlap': "int Command;" + "char Letters[11];" + "byte Temperature;"
}

MoteinoIDs = {
    'Base': 1,
    'GreenDude': 11,
    'SplitFlap': 101,
    'Stealth': 7,
    'TestDevice': 0
}


mynetwork = moteinopy.MoteinoNetwork('/dev/ttyUSB0',
                                     frequency=moteinopy.RF69_433MHZ,
                                     network_id=7,
                                     encryption_key="HugiBogiHugiBogi"
                                     )

SplitFlap = mynetwork.add_device(MoteinoIDs['SplitFlap'],
                                 MoteinoStructs['SplitFlap'],
                                 'SplitFlap')
SplitFlap.add_translation('Command',
                          ('Status', 99),
                          ('Disp', 10101),
                          ('ClearAll', 10102))
