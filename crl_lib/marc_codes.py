"""
A collection of codes found in MARC records.

Example usages:

    import crl_utiles.marc_codes

    language_name = crl_utiles.marc_codes.language_codes(language_marc_code)
    country_name_without_us_states = crl_utiles.marc_codes.country_codes(country_marc_code)
    country_name_with_us_states = crl_utiles.marc_codes.country_codes_with_states(country_marc_code)

    set_of_top_level_lc_classes = crl_utiles.marc_codes.set_of_valid_lc_classes()
    is_valid_lc_class_boolean = crl_utiles.marc_codes.check_for_valid_lc_class(lc_class)

"""

def set_of_valid_lc_classes():
    """Returns a set of legal top level LC classes."""
    valid = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'Z'}
    return valid


def language_codes(code_in):

    """
    convert MARC language code to English
    """
    # remove extraneous input & normalize to lower case
    code_in = code_in.replace('/', '')
    code_in = code_in.replace('\\', '')
    code_in = code_in.lower().strip()

    if code_in == 'aar':
        return 'Afar'
    elif code_in == 'abk':
        return 'Abkhaz'
    elif code_in == 'ace':
        return 'Achinese'
    elif code_in == 'ach':
        return 'Acoli'
    elif code_in == 'ada':
        return 'Adangme'
    elif code_in == 'ady':
        return 'Adygei'
    elif code_in == 'afa':
        return 'Afroasiatic (Other)'
    elif code_in == 'afh':
        return 'Afrihili (Artificial language)'
    elif code_in == 'afr':
        return 'Afrikaans'
    elif code_in == 'ain':
        return 'Ainu'
    elif code_in == 'ajm':
        return 'Aljamía'
    elif code_in == 'aka':
        return 'Akan'
    elif code_in == 'akk':
        return 'Akkadian'
    elif code_in == 'alb':
        return 'Albanian'
    elif code_in == 'ale':
        return 'Aleut'
    elif code_in == 'alg':
        return 'Algonquian (Other)'
    elif code_in == 'alt':
        return 'Altai'
    elif code_in == 'amh':
        return 'Amharic'
    elif code_in == 'ang':
        return 'English, Old (ca. 450-1100)'
    elif code_in == 'anp':
        return 'Angika'
    elif code_in == 'apa':
        return 'Apache languages'
    elif code_in == 'ara':
        return 'Arabic'
    elif code_in == 'arc':
        return 'Aramaic'
    elif code_in == 'arg':
        return 'Aragonese'
    elif code_in == 'arm':
        return 'Armenian'
    elif code_in == 'arn':
        return 'Mapuche'
    elif code_in == 'arp':
        return 'Arapaho'
    elif code_in == 'art':
        return 'Artificial (Other)'
    elif code_in == 'arw':
        return 'Arawak'
    elif code_in == 'asm':
        return 'Assamese'
    elif code_in == 'ast':
        return 'Bable'
    elif code_in == 'ath':
        return 'Athapascan (Other)'
    elif code_in == 'aus':
        return 'Australian languages'
    elif code_in == 'ava':
        return 'Avaric'
    elif code_in == 'ave':
        return 'Avestan'
    elif code_in == 'awa':
        return 'Awadhi'
    elif code_in == 'aym':
        return 'Aymara'
    elif code_in == 'aze':
        return 'Azerbaijani'
    elif code_in == 'bad':
        return 'Banda languages'
    elif code_in == 'bai':
        return 'Bamileke languages'
    elif code_in == 'bak':
        return 'Bashkir'
    elif code_in == 'bal':
        return 'Baluchi'
    elif code_in == 'bam':
        return 'Bambara'
    elif code_in == 'ban':
        return 'Balinese'
    elif code_in == 'baq':
        return 'Basque'
    elif code_in == 'bas':
        return 'Basa'
    elif code_in == 'bat':
        return 'Baltic (Other)'
    elif code_in == 'bej':
        return 'Beja'
    elif code_in == 'bel':
        return 'Belarusian'
    elif code_in == 'bem':
        return 'Bemba'
    elif code_in == 'ben':
        return 'Bengali'
    elif code_in == 'ber':
        return 'Berber (Other)'
    elif code_in == 'bho':
        return 'Bhojpuri'
    elif code_in == 'bih':
        return 'Bihari (Other)'
    elif code_in == 'bik':
        return 'Bikol'
    elif code_in == 'bin':
        return 'Edo'
    elif code_in == 'bis':
        return 'Bislama'
    elif code_in == 'bla':
        return 'Siksika'
    elif code_in == 'bnt':
        return 'Bantu (Other)'
    elif code_in == 'bos':
        return 'Bosnian'
    elif code_in == 'bra':
        return 'Braj'
    elif code_in == 'bre':
        return 'Breton'
    elif code_in == 'btk':
        return 'Batak'
    elif code_in == 'bua':
        return 'Buriat'
    elif code_in == 'bug':
        return 'Bugis'
    elif code_in == 'bul':
        return 'Bulgarian'
    elif code_in == 'bur':
        return 'Burmese'
    elif code_in == 'byn':
        return 'Bilin'
    elif code_in == 'cad':
        return 'Caddo'
    elif code_in == 'cai':
        return 'Central American Indian (Other)'
    elif code_in == 'cam':
        return 'Khmer'
    elif code_in == 'car':
        return 'Carib'
    elif code_in == 'cat':
        return 'Catalan'
    elif code_in == 'cau':
        return 'Caucasian (Other)'
    elif code_in == 'ceb':
        return 'Cebuano'
    elif code_in == 'cel':
        return 'Celtic (Other)'
    elif code_in == 'cha':
        return 'Chamorro'
    elif code_in == 'chb':
        return 'Chibcha'
    elif code_in == 'che':
        return 'Chechen'
    elif code_in == 'chg':
        return 'Chagatai'
    elif code_in == 'chi':
        return 'Chinese'
    elif code_in == 'chk':
        return 'Chuukese'
    elif code_in == 'chm':
        return 'Mari'
    elif code_in == 'chn':
        return 'Chinook jargon'
    elif code_in == 'cho':
        return 'Choctaw'
    elif code_in == 'chp':
        return 'Chipewyan'
    elif code_in == 'chr':
        return 'Cherokee'
    elif code_in == 'chu':
        return 'Church Slavic'
    elif code_in == 'chv':
        return 'Chuvash'
    elif code_in == 'chy':
        return 'Cheyenne'
    elif code_in == 'cmc':
        return 'Chamic languages'
    elif code_in == 'cop':
        return 'Coptic'
    elif code_in == 'cor':
        return 'Cornish'
    elif code_in == 'cos':
        return 'Corsican'
    elif code_in == 'cpe':
        return 'Creoles and Pidgins, English-based (Other)'
    elif code_in == 'cpf':
        return 'Creoles and Pidgins, French-based (Other)'
    elif code_in == 'cpp':
        return 'Creoles and Pidgins, Portuguese-based (Other)'
    elif code_in == 'cre':
        return 'Cree'
    elif code_in == 'crh':
        return 'Crimean Tatar'
    elif code_in == 'crp':
        return 'Creoles and Pidgins (Other)'
    elif code_in == 'csb':
        return 'Kashubian'
    elif code_in == 'cus':
        return 'Cushitic (Other)'
    elif code_in == 'cze':
        return 'Czech'
    elif code_in == 'dak':
        return 'Dakota'
    elif code_in == 'dan':
        return 'Danish'
    elif code_in == 'dar':
        return 'Dargwa'
    elif code_in == 'day':
        return 'Dayak'
    elif code_in == 'del':
        return 'Delaware'
    elif code_in == 'den':
        return 'Slavey'
    elif code_in == 'dgr':
        return 'Dogrib'
    elif code_in == 'din':
        return 'Dinka'
    elif code_in == 'div':
        return 'Divehi'
    elif code_in == 'doi':
        return 'Dogri'
    elif code_in == 'dra':
        return 'Dravidian (Other)'
    elif code_in == 'dsb':
        return 'Lower Sorbian'
    elif code_in == 'dua':
        return 'Duala'
    elif code_in == 'dum':
        return 'Dutch, Middle (ca. 1050-1350)'
    elif code_in == 'dut':
        return 'Dutch'
    elif code_in == 'dyu':
        return 'Dyula'
    elif code_in == 'dzo':
        return 'Dzongkha'
    elif code_in == 'efi':
        return 'Efik'
    elif code_in == 'egy':
        return 'Egyptian'
    elif code_in == 'eka':
        return 'Ekajuk'
    elif code_in == 'elx':
        return 'Elamite'
    elif code_in == 'eng':
        return 'English'
    elif code_in == 'enm':
        return 'English, Middle (1100-1500)'
    elif code_in == 'epo':
        return 'Esperanto'
    elif code_in == 'esk':
        return 'Eskimo languages'
    elif code_in == 'esp':
        return 'Esperanto'
    elif code_in == 'est':
        return 'Estonian'
    elif code_in == 'eth':
        return 'Ethiopic'
    elif code_in == 'ewe':
        return 'Ewe'
    elif code_in == 'ewo':
        return 'Ewondo'
    elif code_in == 'fan':
        return 'Fang'
    elif code_in == 'fao':
        return 'Faroese'
    elif code_in == 'far':
        return 'Faroese'
    elif code_in == 'fat':
        return 'Fanti'
    elif code_in == 'fij':
        return 'Fijian'
    elif code_in == 'fil':
        return 'Filipino'
    elif code_in == 'fin':
        return 'Finnish'
    elif code_in == 'fiu':
        return 'FinnoUgrian (Other)'
    elif code_in == 'fon':
        return 'Fon'
    elif code_in == 'fre':
        return 'French'
    elif code_in == 'fri':
        return 'Frisian'
    elif code_in == 'frm':
        return 'French, Middle (ca. 1300-1600)'
    elif code_in == 'fro':
        return 'French, Old (ca. 842-1300)'
    elif code_in == 'frr':
        return 'North Frisian'
    elif code_in == 'frs':
        return 'East Frisian'
    elif code_in == 'fry':
        return 'Frisian'
    elif code_in == 'ful':
        return 'Fula'
    elif code_in == 'fur':
        return 'Friulian'
    elif code_in == 'gaa':
        return 'Gã'
    elif code_in == 'gae':
        return 'Scottish Gaelix'
    elif code_in == 'gag':
        return 'Galician'
    elif code_in == 'gal':
        return 'Oromo'
    elif code_in == 'gay':
        return 'Gayo'
    elif code_in == 'gba':
        return 'Gbaya'
    elif code_in == 'gem':
        return 'Germanic (Other)'
    elif code_in == 'geo':
        return 'Georgian'
    elif code_in == 'ger':
        return 'German'
    elif code_in == 'gez':
        return 'Ethiopic'
    elif code_in == 'gil':
        return 'Gilbertese'
    elif code_in == 'gla':
        return 'Scottish Gaelic'
    elif code_in == 'gle':
        return 'Irish'
    elif code_in == 'glg':
        return 'Galician'
    elif code_in == 'glv':
        return 'Manx'
    elif code_in == 'gmh':
        return 'German, Middle High (ca. 1050-1500)'
    elif code_in == 'goh':
        return 'German, Old High (ca. 750-1050)'
    elif code_in == 'gon':
        return 'Gondi'
    elif code_in == 'gor':
        return 'Gorontalo'
    elif code_in == 'got':
        return 'Gothic'
    elif code_in == 'grb':
        return 'Grebo'
    elif code_in == 'grc':
        return 'Greek, Ancient (to 1453)'
    elif code_in == 'gre':
        return 'Greek, Modern (1453)'
    elif code_in == 'grn':
        return 'Guarani'
    elif code_in == 'gsw':
        return 'Swiss German'
    elif code_in == 'gua':
        return 'Guarani'
    elif code_in == 'guj':
        return 'Gujarati'
    elif code_in == 'gwi':
        return 'Gwich\'in'
    elif code_in == 'hai':
        return 'Haida'
    elif code_in == 'hat':
        return 'Haitian French Creole'
    elif code_in == 'hau':
        return 'Hausa'
    elif code_in == 'haw':
        return 'Hawaiian'
    elif code_in == 'heb':
        return 'Hebrew'
    elif code_in == 'her':
        return 'Herero'
    elif code_in == 'hil':
        return 'Hiligaynon'
    elif code_in == 'him':
        return 'Western Pahari languages'
    elif code_in == 'hin':
        return 'Hindi'
    elif code_in == 'hit':
        return 'Hittite'
    elif code_in == 'hmn':
        return 'Hmong'
    elif code_in == 'hmo':
        return 'Hiri Motu'
    elif code_in == 'hrv':
        return 'Croatian'
    elif code_in == 'hsb':
        return 'Upper Sorbian'
    elif code_in == 'hun':
        return 'Hungarian'
    elif code_in == 'hup':
        return 'Hupa'
    elif code_in == 'iba':
        return 'Iban'
    elif code_in == 'ibo':
        return 'Igbo'
    elif code_in == 'ice':
        return 'Icelandic'
    elif code_in == 'ido':
        return 'Ido'
    elif code_in == 'iii':
        return 'Sichuan Yi'
    elif code_in == 'ijo':
        return 'Ijo'
    elif code_in == 'iku':
        return 'Inuktitut'
    elif code_in == 'ile':
        return 'Interlingue'
    elif code_in == 'ilo':
        return 'Iloko'
    elif code_in == 'ina':
        return 'Interlingua (International Auxiliary Language Association)'
    elif code_in == 'inc':
        return 'Indic (Other)'
    elif code_in == 'ind':
        return 'Indonesian'
    elif code_in == 'ine':
        return 'IndoEuropean (Other)'
    elif code_in == 'inh':
        return 'Ingush'
    elif code_in == 'int':
        return 'Interlingua (International Auxiliary Language Association)'
    elif code_in == 'ipk':
        return 'Inupiaq'
    elif code_in == 'ira':
        return 'Iranian (Other)'
    elif code_in == 'iri':
        return 'Irish'
    elif code_in == 'iro':
        return 'Iroquoian (Other)'
    elif code_in == 'ita':
        return 'Italian'
    elif code_in == 'jav':
        return 'Javanese'
    elif code_in == 'jbo':
        return 'Lojban (Artificial language)'
    elif code_in == 'jpn':
        return 'Japanese'
    elif code_in == 'jpr':
        return 'JudeoPersian'
    elif code_in == 'jrb':
        return 'JudeoArabic'
    elif code_in == 'kaa':
        return 'KaraKalpak'
    elif code_in == 'kab':
        return 'Kabyle'
    elif code_in == 'kac':
        return 'Kachin'
    elif code_in == 'kal':
        return 'Kalâtdlisut'
    elif code_in == 'kam':
        return 'Kamba'
    elif code_in == 'kan':
        return 'Kannada'
    elif code_in == 'kar':
        return 'Karen languages'
    elif code_in == 'kas':
        return 'Kashmiri'
    elif code_in == 'kau':
        return 'Kanuri'
    elif code_in == 'kaw':
        return 'Kawi'
    elif code_in == 'kaz':
        return 'Kazakh'
    elif code_in == 'kbd':
        return 'Kabardian'
    elif code_in == 'kha':
        return 'Khasi'
    elif code_in == 'khi':
        return 'Khoisan (Other)'
    elif code_in == 'khm':
        return 'Khmer'
    elif code_in == 'kho':
        return 'Khotanese'
    elif code_in == 'kik':
        return 'Kikuyu'
    elif code_in == 'kin':
        return 'Kinyarwanda'
    elif code_in == 'kir':
        return 'Kyrgyz'
    elif code_in == 'kmb':
        return 'Kimbundu'
    elif code_in == 'kok':
        return 'Konkani'
    elif code_in == 'kom':
        return 'Komi'
    elif code_in == 'kon':
        return 'Kongo'
    elif code_in == 'kor':
        return 'Korean'
    elif code_in == 'kos':
        return 'Kosraean'
    elif code_in == 'kpe':
        return 'Kpelle'
    elif code_in == 'krc':
        return 'KarachayBalkar'
    elif code_in == 'krl':
        return 'Karelian'
    elif code_in == 'kro':
        return 'Kru (Other)'
    elif code_in == 'kru':
        return 'Kurukh'
    elif code_in == 'kua':
        return 'Kuanyama'
    elif code_in == 'kum':
        return 'Kumyk'
    elif code_in == 'kur':
        return 'Kurdish'
    elif code_in == 'kus':
        return 'Kusaie'
    elif code_in == 'kut':
        return 'Kootenai'
    elif code_in == 'lad':
        return 'Ladino'
    elif code_in == 'lah':
        return 'Lahndā'
    elif code_in == 'lam':
        return 'Lamba (Zambia and Congo)'
    elif code_in == 'lan':
        return 'Occitan (post 1500)'
    elif code_in == 'lao':
        return 'Lao'
    elif code_in == 'lap':
        return 'Sami'
    elif code_in == 'lat':
        return 'Latin'
    elif code_in == 'lav':
        return 'Latvian'
    elif code_in == 'lez':
        return 'Lezgian'
    elif code_in == 'lim':
        return 'Limburgish'
    elif code_in == 'lin':
        return 'Lingala'
    elif code_in == 'lit':
        return 'Lithuanian'
    elif code_in == 'lol':
        return 'MongoNkundu'
    elif code_in == 'loz':
        return 'Lozi'
    elif code_in == 'ltz':
        return 'Luxembourgish'
    elif code_in == 'lua':
        return 'LubaLulua'
    elif code_in == 'lub':
        return 'LubaKatanga'
    elif code_in == 'lug':
        return 'Ganda'
    elif code_in == 'lui':
        return 'Luiseño'
    elif code_in == 'lun':
        return 'Lunda'
    elif code_in == 'luo':
        return 'Luo (Kenya and Tanzania)'
    elif code_in == 'lus':
        return 'Lushai'
    elif code_in == 'mac':
        return 'Macedonian'
    elif code_in == 'mad':
        return 'Madurese'
    elif code_in == 'mag':
        return 'Magahi'
    elif code_in == 'mah':
        return 'Marshallese'
    elif code_in == 'mai':
        return 'Maithili'
    elif code_in == 'mak':
        return 'Makasar'
    elif code_in == 'mal':
        return 'Malayalam'
    elif code_in == 'man':
        return 'Mandingo'
    elif code_in == 'mao':
        return 'Maori'
    elif code_in == 'map':
        return 'Austronesian (Other)'
    elif code_in == 'mar':
        return 'Marathi'
    elif code_in == 'mas':
        return 'Maasai'
    elif code_in == 'max':
        return 'Manx'
    elif code_in == 'may':
        return 'Malay'
    elif code_in == 'mdf':
        return 'Moksha'
    elif code_in == 'mdr':
        return 'Mandar'
    elif code_in == 'men':
        return 'Mende'
    elif code_in == 'mga':
        return 'Irish, Middle (ca. 1100-1550)'
    elif code_in == 'mic':
        return 'Micmac'
    elif code_in == 'min':
        return 'Minangkabau'
    elif code_in == 'mis':
        return 'Miscellaneous languages'
    elif code_in == 'mkh':
        return 'MonKhmer (Other)'
    elif code_in == 'mla':
        return 'Malagasy'
    elif code_in == 'mlg':
        return 'Malagasy'
    elif code_in == 'mlt':
        return 'Maltese'
    elif code_in == 'mnc':
        return 'Manchu'
    elif code_in == 'mni':
        return 'Manipuri'
    elif code_in == 'mno':
        return 'Manobo languages'
    elif code_in == 'moh':
        return 'Mohawk'
    elif code_in == 'mol':
        return 'Moldavian'
    elif code_in == 'mon':
        return 'Mongolian'
    elif code_in == 'mos':
        return 'Mooré'
    elif code_in == 'mul':
        return 'Multiple languages'
    elif code_in == 'mun':
        return 'Munda (Other)'
    elif code_in == 'mus':
        return 'Creek'
    elif code_in == 'mwl':
        return 'Mirandese'
    elif code_in == 'mwr':
        return 'Marwari'
    elif code_in == 'myn':
        return 'Mayan languages'
    elif code_in == 'myv':
        return 'Erzya'
    elif code_in == 'nah':
        return 'Nahuatl'
    elif code_in == 'nai':
        return 'North American Indian (Other)'
    elif code_in == 'nap':
        return 'Neapolitan Italian'
    elif code_in == 'nau':
        return 'Nauru'
    elif code_in == 'nav':
        return 'Navajo'
    elif code_in == 'nbl':
        return 'Ndebele (South Africa)'
    elif code_in == 'nde':
        return 'Ndebele (Zimbabwe)'
    elif code_in == 'ndo':
        return 'Ndonga'
    elif code_in == 'nds':
        return 'Low German'
    elif code_in == 'nep':
        return 'Nepali'
    elif code_in == 'new':
        return 'Newari'
    elif code_in == 'nia':
        return 'Nias'
    elif code_in == 'nic':
        return 'NigerKordofanian (Other)'
    elif code_in == 'niu':
        return 'Niuean'
    elif code_in == 'nno':
        return 'Norwegian (Nynorsk)'
    elif code_in == 'nob':
        return 'Norwegian (Bokmål)'
    elif code_in == 'nog':
        return 'Nogai'
    elif code_in == 'non':
        return 'Old Norse'
    elif code_in == 'nor':
        return 'Norwegian'
    elif code_in == 'nqo':
        return 'N\'Ko'
    elif code_in == 'nso':
        return 'Northern Sotho'
    elif code_in == 'nub':
        return 'Nubian languages'
    elif code_in == 'nwc':
        return 'Newari, Old'
    elif code_in == 'nya':
        return 'Nyanja'
    elif code_in == 'nym':
        return 'Nyamwezi'
    elif code_in == 'nyn':
        return 'Nyankole'
    elif code_in == 'nyo':
        return 'Nyoro'
    elif code_in == 'nzi':
        return 'Nzima'
    elif code_in == 'oci':
        return 'Occitan (post1500)'
    elif code_in == 'oji':
        return 'Ojibwa'
    elif code_in == 'ori':
        return 'Oriya'
    elif code_in == 'orm':
        return 'Oromo'
    elif code_in == 'osa':
        return 'Osage'
    elif code_in == 'oss':
        return 'Ossetic'
    elif code_in == 'ota':
        return 'Turkish, Ottoman'
    elif code_in == 'oto':
        return 'Otomian languages'
    elif code_in == 'paa':
        return 'Papuan (Other)'
    elif code_in == 'pag':
        return 'Pangasinan'
    elif code_in == 'pal':
        return 'Pahlavi'
    elif code_in == 'pam':
        return 'Pampanga'
    elif code_in == 'pan':
        return 'Panjabi'
    elif code_in == 'pap':
        return 'Papiamento'
    elif code_in == 'pau':
        return 'Palauan'
    elif code_in == 'peo':
        return 'Old Persian (ca. 600-400 B.C.)'
    elif code_in == 'per':
        return 'Persian'
    elif code_in == 'phi':
        return 'Philippine (Other)'
    elif code_in == 'phn':
        return 'Phoenician'
    elif code_in == 'pli':
        return 'Pali'
    elif code_in == 'pol':
        return 'Polish'
    elif code_in == 'pon':
        return 'Pohnpeian'
    elif code_in == 'por':
        return 'Portuguese'
    elif code_in == 'pra':
        return 'Prakrit languages'
    elif code_in == 'pro':
        return 'Provençal (to 1500)'
    elif code_in == 'pus':
        return 'Pushto'
    elif code_in == 'que':
        return 'Quechua'
    elif code_in == 'raj':
        return 'Rajasthani'
    elif code_in == 'rap':
        return 'Rapanui'
    elif code_in == 'rar':
        return 'Rarotongan'
    elif code_in == 'roa':
        return 'Romance (Other)'
    elif code_in == 'roh':
        return 'RaetoRomance'
    elif code_in == 'rom':
        return 'Romani'
    elif code_in == 'rum':
        return 'Romanian'
    elif code_in == 'run':
        return 'Rundi'
    elif code_in == 'rup':
        return 'Aromanian'
    elif code_in == 'rus':
        return 'Russian'
    elif code_in == 'sad':
        return 'Sandawe'
    elif code_in == 'sag':
        return 'Sango (Ubangi Creole)'
    elif code_in == 'sah':
        return 'Yakut'
    elif code_in == 'sai':
        return 'South American Indian (Other)'
    elif code_in == 'sal':
        return 'Salishan languages'
    elif code_in == 'sam':
        return 'Samaritan Aramaic'
    elif code_in == 'san':
        return 'Sanskrit'
    elif code_in == 'sao':
        return 'Samoan'
    elif code_in == 'sas':
        return 'Sasak'
    elif code_in == 'sat':
        return 'Santali'
    elif code_in == 'scc':
        return 'Serbian'
    elif code_in == 'scn':
        return 'Sicilian Italian'
    elif code_in == 'sco':
        return 'Scots'
    elif code_in == 'scr':
        return 'Croatian'
    elif code_in == 'sel':
        return 'Selkup'
    elif code_in == 'sem':
        return 'Semitic (Other)'
    elif code_in == 'sga':
        return 'Irish, Old (to 1100)'
    elif code_in == 'sgn':
        return 'Sign languages'
    elif code_in == 'shn':
        return 'Shan'
    elif code_in == 'sho':
        return 'Shona'
    elif code_in == 'sid':
        return 'Sidamo'
    elif code_in == 'sin':
        return 'Sinhalese'
    elif code_in == 'sio':
        return 'Siouan (Other)'
    elif code_in == 'sit':
        return 'SinoTibetan (Other)'
    elif code_in == 'sla':
        return 'Slavic (Other)'
    elif code_in == 'slo':
        return 'Slovak'
    elif code_in == 'slv':
        return 'Slovenian'
    elif code_in == 'sma':
        return 'Southern Sami'
    elif code_in == 'sme':
        return 'Northern Sami'
    elif code_in == 'smi':
        return 'Sami'
    elif code_in == 'smj':
        return 'Lule Sami'
    elif code_in == 'smn':
        return 'Inari Sami'
    elif code_in == 'smo':
        return 'Samoan'
    elif code_in == 'sms':
        return 'Skolt Sami'
    elif code_in == 'sna':
        return 'Shona'
    elif code_in == 'snd':
        return 'Sindhi'
    elif code_in == 'snh':
        return 'Sinhalese'
    elif code_in == 'snk':
        return 'Soninke'
    elif code_in == 'sog':
        return 'Sogdian'
    elif code_in == 'som':
        return 'Somali'
    elif code_in == 'son':
        return 'Songhai'
    elif code_in == 'sot':
        return 'Sotho'
    elif code_in == 'spa':
        return 'Spanish'
    elif code_in == 'srd':
        return 'Sardinian'
    elif code_in == 'srn':
        return 'Sranan'
    elif code_in == 'srp':
        return 'Serbian'
    elif code_in == 'srr':
        return 'Serer'
    elif code_in == 'ssa':
        return 'NiloSaharan (Other)'
    elif code_in == 'sso':
        return 'Sotho'
    elif code_in == 'ssw':
        return 'Swazi'
    elif code_in == 'suk':
        return 'Sukuma'
    elif code_in == 'sun':
        return 'Sundanese'
    elif code_in == 'sus':
        return 'Susu'
    elif code_in == 'sux':
        return 'Sumerian'
    elif code_in == 'swa':
        return 'Swahili'
    elif code_in == 'swe':
        return 'Swedish'
    elif code_in == 'swz':
        return 'Swazi'
    elif code_in == 'syc':
        return 'Syriac'
    elif code_in == 'syr':
        return 'Syriac, Modern'
    elif code_in == 'tag':
        return 'Tagalog'
    elif code_in == 'tah':
        return 'Tahitian'
    elif code_in == 'tai':
        return 'Tai (Other)'
    elif code_in == 'taj':
        return 'Tajik'
    elif code_in == 'tam':
        return 'Tamil'
    elif code_in == 'tar':
        return 'Tatar'
    elif code_in == 'tat':
        return 'Tatar'
    elif code_in == 'tel':
        return 'Telugu'
    elif code_in == 'tem':
        return 'Temne'
    elif code_in == 'ter':
        return 'Terena'
    elif code_in == 'tet':
        return 'Tetum'
    elif code_in == 'tgk':
        return 'Tajik'
    elif code_in == 'tgl':
        return 'Tagalog'
    elif code_in == 'tha':
        return 'Thai'
    elif code_in == 'tib':
        return 'Tibetan'
    elif code_in == 'tig':
        return 'Tigré'
    elif code_in == 'tir':
        return 'Tigrinya'
    elif code_in == 'tiv':
        return 'Tiv'
    elif code_in == 'tkl':
        return 'Tokelauan'
    elif code_in == 'tlh':
        return 'Klingon (Artificial language)'
    elif code_in == 'tli':
        return 'Tlingit'
    elif code_in == 'tmh':
        return 'Tamashek'
    elif code_in == 'tog':
        return 'Tonga (Nyasa)'
    elif code_in == 'ton':
        return 'Tongan'
    elif code_in == 'tpi':
        return 'Tok Pisin'
    elif code_in == 'tru':
        return 'Truk'
    elif code_in == 'tsi':
        return 'Tsimshian'
    elif code_in == 'tsn':
        return 'Tswana'
    elif code_in == 'tso':
        return 'Tsonga'
    elif code_in == 'tsw':
        return 'Tswana'
    elif code_in == 'tuk':
        return 'Turkmen'
    elif code_in == 'tum':
        return 'Tumbuka'
    elif code_in == 'tup':
        return 'Tupi languages'
    elif code_in == 'tur':
        return 'Turkish'
    elif code_in == 'tut':
        return 'Altaic (Other)'
    elif code_in == 'tvl':
        return 'Tuvaluan'
    elif code_in == 'twi':
        return 'Twi'
    elif code_in == 'tyv':
        return 'Tuvinian'
    elif code_in == 'udm':
        return 'Udmurt'
    elif code_in == 'uga':
        return 'Ugaritic'
    elif code_in == 'uig':
        return 'Uighur'
    elif code_in == 'ukr':
        return 'Ukrainian'
    elif code_in == 'umb':
        return 'Umbundu'
    elif code_in == 'und':
        return 'Undetermined'
    elif code_in == 'urd':
        return 'Urdu'
    elif code_in == 'uzb':
        return 'Uzbek'
    elif code_in == 'vai':
        return 'Vai'
    elif code_in == 'ven':
        return 'Venda'
    elif code_in == 'vie':
        return 'Vietnamese'
    elif code_in == 'vol':
        return 'Volapük'
    elif code_in == 'vot':
        return 'Votic'
    elif code_in == 'wak':
        return 'Wakashan languages'
    elif code_in == 'wal':
        return 'Wolayta'
    elif code_in == 'war':
        return 'Waray'
    elif code_in == 'was':
        return 'Washoe'
    elif code_in == 'wel':
        return 'Welsh'
    elif code_in == 'wen':
        return 'Sorbian (Other)'
    elif code_in == 'wln':
        return 'Walloon'
    elif code_in == 'wol':
        return 'Wolof'
    elif code_in == 'xal':
        return 'Oirat'
    elif code_in == 'xho':
        return 'Xhosa'
    elif code_in == 'yao':
        return 'Yao (Africa)'
    elif code_in == 'yap':
        return 'Yapese'
    elif code_in == 'yid':
        return 'Yiddish'
    elif code_in == 'yor':
        return 'Yoruba'
    elif code_in == 'ypk':
        return 'Yupik languages'
    elif code_in == 'zap':
        return 'Zapotec'
    elif code_in == 'zbl':
        return 'Blissymbolics'
    elif code_in == 'zen':
        return 'Zenaga'
    elif code_in == 'zha':
        return 'Zhuang'
    elif code_in == 'znd':
        return 'Zande languages'
    elif code_in == 'zul':
        return 'Zulu'
    elif code_in == 'zun':
        return 'Zuni'
    elif code_in == 'zxx':
        return 'No linguistic content'
    elif code_in == 'zza':
        return 'Zaza'


# ------------------------------------------------------------------------------


def country_codes(code_in):
    """
    MARC country code to country name
    Returns all US states & Canadian provinces as "USA" or "Canada" respectively
    So 'nyu' returns "USA" rather than "New York (State)"
    """

    code_in = code_in.lower().strip()

    if code_in == 'aa':
        return 'Albania'
    elif code_in == 'abc':
        return 'Canada'
    elif code_in == 'ac':
        return 'Ashmore and Cartier Islands'
    elif code_in == 'aca':
        return 'Australia'
    elif code_in == 'ae':
        return 'Algeria'
    elif code_in == 'af':
        return 'Afghanistan'
    elif code_in == 'ag':
        return 'Argentina'
    elif code_in == 'ai':
        return 'Anguilla'
    elif code_in == 'ai':
        return 'Armenia (Republic)'
    elif code_in == 'air':
        return 'USSR'
    elif code_in == 'aj':
        return 'Azerbaijan'
    elif code_in == 'ajr':
        return 'USSR'
    elif code_in == 'aku':
        return 'USA'
    elif code_in == 'alu':
        return 'USA'
    elif code_in == 'am':
        return 'Anguilla'
    elif code_in == 'an':
        return 'Andorra'
    elif code_in == 'ao':
        return 'Angola'
    elif code_in == 'aq':
        return 'Antigua and Barbuda'
    elif code_in == 'aru':
        return 'USA'
    elif code_in == 'as':
        return 'American Samoa'
    elif code_in == 'at':
        return 'Australia'
    elif code_in == 'au':
        return 'Austria'
    elif code_in == 'aw':
        return 'Aruba'
    elif code_in == 'ay':
        return 'Antarctica'
    elif code_in == 'azu':
        return 'USA'
    elif code_in == 'ba':
        return 'Bahrain'
    elif code_in == 'bb':
        return 'Barbados'
    elif code_in == 'bcc':
        return 'Canada'
    elif code_in == 'bd':
        return 'Burundi'
    elif code_in == 'be':
        return 'Belgium'
    elif code_in == 'bf':
        return 'Bahamas'
    elif code_in == 'bg':
        return 'Bangladesh'
    elif code_in == 'bh':
        return 'Belize'
    elif code_in == 'bi':
        return 'British Indian Ocean Territory'
    elif code_in == 'bl':
        return 'Brazil'
    elif code_in == 'bm':
        return 'Bermuda Islands'
    elif code_in == 'bn':
        return 'Bosnia and Hercegovina'
    elif code_in == 'bo':
        return 'Bolivia'
    elif code_in == 'bp':
        return 'Solomon Islands'
    elif code_in == 'br':
        return 'Burma'
    elif code_in == 'bs':
        return 'Botswana'
    elif code_in == 'bt':
        return 'Bhutan'
    elif code_in == 'bu':
        return 'Bulgaria'
    elif code_in == 'bv':
        return 'Bouvet Island'
    elif code_in == 'bw':
        return 'Belarus'
    elif code_in == 'bwr':
        return 'USSR'
    elif code_in == 'bx':
        return 'Brunei'
    elif code_in == 'ca':
        return 'Caribbean Netherlands'
    elif code_in == 'cau':
        return 'USA'
    elif code_in == 'cb':
        return 'Cambodia'
    elif code_in == 'cc':
        return 'China'
    elif code_in == 'cd':
        return 'Chad'
    elif code_in == 'ce':
        return 'Sri Lanka'
    elif code_in == 'cf':
        return 'Congo (Brazzaville)'
    elif code_in == 'cg':
        return 'Congo (Democratic Republic)'
    elif code_in == 'ch':
        return 'China (Republic : 1949- )'
    elif code_in == 'ci':
        return 'Croatia'
    elif code_in == 'cj':
        return 'Cayman Islands'
    elif code_in == 'ck':
        return 'Colombia'
    elif code_in == 'cl':
        return 'Chile'
    elif code_in == 'cm':
        return 'Cameroon'
    elif code_in == 'cn':
        return 'Canada'
    elif code_in == 'co':
        return 'Curaçao'
    elif code_in == 'cou':
        return 'USA'
    elif code_in == 'cp':
        return 'Canton and Enderbury Islands'
    elif code_in == 'cq':
        return 'Comoros'
    elif code_in == 'cr':
        return 'Costa Rica'
    elif code_in == 'cs':
        return 'Czechoslovakia'
    elif code_in == 'ctu':
        return 'USA'
    elif code_in == 'cu':
        return 'Cuba'
    elif code_in == 'cv':
        return 'Cape Verde'
    elif code_in == 'cw':
        return 'Cook Islands'
    elif code_in == 'cx':
        return 'Central African Republic'
    elif code_in == 'cy':
        return 'Cyprus'
    elif code_in == 'cz':
        return 'Canal Zone'
    elif code_in == 'dcu':
        return 'USA'
    elif code_in == 'deu':
        return 'USA'
    elif code_in == 'dk':
        return 'Denmark'
    elif code_in == 'dm':
        return 'Benin'
    elif code_in == 'dq':
        return 'Dominica'
    elif code_in == 'dr':
        return 'Dominican Republic'
    elif code_in == 'ea':
        return 'Eritrea'
    elif code_in == 'ec':
        return 'Ecuador'
    elif code_in == 'eg':
        return 'Equatorial Guinea'
    elif code_in == 'em':
        return 'Timor-Leste'
    elif code_in == 'enk':
        return 'England'
    elif code_in == 'er':
        return 'Estonia'
    elif code_in == 'err':
        return 'USSR'
    elif code_in == 'es':
        return 'El Salvador'
    elif code_in == 'et':
        return 'Ethiopia'
    elif code_in == 'fa':
        return 'Faroe Islands'
    elif code_in == 'fg':
        return 'French Guiana'
    elif code_in == 'fi':
        return 'Finland'
    elif code_in == 'fj':
        return 'Fiji'
    elif code_in == 'fk':
        return 'Falkland Islands'
    elif code_in == 'flu':
        return 'USA'
    elif code_in == 'fm':
        return 'Micronesia (Federated States)'
    elif code_in == 'fp':
        return 'French Polynesia'
    elif code_in == 'fr':
        return 'France'
    elif code_in == 'fs':
        return 'Terres australes et antarctiques françaises'
    elif code_in == 'ft':
        return 'Djibouti'
    elif code_in == 'gau':
        return 'USA'
    elif code_in == 'gb':
        return 'Kiribati'
    elif code_in == 'gd':
        return 'Grenada'
    elif code_in == 'ge':
        return 'Germany (East)'
    elif code_in == 'gh':
        return 'Ghana'
    elif code_in == 'gi':
        return 'Gibraltar'
    elif code_in == 'gl':
        return 'Greenland'
    elif code_in == 'gm':
        return 'Gambia'
    elif code_in == 'gn':
        return 'Gilbert and Ellice Islands'
    elif code_in == 'go':
        return 'Gabon'
    elif code_in == 'gp':
        return 'Guadeloupe'
    elif code_in == 'gr':
        return 'Greece'
    elif code_in == 'gs':
        return 'Georgia (Republic)'
    elif code_in == 'gsr':
        return 'USSR'
    elif code_in == 'gt':
        return 'Guatemala'
    elif code_in == 'gu':
        return 'Guam'
    elif code_in == 'gv':
        return 'Guinea'
    elif code_in == 'gw':
        return 'Germany'
    elif code_in == 'gy':
        return 'Guyana'
    elif code_in == 'gz':
        return 'Gaza Strip'
    elif code_in == 'hiu':
        return 'USA'
    elif code_in == 'hk':
        return 'Hong Kong'
    elif code_in == 'hm':
        return 'Heard and McDonald Islands'
    elif code_in == 'ho':
        return 'Honduras'
    elif code_in == 'ht':
        return 'Haiti'
    elif code_in == 'hu':
        return 'Hungary'
    elif code_in == 'iau':
        return 'USA'
    elif code_in == 'ic':
        return 'Iceland'
    elif code_in == 'idu':
        return 'USA'
    elif code_in == 'ie':
        return 'Ireland'
    elif code_in == 'ii':
        return 'India'
    elif code_in == 'ilu':
        return 'USA'
    elif code_in == 'inu':
        return 'USA'
    elif code_in == 'io':
        return 'Indonesia'
    elif code_in == 'iq':
        return 'Iraq'
    elif code_in == 'ir':
        return 'Iran'
    elif code_in == 'is':
        return 'Israel'
    elif code_in == 'it':
        return 'Italy'
    elif code_in == 'iu':
        return 'Israel-Syria Demilitarized Zones'
    elif code_in == 'iv':
        return 'Côte d\'Ivoire'
    elif code_in == 'iw':
        return 'Israel-Jordan Demilitarized Zones'
    elif code_in == 'iy':
        return 'Iraq-Saudi Arabia Neutral Zone'
    elif code_in == 'ja':
        return 'Japan'
    elif code_in == 'ji':
        return 'Johnston Atoll'
    elif code_in == 'jm':
        return 'Jamaica'
    elif code_in == 'jn':
        return 'Jan Mayen'
    elif code_in == 'jo':
        return 'Jordan'
    elif code_in == 'ke':
        return 'Kenya'
    elif code_in == 'kg':
        return 'Kyrgyzstan'
    elif code_in == 'kgr':
        return 'USSR'
    elif code_in == 'kn':
        return 'Korea (North)'
    elif code_in == 'ko':
        return 'Korea (South)'
    elif code_in == 'ksu':
        return 'USA'
    elif code_in == 'ku':
        return 'Kuwait'
    elif code_in == 'kv':
        return 'Kosovo'
    elif code_in == 'kyu':
        return 'USA'
    elif code_in == 'kz':
        return 'Kazakhstan'
    elif code_in == 'kzr':
        return 'USSR'
    elif code_in == 'lau':
        return 'USA'
    elif code_in == 'lb':
        return 'Liberia'
    elif code_in == 'le':
        return 'Lebanon'
    elif code_in == 'lh':
        return 'Liechtenstein'
    elif code_in == 'li':
        return 'Lithuania'
    elif code_in == 'lir':
        return 'USSR'
    elif code_in == 'ln':
        return 'Central and Southern Line Islands'
    elif code_in == 'lo':
        return 'Lesotho'
    elif code_in == 'ls':
        return 'Laos'
    elif code_in == 'lu':
        return 'Luxembourg'
    elif code_in == 'lv':
        return 'Latvia'
    elif code_in == 'lvr':
        return 'USSR'
    elif code_in == 'ly':
        return 'Libya'
    elif code_in == 'mau':
        return 'USA'
    elif code_in == 'mbc':
        return 'Canada'
    elif code_in == 'mc':
        return 'Monaco'
    elif code_in == 'mdu':
        return 'USA'
    elif code_in == 'meu':
        return 'USA'
    elif code_in == 'mf':
        return 'Mauritius'
    elif code_in == 'mg':
        return 'Madagascar'
    elif code_in == 'mh':
        return 'Macao'
    elif code_in == 'miu':
        return 'USA'
    elif code_in == 'mj':
        return 'Montserrat'
    elif code_in == 'mk':
        return 'Oman'
    elif code_in == 'ml':
        return 'Mali'
    elif code_in == 'mm':
        return 'Malta'
    elif code_in == 'mnu':
        return 'USA'
    elif code_in == 'mo':
        return 'Montenegro'
    elif code_in == 'mou':
        return 'USA'
    elif code_in == 'mp':
        return 'Mongolia'
    elif code_in == 'mq':
        return 'Martinique'
    elif code_in == 'mr':
        return 'Morocco'
    elif code_in == 'msu':
        return 'USA'
    elif code_in == 'mtu':
        return 'USA'
    elif code_in == 'mu':
        return 'Mauritania'
    elif code_in == 'mv':
        return 'Moldova'
    elif code_in == 'mvr':
        return 'USSR'
    elif code_in == 'mw':
        return 'Malawi'
    elif code_in == 'mx':
        return 'Mexico'
    elif code_in == 'my':
        return 'Malaysia'
    elif code_in == 'mz':
        return 'Mozambique'
    elif code_in == 'na':
        return 'Netherlands Antilles'
    elif code_in == 'nbu':
        return 'USA'
    elif code_in == 'ncu':
        return 'USA'
    elif code_in == 'ndu':
        return 'USA'
    elif code_in == 'ne':
        return 'Netherlands'
    elif code_in == 'nfc':
        return 'Canada'
    elif code_in == 'ng':
        return 'Niger'
    elif code_in == 'nhu':
        return 'USA'
    elif code_in == 'nik':
        return 'Northern Ireland'
    elif code_in == 'nju':
        return 'USA'
    elif code_in == 'nkc':
        return 'Canada'
    elif code_in == 'nl':
        return 'New Caledonia'
    elif code_in == 'nm':
        return 'Northern Mariana Islands'
    elif code_in == 'nmu':
        return 'USA'
    elif code_in == 'nn':
        return 'Vanuatu'
    elif code_in == 'no':
        return 'Norway'
    elif code_in == 'np':
        return 'Nepal'
    elif code_in == 'nq':
        return 'Nicaragua'
    elif code_in == 'nr':
        return 'Nigeria'
    elif code_in == 'nsc':
        return 'Canada'
    elif code_in == 'ntc':
        return 'Canada'
    elif code_in == 'nu':
        return 'Nauru'
    elif code_in == 'nuc':
        return 'Canada'
    elif code_in == 'nvu':
        return 'USA'
    elif code_in == 'nw':
        return 'Northern Mariana Islands'
    elif code_in == 'nx':
        return 'Norfolk Island'
    elif code_in == 'nyu':
        return 'USA'
    elif code_in == 'nz':
        return 'New Zealand'
    elif code_in == 'ohu':
        return 'USA'
    elif code_in == 'oku':
        return 'USA'
    elif code_in == 'onc':
        return 'Canada'
    elif code_in == 'oru':
        return 'USA'
    elif code_in == 'ot':
        return 'Mayotte'
    elif code_in == 'pau':
        return 'USA'
    elif code_in == 'pc':
        return 'Pitcairn Island'
    elif code_in == 'pe':
        return 'Peru'
    elif code_in == 'pf':
        return 'Paracel Islands'
    elif code_in == 'pg':
        return 'Guinea-Bissau'
    elif code_in == 'ph':
        return 'Philippines'
    elif code_in == 'pic':
        return 'Canada'
    elif code_in == 'pk':
        return 'Pakistan'
    elif code_in == 'pl':
        return 'Poland'
    elif code_in == 'pn':
        return 'Panama'
    elif code_in == 'po':
        return 'Portugal'
    elif code_in == 'pp':
        return 'Papua New Guinea'
    elif code_in == 'pr':
        return 'Puerto Rico'
    elif code_in == 'pt':
        return 'Portuguese Timor'
    elif code_in == 'pw':
        return 'Palau'
    elif code_in == 'py':
        return 'Paraguay'
    elif code_in == 'qa':
        return 'Qatar'
    elif code_in == 'qea':
        return 'Australia'
    elif code_in == 'quc':
        return 'Canada'
    elif code_in == 'rb':
        return 'Serbia'
    elif code_in == 're':
        return 'Réunion'
    elif code_in == 'rh':
        return 'Zimbabwe'
    elif code_in == 'riu':
        return 'USA'
    elif code_in == 'rm':
        return 'Romania'
    elif code_in == 'ru':
        return 'Russia (Federation)'
    elif code_in == 'rur':
        return 'USSR'
    elif code_in == 'rw':
        return 'Rwanda'
    elif code_in == 'ry':
        return 'Ryukyu Islands, Southern'
    elif code_in == 'sa':
        return 'South Africa'
    elif code_in == 'sb':
        return 'Svalbard'
    elif code_in == 'sc':
        return 'Saint-Barthélemy'
    elif code_in == 'scu':
        return 'USA'
    elif code_in == 'sd':
        return 'South Sudan'
    elif code_in == 'sdu':
        return 'USA'
    elif code_in == 'se':
        return 'Seychelles'
    elif code_in == 'sf':
        return 'Sao Tome and Principe'
    elif code_in == 'sg':
        return 'Senegal'
    elif code_in == 'sh':
        return 'Spanish North Africa'
    elif code_in == 'si':
        return 'Singapore'
    elif code_in == 'sj':
        return 'Sudan'
    elif code_in == 'sk':
        return 'Sikkim'
    elif code_in == 'sl':
        return 'Sierra Leone'
    elif code_in == 'sm':
        return 'San Marino'
    elif code_in == 'sn':
        return 'Sint Maarten'
    elif code_in == 'snc':
        return 'Canada'
    elif code_in == 'so':
        return 'Somalia'
    elif code_in == 'sp':
        return 'Spain'
    elif code_in == 'sq':
        return 'Swaziland'
    elif code_in == 'sr':
        return 'Surinam'
    elif code_in == 'ss':
        return 'Western Sahara'
    elif code_in == 'st':
        return 'Saint-Martin'
    elif code_in == 'stk':
        return 'Scotland'
    elif code_in == 'su':
        return 'Saudi Arabia'
    elif code_in == 'sv':
        return 'Swan Islands'
    elif code_in == 'sw':
        return 'Sweden'
    elif code_in == 'sx':
        return 'Namibia'
    elif code_in == 'sy':
        return 'Syria'
    elif code_in == 'sz':
        return 'Switzerland'
    elif code_in == 'ta':
        return 'Tajikistan'
    elif code_in == 'tar':
        return 'USSR'
    elif code_in == 'tc':
        return 'Turks and Caicos Islands'
    elif code_in == 'tg':
        return 'Togo'
    elif code_in == 'th':
        return 'Thailand'
    elif code_in == 'ti':
        return 'Tunisia'
    elif code_in == 'tk':
        return 'Turkmenistan'
    elif code_in == 'tkr':
        return 'USSR'
    elif code_in == 'tl':
        return 'Tokelau'
    elif code_in == 'tma':
        return 'Australia'
    elif code_in == 'tnu':
        return 'USA'
    elif code_in == 'to':
        return 'Tonga'
    elif code_in == 'tr':
        return 'Trinidad and Tobago'
    elif code_in == 'ts':
        return 'United Arab Emirates'
    elif code_in == 'tt':
        return 'Trust Territory of the Pacific Islands'
    elif code_in == 'tu':
        return 'Turkey'
    elif code_in == 'tv':
        return 'Tuvalu'
    elif code_in == 'txu':
        return 'USA'
    elif code_in == 'tz':
        return 'Tanzania'
    elif code_in == 'ua':
        return 'Egypt'
    elif code_in == 'uc':
        return 'United States Misc. Caribbean Islands'
    elif code_in == 'ug':
        return 'Uganda'
    elif code_in == 'ui':
        return 'United Kingdom Misc. Islands'
    elif code_in == 'uik':
        return 'United Kingdom Misc. Islands'
    elif code_in == 'uk':
        return 'United Kingdom'
    elif code_in == 'un':
        return 'Ukraine'
    elif code_in == 'unr':
        return 'USSR'
    elif code_in == 'up':
        return 'United States Misc. Pacific Islands'
    elif code_in == 'ur':
        return 'Soviet Union'
    elif code_in == 'us':
        return 'United States'
    elif code_in == 'utu':
        return 'USA'
    elif code_in == 'uv':
        return 'Burkina Faso'
    elif code_in == 'uy':
        return 'Uruguay'
    elif code_in == 'uz':
        return 'Uzbekistan'
    elif code_in == 'uzr':
        return 'USSR'
    elif code_in == 'vau':
        return 'USA'
    elif code_in == 'vb':
        return 'British Virgin Islands'
    elif code_in == 'vc':
        return 'Vatican City'
    elif code_in == 've':
        return 'Venezuela'
    elif code_in == 'vi':
        return 'Virgin Islands of the United States'
    elif code_in == 'vm':
        return 'Vietnam'
    elif code_in == 'vn':
        return 'Vietnam, North'
    elif code_in == 'vp':
        return 'Various places'
    elif code_in == 'vra':
        return 'Australia'
    elif code_in == 'vs':
        return 'Vietnam, South'
    elif code_in == 'vtu':
        return 'USA'
    elif code_in == 'wau':
        return 'USA'
    elif code_in == 'wb':
        return 'West Berlin'
    elif code_in == 'wea':
        return 'Australia'
    elif code_in == 'wf':
        return 'Wallis and Futuna'
    elif code_in == 'wiu':
        return 'USA'
    elif code_in == 'wj':
        return 'West Bank of the Jordan River'
    elif code_in == 'wk':
        return 'Wake Island'
    elif code_in == 'wlk':
        return 'Wales'
    elif code_in == 'ws':
        return 'Samoa'
    elif code_in == 'wvu':
        return 'USA'
    elif code_in == 'wyu':
        return 'USA'
    elif code_in == 'xa':
        return 'Christmas Island (Indian Ocean)'
    elif code_in == 'xb':
        return 'Cocos (Keeling) Islands'
    elif code_in == 'xc':
        return 'Maldives'
    elif code_in == 'xd':
        return 'Saint Kitts-Nevis'
    elif code_in == 'xe':
        return 'Marshall Islands'
    elif code_in == 'xf':
        return 'Midway Islands'
    elif code_in == 'xga':
        return 'Australia'
    elif code_in == 'xh':
        return 'Niue'
    elif code_in == 'xi':
        return 'Saint Kitts-Nevis-Anguilla'
    elif code_in == 'xj':
        return 'Saint Helena'
    elif code_in == 'xk':
        return 'Saint Lucia'
    elif code_in == 'xl':
        return 'Saint Pierre and Miquelon'
    elif code_in == 'xm':
        return 'Saint Vincent and the Grenadines'
    elif code_in == 'xn':
        return 'Macedonia'
    elif code_in == 'xna':
        return 'Australia'
    elif code_in == 'xo':
        return 'Slovakia'
    elif code_in == 'xoa':
        return 'Australia'
    elif code_in == 'xp':
        return 'Spratly Island'
    elif code_in == 'xr':
        return 'Czech Republic'
    elif code_in == 'xra':
        return 'Australia'
    elif code_in == 'xs':
        return 'South Georgia and the South Sandwich Islands'
    elif code_in == 'xv':
        return 'Slovenia'
    elif code_in == 'xx':
        return 'No place, unknown, or undetermined'
    elif code_in == 'xxc':
        return 'Canada'
    elif code_in == 'xxk':
        return 'United Kingdom'
    elif code_in == 'xxr':
        return 'USSR'
    elif code_in == 'xxu':
        return 'USA'
    elif code_in == 'ye':
        return 'Yemen'
    elif code_in == 'ykc':
        return 'Canada'
    elif code_in == 'ys':
        return 'Yemen (People\'s Democratic Republic)'
    elif code_in == 'yu':
        return 'Serbia and Montenegro'
    elif code_in == 'za':
        return 'Zambia'
    
    return None


# ------------------------------------------------------------------------------


def country_codes_with_states(code_in):
    """
    Returns country names from MARC country codes.
    This version includes US states & Canadian provinces
    So "nyu" returns "New York (State)" rather than USA
    MOST OF THE TIME THE NO-STATE VARIANT IS THE BETTER CHOICE
    """

    code_in = code_in.lower().strip()

    if code_in == 'aa':
        return 'Albania'
    elif code_in == 'abc':
        return 'Alberta'
    elif code_in == 'ac':
        return 'Ashmore and Cartier Islands'
    elif code_in == 'aca':
        return 'Australian Capital Territory'
    elif code_in == 'ae':
        return 'Algeria'
    elif code_in == 'af':
        return 'Afghanistan'
    elif code_in == 'ag':
        return 'Argentina'
    elif code_in == 'ai':
        return 'Anguilla'
    elif code_in == 'ai':
        return 'Armenia (Republic)'
    elif code_in == 'air':
        return 'Armenian S.S.R.'
    elif code_in == 'aj':
        return 'Azerbaijan'
    elif code_in == 'ajr':
        return 'Azerbaijan S.S.R.'
    elif code_in == 'aku':
        return 'Alaska'
    elif code_in == 'alu':
        return 'Alabama'
    elif code_in == 'am':
        return 'Anguilla'
    elif code_in == 'an':
        return 'Andorra'
    elif code_in == 'ao':
        return 'Angola'
    elif code_in == 'aq':
        return 'Antigua and Barbuda'
    elif code_in == 'aru':
        return 'Arkansas'
    elif code_in == 'as':
        return 'American Samoa'
    elif code_in == 'at':
        return 'Australia'
    elif code_in == 'au':
        return 'Austria'
    elif code_in == 'aw':
        return 'Aruba'
    elif code_in == 'ay':
        return 'Antarctica'
    elif code_in == 'azu':
        return 'Arizona'
    elif code_in == 'ba':
        return 'Bahrain'
    elif code_in == 'bb':
        return 'Barbados'
    elif code_in == 'bcc':
        return 'British Columbia'
    elif code_in == 'bd':
        return 'Burundi'
    elif code_in == 'be':
        return 'Belgium'
    elif code_in == 'bf':
        return 'Bahamas'
    elif code_in == 'bg':
        return 'Bangladesh'
    elif code_in == 'bh':
        return 'Belize'
    elif code_in == 'bi':
        return 'British Indian Ocean Territory'
    elif code_in == 'bl':
        return 'Brazil'
    elif code_in == 'bm':
        return 'Bermuda Islands'
    elif code_in == 'bn':
        return 'Bosnia and Herzegovina'
    elif code_in == 'bo':
        return 'Bolivia'
    elif code_in == 'bp':
        return 'Solomon Islands'
    elif code_in == 'br':
        return 'Burma'
    elif code_in == 'bs':
        return 'Botswana'
    elif code_in == 'bt':
        return 'Bhutan'
    elif code_in == 'bu':
        return 'Bulgaria'
    elif code_in == 'bv':
        return 'Bouvet Island'
    elif code_in == 'bw':
        return 'Belarus'
    elif code_in == 'bwr':
        return 'Byelorussian S.S.R.'
    elif code_in == 'bx':
        return 'Brunei'
    elif code_in == 'ca':
        return 'Caribbean Netherlands'
    elif code_in == 'cau':
        return 'California'
    elif code_in == 'cb':
        return 'Cambodia'
    elif code_in == 'cc':
        return 'China'
    elif code_in == 'cd':
        return 'Chad'
    elif code_in == 'ce':
        return 'Sri Lanka'
    elif code_in == 'cf':
        return 'Congo (Brazzaville)'
    elif code_in == 'cg':
        return 'Congo (Democratic Republic)'
    elif code_in == 'ch':
        return 'China (Republic : 1949- )'
    elif code_in == 'ci':
        return 'Croatia'
    elif code_in == 'cj':
        return 'Cayman Islands'
    elif code_in == 'ck':
        return 'Colombia'
    elif code_in == 'cl':
        return 'Chile'
    elif code_in == 'cm':
        return 'Cameroon'
    elif code_in == 'cn':
        return 'Canada'
    elif code_in == 'co':
        return 'Curaçao'
    elif code_in == 'cou':
        return 'Colorado'
    elif code_in == 'cp':
        return 'Canton and Enderbury Islands'
    elif code_in == 'cq':
        return 'Comoros'
    elif code_in == 'cr':
        return 'Costa Rica'
    elif code_in == 'cs':
        return 'Czechoslovakia'
    elif code_in == 'ctu':
        return 'Connecticut'
    elif code_in == 'cu':
        return 'Cuba'
    elif code_in == 'cv':
        return 'Cabo Verde'
    elif code_in == 'cw':
        return 'Cook Islands'
    elif code_in == 'cx':
        return 'Central African Republic'
    elif code_in == 'cy':
        return 'Cyprus'
    elif code_in == 'cz':
        return 'Canal Zone'
    elif code_in == 'dcu':
        return 'District of Columbia'
    elif code_in == 'deu':
        return 'Delaware'
    elif code_in == 'dk':
        return 'Denmark'
    elif code_in == 'dm':
        return 'Benin'
    elif code_in == 'dq':
        return 'Dominica'
    elif code_in == 'dr':
        return 'Dominican Republic'
    elif code_in == 'ea':
        return 'Eritrea'
    elif code_in == 'ec':
        return 'Ecuador'
    elif code_in == 'eg':
        return 'Equatorial Guinea'
    elif code_in == 'em':
        return 'Timor-Leste'
    elif code_in == 'enk':
        return 'England'
    elif code_in == 'er':
        return 'Estonia'
    elif code_in == 'err':
        return 'Estonia'
    elif code_in == 'es':
        return 'El Salvador'
    elif code_in == 'et':
        return 'Ethiopia'
    elif code_in == 'fa':
        return 'Faroe Islands'
    elif code_in == 'fg':
        return 'French Guiana'
    elif code_in == 'fi':
        return 'Finland'
    elif code_in == 'fj':
        return 'Fiji'
    elif code_in == 'fk':
        return 'Falkland Islands'
    elif code_in == 'flu':
        return 'Florida'
    elif code_in == 'fm':
        return 'Micronesia (Federated States)'
    elif code_in == 'fp':
        return 'French Polynesia'
    elif code_in == 'fr':
        return 'France'
    elif code_in == 'fs':
        return 'Terres australes et antarctiques françaises'
    elif code_in == 'ft':
        return 'Djibouti'
    elif code_in == 'gau':
        return 'Georgia'
    elif code_in == 'gb':
        return 'Kiribati'
    elif code_in == 'gd':
        return 'Grenada'
    elif code_in == 'ge':
        return 'Germany (East)'
    elif code_in == 'gh':
        return 'Ghana'
    elif code_in == 'gi':
        return 'Gibraltar'
    elif code_in == 'gl':
        return 'Greenland'
    elif code_in == 'gm':
        return 'Gambia'
    elif code_in == 'gn':
        return 'Gilbert and Ellice Islands'
    elif code_in == 'go':
        return 'Gabon'
    elif code_in == 'gp':
        return 'Guadeloupe'
    elif code_in == 'gr':
        return 'Greece'
    elif code_in == 'gs':
        return 'Georgia (Republic)'
    elif code_in == 'gsr':
        return 'Georgian S.S.R.'
    elif code_in == 'gt':
        return 'Guatemala'
    elif code_in == 'gu':
        return 'Guam'
    elif code_in == 'gv':
        return 'Guinea'
    elif code_in == 'gw':
        return 'Germany'
    elif code_in == 'gy':
        return 'Guyana'
    elif code_in == 'gz':
        return 'Gaza Strip'
    elif code_in == 'hiu':
        return 'Hawaii'
    elif code_in == 'hk':
        return 'Hong Kong'
    elif code_in == 'hm':
        return 'Heard and McDonald Islands'
    elif code_in == 'ho':
        return 'Honduras'
    elif code_in == 'ht':
        return 'Haiti'
    elif code_in == 'hu':
        return 'Hungary'
    elif code_in == 'iau':
        return 'Iowa'
    elif code_in == 'ic':
        return 'Iceland'
    elif code_in == 'idu':
        return 'Idaho'
    elif code_in == 'ie':
        return 'Ireland'
    elif code_in == 'ii':
        return 'India'
    elif code_in == 'ilu':
        return 'Illinois'
    elif code_in == 'inu':
        return 'Indiana'
    elif code_in == 'io':
        return 'Indonesia'
    elif code_in == 'iq':
        return 'Iraq'
    elif code_in == 'ir':
        return 'Iran'
    elif code_in == 'is':
        return 'Israel'
    elif code_in == 'it':
        return 'Italy'
    elif code_in == 'iu':
        return 'Israel-Syria Demilitarized Zones'
    elif code_in == 'iv':
        return 'Côte d\'Ivoire'
    elif code_in == 'iw':
        return 'Israel-Jordan Demilitarized Zones'
    elif code_in == 'iy':
        return 'Iraq-Saudi Arabia Neutral Zone'
    elif code_in == 'ja':
        return 'Japan'
    elif code_in == 'ji':
        return 'Johnston Atoll'
    elif code_in == 'jm':
        return 'Jamaica'
    elif code_in == 'jn':
        return 'Jan Mayen'
    elif code_in == 'jo':
        return 'Jordan'
    elif code_in == 'ke':
        return 'Kenya'
    elif code_in == 'kg':
        return 'Kyrgyzstan'
    elif code_in == 'kgr':
        return 'Kirghiz S.S.R.'
    elif code_in == 'kn':
        return 'Korea (North)'
    elif code_in == 'ko':
        return 'Korea (South)'
    elif code_in == 'ksu':
        return 'Kansas'
    elif code_in == 'ku':
        return 'Kuwait'
    elif code_in == 'kv':
        return 'Kosovo'
    elif code_in == 'kyu':
        return 'Kentucky'
    elif code_in == 'kz':
        return 'Kazakhstan'
    elif code_in == 'kzr':
        return 'Kazakh S.S.R.'
    elif code_in == 'lau':
        return 'Louisiana'
    elif code_in == 'lb':
        return 'Liberia'
    elif code_in == 'le':
        return 'Lebanon'
    elif code_in == 'lh':
        return 'Liechtenstein'
    elif code_in == 'li':
        return 'Lithuania'
    elif code_in == 'lir':
        return 'Lithuania'
    elif code_in == 'ln':
        return 'Central and Southern Line Islands'
    elif code_in == 'lo':
        return 'Lesotho'
    elif code_in == 'ls':
        return 'Laos'
    elif code_in == 'lu':
        return 'Luxembourg'
    elif code_in == 'lv':
        return 'Latvia'
    elif code_in == 'lvr':
        return 'Latvia'
    elif code_in == 'ly':
        return 'Libya'
    elif code_in == 'mau':
        return 'Massachusetts'
    elif code_in == 'mbc':
        return 'Manitoba'
    elif code_in == 'mc':
        return 'Monaco'
    elif code_in == 'mdu':
        return 'Maryland'
    elif code_in == 'meu':
        return 'Maine'
    elif code_in == 'mf':
        return 'Mauritius'
    elif code_in == 'mg':
        return 'Madagascar'
    elif code_in == 'mh':
        return 'Macao'
    elif code_in == 'miu':
        return 'Michigan'
    elif code_in == 'mj':
        return 'Montserrat'
    elif code_in == 'mk':
        return 'Oman'
    elif code_in == 'ml':
        return 'Mali'
    elif code_in == 'mm':
        return 'Malta'
    elif code_in == 'mnu':
        return 'Minnesota'
    elif code_in == 'mo':
        return 'Montenegro'
    elif code_in == 'mou':
        return 'Missouri'
    elif code_in == 'mp':
        return 'Mongolia'
    elif code_in == 'mq':
        return 'Martinique'
    elif code_in == 'mr':
        return 'Morocco'
    elif code_in == 'msu':
        return 'Mississippi'
    elif code_in == 'mtu':
        return 'Montana'
    elif code_in == 'mu':
        return 'Mauritania'
    elif code_in == 'mv':
        return 'Moldova'
    elif code_in == 'mvr':
        return 'Moldavian S.S.R.'
    elif code_in == 'mw':
        return 'Malawi'
    elif code_in == 'mx':
        return 'Mexico'
    elif code_in == 'my':
        return 'Malaysia'
    elif code_in == 'mz':
        return 'Mozambique'
    elif code_in == 'na':
        return 'Netherlands Antilles'
    elif code_in == 'nbu':
        return 'Nebraska'
    elif code_in == 'ncu':
        return 'North Carolina'
    elif code_in == 'ndu':
        return 'North Dakota'
    elif code_in == 'ne':
        return 'Netherlands'
    elif code_in == 'nfc':
        return 'Newfoundland and Labrador'
    elif code_in == 'ng':
        return 'Niger'
    elif code_in == 'nhu':
        return 'New Hampshire'
    elif code_in == 'nik':
        return 'Northern Ireland'
    elif code_in == 'nju':
        return 'New Jersey'
    elif code_in == 'nkc':
        return 'New Brunswick'
    elif code_in == 'nl':
        return 'New Caledonia'
    elif code_in == 'nm':
        return 'Northern Mariana Islands'
    elif code_in == 'nmu':
        return 'New Mexico'
    elif code_in == 'nn':
        return 'Vanuatu'
    elif code_in == 'no':
        return 'Norway'
    elif code_in == 'np':
        return 'Nepal'
    elif code_in == 'nq':
        return 'Nicaragua'
    elif code_in == 'nr':
        return 'Nigeria'
    elif code_in == 'nsc':
        return 'Nova Scotia'
    elif code_in == 'ntc':
        return 'Northwest Territories'
    elif code_in == 'nu':
        return 'Nauru'
    elif code_in == 'nuc':
        return 'Nunavut'
    elif code_in == 'nvu':
        return 'Nevada'
    elif code_in == 'nw':
        return 'Northern Mariana Islands'
    elif code_in == 'nx':
        return 'Norfolk Island'
    elif code_in == 'nyu':
        return 'New York (State)'
    elif code_in == 'nz':
        return 'New Zealand'
    elif code_in == 'ohu':
        return 'Ohio'
    elif code_in == 'oku':
        return 'Oklahoma'
    elif code_in == 'onc':
        return 'Ontario'
    elif code_in == 'oru':
        return 'Oregon'
    elif code_in == 'ot':
        return 'Mayotte'
    elif code_in == 'pau':
        return 'Pennsylvania'
    elif code_in == 'pc':
        return 'Pitcairn Island'
    elif code_in == 'pe':
        return 'Peru'
    elif code_in == 'pf':
        return 'Paracel Islands'
    elif code_in == 'pg':
        return 'Guinea-Bissau'
    elif code_in == 'ph':
        return 'Philippines'
    elif code_in == 'pic':
        return 'Prince Edward Island'
    elif code_in == 'pk':
        return 'Pakistan'
    elif code_in == 'pl':
        return 'Poland'
    elif code_in == 'pn':
        return 'Panama'
    elif code_in == 'po':
        return 'Portugal'
    elif code_in == 'pp':
        return 'Papua New Guinea'
    elif code_in == 'pr':
        return 'Puerto Rico'
    elif code_in == 'pt':
        return 'Portuguese Timor'
    elif code_in == 'pw':
        return 'Palau'
    elif code_in == 'py':
        return 'Paraguay'
    elif code_in == 'qa':
        return 'Qatar'
    elif code_in == 'qea':
        return 'Queensland'
    elif code_in == 'quc':
        return 'Québec (Province)'
    elif code_in == 'rb':
        return 'Serbia'
    elif code_in == 're':
        return 'Réunion'
    elif code_in == 'rh':
        return 'Zimbabwe'
    elif code_in == 'riu':
        return 'Rhode Island'
    elif code_in == 'rm':
        return 'Romania'
    elif code_in == 'ru':
        return 'Russia (Federation)'
    elif code_in == 'rur':
        return 'Russian S.F.S.R.'
    elif code_in == 'rw':
        return 'Rwanda'
    elif code_in == 'ry':
        return 'Ryukyu Islands, Southern'
    elif code_in == 'sa':
        return 'South Africa'
    elif code_in == 'sb':
        return 'Svalbard'
    elif code_in == 'sc':
        return 'Saint-Barthélemy'
    elif code_in == 'scu':
        return 'South Carolina'
    elif code_in == 'sd':
        return 'South Sudan'
    elif code_in == 'sdu':
        return 'South Dakota'
    elif code_in == 'se':
        return 'Seychelles'
    elif code_in == 'sf':
        return 'Sao Tome and Principe'
    elif code_in == 'sg':
        return 'Senegal'
    elif code_in == 'sh':
        return 'Spanish North Africa'
    elif code_in == 'si':
        return 'Singapore'
    elif code_in == 'sj':
        return 'Sudan'
    elif code_in == 'sk':
        return 'Sikkim'
    elif code_in == 'sl':
        return 'Sierra Leone'
    elif code_in == 'sm':
        return 'San Marino'
    elif code_in == 'sn':
        return 'Sint Maarten'
    elif code_in == 'snc':
        return 'Saskatchewan'
    elif code_in == 'so':
        return 'Somalia'
    elif code_in == 'sp':
        return 'Spain'
    elif code_in == 'sq':
        return 'Swaziland'
    elif code_in == 'sr':
        return 'Surinam'
    elif code_in == 'ss':
        return 'Western Sahara'
    elif code_in == 'st':
        return 'Saint-Martin'
    elif code_in == 'stk':
        return 'Scotland'
    elif code_in == 'su':
        return 'Saudi Arabia'
    elif code_in == 'sv':
        return 'Swan Islands'
    elif code_in == 'sw':
        return 'Sweden'
    elif code_in == 'sx':
        return 'Namibia'
    elif code_in == 'sy':
        return 'Syria'
    elif code_in == 'sz':
        return 'Switzerland'
    elif code_in == 'ta':
        return 'Tajikistan'
    elif code_in == 'tar':
        return 'Tajik S.S.R.'
    elif code_in == 'tc':
        return 'Turks and Caicos Islands'
    elif code_in == 'tg':
        return 'Togo'
    elif code_in == 'th':
        return 'Thailand'
    elif code_in == 'ti':
        return 'Tunisia'
    elif code_in == 'tk':
        return 'Turkmenistan'
    elif code_in == 'tkr':
        return 'Turkmen S.S.R.'
    elif code_in == 'tl':
        return 'Tokelau'
    elif code_in == 'tma':
        return 'Tasmania'
    elif code_in == 'tnu':
        return 'Tennessee'
    elif code_in == 'to':
        return 'Tonga'
    elif code_in == 'tr':
        return 'Trinidad and Tobago'
    elif code_in == 'ts':
        return 'United Arab Emirates'
    elif code_in == 'tt':
        return 'Trust Territory of the Pacific Islands'
    elif code_in == 'tu':
        return 'Turkey'
    elif code_in == 'tv':
        return 'Tuvalu'
    elif code_in == 'txu':
        return 'Texas'
    elif code_in == 'tz':
        return 'Tanzania'
    elif code_in == 'ua':
        return 'Egypt'
    elif code_in == 'uc':
        return 'United States Misc. Caribbean Islands'
    elif code_in == 'ug':
        return 'Uganda'
    elif code_in == 'ui':
        return 'United Kingdom Misc. Islands'
    elif code_in == 'uik':
        return 'United Kingdom Misc. Islands'
    elif code_in == 'uk':
        return 'United Kingdom'
    elif code_in == 'un':
        return 'Ukraine'
    elif code_in == 'unr':
        return 'Ukraine'
    elif code_in == 'up':
        return 'United States Misc. Pacific Islands'
    elif code_in == 'ur':
        return 'Soviet Union'
    elif code_in == 'us':
        return 'United States'
    elif code_in == 'utu':
        return 'Utah'
    elif code_in == 'uv':
        return 'Burkina Faso'
    elif code_in == 'uy':
        return 'Uruguay'
    elif code_in == 'uz':
        return 'Uzbekistan'
    elif code_in == 'uzr':
        return 'Uzbek S.S.R.'
    elif code_in == 'vau':
        return 'Virginia'
    elif code_in == 'vb':
        return 'British Virgin Islands'
    elif code_in == 'vc':
        return 'Vatican City'
    elif code_in == 've':
        return 'Venezuela'
    elif code_in == 'vi':
        return 'Virgin Islands of the United States'
    elif code_in == 'vm':
        return 'Vietnam'
    elif code_in == 'vn':
        return 'Vietnam, North'
    elif code_in == 'vp':
        return 'Various places'
    elif code_in == 'vra':
        return 'Victoria'
    elif code_in == 'vs':
        return 'Vietnam, South'
    elif code_in == 'vtu':
        return 'Vermont'
    elif code_in == 'wau':
        return 'Washington (State)'
    elif code_in == 'wb':
        return 'West Berlin'
    elif code_in == 'wea':
        return 'Western Australia'
    elif code_in == 'wf':
        return 'Wallis and Futuna'
    elif code_in == 'wiu':
        return 'Wisconsin'
    elif code_in == 'wj':
        return 'West Bank of the Jordan River'
    elif code_in == 'wk':
        return 'Wake Island'
    elif code_in == 'wlk':
        return 'Wales'
    elif code_in == 'ws':
        return 'Samoa'
    elif code_in == 'wvu':
        return 'West Virginia'
    elif code_in == 'wyu':
        return 'Wyoming'
    elif code_in == 'xa':
        return 'Christmas Island (Indian Ocean)'
    elif code_in == 'xb':
        return 'Cocos (Keeling) Islands'
    elif code_in == 'xc':
        return 'Maldives'
    elif code_in == 'xd':
        return 'Saint Kitts-Nevis'
    elif code_in == 'xe':
        return 'Marshall Islands'
    elif code_in == 'xf':
        return 'Midway Islands'
    elif code_in == 'xga':
        return 'Coral Sea Islands Territory'
    elif code_in == 'xh':
        return 'Niue'
    elif code_in == 'xi':
        return 'Saint Kitts-Nevis-Anguilla'
    elif code_in == 'xj':
        return 'Saint Helena'
    elif code_in == 'xk':
        return 'Saint Lucia'
    elif code_in == 'xl':
        return 'Saint Pierre and Miquelon'
    elif code_in == 'xm':
        return 'Saint Vincent and the Grenadines'
    elif code_in == 'xn':
        return 'Macedonia'
    elif code_in == 'xna':
        return 'New South Wales'
    elif code_in == 'xo':
        return 'Slovakia'
    elif code_in == 'xoa':
        return 'Northern Territory'
    elif code_in == 'xp':
        return 'Spratly Island'
    elif code_in == 'xr':
        return 'Czech Republic'
    elif code_in == 'xra':
        return 'South Australia'
    elif code_in == 'xs':
        return 'South Georgia and the South Sandwich Islands'
    elif code_in == 'xv':
        return 'Slovenia'
    elif code_in == 'xx':
        return 'No place, unknown, or undetermined'
    elif code_in == 'xxc':
        return 'Canada'
    elif code_in == 'xxk':
        return 'United Kingdom'
    elif code_in == 'xxr':
        return 'Soviet Union'
    elif code_in == 'xxu':
        return 'United States'
    elif code_in == 'ye':
        return 'Yemen'
    elif code_in == 'ykc':
        return 'Yukon Territory'
    elif code_in == 'ys':
        return 'Yemen (People\'s Democratic Republic)'
    elif code_in == 'yu':
        return 'Serbia and Montenegro'
    elif code_in == 'za':
        return 'Zambia'

    return None


def check_for_valid_lc_class(lc_class):
    """
    Check that an LC class is on the list of valid ones.

    Leading underscore in method name in case we add a check_lc_class in a utilities module

    """

    # I've done some testing and it seems a series of if statements is faster than a dict or set
    # TODO: Maybe order them by frequency, so the most common classes would be found right away.

    #   Import 2 or 3 digit LC class.
    #   Export check: 1-> OK, 0-> failed

    lc_class = lc_class.upper()

    if len(lc_class) < 1:
        return False
    elif len(lc_class) > 3:
        return False
    valid_lc_classes = {
        "A", "AC", "AE", "AG", "AI", "AM", "AN", "AP", "AS", "AY", "AZ", "B",
        "BC", "BD", "BF", "BH", "BJ", "BL", "BM", "BP", "BQ", "BR", "BS", "BT",
        "BV", "BX", "C", "CB", "CC", "CD", "CE", "CJ", "CN", "CR", "CS", "CT",
        "D", "DA", "DAW", "DB", "DC", "DD", "DE", "DF", "DG", "DH", "DJ", "DJK",
        "DK", "DL", "DP", "DQ", "DR", "DS", "DT", "DU", "DX", "E", "F", "G",
        "GA", "GB", "GC", "GE", "GF", "GN", "GR", "GT", "GV", "H", "HA", "HB",
        "HC", "HD", "HE", "HF", "HG", "HJ", "HM", "HN", "HQ", "HS", "HT", "HV",
        "HX", "J", "JA", "JC", "JF", "JJ", "JK", "JL", "JN", "JQ", "JS", "JV",
        "JX", "JZ", "K", "KB", "KBM", "KBP", "KBR", "KBU", "KD", "KDC", "KDE",
        "KDG", "KDK", "KDZ", "KE", "KEA", "KEB", "KEM", "KEN", "KEO", "KEP",
        "KEQ", "KES", "KEY", "KEZ", "KF", "KFA", "KFC", "KFD", "KFF", "KFG",
        "KFH", "KFI", "KFK", "KFL", "KFM", "KFN", "KFO", "KFP", "KFR", "KFS",
        "KFT", "KFU", "KFV", "KFW", "KFX", "KFZ", "KG", "KGA", "KGB", "KGC",
        "KGD", "KGE", "KGF", "KGG", "KGH", "KGJ", "KGK", "KGL", "KGM", "KGN",
        "KGP", "KGQ", "KGR", "KGS", "KGT", "KGU", "KGV", "KGW", "KGX", "KGY",
        "KGZ", "KH", "KHA", "KHC", "KHD", "KHF", "KHH", "KHK", "KHL", "KHM",
        "KHN", "KHP", "KHQ", "KHS", "KHU", "KHW", "KJ", "KJA", "KJC", "KJE",
        "KJG", "KJH", "KJJ", "KJK", "KJM", "KJN", "KJP", "KJR", "KJS", "KJT",
        "KJV", "KJW", "KK", "KKA", "KKB", "KKC", "KKE", "KKF", "KKG", "KKH",
        "KKI", "KKJ", "KKK", "KKL", "KKM", "KKN", "KKP", "KKQ", "KKR", "KKS",
        "KKT", "KKV", "KKW", "KKX", "KKY", "KKZ", "KL", "KLA", "KLB", "KLD",
        "KLE", "KLF", "KLH", "KLM", "KLN", "KLP", "KLQ", "KLR", "KLS", "KLT",
        "KLV", "KLW", "KM", "KMC", "KME", "KMF", "KMG", "KMH", "KMJ", "KMK",
        "KML", "KMM", "KMN", "KMP", "KMQ", "KMS", "KMT", "KMU", "KMV", "KMX",
        "KMY", "KNC", "KNE", "KNF", "KNG", "KNH", "KNK", "KNL", "KNM", "KNN",
        "KNP", "KNQ", "KNR", "KNS", "KNT", "KNU", "KNV", "KNW", "KNX", "KNY",
        "KPA", "KPC", "KPE", "KPF", "KPG", "KPH", "KPJ", "KPK", "KPL", "KPM",
        "KPP", "KPS", "KPT", "KPV", "KPW", "KQ", "KQC", "KQE", "KQG", "KQH",
        "KQJ", "KQK", "KQM", "KQP", "KQT", "KQV", "KQW", "KQX", "KRB", "KRC",
        "KRE", "KRG", "KRK", "KRL", "KRM", "KRN", "KRP", "KRR", "KRS", "KRU",
        "KRV", "KRW", "KRX", "KRY", "KSA", "KSC", "KSE", "KSG", "KSH", "KSK",
        "KSL", "KSN", "KSP", "KSR", "KSS", "KST", "KSU", "KSV", "KSW", "KSX",
        "KSY", "KSZ", "KTA", "KTC", "KTD", "KTE", "KTF", "KTG", "KTH", "KTJ",
        "KTK", "KTL", "KTN", "KTQ", "KTR", "KTT", "KTU", "KTV", "KTW", "KTX",
        "KTY", "KTZ", "KU", "KUA", "KUH", "KUN", "KUQ", "KVB", "KVC", "KVE",
        "KVH", "KVL", "KVM", "KVN", "KVP", "KVQ", "KVR", "KVS", "KVU", "KVW",
        "KWA", "KWC", "KWE", "KWG", "KWH", "KWL", "KWP", "KWQ", "KWR", "KWT",
        "KWW", "KWX", "KZ", "KZA", "KZD", "L", "LA", "LB", "LC", "LD", "LE",
        "LF", "LG", "LH", "LJ", "LT", "M", "ML", "MT", "N", "NA", "NB", "NC",
        "ND", "NE", "NK", "NX", "P", "PA", "PB", "PC", "PD", "PE", "PF", "PG",
        "PH", "PJ", "PK", "PL", "PM", "PN", "PQ", "PR", "PS", "PT", "PZ", "Q",
        "QA", "QB", "QC", "QD", "QE", "QH", "QK", "QL", "QM", "QP", "QR", "R",
        "RA", "RB", "RC", "RD", "RE", "RF", "RG", "RJ", "RK", "RL", "RM", "RS",
        "RT", "RV", "RX", "RZ", "S", "SB", "SD", "SF", "SH", "SK", "T", "TA",
        "TC", "TD", "TE", "TF", "TG", "TH", "TJ", "TK", "TL", "TN", "TP", "TR",
        "TS", "TT", "TX", "U", "UA", "UB", "UC", "UD", "UE", "UF", "UG", "UH",
        "V", "VA", "VB", "VC", "VD", "VE", "VF", "VG", "VK", "VM", "Z", "ZA"
    }

    if lc_class in valid_lc_classes:
        return True
    return False
