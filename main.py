from flask import Flask, render_template, request
import cv2
import sqlite3
import os
import requests
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ============================================================
# SMART PLANT CARE SYSTEM - FRESH MAIN.PY
# ============================================================

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATABASE = "plant_growth.db"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")
PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY")
def get_perenual_plant(plant_name):
    if not PERENUAL_API_KEY:
        return None

    try:
        url = "https://perenual.com/api/v2/species-list"

        response = requests.get(
            url,
            params={
                "key": PERENUAL_API_KEY,
                "q": plant_name
            },
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("data"):
            return data["data"][0]

        return None

    except Exception as e:
        print("Perenual API Error:", e)
        return None

# ============================================================
# TRANSLATIONS
# ============================================================

translations = {
    "en": {
        "result": "🌱 Plant Analysis Result",
        "voice": "🔊 Voice",
        "name": "🌿 Plant Name",
        "area": "📊 Plant Area",
        "growth": "📈 Growth",
        "history": "📈 Growth History",
        "care": "🌿 Care Guide",
        "water": "💧 Water",
        "sunlight": "☀️ Sunlight",
        "soil": "🌱 Soil",
        "temperature": "🌡️ Temperature",
        "nutrients": "🌿 Nutrients",
        "alert": "⚠️ Care Alert",
        "back": "⬅️ Upload Another Photo"
    },
    "ta": {
        "result": "🌱 தாவர பகுப்பாய்வு முடிவு",
        "voice": "🔊 குரல்",
        "name": "🌿 தாவரத்தின் பெயர்",
        "area": "📊 தாவர பரப்பளவு",
        "growth": "📈 வளர்ச்சி",
        "history": "📈 வளர்ச்சி வரலாறு",
        "care": "🌿 பராமரிப்பு வழிகாட்டி",
        "water": "💧 தண்ணீர்",
        "sunlight": "☀️ சூரிய ஒளி",
        "soil": "🌱 மண்",
        "temperature": "🌡️ வெப்பநிலை",
        "nutrients": "🌿 ஊட்டச்சத்துக்கள்",
        "alert": "⚠️ பராமரிப்பு எச்சரிக்கை",
        "back": "⬅️ மற்றொரு புகைப்படத்தை பதிவேற்றவும்"
    },
    "hi": {
        "result": "🌱 पौधे का विश्लेषण",
        "voice": "🔊 आवाज़",
        "name": "🌿 पौधे का नाम",
        "area": "📊 पौधे का क्षेत्रफल",
        "growth": "📈 वृद्धि",
        "history": "📈 वृद्धि इतिहास",
        "care": "🌿 देखभाल मार्गदर्शिका",
        "water": "💧 पानी",
        "sunlight": "☀️ धूप",
        "soil": "🌱 मिट्टी",
        "temperature": "🌡️ तापमान",
        "nutrients": "🌿 पोषक तत्व",
        "alert": "⚠️ देखभाल चेतावनी",
        "back": "⬅️ दूसरी फोटो अपलोड करें"
    }
}

# ============================================================
# PLANT DATABASE
# Format:
# common name : Tamil / Hindi / scientific name / category
# ============================================================

PLANT_DATABASE = {}

def add_plants(rows, category="Plant"):
    for english, tamil, hindi, scientific in rows:
        PLANT_DATABASE[english.lower()] = {
            "english": english,
            "ta": tamil,
            "hi": hindi,
            "scientific": scientific,
            "category": category
        }

# ============================================================
# TREES
# ============================================================

add_plants([
("Neem","வேம்பு","नीम","Azadirachta indica"),
("Banyan","ஆலமரம்","बरगद","Ficus benghalensis"),
("Peepal","அரச மரம்","पीपल","Ficus religiosa"),
("Mango","மாமரம்","आम","Mangifera indica"),
("Tamarind","புளிய மரம்","इमली","Tamarindus indica"),
("Coconut palm","தென்னை மரம்","नारियल","Cocos nucifera"),
("Palmyra palm","பனை மரம்","ताड़","Borassus flabellifer"),
("Areca nut palm","பாக்கு மரம்","सुपारी","Areca catechu"),
("Wild date palm","ஈச்ச மரம்","खजूर","Phoenix sylvestris"),
("Sugar palm","கூந்தல்பனை","माड़","Caryota urens"),
("Jackfruit","பலா மரம்","कटहल","Artocarpus heterophyllus"),
("Breadfruit","சீமைபலா","बेड़फ्रूट","Artocarpus altilis"),
("Teak","தேக்கு","सागौन","Tectona grandis"),
("Sandalwood","சந்தன மரம்","चंदन","Santalum album"),
("Red sandalwood","செஞ்சந்தனம்","रक्त चंदन","Pterocarpus santalinus"),
("Indian rosewood","ஈட்டி மரம்","शीशम","Dalbergia latifolia"),
("Indian kino tree","வேங்கை","பீஜா","Pterocarpus marsupium"),
("Gulmohar","செம்மயிற்கொன்றை","गुलमोहर","Delonix regia"),
("Golden shower tree","கொன்றை","अमलतास","Cassia fistula"),
("Copper pod","மஞ்சள் கொன்றை","पीला गुलमोहर","Peltophorum pterocarpum"),
("Rain tree","தூங்குமூஞ்சி மரம்","विलायती सिरिस","Samanea saman"),
("Babul","கருவேலம்","बबूल","Vachellia nilotica"),
("Khair","கருங்காலி","खैर","Senegalia catechu"),
("Siris","வாகை","सिरिस","Albizia lebbeck"),
("Arjuna","மருது","अर्जुन","Terminalia arjuna"),
("Beleric myrobalan","தான்றிக்காய்","बहेड़ा","Terminalia bellirica"),
("Chebulic myrobalan","கடுக்காய்","हरड़","Terminalia chebula"),
("Indian almond","நாட்டு வாதுமை","जंगली बादाम","Terminalia catappa"),
("Indian gooseberry","நெல்லி","आँवला","Phyllanthus emblica"),
("Jamun","நாவல்","जामुन","Syzygium cumini"),
("Rose apple","பன்னீர் நாவல்","गुलाब जामुन","Syzygium jambos"),
("Clove","கிராம்பு","लौंग","Syzygium aromaticum"),
("Guava","கொய்யா","अमरूद","Psidium guajava"),
("Lemon","எலுமிச்சை","नींबू","Citrus limon"),
("Mandarin orange","ஆரஞ்சு","संतरा","Citrus reticulata"),
("Sweet lime","சாத்துக்குடி","मौसंबी","Citrus limetta"),
("Pomelo","பம்பளிமாஸ்","चकोतरा","Citrus maxima"),
("Papaya","பப்பாளி","पपीता","Carica papaya"),
("Sapota","சப்போட்டா","चीकू","Manilkara zapota"),
("Custard apple","சீதாப்பழம்","शरीफा","Annona squamosa"),
("Wood apple","விளா மரம்","कैथा","Limonia acidissima"),
("Bael","வில்வம்","बेल","Aegle marmelos"),
("Indian jujube","இலந்தை","बेर","Ziziphus mauritiana"),
("Cashew","முந்திரி","काजू","Anacardium occidentale"),
("Mahua","இலுப்பை","महुआ","Madhuca longifolia"),
("Pongame oil tree","புங்கை","करंज","Pongamia pinnata"),
("Indian coral tree","கல்யாண முருங்கை","पंगारा","Erythrina variegata"),
("Drumstick tree","முருங்கை","सहजन","Moringa oleifera"),
("Curry leaf tree","கறிவேப்பிலை","कड़ी पत्ता","Murraya koenigii"),
("Ashoka","அசோக மரம்","अशोक","Saraca asoca"),
("Mast tree","நெட்டிலிங்கம்","अशोक","Polyalthia longifolia"),
("Eucalyptus","தைல மரம்","नीलगिरी","Eucalyptus globulus"),
("Casuarina","சவுக்கு","जंगली झाऊ","Casuarina equisetifolia"),
("Red silk cotton tree","இலவம் மரம்","सेमल","Bombax ceiba"),
("Kapok","வெள்ளை இலவம்","सफेद सेमल","Ceiba pentandra"),
("Flame of the forest","பலாசு","पलाश","Butea monosperma"),
("Sal","சால மரம்","साल","Shorea robusta"),
("Deodar cedar","தேவதாரு","देवदार","Cedrus deodara"),
("Chir pine","பைன் மரம்","चीड़","Pinus roxburghii"),
("Persian lilac","மலைவேம்பு","बकायन","Melia azedarach"),
("Indian cork tree","மரமல்லி","आकाश नीम","Millingtonia hortensis"),
("Kadam","கடம்பு","कदंब","Neolamarckia cadamba"),
("Spanish cherry","மகிழம்","मौलसिरी","Mimusops elengi"),
("Golden champak","சண்பகம்","चंपा","Magnolia champaca"),
("Ceylon ironwood","நாகசம்பகம்","नागकेसर","Mesua ferrea"),
("Night jasmine","பவளமல்லி","हरसिंगार","Nyctanthes arbor-tristis"),
("Portia tree","பூவரசு","पारस पीपल","Thespesia populnea"),
("Cluster fig","அத்தி","गूलर","Ficus racemosa"),
("Wavy-leaf fig","இச்சி","पाकर","Ficus virens"),
("Indian rubber fig","ரப்பர் அத்தி","रबर का पेड़","Ficus elastica"),
("White mulberry","முசுக்கட்டை","शहतूत","Morus alba"),
("Soapnut","பூந்திக்கொட்டை","रीठा","Sapindus mukorossi"),
("Manila tamarind","கொடுக்காப்புளி","जंगल जलेबी","Pithecellobium dulce"),
("Subabul","சூபாபுல்","सुबबूल","Leucaena leucocephala"),
("Gliricidia","கிளரிசீடியா","गिरिपुष्प","Gliricidia sepium"),
("Agathi","அகத்தி","अगस्त्य","Sesbania grandiflora"),
("Kokum","கோகம்","कोकम","Garcinia indica"),
("Nutmeg","ஜாதிக்காய்","जायफल","Myristica fragrans"),
("Cinnamon","இலவங்கப்பட்டை","दालचीनी","Cinnamomum verum"),
("Camphor tree","கற்பூர மரம்","कपूर","Cinnamomum camphora"),
("Rubber tree","ரப்பர் மரம்","रबर","Hevea brasiliensis"),
("Cocoa","கோக்கோ","कोको","Theobroma cacao"),
("Lychee","லிச்சி","लीची","Litchi chinensis"),
("Apple","ஆப்பிள்","सेब","Malus domestica"),
("Peach","பீச்","आडू","Prunus persica"),
("Plum","பிளம்","आलूबुखारा","Prunus domestica"),
("Almond","பாதாம்","बादाम","Prunus dulcis"),
("Walnut","அக்ரூட்","अखरोट","Juglans regia"),
("Star fruit","தமரத்தை","कमरख","Averrhoa carambola"),
("Bilimbi","இரும்புளி","बिलिम்பी","Averrhoa bilimbi"),
("Mahogany","மகோகனி","महोगनी","Swietenia mahagoni"),
("Silver oak","சில்வர் ஓக்","सिल्वर ओक","Grevillea robusta"),
("African tulip tree","ஆப்பிரிக்க டுலிப்","अफ्रीकन ट्यूलिप","Spathodea campanulata"),
("Jacaranda","நீலமோகம்","जकरंदा","Jacaranda mimosifolia"),
("Orchid tree","மந்தாரை","कचनार","Bauhinia variegata"),
("Devil tree","ஏழிலைப்பாலை","सप्तपर्णी","Alstonia scholaris"),
("Yellow teak","மஞ்சக்கடம்பு","हल्दू","Haldina cordifolia"),
("Headache tree","முன்னை","अरणी","Premna serratifolia"),
("Strychnine tree","எட்டி","कुचला","Strychnos nux-vomica"),
("Axlewood","வெக்காளி","धावड़ा","Anogeissus latifolia"),
("Noni","நுணா","नोनी","Morinda citrifolia"),
("Oil palm","எண்ணெய் பனை","ऑयल पाम","Elaeis guineensis"),
("Royal palm","ராயல் பனை","रॉयल पाम","Roystonea regia"),
("Avocado","வெண்ணெய் பழம்","माखनफल","Persea americana"),
("Dragon fruit","டிராகன் பழம்","ड्रैगन फ्रूट","Selenicereus undatus"),
("Fig","அத்திப்பழம் (அஞ்சீர்)","अंजीर","Ficus carica"),
("Date palm","பேரீச்சை","खजूर","Phoenix dactylifera"),
("Pear","பேரிக்காய்","नाशपाती","Pyrus communis"),
("Mangosteen","மங்குஸ்தான்","मैंगोस्टीन","Garcinia mangostana"),
("Rambutan","ரம்புட்டான்","रामबूटान","Nephelium lappaceum"),
("Soursop","முள் சீத்தா","हनुमान फल","Annona muricata"),
("Bullock's heart","ராம்சீதா","रामफल","Annona reticulata"),
("Pistachio","பிஸ்தா","पिस्ता","Pistacia vera"),
("Star anise","அன்னாசிப்பூ","चक्र फूल","Illicium verum"),
("Gmelina","குமிழ்","गम्हार","Gmelina arborea"),
("Toon","சந்தன வேம்பு","तून","Toona ciliata"),
("Alexandrian laurel","புன்னை","सुल्तान चंपा","Calophyllum inophyllum"),
("Wodier tree","ஓதியன்","झिंझान","Lannea coromandelica"),
("Lasora","நறுவிலி","लसोड़ा","Cordia dichotoma"),
("Singapore cherry","சிங்கப்பூர் செர்ரி","सिंगापुर चेरी","Muntingia calabura")
], "Tree")

# ============================================================
# SHRUBS / COMMON PLANTS
# ============================================================

add_plants([
("Hibiscus","செம்பருத்தி","गुड़हल","Hibiscus rosa-sinensis"),
("Arabian jasmine","மல்லிகை","मोगरा","Jasminum sambac"),
("Spanish jasmine","ஜாதிமல்லி","चமेली","Jasminum grandiflorum"),
("Juhi jasmine","முல்லை","जूही","Jasminum auriculatum"),
("Rose","பன்னீர் ரோஜா","गुलाब","Rosa × damascena"),
("Oleander","அரளி","कनेर","Nerium oleander"),
("Yellow oleander","மஞ்சள் அரளி","पीला कनेर","Cascabela thevetia"),
("Crossandra","கனகாம்பரம்","कनकम्बर","Crossandra infundibuliformis"),
("Ixora","இட்லிப்பூ (வெட்சி)","रगम","Ixora coccinea"),
("Lantana","உன்னிச்செடி","घाणेरी","Lantana camara"),
("Bougainvillea","காகிதப்பூ","बोगनविलिया","Bougainvillea glabra"),
("Henna","மருதாணி","मेहंदी","Lawsonia inermis"),
("Cotton","பருத்தி","कपास","Gossypium hirsutum"),
("Castor","ஆமணக்கு","अरंडी","Ricinus communis"),
("Physic nut","காட்டாமணக்கு","रतनजोत","Jatropha curcas"),
("Pigeon pea","துவரை","अरहर","Cajanus cajan"),
("Tea","தேயிலை","चाय","Camellia sinensis"),
("Coffee","காபி","कॉफी","Coffea arabica"),
("Chilli","மிளகாய்","मिर्च","Capsicum annuum"),
("Turkey berry","சுண்டைக்காய்","जंगली बैंगन","Solanum torvum"),
("Thorn apple","ஊமத்தை","धतूरा","Datura metel"),
("Crown flower","எருக்கு","आक","Calotropis gigantea"),
("Malabar nut","ஆடாதொடை","अडूसा","Justicia adhatoda"),
("Tanner's cassia","ஆவாரை","तरवड़","Senna auriculata"),
("Indian senna","நிலவாகை","सोनामुखी","Senna alexandrina"),
("Candle bush","சீமை அகத்தி","दादमर्दन","Senna alata"),
("Coffee senna","பேயாவாரை","कसौंदी","Senna occidentalis"),
("Sickle senna","தகரை","चकवड़","Senna tora"),
("Five-leaved chaste tree","நொச்சி","सम्हालू","Vitex negundo"),
("Ashwagandha","அமுக்கரா","अश्वगंधा","Withania somnifera"),
("Yellow-berried nightshade","கண்டங்கத்தரி","कटेरी","Solanum virginianum"),
("Indian spurge tree","சதுரக்கள்ளி","थूहर","Euphorbia neriifolia"),
("Poinsettia","பாயின்செட்டியா","लालपत्ती","Euphorbia pulcherrima"),
("Cape jasmine","காந்தராஜ்","गंधराज","Gardenia jasminoides"),
("Crape jasmine","நந்தியாவட்டை","चांदनी","Tabernaemontana divaricata"),
("Night queen","இரவுராணி","रात की रानी","Cestrum nocturnum"),
("Allamanda","அலமண்டா","अलमांडा","Allamanda cathartica"),
("Bottle brush","பாட்டில் பிரஷ்","बॉटल ब्रश","Callistemon citrinus"),
("Indian mallow","துத்தி","अतिबला","Abutilon indicum"),
("Country mallow","நிலத்துத்தி","खला","Sida cordifolia"),
("Karonda","களாக்காய்","करौंदा","Carissa carandas"),
("Indian barberry","மரமஞ்சள்","दारुहल्दी","Berberis aristata"),
("Peacock flower","மயில் கொன்றை","गुलमोहर","Caesalpinia pulcherrima"),
("Neelakurinji","குறிஞ்சி","नीलकुरिंजी","Strobilanthes kunthiana"),
("Desert rose","அரளியம்","एडेनियम","Adenium obesum"),
("Powder puff","காலியாந்தரா","पाउडर पफ","Calliandra haematocephala"),
("Ceylon leadwort","கொடிவேலி","चित्रक","Plumbago zeylanica"),
("Purple tephrosia","கொழுஞ்சி","सरफोंक","Tephrosia purpurea"),
("Mesquite","சீமைக்கருவேலம்","विलायती बबूल","Prosopis juliflora"),
("Prickly pear","சப்பாத்திக்கள்ளி","नागफनी","Opuntia dillenii"),
("Screw pine","தாழை","केवड़ा","Pandanus odorifer"),
("Orange jasmine","காமினி","कामिनी","Murraya paniculata")
], "Shrub")

# ============================================================
# HERBS / MEDICINAL PLANTS
# ============================================================

add_plants([
("Holy basil (Tulsi)","துளசி","तुलसी","Ocimum tenuiflorum"),
("Sweet basil","திருநீற்றுப்பச்சிலை","बबुई तुलसी","Ocimum basilicum"),
("Mint","புதினா","पुदीना","Mentha spicata"),
("Coriander","கொத்தமல்லி","धनिया","Coriandrum sativum"),
("Turmeric","மஞ்சள்","हल्दी","Curcuma longa"),
("Wild turmeric","காட்டு மஞ்சள்","जंगली हल्दी","Curcuma aromatica"),
("Ginger","இஞ்சி","अदरक","Zingiber officinale"),
("Cardamom","ஏலக்காய்","इलायची","Elettaria cardamomum"),
("Greater galangal","பேரரத்தை","कुलंजन","Alpinia galanga"),
("Fenugreek","வெந்தயம்","मेथी","Trigonella foenum-graecum"),
("Aloe vera","கற்றாழை","घृतकुमारी","Aloe vera"),
("Brahmi","நீர்ப்பிரம்மி","ब्राह्मी","Bacopa monnieri"),
("Indian pennywort","வல்லாரை","मंडूकपर्णी","Centella asiatica"),
("False daisy (Bhringraj)","கரிசாலாங்கண்ணி","भांगरा","Eclipta prostrata"),
("Touch-me-not","தொட்டாற்சிணுங்கி","लाजवंती","Mimosa pudica"),
("Wild asparagus (Shatavari)","தண்ணீர்விட்டான் கிழங்கு","शतावरी","Asparagus racemosus"),
("Giloy","சீந்தில்","गिलोय","Tinospora cordifolia"),
("Indian copperleaf","குப்பைமேனி","कुफ्फी","Acalypha indica"),
("Long pepper","திப்பிலி","पिप्पली","Piper longum"),
("Black pepper","மிளகு","काली मिर्च","Piper nigrum"),
("Betel leaf","வெற்றிலை","पान","Piper betle"),
("King of bitters (Kalmegh)","நிலவேம்பு","कालमेघ","Andrographis paniculata"),
("Puncture vine","நெருஞ்சில்","गोखरू","Tribulus terrestris"),
("Leucas (Thumbai)","தும்பை","गूमा","Leucas aspera"),
("Lemongrass","எலுமிச்சைப்புல்","नींबू घास","Cymbopogon citratus"),
("Vetiver","வெட்டிவேர்","खस","Chrysopogon zizanioides"),
("Indian borage","கற்பூரவள்ளி","पत्थरचूर","Coleus amboinicus"),
("Black nightshade","மணத்தக்காளி","मकोय","Solanum nigrum"),
("Cumin","சீரகம்","जीरा","Cuminum cyminum"),
("Black cumin","கருஞ்சீரகம்","कलौंजी","Nigella sativa"),
("Fennel","சோம்பு","सौंफ","Foeniculum vulgare"),
("Ajwain","ஓமம்","अजवाइन","Trachyspermum ammi"),
("Mustard","கடுகு","सरसों","Brassica juncea"),
("Sesame","எள்","तिल","Sesamum indicum"),
("Garlic","பூண்டு","लहसुन","Allium sativum"),
("Onion","வெங்காயம்","प्याज","Allium cepa"),
("Asafoetida","பெருங்காயம்","हींग","Ferula assa-foetida"),
("Saffron","குங்குமப்பூ","केसर","Crocus sativus"),
("Licorice","அதிமதுரம்","मुलेठी","Glycyrrhiza glabra"),
("Sweet flag","வசம்பு","वच","Acorus calamus"),
("Indian snakeroot","சர்ப்பகந்தி","सर्पगंधा","Rauwolfia serpentina"),
("Stevia","ஸ்டீவியா","स्टीविया","Stevia rebaudiana"),
("Flax","ஆளி விதை","अलसी","Linum usitatissimum"),
("Cissus","பிரண்டை","हड़जोड़","Cissus quadrangularis"),
("Hogweed","மூக்கிரட்டை","पुनर्नवा","Boerhavia diffusa"),
("Stone breaker","கீழாநெல்லி","भूमि आंवला","Phyllanthus niruri"),
("Indian bay leaf","பிரிஞ்சி இலை","तेज पत्ता","Cinnamomum tamala"),
("Dill","சதகுப்பை","सोया","Anethum graveolens"),
("Strawberry","ஸ்ட்ராபெர்ரி","स्ट्रॉबेरी","Fragaria × ananassa")
], "Herb")

# ============================================================
# FLOWERING PLANTS
# ============================================================

add_plants([
("Sacred lotus","தாமரை","कमल","Nelumbo nucifera"),
("Water lily","அல்லி","कुमुदिनी","Nymphaea nouchali"),
("Water hyacinth","ஆகாயத்தாமரை","जलकुंभी","Eichhornia crassipes"),
("Marigold","செண்டுமல்லி","गेंदा","Tagetes erecta"),
("Chrysanthemum","சாமந்தி","गुलदाउदी","Chrysanthemum indicum"),
("Sunflower","சூரியகாந்தி","सूरजमुखी","Helianthus annuus"),
("Zinnia","ஜின்னியா","जीनिया","Zinnia elegans"),
("Cosmos","காஸ்மோஸ்","कॉसमॉस","Cosmos bipinnatus"),
("Dahlia","டேலியா","डहलिया","Dahlia pinnata"),
("Tuberose","சம்பங்கி","रजनीगंधा","Agave amica"),
("Madagascar periwinkle","நித்தியகல்யாணி","सदाबहार","Catharanthus roseus"),
("Globe amaranth","வாடாமல்லி","गोंफ्रेना","Gomphrena globosa"),
("Cockscomb","கோழிக்கொண்டை","मुर्गकेस","Celosia argentea"),
("Balsam","காசித்தும்பை","गुलमेंहदी","Impatiens balsamina"),
("Four o'clock flower","அந்திமந்தாரை","गुल अब्बास","Mirabilis jalapa"),
("Moss rose","பத்துமணிப்பூ","लूनिया","Portulaca grandiflora"),
("Petunia","பெட்டூனியா","पिटूनியா","Petunia × atkinsiana"),
("Pansy","பான்சி","पैंसी","Viola tricolor"),
("Snapdragon","ஸ்னாப்டிராகன்","स्नैपड्रैगन","Antirrhinum majus"),
("Gladiolus","கிளாடியோலஸ்","ग्लैडियोलस","Gladiolus"),
("Canna lily","கல்வாழை","सर्वजया","Canna indica"),
("Orchid","ஆர்க்கிட்","ऑर्किड","Orchidaceae"),
("Anthurium","ஆந்தூரியம்","एंथूरियम","Anthurium andraeanum"),
("Glory lily","செங்காந்தள்","कलिहारी","Gloriosa superba"),
("Carnation","கார்னேஷன்","कारनेशन","Dianthus caryophyllus"),
("Lavender","லாவெண்டர்","लैवेंडर","Lavandula angustifolia"),
("Daisy","டெய்சி","डेज़ी","Bellis perennis"),
("Rain lily","மழை லில்லி","रेन लिली","Zephyranthes"),
("Gerbera","ஜெர்பரா","जरबेरा","Gerbera jamesonii"),
("Iris","ஐரிஸ்","आइरिस","Iris"),
("Tulip","துலிப்","ट्यूलिप","Tulipa"),
("Lily","லில்லி","लिली","Lilium"),
("Amaryllis","அமரில்லிஸ்","अमैरिलिस","Hippeastrum")
], "Flowering")

# ============================================================
# CLIMBERS / ADDITIONAL COMMON PLANTS
# ============================================================

add_plants([
("Rangoon creeper","ரங்கூன் மல்லி","मधुमालती","Combretum indicum"),
("Butterfly pea","சங்குப்பூ","अपराजिता","Clitoria ternatea"),
("Passion fruit","பேஷன் பழம்","पैशन फ्रूट","Passiflora edulis"),
("Indian sarsaparilla","நன்னாரி","अनंतमूल","Hemidesmus indicus"),
("Gymnema","சர்க்கரைக் கொல்லி","गुड़मार","Gymnema sylvestre"),
("Rosary pea","குன்றிமணி","गुंजा","Abrus precatorius"),
("Velvet bean","பூனைக்காலி","कौंच","Mucuna pruriens"),
("Money plant","மணி பிளான்ட்","मनी प्लांट","Epipremnum aureum"),
("Pothos","மணி பிளான்ட்","मनी प्लांट","Epipremnum aureum"),
("Greater yam","பெருவள்ளிக்கிழங்கு","रतालू","Dioscorea alata"),
("Vanilla","வெனிலா","वनीला","Vanilla planifolia"),
("Malabar spinach","பசலைக்கொடி","पोई","Basella alba"),
("Tomato","தக்காளி","टमाटर","Solanum lycopersicum"),
("Brinjal","கத்தரிக்காய்","बैंगन","Solanum melongena"),
("Okra","வெண்டைக்காய்","भिंडी","Abelmoschus esculentus"),
("Pineapple","அன்னாசி","अनानास","Ananas comosus"),
("Grapes","திராட்சை","अंगूर","Vitis vinifera"),
("Cucumber","வெள்ளரிக்காய்","खीरा","Cucumis sativus"),
("Pumpkin","பூசணிக்காய்","कद्दू","Cucurbita moschata"),
("Bitter gourd","பாகற்காய்","करेला","Momordica charantia"),
("Ivy gourd","கோவைக்காய்","कुंदरू","Coccinia grandis")
], "Climber/Vegetable")

# ============================================================
# LOOKUP MAPS
# ============================================================

scientific_to_common = {}
plant_names = {}

for key, info in PLANT_DATABASE.items():
    scientific_to_common[info["scientific"].lower().strip()] = info["english"]
    plant_names[key] = {
        "en": info["english"],
        "ta": info["ta"],
        "hi": info["hi"]
    }

# Extra aliases
scientific_to_common.update({
    "cissus quadrangularis": "Cissus",
    "portulaca grandiflora": "Moss rose",
    "gloriosa superba": "Glory lily",
    "aegle marmelos": "Bael",
    "azadirachta indica": "Neem",
    "rosa × damascena": "Rose",
    "rosa damascena": "Rose",
    "epipremum aureum": "Money plant",
    "epipremnum aureum": "Money plant"
})

PLANT_NAME_MAP = {
    "neem": {"ta":"வேம்பு","hi":"नीम"},
    "mango": {"ta":"மாமரம்","hi":"आम"},
    "tamarind": {"ta":"புளிய மரம்","hi":"इमली"},
    "coconut palm": {"ta":"தென்னை மரம்","hi":"नारियल"},
    "jackfruit": {"ta":"பலா மரம்","hi":"कटहल"},
    "guava": {"ta":"கொய்யா","hi":"अमरूद"},
    "lemon": {"ta":"எலுமிச்சை","hi":"नींबू"},
    "papaya": {"ta":"பப்பாளி","hi":"पपीता"},
    "bael": {"ta":"வில்வம்","hi":"बेल"},
    "drumstick tree": {"ta":"முருங்கை","hi":"सहजन"},
    "curry leaf tree": {"ta":"கறிவேப்பிலை","hi":"कड़ी पत्ता"},
    "holy basil": {"ta":"துளசி","hi":"तुलसी"},
    "mint": {"ta":"புதினா","hi":"पुदीना"},
    "turmeric": {"ta":"மஞ்சள்","hi":"हल्दी"},
    "ginger": {"ta":"இஞ்சி","hi":"अदरक"},
    "coriander": {"ta":"கொத்தமல்லி","hi":"धनिया"},
    "aloe vera": {"ta":"கற்றாழை","hi":"घृतकुमारी"},
    "brahmi": {"ta":"நீர்ப்பிரம்மி","hi":"ब्राह्मी"},
    "indian pennywort": {"ta":"வல்லாரை","hi":"मंडूकपर्णी"},
    "touch-me-not": {"ta":"தொட்டாற்சிணுங்கி","hi":"लाजवंती"},
    "black pepper": {"ta":"மிளகு","hi":"काली मिर्च"},
    "betel leaf": {"ta":"வெற்றிலை","hi":"पान"},
    "lemongrass": {"ta":"எலுமிச்சைப்புல்","hi":"नींबू घास"},
    "veldt grape": {"ta":"பிரண்டை","hi":"हड़जोड़"},
    "sacred lotus": {"ta":"தாமரை","hi":"कमल"},
    "water lily": {"ta":"அல்லி","hi":"कुमुदिनी"},
    "marigold": {"ta":"செண்டுமல்லி","hi":"गेंदा"},
    "sunflower": {"ta":"சூரியகாந்தி","hi":"सूरजमुखी"},
    "moss rose": {"ta":"பத்துமணிப்பூ","hi":"लूनिया"},
    "glory lily": {"ta":"செங்காந்தள்","hi":"कलिहारी"},
    "rangoon creeper": {"ta":"ரங்கூன் மல்லி","hi":"मधुमालती"},
    "butterfly pea": {"ta":"சங்குப்பூ","hi":"अपराजिता"},
    "money plant": {"ta":"மணி பிளான்ட்","hi":"मनी प्लांट"},
    "pothos": {"ta":"மணி பிளான்ட்","hi":"मनी प्लांट"}
}

# ============================================================
# DATABASE SETUP
# ============================================================

def init_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plant_growth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_date TEXT,
            observation_day INTEGER,
            plant_pixels INTEGER,
            plant_name TEXT,
            scientific_name TEXT,
            confidence REAL
        )
    """)

    columns = [
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(plant_growth)"
        ).fetchall()
    ]

    required = {
        "upload_date": "TEXT",
        "observation_day": "INTEGER",
        "plant_pixels": "INTEGER",
        "plant_name": "TEXT",
        "scientific_name": "TEXT",
        "confidence": "REAL"
    }

    for column, datatype in required.items():
        if column not in columns:
            cursor.execute(
                f"ALTER TABLE plant_growth ADD COLUMN {column} {datatype}"
            )

    conn.commit()
    conn.close()

init_database()

# ============================================================
# IMAGE / GROWTH
# ============================================================

def get_plant_pixels(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return 0

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = (25, 40, 40)
    upper_green = (90, 255, 255)

    mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    return int(cv2.countNonZero(mask))

def save_observation(
    observation_day,
    pixels,
    plant_name,
    scientific_name,
    confidence
):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO plant_growth
        (
            upload_date,
            observation_day,
            plant_pixels,
            plant_name,
            scientific_name,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        observation_day,
        pixels,
        plant_name,
        scientific_name,
        confidence
    ))

    conn.commit()
    conn.close()

def get_growth_history(plant_name=None):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if plant_name:
        cursor.execute("""
            SELECT *
            FROM plant_growth
            WHERE LOWER(plant_name) = LOWER(?)
            ORDER BY
                CASE WHEN observation_day IS NULL THEN 999999
                     ELSE observation_day END,
                id
        """, (plant_name,))
    else:
        cursor.execute("""
            SELECT *
            FROM plant_growth
            ORDER BY id
        """)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def calculate_growth(pixels, plant_name):
    history = get_growth_history(plant_name)

    if not history:
        return 0.0

    baseline = None

    # Prefer earliest observation with valid pixels
    for row in history:
        value = row.get("plant_pixels") or 0
        if value > 0:
            baseline = value
            break

    if not baseline:
        return 0.0

    return round(
        ((pixels - baseline) / baseline) * 100,
        2
    )

# ============================================================
# SCIENTIFIC NAME NORMALIZATION
# ============================================================

def normalize_scientific_name(name):
    if not name:
        return ""
    return " ".join(
        name.strip().lower().split()
    )

# ============================================================
# PLANTNET IDENTIFICATION
# ============================================================

SPECIAL_NAMES = {
    "veldt grape": "Cissus",
    "bone setter": "Cissus",
    "cissus quadrangularis": "Cissus",
    "rose moss": "Moss rose",
    "moss rose": "Moss rose",
    "portulaca": "Moss rose",
    "portulaca grandiflora": "Moss rose",
    "flame lily": "Glory lily",
    "gloriosa": "Glory lily",
    "gloriosa superba": "Glory lily",
    "bael": "Bael",
    "aegle marmelos": "Bael",
    "wood apple": "Wood apple",
    "limonia acidissima": "Wood apple",
    "neem": "Neem",
    "azadirachta indica": "Neem",
    "rose": "Rose",
    "rosa": "Rose",
    "rosa damascena": "Rose",
    "rosa × damascena": "Rose",
    "hibiscus": "Hibiscus",
    "hibiscus rosa-sinensis": "Hibiscus",
    "jasmine": "Arabian jasmine",
    "arabian jasmine": "Arabian jasmine",
    "jasminum sambac": "Arabian jasmine",
    "spanish jasmine": "Spanish jasmine",
    "jasminum grandiflorum": "Spanish jasmine",
    "juhi jasmine": "Juhi jasmine",
    "jasminum auriculatum": "Juhi jasmine",
    "lotus": "Sacred lotus",
    "sacred lotus": "Sacred lotus",
    "nelumbo nucifera": "Sacred lotus",
    "water lily": "Water lily",
    "nymphaea": "Water lily",
    "nymphaea nouchali": "Water lily",
    "marigold": "Marigold",
    "tagetes": "Marigold",
    "tagetes erecta": "Marigold",
    "sunflower": "Sunflower",
    "helianthus annuus": "Sunflower",
    "mango": "Mango",
    "mangifera indica": "Mango",
    "banana": "Banana",
    "musa": "Banana",
    "musa acuminata": "Banana",
    "tomato": "Tomato",
    "solanum lycopersicum": "Tomato",
    "brinjal": "Brinjal",
    "eggplant": "Brinjal",
    "solanum melongena": "Brinjal",
    "chilli": "Chilli",
    "chili": "Chilli",
    "capsicum annuum": "Chilli",
    "okra": "Okra",
    "lady's finger": "Okra",
    "abelmoschus esculentus": "Okra",
    "drumstick": "Drumstick tree",
    "drumstick tree": "Drumstick tree",
    "moringa": "Drumstick tree",
    "moringa oleifera": "Drumstick tree",
    "curry leaf": "Curry leaf tree",
    "curry leaf tree": "Curry leaf tree",
    "murraya koenigii": "Curry leaf tree",
    "holy basil": "Holy basil (Tulsi)",
    "tulsi": "Holy basil (Tulsi)",
    "ocimum tenuiflorum": "Holy basil (Tulsi)",
    "mint": "Mint",
    "mentha": "Mint",
    "mentha spicata": "Mint",
    "aloe vera": "Aloe vera",
    "money plant": "Money plant",
    "pothos": "Money plant",
    "golden pothos": "Money plant",
    "epipremum aureum": "Money plant",
    "epipremnum aureum": "Money plant",
    "coconut": "Coconut palm",
    "coconut palm": "Coconut palm",
    "cocos nucifera": "Coconut palm",
    "guava": "Guava",
    "psidium guajava": "Guava",
    "papaya": "Papaya",
    "carica papaya": "Papaya",
    "lemon": "Lemon",
    "citrus limon": "Lemon",
    "jackfruit": "Jackfruit",
    "artocarpus heterophyllus": "Jackfruit",
    "tamarind": "Tamarind",
    "tamarindus indica": "Tamarind",
    "pineapple": "Pineapple",
    "ananas comosus": "Pineapple",
    "grapes": "Grapes",
    "grape": "Grapes",
    "vitis vinifera": "Grapes",
    "cucumber": "Cucumber",
    "cucumis sativus": "Cucumber",
    "pumpkin": "Pumpkin",
    "cucurbita moschata": "Pumpkin",
    "bitter gourd": "Bitter gourd",
    "momordica charantia": "Bitter gourd",
    "ivy gourd": "Ivy gourd",
    "coccinia grandis": "Ivy gourd",
    "betel leaf": "Betel leaf",
    "piper betle": "Betel leaf",
    "black pepper": "Black pepper",
    "piper nigrum": "Black pepper",
    "turmeric": "Turmeric",
    "curcuma longa": "Turmeric",
    "ginger": "Ginger",
    "zingiber officinale": "Ginger",
    "coriander": "Coriander",
    "coriandrum sativum": "Coriander",
    "brahmi": "Brahmi",
    "bacopa monnieri": "Brahmi",
    "indian pennywort": "Indian pennywort",
    "centella asiatica": "Indian pennywort",
    "touch-me-not": "Touch-me-not",
    "mimosa pudica": "Touch-me-not",
    "butterfly pea": "Butterfly pea",
    "clitoria ternatea": "Butterfly pea",
    "rangoon creeper": "Rangoon creeper",
    "combretum indicum": "Rangoon creeper"
}

def identify_plant(image_path):
    if not PLANTNET_API_KEY:
        print("PLANTNET API KEY NOT FOUND")
        return "Unknown Plant", "Unknown", 0

    url = "https://my-api.plantnet.org/v2/identify/all"

    try:
        with open(image_path, "rb") as image_file:
            files = {"images": image_file}
            data = {"organs": "auto"}

            response = requests.post(
                url,
                params={
                    "api-key": PLANTNET_API_KEY,
                    "nb-results": 5
                },
                files=files,
                data=data,
                timeout=15
            )

        print("PLANTNET STATUS:", response.status_code)

        if response.status_code != 200:
            print("PLANTNET ERROR:", response.text[:500])
            return "Unknown Plant", "Unknown", 0

        result = response.json()
        results = result.get("results", [])

        if not results:
            return "Unknown Plant", "Unknown", 0

        best = results[0]
        species = best.get("species", {})

        scientific_name = (
            species.get(
                "scientificNameWithoutAuthor",
                ""
            ) or ""
        ).strip()

        common_names = species.get(
            "commonNames",
            []
        ) or []

        plant_name = (
            common_names[0].strip()
            if common_names
            else ""
        )

        confidence = float(
            best.get("score", 0) or 0
        )

        scientific_key = normalize_scientific_name(
            scientific_name
        )
        common_key = plant_name.lower().strip()

        if scientific_key in scientific_to_common:
            plant_name = scientific_to_common[scientific_key]

        elif common_key:
            for key in PLANT_DATABASE:
                if key == common_key:
                    plant_name = PLANT_DATABASE[key]["english"]
                    break

        name_lower = plant_name.lower().strip()

        if name_lower in SPECIAL_NAMES:
            plant_name = SPECIAL_NAMES[name_lower]

        if scientific_key in SPECIAL_NAMES:
            plant_name = SPECIAL_NAMES[scientific_key]

        if not plant_name:
            plant_name = "Unknown Plant"

        print("PLANTNET COMMON:", plant_name)
        print("PLANTNET SCIENTIFIC:", scientific_name)
        print("PLANTNET CONFIDENCE:", confidence)

        return plant_name, scientific_name, confidence

    except Exception as e:
        print("PLANTNET ERROR:", e)
        return "Unknown Plant", "Unknown", 0

# ============================================================
# PLANT DETAILS / DISPLAY
# ============================================================

def get_plant_details(
    plant_name,
    scientific_name,
    confidence
):
    scientific = normalize_scientific_name(
        scientific_name
    )

    normal_name = scientific_to_common.get(
        scientific,
        (plant_name or "").strip()
    )

    if not normal_name:
        normal_name = "Unknown Plant"

    key = normal_name.lower().strip()

    # Alias handling
    alias_key = {
        "cissus": "cissus",
        "holy basil (tulsi)": "holy basil (tulsi)"
    }

    info = PLANT_DATABASE.get(key)

    if not info:
        # Search by English name
        for _, item in PLANT_DATABASE.items():
            if item["english"].lower() == key:
                info = item
                break

    if info:
        return {
            "name": info["english"],
            "tamil": info["ta"],
            "hindi": info["hi"],
            "scientific": info["scientific"],
            "category": info.get("category", "Plant"),
            "confidence": confidence
        }

    return {
        "name": normal_name,
        "tamil": normal_name,
        "hindi": normal_name,
        "scientific": scientific_name or "Unknown",
        "category": "Plant",
        "confidence": confidence
    }

def get_display_plant_name(plant_info, language):
    if language == "ta":
        return plant_info.get(
            "tamil",
            plant_info.get("name", "Unknown Plant")
        )

    if language == "hi":
        return plant_info.get(
            "hindi",
            plant_info.get("name", "Unknown Plant")
        )

    return plant_info.get(
        "name",
        "Unknown Plant"
    )

def identify_and_translate(image_path, language):
    plant_name, scientific_name, confidence = identify_plant(
        image_path
    )

    plant_info = get_plant_details(
        plant_name,
        scientific_name,
        confidence
    )

    display_name = get_display_plant_name(
        plant_info,
        language
    )

    return display_name, plant_info, confidence

# ============================================================
# CARE INFORMATION
# ============================================================

def get_care_information(normal_name, language):
    name = (normal_name or "").lower()

    # Money plant / Pothos
    if "pothos" in name or "money plant" in name:
        if language == "ta":
            return {
                "water": "மண் சற்று உலர்ந்த பிறகு தண்ணீர் கொடுக்கவும்.",
                "sunlight": "பிரகாசமான மறைமுக சூரிய ஒளி ஏற்றது.",
                "soil": "நீர் வடிகால் நன்றாக உள்ள மண் பயன்படுத்தவும்.",
                "temperature": "சுமார் 18°C முதல் 30°C வரை ஏற்றது.",
                "nutrients": "வளர்ச்சி காலத்தில் மிதமான உரம் கொடுக்கலாம்.",
                "alert": "அதிகமாக தண்ணீர் ஊற்ற வேண்டாம்."
            }

        if language == "hi":
            return {
                "water": "मिट्टी थोड़ी सूखने के बाद पानी दें।",
                "sunlight": "तेज लेकिन अप्रत्यक्ष धूप उपयुक्त है।",
                "soil": "अच्छी जल निकासी वाली मिट्टी का उपयोग करें।",
                "temperature": "लगभग 18°C से 30°C उपयुक्त है।",
                "nutrients": "वृद्धि के समय हल्की खाद दें।",
                "alert": "बहुत अधिक पानी न दें।"
            }

        return {
            "water": "Water when the soil becomes slightly dry.",
            "sunlight": "Bright indirect sunlight is suitable.",
            "soil": "Use well-draining soil.",
            "temperature": "Around 18°C to 30°C is suitable.",
            "nutrients": "Use mild fertilizer during active growth.",
            "alert": "Avoid overwatering."
        }

    # Neem
    if "neem" in name:
        if language == "ta":
            return {
                "water": "மண் காய்ந்த பிறகு தேவைக்கேற்ப தண்ணீர் கொடுக்கவும்.",
                "sunlight": "நேரடி சூரிய ஒளி நன்றாக ஏற்றது.",
                "soil": "நீர் தேங்காத நன்கு வடிகால் உள்ள மண் பயன்படுத்தவும்.",
                "temperature": "வெப்பமான காலநிலை ஏற்றது.",
                "nutrients": "தேவைக்கேற்ப இயற்கை உரம் பயன்படுத்தலாம்.",
                "alert": "அதிகப்படியான நீர்ப்பாசனத்தை தவிர்க்கவும்."
            }

        if language == "hi":
            return {
                "water": "मिट्टी सूखने के बाद आवश्यकता के अनुसार पानी दें।",
                "sunlight": "सीधी धूप अच्छी रहती है।",
                "soil": "अच्छी जल निकासी वाली मिट्टी का उपयोग करें।",
                "temperature": "गर्म जलवायु उपयुक्त है।",
                "nutrients": "आवश्यकतानुसार जैविक खाद दें।",
                "alert": "बहुत अधिक पानी देने से बचें।"
            }

        return {
            "water": "Water when the soil becomes dry.",
            "sunlight": "Direct sunlight is suitable.",
            "soil": "Use well-draining soil.",
            "temperature": "Warm conditions are suitable.",
            "nutrients": "Use organic fertilizer when needed.",
            "alert": "Avoid excessive watering."
        }

    # Generic care
    if language == "ta":
        return {
            "water": "தாவரத்தின் தேவைக்கு ஏற்ப தண்ணீர் கொடுக்கவும்.",
            "sunlight": "தாவரத்திற்கு ஏற்ற அளவு சூரிய ஒளி வழங்கவும்.",
            "soil": "நீர் தேங்காமல் நல்ல வடிகால் உள்ள மண் பயன்படுத்தவும்.",
            "temperature": "தாவரத்திற்கு ஏற்ற வெப்பநிலையை பராமரிக்கவும்.",
            "nutrients": "தேவைக்கேற்ப சமநிலையான ஊட்டச்சத்து அல்லது உரம் வழங்கவும்.",
            "alert": "தாவரத்தை தொடர்ந்து கவனித்து நோய் அல்லது அழுத்தத்தின் அறிகுறிகளை சரிபார்க்கவும்."
        }

    if language == "hi":
        return {
            "water": "पौधे की आवश्यकता के अनुसार पानी दें।",
            "sunlight": "पौधे के लिए उपयुक्त धूप दें।",
            "soil": "अच्छी जल निकासी वाली मिट्टी का उपयोग करें।",
            "temperature": "पौधे के लिए उपयुक्त तापमान बनाए रखें।",
            "nutrients": "आवश्यकतानुसार संतुलित पोषक तत्व या खाद दें।",
            "alert": "पौधे में बीमारी या तनाव के संकेतों की नियमित जाँच करें।"
        }

    return {
        "water": "Water according to the plant's needs.",
        "sunlight": "Provide suitable sunlight for the plant.",
        "soil": "Use suitable, well-draining soil.",
        "temperature": "Maintain a suitable temperature for the plant.",
        "nutrients": "Use suitable nutrients according to the plant's needs.",
        "alert": "Check the plant regularly for signs of stress or disease."
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")

# ============================================================
# ANALYZE
# ============================================================

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        language = request.form.get(
            "language",
            "en"
        )

        if language not in ("en", "ta", "hi"):
            language = "en"

        observation_raw = request.form.get(
            "observation_day",
            ""
        ).strip()

        try:
            observation_day = (
                int(observation_raw)
                if observation_raw
                else None
            )
        except ValueError:
            observation_day = None

        uploaded_file = request.files.get(
            "plant_image"
        )

        if uploaded_file is None:
            return "Please upload a plant image.", 400

        if not uploaded_file.filename:
            return "Please select a plant image.", 400

        filename = secure_filename(
            uploaded_file.filename
        )

        if not filename:
            return "Invalid file name.", 400

        # Unique file name avoids overwriting old observations
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = (
            f"{timestamp}_{filename}"
        )

        image_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        uploaded_file.save(image_path)

        # Plant area
        pixels = get_plant_pixels(
            image_path
        )

        # PlantNet
        display_name, plant_info, confidence = identify_and_translate(
            image_path,
            language
        )

        # Continuous observation
        if observation_day is None:
            history = get_growth_history(
                plant_info.get("name")
            )

            if history:
                last_day = [
                    row["observation_day"]
                    for row in history
                    if row.get("observation_day") is not None
                ]

                observation_day = (
                    max(last_day) + 1
                    if last_day
                    else 1
                )
            else:
                observation_day = 1

        # Calculate before saving so current image is compared
        # against the previous baseline.
        growth = calculate_growth(
            pixels,
            plant_info.get("name")
        )

        save_observation(
            observation_day,
            pixels,
            plant_info.get("name", display_name),
            plant_info.get("scientific", ""),
            confidence
        )

        # Recalculate history after saving
        history = get_growth_history(
            plant_info.get("name")
        )

        # If this is the first observation, growth is 0.
        if len(history) <= 1:
            growth = 0.0
            # ========================================================
        # GRAPH DATA - CONTINUOUS OBSERVATIONS
        # ========================================================

        baseline_pixels = 0

        for row in history:
            row_pixels = row.get("plant_pixels") or 0

            if row_pixels > 0:
                baseline_pixels = row_pixels
                break

        graph_data = []

        for index, row in enumerate(history):
            row_pixels = row.get("plant_pixels") or 0
            row_day = row.get("observation_day")

            if baseline_pixels > 0:
                row_growth = round(
                    ((row_pixels - baseline_pixels) / baseline_pixels) * 100,
                    2
                )
            else:
                row_growth = 0.0

            if row_day is not None:
                label = f"Day {row_day}"
            else:
                label = f"Observation {index + 1}"

            graph_data.append({
                "label": label,
                "growth": row_growth,
                "observation_day": row_day,
                "plant_pixels": row_pixels
            })
      
        care = get_care_information(
            plant_info.get("name", display_name),
            language
        )

        text = translations[language]

        # Many variable aliases are supplied so existing
        # result.html versions can use whichever names they expect.
        return render_template(
            "result.html",

            language=language,
            translations=text,
            t=text,

            plant_name=display_name,
            display_name=display_name,
            plant_info=plant_info,

            scientific_name=plant_info.get(
                "scientific",
                "Unknown"
            ),

            confidence=confidence,
            confidence_percent=round(
                confidence * 100,
                2
            ),

            plant_pixels=pixels,
            area=pixels,

            observation_day=observation_day,
            growth=growth,
            growth_percentage=growth,

            care=care,
            care_information=care,

            history=history,
            growth_history=history,
            graph_data=graph_data,

            image_filename=filename,
            image_path=image_path,

            labels=text
        )

    except Exception as e:
        print("ANALYZE ERROR:", e)
        return (
            "An error occurred while analyzing the plant. "
            "Please check the terminal for details."
        ), 500

# ============================================================
# GROWTH HISTORY PAGE
# ============================================================

@app.route("/growth")
def growth():
    history = get_growth_history()

    return render_template(
        "growth.html",
        history=history,
        growth_history=history
    )

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():
    return {
        "status": "running",
        "plant_database_count": len(PLANT_DATABASE),
        "plantnet_configured": bool(PLANTNET_API_KEY)
    }

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print("================================================")
    print("🌱 Smart Plant Care System Started!")
    print("🌿 Plant database:", len(PLANT_DATABASE))
    print("🌐 Tamil + English + Hindi supported")
    print("📷 PlantNet identification enabled")
    print("📈 Continuous plant observations enabled")
    print("================================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
