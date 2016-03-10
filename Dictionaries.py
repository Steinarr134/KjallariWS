

EventIDs = {
    'Test1': 1,
    'Execute': 0,
    'Test2': 2,
    'RecievedFromMoteinoNetwork': 100,
}

MoteinoCommands = {
    'CorrectPasscode': 25,
    'Status': 99,
    'Test1': 1,
    'Test2': 2,
    'AckRecieved': 234,
    'NoAckRecieved': 235,
}

MoteinoIDs = {
    'Base': 1,
    'GreenDude': 11,
    'SegulBand': 10,
    'Stealth': 7,
    'TestDevice': 0
}

inv_MoteinoIDs = {v: k for k, v in MoteinoIDs.items()}
