
let  adjectives = ["attractive", "awesome", "bald", "bashful", "bold", "brave", "chatty", "cheerful", "clumsy", "crazy", "cuddly", "curious", "daffy", "dopey", "dreamy", "drunk",
    "enthusiatic", "fierce", "fluffy", "funky", "fuzzy", "gigantic", "grumpy", "hairy", "happy", "hirsute", "hungry", "jolly", "mad", "madcap", "magic", "magnificien", "mannered", "multicolor",
     "mysterious", "mystic", "noisy", "nutty", "lazy", "sagacious", "sexy", "scatterbrain", "shaggy", "shining", "skilled",
    "sleepy", "sneezy", "stylish", "shaggy", "shy", "spoty", "talktive", "timid", "tiny", "vengeful", "vivacious", "voracious", "wily", "wise"];

let  nouns = ["beaver", "bunny", "camel", "carrot", "cheeta", "chicken", "crab", "cub", "cupcake", "deer", "dormouse", "duck", "jackal", "kitten", "horse", "hedgedog",
    "hippopotamus", "lama", "lemur", "leopard", "lynx", "kangaroo", "kitten", "kiwi", "koala", "mammoth", "monkey", "okapi", "otter", "owl",
    "panda", "pangolin", "parrot", "porcupine", "pony", "sloth", "tadpole", "tiger", "tortoise", "turkey", "sea horse", "seal", "squirrel", "unicorn", "whale", "worm"];

let  adjectivesFrM = ["100% bio", "affamé", "agile", "alcoolique", "audacieux", "aventureux", "bavard", "bougon", "bruyant", "caracolant", "chantant",
    "charismatique", "charmant", "chaste", "chauve", "cleptomane", "curieux", "déjanté", "dérangé", "désinvolte", "déterminé", "élégant", "enchanté", "endormi",
    "enjoué",  "étourdi", "farfelu", "funky", "gargantuesque", "gonflable", "gourmand", "grincheux", "hyperactif", "hirsute", "impétueux", "incrédule", "intrépide", "joyeux", "loufoque", "magique",
    "maladroit", "malicieux", "malvoyant", "moqueur", "multicolore", "mystérieux", "paresseux", "pelucheux", "pénible", "perturbé", "poilu", "poilant", "prétentieux", "respectueux", "revêche",
    "roublard", "sagace", "séduisant", "sensible", "simplet", "somnolent", "sophistiqué", "taré", "timide", "tonitruant", "tout doux", "vaillant", "vengeur",
    "vigoureux", "vivace", "vigilant", "vorace"];

let adjectivesFrF = ["100% bio", "affamée", "agile", "alcoolique", "audacieuse", "aventureuse", "bavarde", "bougonne", "bruyante", "caracolante",
  "chantante", "charismatique", "charmante", "chaste", "chauve", "cleptomane", "curieuse", "déjantée", "dérangée", "désinvolte", "déterminée", "distrait",
  "élégante","enchantée", "endormie", "enjouée", "étourdie", "farfelue", "funky", "gargantuesque", "gonflable", "gourmande", "grincheuse", "hirsute", "hyperactive",
  "impétueuse", "incrédule", "intrépide", "joyeuse", "loufoque", "magique", "maladroite", "malicieuse", "malvoyante", "multicolore", "mystérieuse", "mystique",
  "paresseuse", "pénible", "perturbée", "poilue", "poilante", "prétentieuse","respectueuse", "revêche", "roublarde", "sagace",
  "séduisante", "sensible", "simplette", "somnolente", "sophistiquée", "tarée", "timide", "tonitruante", "toute douce", "vaillante", "veloce",
  "vengeuse", "vigoureuse", "vivace", "vigilante", "vorace"];

let  nounsFrM = ["asticot", "blaireau", "bonobo",  "cachalot", "canard", "castor", "chacal", "chameau", "chaton", "chimpanzé", "crabe", "chevreuil", "coyote", "dindon",
    "dromadaire", "écureuil", "étalon", "guépard", "hippopotame", "hérisson", "hypocampe", "kangourou", "kiwi", "koala", "lama", "lapin", "lémurien", "léopard", "loir",
    "lynx", "manchot", "matou", "morse", "okapi", "ornythorinque", "ouistiti", "panda", "paresseux", "perroquet", "poney", "porc-épic", "poulpe", "poussin", "phasme", "ragondin", "rhinocéros"
    , "souriceau", "taureau", "tétard", "tigre"];

let  nounsFrF = ["belette", "biche", "brebis", "chouette", "giraphe", "licorne", "loutre", "mangouste", "marmotte", "poule", "pieuvre", "taupe", "tortue"];

function  generateNickname() {
    if(language == 'fr') {
      return generateNicknameFr();
    } else {
      return generateNicknameEn();
    }
  }

function generateNicknameEn() {

    let adjRank = getRandomNumberBetween(0, adjectives.length);
    let nounsRank = getRandomNumberBetween(0, nouns.length);

    return adjectives[adjRank] + " " + nouns[nounsRank];
  }

function  generateNicknameFr() {

    let total = nounsFrM.length + nounsFrF.length;

    let chanceToBeMale = nounsFrM.length/total;
    let randNumber = Math.random();

    let noun = "";
    let adj = "";
    if(randNumber < chanceToBeMale) {
      noun = nounsFrM[getRandomNumberBetween(0,  nounsFrM.length)];
      adj = adjectivesFrM[getRandomNumberBetween(0,  adjectivesFrM.length)];
    } else {
      noun = nounsFrF[getRandomNumberBetween(0,  nounsFrF.length)];
      adj = adjectivesFrF[getRandomNumberBetween(0,  adjectivesFrF.length)];
    }

    return noun + " " + adj;
  }

function getRandomNumberBetween(from, to) {

    return Math.floor(Math.random() * to) + from;
  }
