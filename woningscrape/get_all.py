import re

import logging 

import time
import random
import datetime

from models import *

#logging.basicConfig(level=logging.DEBUG,
#                    format='%(message)s',
#                    datefmt='[%d/%b/%Y %H:%M:%S]')

def randomwait(max=0.2):
    wait = random.uniform(0.0, max)
    logging.debug('Waiting %f seconds.' % wait)
    time.sleep(wait)

def get_woningen():
    Woning.objects.all().delete()

    from scrape import s
    browse = s

    adcountre = re.compile('Er zijn <b>([0-9]+)</b> advertenties gevonden.')
    pagecountre = re.compile('U ziet pagina <b>([0-9]+)</b> van <b>([0-9]+)</b>')
    linkidre = re.compile('getDetails\(\'([a-z0-9A-Z]+)\'\)')
    
    pricere = re.compile('[0-9]{3,4}(,[0-9]{2}){0,1}')
    zipcodere = re.compile('([0-9]{4} [A-Z]{2}) ([\w]+)')
    wijkre = re.compile('Wijk/Stadsdeel (.*)')
    datere = re.compile('[0-9]{2}-[0-9]{2}-[0-9]{4}')
    surfacere = re.compile('([1-9][0-9]*(,[0-9]*){0,1}) m')
    
    searchurl = 'http://www.woningnet.nl/zoekresultaat.asp'
    detailurl = 'http://www.woningnet.nl/woningdetails.asp'
    
    # Select social housing in and around Amsterdam
    searchdata = 'IID=5&radAanbodType=H'

    detaildata = 'IID=5'

    resultpage = browse.go(url=searchurl, data=searchdata)

    pagecount = resultpage.find(pagecountre, 2).get_number()
    adcount = resultpage.find(adcountre, 1).get_number()

    logging.debug('%d advertisements have been found on %d pages.' % (adcount, pagecount))

    total = 0
    for page in xrange(1, pagecount+1):
        logging.debug('Parsing page %d of %d:' % (page, pagecount))
        
        if page > 1:
            searchpagedata = searchdata + '&pag=%d' % page
            print searchpagedata
            resultpage = browse.go(url=searchurl, data=searchpagedata)
    
        for result_id in resultpage.findall(linkidre, 1):
            logging.debug('Parsing: %s' % result_id)

            randomwait()
            
            detailpagedata = detaildata + '&id=%s' % result_id
            detailpage = browse.go(url=detailurl, data=detailpagedata)
            
            try:
                detailregion = detailpage.first(**{'id':'content'})
            
                try:
                    detailregion.find('Woonversnelling')
                    woonversnelling = True
                    logging.debug('Woonversnelling')
                
                except:
                    woonversnelling = False
            
                addr_details = detailregion.first(**{'id':'details'})
        
                addr_tag = addr_details.first('b')
                address = addr_tag.text
            
                zipcode_tag = addr_tag.next('b')
                zipcode = zipcode_tag.find(zipcodere, 1).text
                        
                gemeente = zipcode_tag.find(zipcodere, 2).text
            
                try:
                    wijk = zipcode_tag.next('b').find(wijkre, 1).text.replace("\n","/")
                except:
                    wijk = zipcode_tag.next('b').text.replace("\n","/")
            
                logging.debug('Found adres: %s' % address)
                logging.debug('Found wijk: %s' % wijk)
                logging.debug('Found postcode: %s' % zipcode)
                logging.debug('Found gemeente: %s' % gemeente)
            
                w_id = result_id.text.strip()
            
                try:
                    w = Woning.objects.get(woningnet_id=w_id)
                    logging.debug('Updating existing woning.')
                except Woning.DoesNotExist:
                    w = Woning(woningnet_id=w_id)
            
                w.woonversnelling = woonversnelling
                    
                w.adres = address
                w.postcode = zipcode

                g, created = Gemeente.objects.get_or_create(naam=gemeente)
                if created:
                    logging.debug('Gemeente %s created.' % gemeente)
                w.gemeente = g
            
                wijk, created = Wijk.objects.get_or_create(naam=wijk, gemeente=g)
                if created:
                    logging.debug('Wijk %s created.' % wijk)
                w.wijk = wijk

        
                # Further details
                for detail in detailregion.all('div', **{'class':'detaillabel'}):
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
                    elif detail.text == 'Leeftijd':
                        value = value.text
                        logging.debug('Found leeftijd: %s' % value)
                        w.leeftijd = value
                    elif detail.text == 'Leeg per':
                        try:
                            value = datetime.datetime.strptime( value.find(datere).text, '%d-%m-%Y')
                        except:
                            logging.debug('Date %s not recognized.' % value)
                            value = None
                        logging.debug('Found leeg per: %s' % value)
                        w.leegper = value
                    elif detail.text == 'Energielabel':
                        value = value.text
                        if value in ENERGIE_LABELS:
                            logging.debug('Found energielabel: %s' % value)
                            w.energielabel = value
                    elif detail.text == 'Totale oppervlakte':
                        try:
                            value = float(value.find(surfacere, 1).text)
                            logging.debug('Found oppervlakte: %f' % value)
                        except:
                            logging.debug('Oppervlakte %s not recognized.' % value)
                            value = None
                        w.oppervlakte = value
                    elif detail.text == 'Totaal aantal kamers':
                        value = value.get_number()
                        logging.debug('Found kamers: %d' % value)
                        w.kamers = value
                    else:
                        logging.debug('Extra - \'%s\': %s' % (detail, value.text))
                        w.extra = w.extra + "%s: %s\n" % (detail.text, value.text)
                    
                logging.info('Saving: %s' % w)
                w.save()
            
                total += 1
                logging.debug('Finished %d of %d results.' % (total, adcount))
                
            except:
                logging.error('Unknown parse error for %s' % detailurl)
