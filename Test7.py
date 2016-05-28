import MoteinoPY as moteinopy

<<<<<<< HEAD
mynetwork = moteinopy.MoteinoNetwork('COM5',
=======
mynetwork = moteinopy.MoteinoNetwork('/dev/ttyUSB0',
>>>>>>> dbc1f49edfe2a0502a9fb566a2202a97d9249efb
                                     frequency=moteinopy.RF69_433MHZ,
                                     network_id=7,
                                     encryption_key="HugiBogiHugiBogi"
                                     )

GreenDude = mynetwork.add_device(11,  "unsigned int Command;byte Lights[7];byte Temperature;", "GreenDude")

GreenDude.add_translation('Command',
                          ('Status', 99),
                          ('Disp', 1101),
                          ('GiveTalkingPillow', 42),
                          ('TakeAwayTalkingPillow', 43),
                          ('SetPassCode', 1102),)
