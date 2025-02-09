import random
import unicodedata
from .base import TaskProvider

class FrenchWordsTaskProvider(TaskProvider):
    E2F_VOCAB = {
        "the city": ["la ville", "la municipalité"],
        "the cities": ["les villes", "les municipalités"],
        "the cinema": ["le cinéma"],
        "the cinemas": ["les cinémas"],
        "the fish": ["le poisson"],
        "the fish": ["les poissons"],
        "the school": ["l'école", "le lycée"],
        "the schools": ["les écoles", "les lycées"],
        "the computer": ["l'ordinateur", "le PC"],
        "the computers": ["les ordinateurs", "les PCs"],
        "the house": ["la maison", "le logement", "le domicile"],
        "the houses": ["les maisons", "les logements", "les domiciles"],
        "the car": ["la voiture", "l'auto"],
        "the cars": ["les voitures", "les autos"],
        "the book": ["le livre", "l'ouvrage"],
        "the books": ["les livres", "les ouvrages"],
        "the phone": ["le téléphone", "le portable"],
        "the phones": ["les téléphones", "les portables"],
        "the friend": ["l'ami", "le copain", "le camarade", "l'amie", "la copine"],
        "the friends": ["les amis", "les copains", "les camarades", "les amies", "les copines"],
        "the family": ["la famille"],
        "the families": ["les familles"],
        "the food": ["la nourriture", "l'aliment"],
        "the foods": ["les nourritures", "les aliments"],
        "the water": ["l'eau"],
        "the waters": ["les eaux"],
        "the coffee": ["le café"],
        "the coffees": ["les cafés"],
        "the tea": ["le thé"],
        "the teas": ["les thés"],
        "the bread": ["le pain"],
        "the breads": ["les pains"],
        "the wine": ["le vin"],
        "the wines": ["les vins"],
        "the park": ["le parc"],
        "the parks": ["les parcs"],
        "the beach": ["la plage"],
        "the beaches": ["les plages"],
        "the sun": ["le soleil"],
        "the suns": ["les soleils"],
        "the moon": ["la lune"],
        "the moons": ["les lunes"],
        "the star": ["l'étoile"],
        "the stars": ["les étoiles"],
        "the cloud": ["le nuage"],
        "the clouds": ["les nuages"],
        "the rain": ["la pluie"],
        "the rains": ["les pluies"],
        "the snow": ["la neige"],
        "the snows": ["les neiges"],
        "the tree": ["l'arbre"],
        "the trees": ["les arbres"],
        "the flower": ["la fleur"],
        "the flowers": ["les fleurs"],
        "the dog": ["le chien", "la chienne"],
        "the dogs": ["les chiens", "les chiennes"],
        "the cat": ["le chat", "la chatte"],
        "the cats": ["les chats", "les chattes"],
        "the bird": ["l'oiseau"],
        "the birds": ["les oiseaux"],
        "the work": ["le travail", "l'emploi"],
        "the works": ["les travaux", "les emplois"],
        "the job": ["le boulot", "l'emploi"],
        "the jobs": ["les boulots", "les emplois"],
        "the money": ["l'argent"],
        "the moneys": ["les argents"],
        "the time": ["le temps"],
        "the times": ["les temps"],
        "the day": ["le jour"],
        "the days": ["les jours"],
        "the night": ["la nuit"],
        "the nights": ["les nuits"],
        "the week": ["la semaine"],
        "the weeks": ["les semaines"],
        "the month": ["le mois"],
        "the months": ["les mois"],
        "the year": ["l'année"],
        "the years": ["les années"],
        "the country": ["le pays"],
        "the countries": ["les pays"],
        "the language": ["la langue"],
        "the languages": ["les langues"],
        "the music": ["la musique"],
        "the musics": ["les musiques"],
        "the song": ["la chanson"],
        "the songs": ["les chansons"],
        "the movie": ["le film"],
        "the movies": ["les films"],
        "the photo": ["la photo", "la photographie"],
        "the photos": ["les photos", "les photographies"],
        "the game": ["le jeu"],
        "the games": ["les jeux"],
        "the sport": ["le sport"],
        "the sports": ["les sports"],
        "the ball": ["la balle", "la balle de revolver", "la balle de fusil", "la balle de carabine"],
        "the balls": ["les balles", "les balles de revolver", "les balles de fusil", "les balles de carabine"],
        "the player": ["le joueur", "l'acteur", "la joueuse", "l'actrice"],
        "the players": ["les joueurs", "les acteurs", "les joueuses", "les actrices"],
        "the team": ["l'équipe"],
        "the teams": ["les équipes"],
        "the goal": ["le but", "l'objectif"],
        "the goals": ["les buts", "les objectifs"]
    }

    F2E_VOCAB = {
        "la ville": ["the city", "the town"],
        "les villes": ["the cities", "the towns"],
        "le cinéma": ["the cinema", "the movie theater"],
        "les cinémas": ["the cinemas", "the movie theaters"],
        "le poisson": ["the fish"],
        "les poissons": ["the fish"],
        "l'école": ["the school"],
        "les écoles": ["the schools"],
        "le lycée": ["the school"],
        "les lycées": ["the schools"],
        "l'ordinateur": ["the computer"],
        "les ordinateurs": ["the computers"],
        "le PC": ["the PC"],
        "les PCs": ["the PCs"],
        "la maison": ["the house", "the home"],
        "les maisons": ["the houses", "the homes"],
        "le logement": ["the housing"],
        "les logements": ["the housings"],
        "le domicile": ["the residence"],
        "les domiciles": ["the residences"],
        "la voiture": ["the car", "the auto"],
        "les voitures": ["the cars", "the autos"],
        "l'auto": ["the car"],
        "les autos": ["the cars"],
        "le livre": ["the book", "the volume"],
        "les livres": ["the books", "the volumes"],
        "l'ouvrage": ["the book"],
        "les ouvrages": ["the books"],
        "le téléphone": ["the phone", "the telephone"],
        "les téléphones": ["the phones", "the telephones"],
        "le portable": ["the mobile phone"],
        "les portables": ["the mobile phones"],
        "l'ami": ["the friend", "the buddy"],
        "les amis": ["the friends", "the buddies"],
        "l'amie": ["the friend", "the buddy"],
        "les amies": ["the friends", "the buddies"],
        "le copain": ["the friend", "the buddy"],
        "les copains": ["the friends", "the buddies"],
        "la copine": ["the friend", "the buddy"],
        "les copines": ["the friends", "the buddies"],
        "le camarade": ["the comrade", "the buddy"],
        "les camarades": ["the comrades", "the buddies"],
        "la famille": ["the family"],
        "les familles": ["the families"],
        "la nourriture": ["the food"],
        "les nourritures": ["the foods"],
        "l'aliment": ["the food"],
        "les aliments": ["the foods"],
        "l'eau": ["the water"],
        "les eaux": ["the waters"],
        "le café": ["the coffee"],
        "les cafés": ["the coffees"],
        "le thé": ["the tea"],
        "les thés": ["the teas"],
        "le pain": ["the bread"],
        "les pains": ["the breads"],
        "le vin": ["the wine"],
        "les vins": ["the wines"],
        "le parc": ["the park"],
        "les parcs": ["the parks"],
        "la plage": ["the beach"],
        "les plages": ["the beaches"],
        "le soleil": ["the sun"],
        "les soleils": ["the suns"],
        "la lune": ["the moon"],
        "les lunes": ["the moons"],
        "l'étoile": ["the star"],
        "les étoiles": ["the stars"],
        "le nuage": ["the cloud"],
        "les nuages": ["the clouds"],
        "la pluie": ["the rain"],
        "les pluies": ["the rains"],
        "la neige": ["the snow"],
        "les neiges": ["the snows"],
        "l'arbre": ["the tree"],
        "les arbres": ["the trees"],
        "la fleur": ["the flower"],
        "les fleurs": ["the flowers"],
        "le chien": ["the dog"],
        "les chiens": ["the dogs"],
        "la chienne": ["the dog"],
        "les chiennes": ["the dogs"],
        "le chat": ["the cat"],
        "les chats": ["the cats"],
        "la chatte": ["the cat"],
        "les chattes": ["the cats"],
        "l'oiseau": ["the bird"],
        "les oiseaux": ["the birds"],
        "le travail": ["the work", "the job"],
        "les travaux": ["the works", "the jobs"],
        "l'emploi": ["the job"],
        "les emplois": ["the jobs"],
        "le boulot": ["the job", "the task"],
        "les boulots": ["the jobs", "the tasks"],
        "l'argent": ["the money"],
        "les argents": ["the moneys"],
        "le temps": ["the time", "the weather"],
        "les temps": ["the times", "the weather"],
        "le jour": ["the day"],
        "les jours": ["the days"],
        "la nuit": ["the night"],
        "les nuits": ["the nights"],
        "la semaine": ["the week"],
        "les semaines": ["the weeks"],
        "le mois": ["the month"],
        "les mois": ["the months"],
        "l'année": ["the year"],
        "les années": ["the years"],
        "le pays": ["the country"],
        "les pays": ["the countries"],
        "la langue": ["the language"],
        "les langues": ["the languages"],
        "la musique": ["the music"],
        "les musiques": ["the musics"],
        "la chanson": ["the song"],
        "les chansons": ["the songs"],
        "le film": ["the movie", "the film"],
        "les films": ["the movies", "the films"],
        "la photo": ["the photo", "the photograph"],
        "les photos": ["the photos", "the photographs"],
        "le jeu": ["the game"],
        "les jeux": ["the games"],
        "le sport": ["the sport"],
        "les sports": ["the sports"],
        "la balle": ["the bullet", "the pellet"],
        "les balles": ["the bullets", "the pellets"],
        "le joueur": ["the player", "the actor"],
        "les joueurs": ["the players", "the actors"],
        "la joueuse": ["the player"],
        "les joueuses": ["the players"],
        "l'acteur": ["the actor"],
        "les acteurs": ["the actors"],
        "l'actrice": ["the actress"],
        "les actrices": ["the actresses"],
        "l'équipe": ["the team"],
        "les équipes": ["the teams"],
        "le but": ["the goal", "the target"],
        "les buts": ["the goals", "the targets"]    
    }

    @property
    def name(self):
        return "French Vocabulary Practice"

    @property
    def description(self):
        direction = "English to French" if self.direction == 'e2f' else "French to English"
        return f"""French Vocabulary Practice ({direction})
        
        Task types enabled: {', '.join(self.active_modes)}
        Accent handling: {'Ignored' if self.ignore_accents else 'Strict'}
        Total words in vocabulary: {len(self.current_vocab)}
        Press Enter to begin when ready."""

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--e2f', action='store_true', default=False, help='English to French translation')
        parser.add_argument('--f2e', action='store_true', default=False, help='French to English translation')
        parser.add_argument('--direct', action='store_true', help='Enable direct translation tasks')
        parser.add_argument('--match', action='store_true', help='Enable matching tasks')
        parser.add_argument('--ignore-accents', action='store_true',
                          help='Treat accented and non-accented versions as identical')
        parser.add_argument('--match-options', type=int, default=3, help='How many options are in match tasks')

    def __init__(self, args):
        self.direction = 'both' if (args.e2f == args.f2e) else 'e2f' if args.e2f else 'f2e'
        match self.direction:
            case 'e2f':  
                self.current_vocab = self.E2F_VOCAB
            case 'f2e':  
                self.current_vocab = self.F2E_VOCAB
            case 'both':
                unique_keys = set(self.E2F_VOCAB.keys()).symmetric_difference(set(self.F2E_VOCAB.keys()))
                self.current_vocab = {k: self.E2F_VOCAB.get(k, self.F2E_VOCAB.get(k)) for k in unique_keys}
        
        self.active_modes = []
        if args.direct: self.active_modes.append('direct')
        if args.match: self.active_modes.append('match')
        if not self.active_modes:
            self.active_modes = ['direct', 'match']
        
        self.match_options = args.match_options
        self.ignore_accents = args.ignore_accents
        self.source_words = list(self.current_vocab.keys())

    def generate_task(self):
        task_type = random.choice(self.active_modes)
        source_word = random.choice(self.source_words)
        
        if task_type == 'direct':
            return self._create_direct_task(source_word)
        return self._create_match_task(source_word)

    def _create_direct_task(self, source_word):
        if self.direction == 'e2f':
            question = f"Translate to French: {source_word}"
        elif self.direction == 'f2e':
            question = f"Translate to English: {source_word}"
        elif source_word in self.E2F_VOCAB:
            question = f"Translate to French: {source_word}"
        else:
            question = f"Translate to English: {source_word}"

        return question, self.current_vocab[source_word]

    def _create_match_task(self, source_word):
        source_lang = "English" if source_word in self.E2F_VOCAB else "French"
        target_lang = "French" if source_lang == "English" else "English"
        vocab = self.E2F_VOCAB if source_lang=="English" else self.F2E_VOCAB
        correct_translations = vocab[source_word]
        correct = random.choice(correct_translations)
        
        distractors = []
        for word, translations in vocab.items():
            if word != source_word:
                distractors.extend(translations)
        
        options = random.sample(distractors, self.match_options - 1)
        options.append(correct)
        random.shuffle(options)
        
        correct_index = options.index(correct) + 1  # Options are 1-based
        
        question = f"Match {target_lang} translation for:\n{source_word}\n"
        for i, opt in enumerate(options, 1):
            question += f"\n{i}) {opt}"
            
        return question, correct_index

    def validate_answer(self, user_answer, correct):
        if isinstance(correct, list):  # Direct translation
            normalized_correct = [self._normalize(a) for a in correct]
            return self._normalize(user_answer) in normalized_correct
        
        # Matching task (correct is index)
        try:
            return int(user_answer) == correct
        except ValueError:
            return False

    def _normalize(self, text):
        normalized = unicodedata.normalize('NFKD', text.lower().strip())
        if self.ignore_accents:
            normalized = ''.join([c for c in normalized 
                                if not unicodedata.combining(c)])
        return normalized