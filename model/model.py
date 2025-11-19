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

        self._tour_per_attrazione = {}
        self._attrazione_per_tour = {}

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
            if relazione['id_tour'] not in self._attrazione_per_tour:
                self._attrazione_per_tour[relazione['id_tour']] = set()
                self._attrazione_per_tour[relazione['id_tour']].add(relazione['id_attrazione'])
            else:
                self._attrazione_per_tour[relazione['id_tour']].add(relazione['id_attrazione'])
            if relazione['id_attrazione'] not in self._tour_per_attrazione:
                self._tour_per_attrazione[relazione['id_attrazione']] = set()
                self._tour_per_attrazione[relazione['id_attrazione']].add(relazione['id_tour'])
            else:
                self._tour_per_attrazione[relazione['id_attrazione']].add(relazione['id_tour'])




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

        if self._valore_ottimo == -1 or valore_corrente > self._valore_ottimo:
            self._costo = costo_corrente
            self._pacchetto_ottimo = copy.deepcopy(pacchetto_parziale)
            self._valore_ottimo = valore_corrente


        for i in range(start_index,len(tour_regione)):
            tour = tour_regione[i]

            if self.soluzione_valida(tour,durata_corrente,costo_corrente,attrazioni_usate,max_giorni,max_budget):

                pacchetto_parziale.append(tour)
                costo_corrente += float(tour.costo)

                for attrazione in self._attrazione_per_tour[tour.id]:
                    valore_corrente += self.attrazioni_map[attrazione].valore_culturale
                    attrazioni_usate.add(self.attrazioni_map[attrazione].nome)
                durata_corrente += tour.durata_giorni

                self._ricorsione((i+1),pacchetto_parziale,durata_corrente,costo_corrente,valore_corrente,attrazioni_usate,max_giorni,max_budget,tour_regione)
                pacchetto_parziale.pop()

    def soluzione_valida(self, tour,durata_corrente,costo_corrente,attrazioni_usate,max_giorni,max_budget):
        if durata_corrente + tour.durata_giorni > max_giorni:
            return False
        if costo_corrente + float(tour.costo) > max_budget:
            return False

        attrazioni = set()
        for attrazione in self._attrazione_per_tour[tour.id]:
            attrazioni.add(self.attrazioni_map[attrazione].nome)
        if len(attrazioni_usate.intersection(attrazioni))>=1:
            return False
        return True

    def get_tour_regione(self,id_regione):
        lista_tour_regione = []
        for i in self.tour_map:
            if self.tour_map[i].id_regione == id_regione:
                lista_tour_regione.append(self.tour_map[i])
        return lista_tour_regione





