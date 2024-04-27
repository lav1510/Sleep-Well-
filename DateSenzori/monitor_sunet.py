from gpiozero import DigitalInputDevice
import time
import threading

class MonitorSunet:
    def __init__(self, stare: threading.Event, modul_microfon: DigitalInputDevice):
        if not isinstance(stare, threading.Event):
            raise TypeError("Parametrul 'stare' trebuie sa fie obiect de tipul threading.Event!")

        if not isinstance(modul_microfon, DigitalInputDevice):
            raise TypeError("Parametrul 'modul_microfon' trebuie sa fie obiect de tipul DigitalInputDevice!")

        self.secunde_zgomot = 0.0
        self.stare = stare
        self.modul_microfon = modul_microfon
        #variabila pentru a sti ca s=0 in diagrama stari
        self.fara_zgomot = True


    def monitorizeaza_sunet(self):
        print("Monitorizarea nivelului de zgomot din camera.")
        #value = 1 liniste, value = 0 zgomot
        secunde_zgomot = 0.0
        toggle = False
        #se presupune liniste in camera
        sunet_anterior = 1
        start = None

        timpi_intre_zgomote = [None] * 5

        while not self.stare.is_set():  
                self.modul_microfon.wait_for_inactive(5)
                if not self.modul_microfon.value and sunet_anterior == 1:
                        start = time.perf_counter()
                        sunet_anterior = 0
                        fara_zgomot = False
                        toggle = True
                        time.sleep(0.1)
                        
                elif self.modul_microfon.value and sunet_anterior == 0:        
                        secunde_zgomot += time.perf_counter() - start
                        sunet_anterior = 1
                        print("Liniste dupa zgomot.")
                elif self.modul_microfon.value and start is not None and time.perf_counter() - start > 600:
                        fara_zgomot = True
                        
                #se asteapta 1 milisecunda
                time.sleep(0.001)

        #cazul in care s-a detectat zgomot care nu s-a oprit
        if not toggle and start is not None:  
                secunde_zgomot += time.perf_counter() - start

        print(f'Numar total de secunde zgomot {secunde_zgomot}')
        print("S-a finalizat monitorizarea nivelului de zgomot din camera.")




if __name__ == "__main__":
    start = time.perf_counter()
    modul_microfon = DigitalInputDevice(23)
    stare_sunet = threading.Event()
    monitor_sunet = MonitorSunet(stare_sunet, modul_microfon)

    thread_sunet = threading.Thread(target=monitor_sunet.monitorizeaza_sunet)
    thread_sunet.start()
    time.sleep(10)
    monitor_sunet.stare.set()
    thread_sunet.join()

    print("Iesire din program")
    modul_microfon.close()
    finish = time.perf_counter()
    print(f'Terminat in {round(finish-start,4)} secunde.')
        
 