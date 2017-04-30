from moteinopy import MoteinoNetwork

mynetwork = MoteinoNetwork("COM7",
                           network_id=7,
                           encryption_key="HugiBogiHugiBogi",
                           base_id=41,
                           init_base=False)

Pope = mynetwork.add_node(1, "int Command;int Number;", "Pope")
Pope.send(99)

