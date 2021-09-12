# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_intent_name, get_dialog_state
from ask_sdk_model import Response,DialogState,Intent
from ask_sdk_model.dialog import ElicitSlotDirective

import requests,json
from xml.etree import ElementTree as ET
from random import choice

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

url = "http://tpancare.panhealth.com/panwebservicev1/Service.asmx?WSDL"

headers = {
            "Content-Type": "text/xml; charset=utf-8"
}


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to pan health , We’re very glad you decided to trust us. You can say Help to know more information"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class RegistrationHandler(AbstractRequestHandler):
    
    '''Handler for Regstration Intent'''
    
    def can_handle(self,handler_input):
        
        return ask_utils.is_intent_name("Registration")(handler_input)
        
    def handle(self,handler_input):
        
        name = ask_utils.request_util.get_slot(handler_input, "name").value
        
        number = ask_utils.request_util.get_slot(handler_input, "phonenumber").value
        
        gender = ask_utils.request_util.get_slot(handler_input, "gender").value
        
        x=name.split()
        Firstname=""
        Midname=""
        Lastname=""
        space_count=len(x)
        if(space_count==1):
            Firstname=x[0]
            Midname=""
            Lastname=""
        elif(space_count==2):
            Firstname=x[0]
            Midname=x[1]
            Lastname=""
        elif(space_count==3):
            Firstname=x[0]
            Midname=x[1]
            Lastname=x[2]
        else:
            Firstname = x[0]
            Midname = x[1]
            Lastname = x[2]
            
        
        if gender.lower() == "male":
            gender = "m"
        if gender.lower() == "female":
            gender = "f"
        if len(gender) > 1:
            gender = gender[0].upper()
        gender = gender.upper()
        
        
        data ="""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <CreateNewMember xmlns="http://tempuri.org/">
                    <strFirst>"""+str(Firstname)+"""</strFirst>
                    <strMid>"""+str(Midname)+"""</strMid>
                    <strLast>"""+str(Lastname)+"""</strLast>
                    <strGen>"""+str(gender)+"""</strGen>
                    <strEmailAdd>"""+str(Firstname)+"""@panhealthmail.com</strEmailAdd>
                    <strPhone>"""+str(number)+"""</strPhone>
                    <intcontacttype>1</intcontacttype>
                </CreateNewMember>
            </soap:Body>
        </soap:Envelope>"""
        
        response = requests.post(url,data = data,headers = headers)

        xmltree = response.content
        
        xmltree = xmltree.decode('utf-8')
        
        xmltree = xmltree.strip()

        myroot = ET.fromstring(xmltree)
        
        logindetails = []
        
        for x in myroot[0][0][0]:
            logindetails.append(x.text)
        
        speak_output = "That’s it! You have successfully registered with PanHealth. Your login ID is "+str(logindetails[0])+" and password is "+str(logindetails[1])
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class LoginHandler(AbstractRequestHandler):
    """Handler for Login of user ."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Login")(handler_input) and get_dialog_state(handler_input = handler_input) == DialogState.COMPLETED

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        loginID = ask_utils.request_util.get_slot(handler_input, "loginID").value
        password = ask_utils.request_util.get_slot(handler_input, "password").value
        try:
            number = ask_utils.request_util.get_slot(handler_input, "number").value
            password = str(password) + str(number)
        except:
            pass
            
        # password = password.lower()
           
        password = password.strip()
        
        password = "".join(password.split(' '))
        password=password.replace(" ","")
        loginID = loginID.rjust(11,"0")
        
        if "A" not in str(loginID) or "a" not in str(loginID):
            loginID = "A"+str(loginID)
            
        if len(str(loginID)) > 12:
            
            speak_output = "Sorry, the information entered is incorrect. please check the ID"#please check
        else:
            data = """<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                      <soap:Body>
                        <getMemberinfo_json xmlns="http://tempuri.org/">
                          <strUserid>"""+str(loginID)+"""</strUserid>
                          <strPass>"""+str(password)+"""</strPass>
                        </getMemberinfo_json>
                      </soap:Body>
                    </soap:Envelope>"""
                        
            response = requests.post(url,data = data,headers = headers)
            jsonobj = json.loads(response.content.decode('utf-8').strip().split('<?xml')[0])
            
            user_session = handler_input.attributes_manager.session_attributes

            if len(jsonobj['Posts']) == 0:
            	speak_output = "Sorry, it seems that the credentials you entered are wrong. Try again with correct credentials. Make sure you have created an account before trying to log in. "
            	user_session[str(loginID)] = False
            else:
            	speak_output = "Details are correct. We are delighted to have you among us "+str(jsonobj['Posts'][0]['ME_FIRSTNAME'])#please check
            	user_session[str(loginID)] = True

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class MedInfoHandler(AbstractRequestHandler):
    """Handler for Medicine Information Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("MedInfo")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        memberID = ask_utils.request_util.get_slot(handler_input,"memberID").value
        memberID = memberID.rjust(11,'0')
        if "A" not in str(memberID) or "a" not in str(memberID):
            memberID = "A"+str(memberID)
        cur_session = handler_input.attributes_manager.session_attributes
        if str(memberID) in cur_session.keys() and cur_session[str(memberID)] :

            if len(str(memberID)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the ID"

            else:

                data = """<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <getMedicineInformation_json xmlns="http://tempuri.org/">
                      <strMemberId>"""+str(memberID)+"""</strMemberId>
                    </getMedicineInformation_json>
                  </soap:Body>
                </soap:Envelope>"""
                response = requests.post(url,data = data,headers = headers) 
                jsonobj = json.loads(response.content.decode('utf-8').strip().split('<?xml')[0])
                
                if len(jsonobj['Posts']) != 0:

                    speak_output = "These are the listed medicines "+str(len(jsonobj['Posts']))+" in your account.: These are the listed medicines : "
                    count=0
                    for i in range(len(jsonobj['Posts'])):
                    	speak_output+=str(jsonobj['Posts'][i]['CMD_MEDICINENAME'])
                    	for j in range(1,7):
                    		if jsonobj['Posts'][i]['CMD_TIME'+str(j)] != None:
                    			count+=1
                    	speak_output+=" of "+str(count)+" times a day "
                    	speak_output += "and "
                    	count=0
                    speak_output = speak_output[:-4]#please check
                else:
                    
                    speak_output="Hmm... something’s not right. I couldn’t find your medicine in your list or you don't have any medicines in yout account"

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )


        else:
            return (
            handler_input.response_builder
                .speak("Sorry the task was not successful. You must Login first")#please check
                .ask("Do you want to login now ?")
                .add_directive(directive=ElicitSlotDirective(updated_intent=Intent(name="Login"),slot_to_elicit="loginID"))
                .response
            )



class AddingMedicinesHandler(AbstractRequestHandler):
    """Handler for AddingMedicines Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AddingMedicines")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        MemberId = ask_utils.request_util.get_slot(handler_input,"memberID").value
        
        MemberId = MemberId.rjust(11,'0')
        
        if "A" not in str(MemberId) or "a" not in str(MemberId):
            MemberId = "A"+str(MemberId)
            
        cur_session = handler_input.attributes_manager.session_attributes
        
        if str(MemberId) in cur_session.keys() and cur_session[str(MemberId)]:

            if len(str(MemberId)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the ID "#please check
                
            else:
                
                physician_name = ask_utils.request_util.get_slot(handler_input,"physician_name").value
                med_name = ask_utils.request_util.get_slot(handler_input,"med_name").value
                quantity = ask_utils.request_util.get_slot(handler_input,"med_quantity").value
                frequency = ask_utils.request_util.get_slot(handler_input,"frequency").value
                comments = ask_utils.request_util.get_slot(handler_input,"comments").value
                morningslot=ask_utils.request_util.get_slot(handler_input,"morningslot").value
                eveningslot=ask_utils.request_util.get_slot(handler_input,"eveningslot").value
                afternoonslot=ask_utils.request_util.get_slot(handler_input,"afternoonslot").value
                nightslot=ask_utils.request_util.get_slot(handler_input,"nightslot").value
                
                total_quantity = int(frequency) * int(quantity)
                
                morningtime = "08:00" if morningslot.lower() == "yes" else ""
                afternoontime = "12:30" if afternoonslot.lower() == "yes" else ""
                eveningtime = "17:30" if eveningslot.lower() == "yes" else ""
                nighttime = "20:30" if nightslot.lower() == "yes" else ""
                
                morningquantity = quantity if morningslot.lower() == "yes" else ""
                afternoonquantity = quantity if afternoonslot.lower() == "yes" else ""
                eveningquantity = quantity if eveningslot.lower() == "yes" else ""
                nightquantity = quantity if nightslot.lower() == "yes" else ""
                
                data ="""<?xml version="1.0" encoding="utf-8"?>
                            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                              <soap:Body>
                                <addMedication xmlns="http://tempuri.org/">
                                  <strMemberId>"""+str(MemberId)+"""</strMemberId>
                                  <strPhysicianName>"""+str(physician_name)+"""</strPhysicianName>
                                  <strMedicineName>"""+str(med_name)+"""</strMedicineName>
                                  <strQuantity>"""+str(quantity)+"""</strQuantity>
                                  <strFrequency>"""+str(frequency)+"""</strFrequency>
                                  <strComments>"""+str(comments)+"""</strComments>
                                  <strProductcode></strProductcode>
                                  <strSerialno></strSerialno>
                                  <strBayno></strBayno>
                                  <strQti1>"""+str(morningquantity)+"""</strQti1>
                                  <strTIME1>"""+str(morningtime)+"""</strTIME1>
                                  <strQti2></strQti2>
                                  <strTIME2></strTIME2>
                                  <strQti3>"""+str(afternoonquantity)+"""</strQti3>
                                  <strTIME3>"""+str(afternoontime)+"""</strTIME3>
                                  <strQti4></strQti4>
                                  <strTIME4></strTIME4>
                                  <strQti5>"""+str(eveningquantity)+"""</strQti5>
                                  <strTIME5>"""+str(eveningtime)+"""</strTIME5>
                                  <strQti6>"""+str(nightquantity)+"""</strQti6>
                                  <strTIME6>"""+str(nighttime)+"""</strTIME6>
                                  <reorderLevel>5</reorderLevel>
                                  <reorderQty>10</reorderQty>
                                  <TotalQty>"""+str(total_quantity)+"""</TotalQty>
                                </addMedication>
                              </soap:Body>
                            </soap:Envelope>"""
                response = requests.post(url,data = data,headers = headers)
                
                xmltree = response.content
                        
                xmltree = xmltree.decode('utf-8')
                        
                xmltree = xmltree.strip()
                
                myroot = ET.fromstring(xmltree)
                
                if myroot[0][0][0].text == 'True':
                    speak_output = "You’re all set ! Your medicine is successfully added. You will be given timely reminders and updates about your medicine. "
                else:
                    speak_output = "Sorry the task was not sucessful. You must start again!"#please check
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )

        else:
            return (
                handler_input.response_builder
                    .speak("Sorry the task was not successful. You must Login first")
                    .ask("Do you want to login now ?")
                    .add_directive(directive = ElicitSlotDirective(updated_intent = Intent('Login') , slot_to_elicit = "loginID"))
                    .response
            )



class SearchMedHandler(AbstractRequestHandler):
    """Handler for SearchMedHandler  Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SearchMed")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        medname = ask_utils.request_util.get_slot(handler_input,"search_med").value
        memberID = ask_utils.request_util.get_slot(handler_input,"search_med_id").value
        memberID = memberID.rjust(11,'0')
        cur_session = handler_input.attributes_manager.session_attributes
        if "A" not in str(memberID) or "a" not in str(memberID):
            memberID = "A"+str(memberID)
        if str(memberID) in cur_session.keys() and cur_session[str(memberID)] :
            if len(str(memberID)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the ID"#please check
            else:
                data ="""<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <getMedicineInformation_json xmlns="http://tempuri.org/">
                                    <strMemberId>"""+str(memberID)+"""</strMemberId>
                                </getMedicineInformation_json>
                            </soap:Body>
                        </soap:Envelope>"""
                response = requests.post(url,data = data,headers = headers)
                jsonobj = json.loads(response.content.decode('utf-8').strip().split('<?xml')[0])
                med_list = []
                timings = []
                for i in range(len(jsonobj['Posts'])):
                    med_list.append(jsonobj['Posts'][i]['CMD_MEDICINENAME'])
                    if jsonobj['Posts'][i]['CMD_MEDICINENAME'].upper() == medname.upper():
                        for j in range(1,7):
                            if jsonobj['Posts'][i]['CMD_TIME'+str(j)] != None:
                                time = jsonobj['Posts'][i]['CMD_TIME'+str(j)]
                                if int(time.split(':')[0]) < 12:
                                    time += "AM"
                                else:
                                    time += "PM"
                                timings.append(time)
                        speak_output="<speak>Bingo! I have found your "+medname+" medicine for you and timings for the same is <say-as interpret-as='time'>"+" ".join(timings)+"</say-as></speak>"#please check
                        break
                else:
                    speak_output="Hmm... something’s not right. I couldn’t find your medicine in your list. You only have following medicines  "+",".join(med_list)
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )
        else:
            return (
            handler_input.response_builder
                .speak("Sorry the task was not sucessful. You must Login first")#please check
                .ask("Do you want to login now ?")
                .add_directive(directive=ElicitSlotDirective(updated_intent=Intent(name="Login"),slot_to_elicit="loginID"))
                .response
            )



class DeleteMedHandler(AbstractRequestHandler):
    """Handler for DeleteMed Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DeleteMed")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        med_name = ask_utils.request_util.get_slot(handler_input,"delete_med").value
        memberID = ask_utils.request_util.get_slot(handler_input,"memid").value
        
        memberID = memberID.rjust(11,'0')
        if "A" not in str(memberID) or "a" not in str(memberID):
            memberID = "A"+str(memberID)
            
        cur_session = handler_input.attributes_manager.session_attributes
        
        if str(memberID) in cur_session.keys() and cur_session[str(memberID)] :

            if len(str(memberID)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the ID"#please check
            else:
                data = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <getMedicineInformation_json xmlns="http://tempuri.org/">
                                    <strMemberId>"""+str(memberID)+"""</strMemberId>
                                </getMedicineInformation_json>
                            </soap:Body>
                        </soap:Envelope>"""
                response = requests.post(url,data = data,headers = headers)
                jsonobj = json.loads(response.content.decode('utf-8').strip().split('<?xml')[0])
                med_list=[]
                if len(jsonobj['Posts']) == 0:
                    speak_output = " Sorry you don't have any medicines in your list to delete. "#please check
                else:
                    for i in range(len(jsonobj['Posts'])):
                        med_list.append(jsonobj['Posts'][i]['CMD_MEDICINENAME'])
                    for x in med_list:
                        if med_name.upper()==x.upper():
                            med_name=x
                            break
                    if med_name in med_list:
                        data = """<?xml version="1.0" encoding="utf-8"?>
                            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                                <soap:Body>
                                    <DeleteMedicine xmlns="http://tempuri.org/">
                                        <strMedName>"""+str(med_name)+"""</strMedName>
                                        <strMemID>"""+str(memberID)+"""</strMemID>
                                    </DeleteMedicine>
                                </soap:Body>
                            </soap:Envelope>"""
                        response = requests.post(url,data = data,headers = headers)
                        
                            
                        xmltree = response.content
                                
                        xmltree = xmltree.decode('utf-8')
                                
                        xmltree = xmltree.strip()
                                
                        myroot = ET.fromstring(xmltree)
                        if myroot[0][0][0].text:
                            data = """<?xml version="1.0" encoding="utf-8"?>
                                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                                        <soap:Body>
                                            <getMedicineInformation_json xmlns="http://tempuri.org/">
                                                <strMemberId>"""+str(memberID)+"""</strMemberId>
                                            </getMedicineInformation_json>
                                        </soap:Body>
                                    </soap:Envelope>"""
                            response = requests.post(url,data = data,headers = headers)
                            jsonobj = json.loads(response.content.decode('utf-8').strip().split('<?xml')[0])
                            new_med_list=[]
                            for i in range(len(jsonobj['Posts'])):
                                new_med_list.append(jsonobj['Posts'][i]['CMD_MEDICINENAME'])
                                
                            speak_output="Congratulations your "+med_name +" medicine is deleted successfully. You have following medicines "+",".join(new_med_list)
                        else:
                            speak_output = "I’m sorry, but there seems to be some internal error. The medicine {} has not been deleted. You can say “help” to know more".format(med_name)#please check
                    else:
                        speak_output="Sorry medicine you entered not found.You only have following medicines "+",".join(med_list)#please check
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )

        else:
            
            return (
            handler_input.response_builder
                .speak("Sorry the task was not successful. You must Login first")#please check
                .ask("Do you want to login now ?")
                .add_directive(directive=ElicitSlotDirective(updated_intent=Intent(name="Login"),slot_to_elicit="loginID"))
                .response
            )


class virtualpillboxHandler(AbstractRequestHandler):
    """ Handler for Virtual pill box. """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("virtualpillbox")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        daytiming = ask_utils.request_util.get_slot(handler_input, "virtual_med").value
        
        daytiming = daytiming.lower()
        
        memberID = ask_utils.request_util.get_slot(handler_input,"memID").value
        
        memberID = memberID.rjust(11,'0')
        
        if "A" not in str(memberID) or "a" not in str(memberID):
            memberID = "A"+str(memberID)
            
        cur_session = handler_input.attributes_manager.session_attributes
        
        if str(memberID) in cur_session.keys() and cur_session[str(memberID)] :
            
            if len(str(memberID)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the ID"
                    
            data = """<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <getMedicineInformation_json xmlns="http://tempuri.org/">
                      <strMemberId>"""+str(memberID)+"""</strMemberId>
                    </getMedicineInformation_json>
                  </soap:Body>
                </soap:Envelope>"""
                        
            response = requests.post(url,data = data,headers = headers)
            
            xmltree = response.content
                    
            xmltree = xmltree.decode('utf-8')
                    
            xmltree = xmltree.strip()
            
            xmltree = xmltree.split('<?xml ')
            
            jsonobj = json.loads(xmltree[0])
            
            morning_timings=['06:30','07:00','07:30','08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30']
            evening_timings=['17:00','17:30','18:00','18:30','19:00','19:30','20:00']
            afternoon_timings=['12:00','12:30','13:00','13:30','14:00','14:30','15:00','15:30','16:00','16:30']
            night_timimgs=['20:00','20:30','21:00','21:30','22:00','22:30','23:00','23:00']
            other_timings1=['13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00']
            other_timings2=['08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30']
            
            speak_output="Your "+str(daytiming)+" medicines are : "
            
            flag=False
            
            for i in range(len(jsonobj['Posts'])):
                if daytiming == "morning" and jsonobj['Posts'][i]['CMD_TIME1'] in morning_timings:
                    speak_output+=jsonobj['Posts'][i]['CMD_MEDICINENAME']+" of Dosage "+jsonobj['Posts'][i]['CMD_QTY1']+" , "
                    flag = True
                elif daytiming == "afternoon" and jsonobj['Posts'][i]['CMD_TIME2'] in afternoon_timings:
                    speak_output+=jsonobj['Posts'][i]['CMD_MEDICINENAME']+" of Dosage "+jsonobj['Posts'][i]['CMD_QTY2']+" , "
                    flag = True
                elif daytiming == "evening" and jsonobj['Posts'][i]['CMD_TIME3'] in evening_timings:
                    speak_output+=jsonobj['Posts'][i]['CMD_MEDICINENAME']+" of Dosage "+jsonobj['Posts'][i]['CMD_QTY3']+" , "
                    flag = True
                elif daytiming == "night" and jsonobj['Posts'][i]['CMD_TIME4'] in night_timimgs:
                    speak_output+=jsonobj['Posts'][i]['CMD_MEDICINENAME']+" of Dosage "+jsonobj['Posts'][i]['CMD_QTY4']+" , "
                    flag = True
            if not flag:
                speak_output = "No Medicines Found" #please check
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )
        
        else:
            return (
                handler_input.response_builder
                    .speak("Sorry the task was not successful. You must Login first!")#please check
                    .ask("Do you want to login now ?")
                    .add_directive(directive = ElicitSlotDirective(updated_intent = Intent('Login') , slot_to_elicit = "loginID"))
                    .response
            )



class refillmedIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("refillmed")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        memberID=ask_utils.request_util.get_slot(handler_input,"memid").value
        
        memberID = memberID.rjust(11,'0')
        if "A" not in str(memberID) or "a" not in str(memberID):
            memberID = "A"+str(memberID)
        medname = ask_utils.request_util.get_slot(handler_input,"medname").value
        total =  ask_utils.request_util.get_slot(handler_input,"totalqty").value
        
        cur_session = handler_input.attributes_manager.session_attributes

        if str(memberID) in cur_session.keys() and cur_session[str(memberID)]:
            if len(str(memberID)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the ID"#please check
            else:
                data="""<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                      <soap:Body>
                        <addMedQuentity xmlns="http://tempuri.org/">
                          <strMemberId>"""+str(memberID)+"""</strMemberId>
                          <strMedicineName>"""+str(medname)+"""</strMedicineName>
                          <reorderLevel>5</reorderLevel>
                          <reorderQty>10</reorderQty>
                          <TotalQty>"""+str(total)+"""</TotalQty>
                        </addMedQuentity>
                      </soap:Body>
                    </soap:Envelope>"""
                response = requests.post(url,data = data,headers = headers) 
                xmltree = response.content                      
                xmltree = xmltree.decode('utf-8')
                    
                xmltree = xmltree.strip()
                 
                myroot = ET.fromstring(xmltree)
                if myroot[0][0][0].text == 'True':
                    speak_output = "You’re all set ! Your medicine is successfully updated. You will be given timely reminders and updates about your medicine. "
                else:
                    speak_output = "Sorry the task was not sucessful. You must start again!"#please check

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )
        else:
            return (
                handler_input.response_builder
                    .speak("Sorry the task was not successful. You must Login first")
                    .ask("Do you want to login now ?")
                    .add_directive(directive = ElicitSlotDirective(updated_intent = Intent('Login') , slot_to_elicit = "loginID"))
                    .response
            )


class setReminderIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("setReminder")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        memberID=ask_utils.request_util.get_slot(handler_input,"memid").value
        
        memberID = memberID.rjust(11,'0')
        if "A" not in str(memberID) or "a" not in str(memberID):
            memberID = "A"+str(memberID)
        calldate = ask_utils.request_util.get_slot(handler_input,"calldate").value
        calltime =  ask_utils.request_util.get_slot(handler_input,"calltime").value
        phonenum =  ask_utils.request_util.get_slot(handler_input,"phonenum").value
        remdesc = "Medication"
        cur_session = handler_input.attributes_manager.session_attributes

        if str(memberID) in cur_session.keys() and cur_session[str(memberID)]:
            if len(str(memberID)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the credentials you entered"#please check
            else:
                data="""<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <SetReminders xmlns="http://tempuri.org/">
                                    <strCUSTOMER_ID>"""+str(memberID)+"""</strCUSTOMER_ID>
                                    <strCALLDATE>"""+str(calldate)+"""</strCALLDATE>
                                    <strCALLTIME>"""+str(calltime)+"""</strCALLTIME>
                                    <strREMDESC>"""+str(remdesc)+"""</strREMDESC>
                                    <strME_ID>9999</strME_ID>
                                    <strPHONENO>"""+str(phonenum)+"""</strPHONENO>
                                </SetReminders>
                            </soap:Body>
                        </soap:Envelope>"""
                response = requests.post(url,data = data,headers = headers) 
                xmltree = response.content                      
                xmltree = xmltree.decode('utf-8')
                    
                xmltree = xmltree.strip()
                 
                myroot = ET.fromstring(xmltree)
                if myroot[0][0][0].text == 'True':
                    speak_output = "You’re all set ! You will be given timely reminders about your medicine. "
                else:
                    speak_output = "Sorry the task was not sucessful. You must start again!"#please check

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )
        else:
            return (
                handler_input.response_builder
                    .speak("Sorry the task was not successful. You must Login first")
                    .ask("Do you want to login now ?")
                    .add_directive(directive = ElicitSlotDirective(updated_intent = Intent('Login') , slot_to_elicit = "loginID"))
                    .response
            )

class takeMedicationIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("takeMedication")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        memberID=ask_utils.request_util.get_slot(handler_input,"memid").value
        
        memberID = memberID.rjust(11,'0')
        if "A" not in str(memberID) or "a" not in str(memberID):
            memberID = "A"+str(memberID)
        medname = ask_utils.request_util.get_slot(handler_input,"mednametaking").value
        medqty =  ask_utils.request_util.get_slot(handler_input,"medqty").value
        
        cur_session = handler_input.attributes_manager.session_attributes

        if str(memberID) in cur_session.keys() and cur_session[str(memberID)]:
            if len(str(memberID)) > 12:
                speak_output = "Sorry, the information entered is incorrect. please check the credentials you entered"#please check
            else:
                data="""<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <Take_Medication xmlns="http://tempuri.org/">
                                     <strUser_id>"""+str(memberID)+"""</strUser_id>
                                     <intMedicineid></intMedicineid>
                                     <strMedicineName>"""+str(medname)+"""</strMedicineName>
                                     <strMedQty>"""+str(medqty)+"""</strMedQty>
                                     <strDay></strDay>
                                     <strBayno></strBayno>
                                     <strtimespan></strtimespan>
                                     <intstate></intstate>
                                     <timestamp></timestamp>
                                </Take_Medication>
                              </soap:Body>
                        </soap:Envelope>"""
                response = requests.post(url,data = data,headers = headers) 
                xmltree = response.content                      
                xmltree = xmltree.decode('utf-8')
                    
                xmltree = xmltree.strip()
                 
                myroot = ET.fromstring(xmltree)
                if myroot[0][0][0].text == 'True':
                    speak_output = "You’re all set ! Your medicine will be updated. "
                else:
                    speak_output = "Sorry the task was not sucessful. You must start again!"#please check

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )
        else:
            return (
                handler_input.response_builder
                    .speak("Sorry the task was not successful. You must Login first")
                    .ask("Do you want to login now ?")
                    .add_directive(directive = ElicitSlotDirective(updated_intent = Intent('Login') , slot_to_elicit = "loginID"))
                    .response
            )
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        pan_health_services = [
            "For registering yourself with pan health you can say 'Create Pan Health Account'",
            
            "Say 'login to my pan health account' to get connected with pan health services",
            
            "You can also say 'Add my medicines to my account'",
            
            "Search my medicine in existing list of my account",
            
            "For Deleting the medicine you can say 'I want to delete a medicine'",
            
            "For Medicines Information you can say 'I wonder if you tell me about my medicines'",
            
            "You can also check your morning or evening medicines by 'Tell me my morning medicines'"
            
        ]
        
        random_service = choice(pan_health_services)
        
        speak_output = "Hello there!  "+str(random_service)
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(RegistrationHandler())
sb.add_request_handler(LoginHandler())
sb.add_request_handler(MedInfoHandler())
sb.add_request_handler(AddingMedicinesHandler())
sb.add_request_handler(SearchMedHandler())
sb.add_request_handler(DeleteMedHandler())
sb.add_request_handler(virtualpillboxHandler())
sb.add_request_handler(refillmedIntentHandler())
sb.add_request_handler(setReminderIntentHandler())
sb.add_request_handler(takeMedicationIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()