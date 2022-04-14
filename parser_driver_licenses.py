import os
import zipcodes
import re
import json
import base_parser
import dateutil.parser
from difflib import SequenceMatcher
import sys
import csv
import datetime as dt
from datetime import datetime
import pyap
import dateutil.parser
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

#from uszipcode import SearchEngine
#import pyap
#from commonregex import CommonRegex

# Problems I'm seeing:
# Name is not registering
# Addresses are not accurate when there are multiple on the screen
# find ending point for each card
# fixed states
#   names must be more than one letter long
#   check for names line by line
#   25906 has different countries, but multiple names
# expiration dates are not being properly captured
#

class DriverLiecense:

    def __init__(self):
        self.date = None
        self.victimname = []
        self.photo_id = None
        self.state = []
        self.zipcode = []
        self.full_address = []
        self.valid_dl = None
        self.dl_number = None
    
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_date_and_id_from_title(self, title):
        re1 = title.split("@")
        photo_id = re1[0].split("_")[1]
        date = re1[1].split("_")[0]
        print(photo_id)
        return photo_id, date

    def check_zipcode(self,content):
        # return all the information related to zipcode too
        # libpostal to get address
        # find zipcode 5-digit and extract other into
        # get the city info
        result = []
        state_names = {
            "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
            "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
            "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
            "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
            "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
            "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
            "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
            "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
            "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
            "West Virginia": "WV", "Wisconsin": "WI",
        }

        for i in re.finditer(r'(?!\A)\b\d{5}(?:-\d{4})?\b', content):
            # print(i)
            if zipcodes.is_real(i.group()):
                state  = zipcodes.matching(i.group())[0]['state']
                if state in content:
                    result.append((i.group(), state))
                    return result
        content = content.lower()
        test = content.split(' ')
        # print(test)
        for k, v in state_names.items():
            for i in test:
                if self.similar(k.lower(), i) > .75:
                    # print("this worked")
                    result.append((None, v))    
        return result

    def victim_name(self, content):
        result  = []
        v_name = []
        content_lower = content.lower()
        words = content_lower.split(" ")
        #print(words)
        for i,word in enumerate(words):
            if ((word == "1" or word == "2") or (word == "FN" or word == "LN") or (word=="ln" or word=="fn")) and i+1 <= len(words):
                # print(word, " ", words[i+1])
                v_name.append(words[i+1])
        # print(v_name)

        for dl_victimname in v_name:
            # print(dl_victimname)
            if  dl_victimname:
                result.append(1)
            else:
                result.append(0)
        if sum(result) > 0:
            return 1
        return 0
    
    def validate_exp_date(self, content):
        result  = []
        exp_dates = []
        content_lower = content.lower()
        words = content_lower.split(" ")
        for i,word in enumerate(words):
            # if word.lower() == "5ein" or word.lower() == "exp" or word.lower() =='expires' and i+1 <= len(words):
            # if self.similar(word.lower(), "exp") > .8 or self.similar(word.lower(), "expires") > .8 and i+1 <= len(words):
            if i+1 < len(words):
                if "/" in words[i+1] or "-" in words[i+1]:
                    if "," in words[i+1]:
                        continue
                    else:
                        exp_dates.append(words[i+1])

        for exp_date in exp_dates:
            # print(dl_date)
            #dl_date = datetime.strptime(dl_date, "%m/%d/%Y")
            try:
                dl_date=dateutil.parser.parse(exp_date)
                # print(dl_date)
                curr_date = dt.date.today()
                if  dl_date.date() > curr_date:
                    result.append(1)
                else:
                    result.append(0)
            except Exception as e:
                # print(exp_date, " the exception is: ", e)
                result.append(0)
        if sum(result) > 0:
            return 1
        return 0

    def validate_full_address(self, content):
        
        result = []
        address = []
        content_lower = content.lower()
        words = content_lower.split(" ")
        dl_regex_full_address = pyap.parse(content, country='US')
        # print(dl_regex_full_address)
        #[r"\d+[ ](?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?[ ]{(?:[A-Z][a-z.-]+[ ]?)+},[ ](?:AlabamaAlaskaArizonaArkansasCaliforniaColoradoConnecticutDelawareFloridaGeorgiaHawaiiIdahoIllinoisIndianaIowaKansasKentuckyLouisianaMaineMarylandMassachusettsMichiganMinnesotaMississippiMissouriMontanaNebraskaNevadaNew[ ]HampshireNew[ ]JerseyNew[ ]MexicoNew[ ]YorkNorth[ ]CarolinaNorth[ ]DakotaOhioOklahomaOregonPennsylvaniaRhode[ ]IslandSouth[ ]CarolinaSouth[ ]DakotaTennesseeTexasUtahVermontVirginiaWashingtonWest[ ]VirginiaWisconsinWyoming|AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)[ ]\b\d{5}(?:-\d{4})?\b"]
        #["\s+(\d{2,5}\s+)(?![a|p]m\b)(([a-zA-Z|\s+]{1,5}){1,2})?([\s|,|.]+)?(([a-zA-Z|\s+]{1,30}){1,4})(court|ct|street|st|drive|dr|lane|ln|road|rd|blvd)([\s|,|.|;]+)?(([a-zA-Z|\s+]{1,30}){1,2})([\s|,|.]+)?\b(AK|AL|AR|AZ|CA|CO|CT|DC|DE|FL|GA|GU|HI|IA|ID|IL|IN|KS|KY|LA|MA|MD|ME|MI|MN|MO|MS|MT|NC|ND|NE|NH|NJ|NM|NV|NY|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VA|VI|VT|WA|WI|WV|WY)([\s|,|.]+)?(\s+\d{5})?([\s|,|.]+)(?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?[ ]{(?:[A-Z][a-z.-]+[ ]?)+},[ ](?:AlabamaAlaskaArizonaArkansasCaliforniaColoradoConnecticutDelawareFloridaGeorgiaHawaiiIdahoIllinoisIndianaIowaKansasKentuckyLouisianaMaineMarylandMassachusettsMichiganMinnesotaMississippiMissouriMontanaNebraskaNevadaNew[ ]HampshireNew[ ]JerseyNew[ ]MexicoNew[ ]YorkNorth[ ]CarolinaNorth[ ]DakotaOhioOklahomaOregonPennsylvaniaRhode[ ]IslandSouth[ ]CarolinaSouth[ ]DakotaTennesseeTexasUtahVermontVirginiaWashingtonWest[ ]VirginiaWisconsinWyoming|AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)[ ]\b\d{5}(?:-\d{4})?\b"]
        #["^\d{1,6}\040([A-Z]{1}[a-z]{1,}\040[A-Z]{1}[a-z]{1,})$|^\d{1,6}\040([A-Z]{1}[a-z]{1,}\040[A-Z]{1}[a-z]{1,}\040[A-Z]{1}[a-z]{1,})$|^\d{1,6}\040([A-Z]{1}[a-z]{1,}\040[A-Z]{1}[a-z]{1,}\040[A-Z]{1}[a-z]{1,}\040[A-Z]{1}[a-z]{1,})$"]
        #dl_regex_full_address = [r"\d+[ ](?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?[ ]{(?:[A-Z][a-z.-]+[ ]?)+},[ ](?:AlabamaAlaskaArizonaArkansasCaliforniaColoradoConnecticutDelawareFloridaGeorgiaHawaiiIdahoIllinoisIndianaIowaKansasKentuckyLouisianaMaineMarylandMassachusettsMichiganMinnesotaMississippiMissouriMontanaNebraskaNevadaNew[ ]HampshireNew[ ]JerseyNew[ ]MexicoNew[ ]YorkNorth[ ]CarolinaNorth[ ]DakotaOhioOklahomaOregonPennsylvaniaRhode[ ]IslandSouth[ ]CarolinaSouth[ ]DakotaTennesseeTexasUtahVermontVirginiaWashingtonWest[ ]VirginiaWisconsinWyoming|AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)[ ]\b\d{5}(?:-\d{4})?\b"]
        # for i,word in enumerate(words):
        #     if word == dl_regex_full_address:
        #         #if "/" in words[i+1] or "-" in words[i+1]:
        #         address.append(words[i+1])
        # print(address)
        
        # for dl_address in address:
        #     print(dl_address)
        #print("address_list",len(dl_regex_full_address))
        if  len(dl_regex_full_address)>0:
            # print("result",1)
            return 1 
            
        else:
            # print("result",0)
            return 0
        # if len(result) > 0:
        #     return 1
        # return 0
        
        # for r in dl_regex_full_address:
        #     for i in re.finditer(r, content):
        #         result.add(i.group())
        # if len(result) > 0:
        #     return 1
        # return 0
    
    def validate_dl_number(self, content):
        #[a-zA-Z]\d{7} CA
        #[a-zA-Z]\d{3}-\d{3}-\d{2}-\d{3}-\d FL
        result = set()

        dl_regex_usa_states = ["[a-zA-Z]\d{7}","[a-zA-Z]\d{3}-\d{3}-\d{2}-\d{3}-\d",
        "\d{7}","[a-zA-Z]\d{3}\d{3}\d{3}\d{3}","[a-zA-Z]\d{12}","[a-zA-Z]\d{3}-\d{3}-\d{2}-\d{3}-\d",
        "[a-zA-Z]\d{8}","\d{9}", "9\d{8}", "[a-zA-Z]\d{7}", "\d{2}-\d{3}-\d{4}",
        "\d{9}","[a-zA-Z]\d{8}","[a-zA-Z]{2}\d{6}[a-zA-Z]","[a-zA-Z]\d{3}-\d{4}-\d{4}", 
        "[a-zA-Z]\d{11}", "\d{4}-\d{2}-\d{4}", "\d{3}[a-zA-Z]{2}\d{4}", "[a-zA-Z]\d{2}-\d{2}-\d{4}",
        "[a-zA-Z]\d{2}-\d{3}-\d{3}", "[a-zA-Z]-\d{3}-\d{3}-\d{3}-\d{3}", "[a-zA-Z]-\d{3}-\d{3}-\d{3}-\d{3}",
        "[a-zA-Z]\d{12}","[a-zA-Z]\d{9}", "[a-zA-Z]\s\d{3}\s\d{3}\s\d{3}\s\d{3}","[a-zA-Z]\d{12}",
        "\d{3}-\d{2}-\d{4}","(([0][1-9]|[1][0-2])\d{3}([1-9][0-9]{3})41([0][1-9]|[1][0-9]|[3][0-1]))",
        "\d{10}", "([0][1-9]|[1][0-2])[a-zA-Z]{3}\d{2}(0[1-9]|[1-2][0-9]|3[0-1])\d", "[a-zA-Z]\d{4} \d{5} \d{5}","[a-zA-Z]\\d{14}",
        "\d{3} \d{3} \d{3}", "\d{12}", "[a-zA-Z]{3}-\d{2}-\d{4}", "[a-zA-Z]{1}[0-9]{4,8}", 
        "[a-zA-Z]{2}[0-9]{3,7}", "[0-9]{8}", "[a-zA-Z]\d{9}", "\d{7}", "\d{2}\s\d{3}\s\d{3}", "[1-9]{2}\d{5}", "\d{7,9}", "\d{7}[a-zA-Z]"
        ,"[a-zA-Z]\d{2}-\d{2}-\d{4}", "[a-zA-Z]\d{8}", "[a-zA-Z]{3}\*\*[a-zA-Z]{2}\d{3}[a-zA-Z]\d", "[a-zA-Z]\d{6}", "[a-zA-Z]\d{3}-\d{4}-\d{4}-\d{2}",
        "\d{6}-\d{3}"]

        for r in dl_regex_usa_states:
            for i in re.finditer(r, content):
                result.add(i.group())
        if len(result) > 0:
            return 1
        return 0
    
    # def data_assign_rowby(self, photo_id, date, victimname, zipcodes, states, valid_dl, dl_number, full_address, writer):
    def data_assign_rowby(self, photo_id, date, victimname, zipcodes, states, valid_dl, dl_number, full_address, writer):
        num_zip = len(zipcodes)
        num_states = len(states)
        
        if num_zip == 0 and num_states == 0:
            print("im here")
            writer.writerow([photo_id, date, victimname, "", "", valid_dl, dl_number, full_address])
        
        for i in range(len(zipcodes)):
            if len(zipcodes) > 0:
                zipcode = zipcodes.pop(0)
                state = states.pop(0)
                num_zip -= 1
            else:
                zipcode = ""
                state = ""
            writer.writerow([photo_id, date, victimname, zipcode, state, valid_dl, dl_number, full_address])

if __name__ == '__main__':
    folder_textdoc_path = "C:/Users/jonat/OneDrive/Documents/VisualStudioRepositories/Drivers_Licenses_Parser/TextfilesDL"
    # folder_textdoc_path = "C:/Users/jonat/OneDrive/Documents/EBCS Research/TestText"
    textdoc_paths = base_parser.get_textdoc_paths(folder_textdoc_path)
    headerList = ['Pic Id', 'Date', 'Victim Name', 'Zipcode', 'State', 'Valid DL','DL Number','Full Address']
    with open('driver_licenses_3'+'.csv','w', newline='', encoding='utf-8') as f1:
        dw = csv.DictWriter(f1, delimiter=',', fieldnames=headerList)
        dw.writeheader()
        writer=csv.writer(f1, delimiter=',')#lineterminator='\n',
    # for i in np.arange(0,9):
    #     row = data[i]
    #     writer.writerow(row)
  
        for text_doc in textdoc_paths:
            writer=csv.writer(f1, delimiter=',')
            dl = DriverLiecense()
            file_name = os.path.basename(text_doc)

            #### parse photo id and date
            photo_id, date = dl.get_date_and_id_from_title(file_name)
            if photo_id:
                dl.photo_id = photo_id
            if date:
                dl.date = date

            ### parse zipcode and state
            with open(text_doc, encoding = "utf-8") as f:
                content = f.readlines()
            if content:
                text_des = ' '.join(content[0:len(content)-1])
            else:
                writer.writerow([dl.photo_id, dl.date, "", "", "", ""])
                continue
            # print((text_des).encode('utf-8'))

            if content:
                # if photo_id == '221134':
                    # print(text_des)
                info_zipcode = dl.check_zipcode(text_des)
                dl.zipcode.extend([i[0] for i in info_zipcode])
                dl.state.extend([i[1] for i in info_zipcode])

                # for i in dl.zipcode:
                #     print("zip", i)
                # for i in dl.state:
                #     print("state", i)

                ## Validate victim name
                valid_victim_name = dl.victim_name(text_des)
                # print(valid_victim_name)
                if valid_victim_name:
                    dl.victimname = valid_victim_name
                else:
                    dl.victimname='NA'

                ### validate date
                valid_date = dl.validate_exp_date(text_des)
                dl.valid_dl = valid_date

                ##Validate full address
                valid_full_address = dl.validate_full_address(text_des)
                dl.full_address = valid_full_address

                ## validate drivers lience number
                liecense_num = dl.validate_dl_number(text_des)
                dl.dl_number = liecense_num
                # print(dl.dl_number)
                print("------------------")

            # for i,code in enumerate(check.zipcode):
            #     writer.writerow()



            # print(check.photo_id, check.date, check.bankname, check.zipcode, check.state, check.amount)
            #writer.writerow([dl.photo_id, dl.date, dl.victimname, dl.zipcode, dl.state, dl.valid_dl, dl.dl_number, ''])
            dl.data_assign_rowby(dl.photo_id, dl.date, dl.victimname, dl.zipcode, dl.state, dl.valid_dl, dl.dl_number, dl.full_address, writer)
