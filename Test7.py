import MoteinoPY as moteinopy

mynetwork = moteinopy.MoteinoNetwork('/dev/ttyUSB0',
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
