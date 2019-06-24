from MoteinoConfig import SplitFlap
import time

def final_countdown():
        for i in range(60, -1, -5):
            SplitFlap.send("Disp", str(i).ljust(11, ' ') if i % 10 == 0 else str(i).rjust(11, ' '))
            time.sleep(5)

if __name__ == '__main__':
    final_countdown()