import copy

from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        relazioni = TourDAO.get_tour_attrazioni()
        for relazione in relazioni:
             # creo una tupla (nome attrazione, valore culturale) in modo da tenere traccia del valore culturale dato che non ho più l'id dell'attrazione
            self.tour_map[relazione['id_tour']].attrazioni.add((self.attrazioni_map[relazione['id_attrazione']].nome,
                                                               self.attrazioni_map[relazione['id_attrazione']].valore_culturale))
            self.attrazioni_map[relazione['id_attrazione']].tour.add(relazione['id_tour'])


    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1
        tour_regione = self.get_tour_regione(id_regione)
        self._ricorsione(0,[],0,0.0,0,set(),max_giorni,max_budget,tour_regione)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set,max_giorni: int, max_budget: float,tour_regione):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        if self._valore_ottimo == -1 or (valore_corrente > self._valore_ottimo):
            self._costo = costo_corrente
            self._pacchetto_ottimo = copy.deepcopy(pacchetto_parziale)
            self._valore_ottimo = valore_corrente


        for i in range(start_index,len(tour_regione)):
            tour = tour_regione[i]

            if self.soluzione_valida(tour,durata_corrente,costo_corrente,attrazioni_usate,max_giorni,max_budget):

                pacchetto_parziale.append(tour)
                nuovo_costo_corrente = costo_corrente + float(tour.costo)
                nuovo_valore_corrente = valore_corrente
                nuove_attrazioni_usate = attrazioni_usate
                for attrazione in self.tour_map[tour.id].attrazioni:
                    nuovo_valore_corrente += attrazione[1]
                    nuove_attrazioni_usate.add(attrazione[0])
                nuova_durata_corrente = durata_corrente + tour.durata_giorni

                self._ricorsione((i+1),pacchetto_parziale,nuova_durata_corrente,nuovo_costo_corrente,nuovo_valore_corrente,nuove_attrazioni_usate,max_giorni,max_budget,tour_regione)
                pacchetto_parziale.pop()


    def soluzione_valida(self, tour,durata_corrente,costo_corrente,attrazioni_usate,max_giorni,max_budget):
        if durata_corrente + tour.durata_giorni > max_giorni:
            return False
        if costo_corrente + float(tour.costo) > max_budget:
            return False

        attrazioni = set()
        for attrazione in self.tour_map[tour.id].attrazioni:
            attrazioni.add(attrazione)
        if len(attrazioni_usate.intersection(attrazioni))>=1:
            return False
        return True

    def get_tour_regione(self,id_regione):
        lista_tour_regione = []
        for i in self.tour_map:
            if self.tour_map[i].id_regione == id_regione:
                lista_tour_regione.append(self.tour_map[i])
        return lista_tour_regione





