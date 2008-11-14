import re

import logging 

import time
import random

from models import *

#logging.basicConfig(level=logging.DEBUG,
#                    format='%(message)s',
#                    datefmt='[%d/%b/%Y %H:%M:%S]')

def randomwait(max=0.5):
    wait = random.uniform(0.0, max)
    logging.debug('Waiting %f seconds.' % wait)
    time.sleep(wait)

def get_woningen():
    from scrape import s
    browse = s

    adcountre = re.compile('Er zijn <b>([0-9]+)</b> advertenties gevonden.')
    pagecountre = re.compile('U ziet pagina <b>([0-9]+)</b> van <b>([0-9]+)</b>')
    linkidre = re.compile('getDetails\(\'([a-z0-9A-Z]+)\'\)')
    
    pricere = re.compile('[0-9]{3,4}(,[0-9]{2}){0,1}')
    
    zipcodere = re.compile('([0-9]{4} [A-Z]{2}) ([\w]+)')

    searchurl = 'http://www.woningnet.nl/zoekresultaat.asp'
    detailurl = 'http://www.woningnet.nl/woningdetails.asp'
    
    # Select social housing in and around Amsterdam
    searchdata = 'IID=5&radAanbodType=H'

    detaildata = 'IID=5'

    resultpage = browse.go(url=searchurl, data=searchdata)

    pagecount = resultpage.find(pagecountre, 2).get_number()
    adcount = resultpage.find(adcountre, 1).get_number()

    logging.debug('%d advertisements have been found on %d pages.' % (adcount, pagecount))

    for page in [1,]: #xrange(1, pagecount+1):
        logging.debug('Parsing page %d of %d:' % (page, pagecount))
    
        for result_id in resultpage.findall(linkidre, 1):
            logging.debug('Parsing: %s' % result_id)

            randomwait()
            detailpagedata = detaildata + '&id=%s' % result_id
            detailpage = browse.go(url=detailurl, data=detailpagedata)
            
            addr_details = detailpage.first(**{'id':'details'})
    
            addr_tag = addr_details.first('b')
            address = addr_tag.text
            
            zipcode_tag = addr_tag.next('b')
            zipcode = zipcode_tag.find(zipcodere, 1)
            
            gemeente = zipcode_tag.find(zipcodere, 2)
            
            logging.debug('Found adres: %s' % address)
            logging.debug('Found postcode: %s' % zipcode)
            logging.debug('Found gemeente: %s' % gemeente)
            
            try:
                w = Woning.objects.get(woningnet_id=result_id.text)
            except Woning.DoesNotExist:
                w = Woning(woningnet_id=result_id.text)
                        
            w.adres = address
            w.postcode = zipcode
            g, created = Gemeente.objects.get_or_create(naam=gemeente.text)
            w.gemeente = g
        
            # Further details
            for detail in detailpage.all('div', **{'class':'detaillabel'}):
                value = detail.next()

                if detail.text == 'Rekenhuur':
                    value = float(value.find(pricere).text.replace(',','.'))
                    logging.debug('Found rekenhuur: %f' % value)
                    w.rekenhuur = value
                elif detail.text == 'Bruto huur':
                    value = float(value.find(pricere).text.replace(',','.'))
                    logging.debug('Found brutohuur: %f' % value)
                    w.brutohuur = value
                elif detail.text == 'Woningnummer':
                    value = value.text
                    logging.debug('Found woningnummer %s' % value)
                    w.woningnummer = value
                elif detail.text == 'Reacties tot nu toe':
                    value = value.get_number()
                    logging.debug('Found reacties: %d' % value)
                    w.reacties = value
                elif detail.text == 'Type woning':
                    value = value.text
                    logging.debug('Found type: %s' % value)
                    w.woningtype = value
                else:
                    logging.debug('Extra - \'%s\': %s' % (detail, value.text))
                    w.extra = w.extra + "%s: %s\n" % (detail.text, value.text)
                    
            logging.debug('Saving: %s' % w)
            w.save()
        

        searchpagedata = searchdata + '&page%d' % page
        resultpage = browse.go(url=searchurl, data=searchpagedata)