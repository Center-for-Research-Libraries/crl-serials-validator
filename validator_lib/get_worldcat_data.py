import logging

from crl_lib.wc_api import WcApi
from crl_lib.marc_fields import WorldCatMarcFields


class WorldCatMarcDataExtractor:
    """
    Take a WorldCat OCLC, get the MARC and get required fields from it, then send the data to the local database.

    Instantiating this object runs through every OCLC number in the local database, processes them, and exports the
    results to the local database.

    Note that there's no analysis in this object, just pure data gathering.
    """
    def __init__(self):
        self.logger = logging.getLogger('validator')
        self.logger.info('Getting WorldCat data.')
        self.wc_api = WcApi()

    def get_worldcat_marc_data(self, oclc):
        if oclc or str(oclc) != 'None':
            marc = self.wc_api.fetch_marc_from_api(oclc, recent_only=True)
        else:
            marc = None
        return_dummy_data = False
        if not marc:
            # if no MARC get a dummy MARC record to run the process. We'll later erase all of the extracted data.
            self.logger.info('No WorldCat MARC returned from OCLC {}'.format(oclc))
            marc = self.get_dummy_marc()
            return_dummy_data = True
        mf = WorldCatMarcFields(marc)
        worldcat_data = {
            'wc_oclc': mf.oclc,
            'oclcs_019': '; '.join(mf.oclcs_019),
            'wc_issn_a': mf.issn_a,
            'issn_l': mf.issn_l,
            'wc_title': mf.title,
            'uniform_title': mf.uniform_title,
            'title_h': mf.title_h,
            'publisher': mf.publisher,
            'record_type': mf.record_type,
            'form': mf.form,
            'bib_lvl': mf.bib_lvl,
            'serial_type': mf.serial_type,
            'carrier_type': mf.carrier_type,
            'media_type': mf.media_type,
            'place': mf.place.replace('\\', ''),
            'lang': mf.lang.replace('\\', ''),
            'govt_pub': mf.govt_pub,
            'authentication_code': mf.authentication_code,
            'cat_agent': mf.cat_agent,
            'cat_lang': mf.cat_lang,
            'lc_class': mf.lc_class,
            'dewey': mf.dewey,
            '008_year_1': mf.year_1,
            '008_year_2': mf.year_2,
            'start_including_362': mf.combined_start_year,
            'end_including_362': mf.combined_end_year,
            'wc_line_362': '; '.join(mf.line_362),
            'current_freq': mf.current_freq,
            'former_freq': mf.former_freq,
            'preceding_oclcs': '; '.join(mf.preceding_oclcs),
            'succeeding_oclcs': '; '.join(mf.succeeding_oclcs),
            'other_oclcs': '; '.join(mf.other_oclcs),
            'numbering_peculiarities': mf.numbering_peculiarities,
        }

        # if there isn't a WorldCat record to work with, return everything as blank
        if return_dummy_data is True:
            for cat in worldcat_data:
                worldcat_data[cat] = ''
            return worldcat_data
        return worldcat_data

    @staticmethod
    def get_dummy_marc():
        """
        For titles either without an OCLC number that can be found in WorldCat, we will use dummy MARC data to run
        through the system, then we'll delete the results of that data. This is mainly so that we can add/remove 
        inputs in just one place (the worldcat_data dict) without having to sync it in some other place.
        """
        dummy_marc_list = [
            '=LDR  00000cas a2200000   4500',
            '=001  4631395',
            '=008  790208d19781978iluuu\\\\\\\\c\\\\\\\\0\\\\\\a0eng\\c',
            '=010  \\\\$asc 79004569 ',
            '=040  \\\\$aIAL',
            '=012  \\\\$a2$b3',
            '=016  \\\\$a(AMICUS)000000910364',
            '=019  \\\\$a4534994$a4573880$a4753739$a1032843045',
            '=022  0\\$a0273-0766$l0273-0766$21',
            '=029  1\\$aNLC$b000000910364',
            '=041  0\\$aeng$amul',
            '=042  \\\\$apcc$ansdp',
            '=043  \\\\$an-us-il',
            '=050  \\4$aZ6945$b.C432',
            '=082  04$a016.05$bC3967c, sup.',
            '=110  2\\$aCenter for Research Libraries (U.S.)',
            '=210  0\\$aCent. Res. Libr. cat., Ser., Suppl.',
            '=222  \\4$aThe Center For Research Libraries catalogue. Serials. Supplement',
            '=245  1\\$aFailed title',
            '=260  \\\\$aChicago,$bCenter for Research Libraries,$c1978.',
            '=300  \\\\$a1 volume$c29 cm',
            '=336  \\\\$atext$btxt$2rdacontent',
            '=337  \\\\$aunmediated$bn$2rdamedia',
            '=338  \\\\$avolume$bnc$2rdacarrier',
            '=362  0\\$a1st.',
            '=610  20$aCenter for Research Libraries (U.S.)$vCatalogs.',
            '=610  27$aCenter for Research Libraries (U.S.)$2fast$0(OCoLC)fst00512329',
            '=650  \\0$aPeriodicals$vBibliography$vPeriodicals.',
            '=650  \\0$aSerial publications$vBibliography$vPeriodicals.',
            '=650  \\7$aPeriodicals.$2fast$0(OCoLC)fst01058072',
            '=650  \\7$aSerial publications.$2fast$0(OCoLC)fst01113123',
            '=650  \\2$aCatalogs, Library$zChicago.',
            '=650  \\2$aPeriodicals as Topic$zChicago$vcatalogs.',
            '=655  \\7$aBibliography.$2fast$0(OCoLC)fst01423717',
            '=655  \\7$aCatalogs.$2fast$0(OCoLC)fst01423692',
            '=655  \\7$aPeriodicals.$2fast$0(OCoLC)fst01411641',
            '=936  \\\\$aUnknown$a1st (surrogate)',
            ''
        ]
        return "\n".join(dummy_marc_list)
