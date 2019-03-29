########################################################################
# Imports

import wx
import wx.adv
import sys
import os, shutil
import cgi
from sqlalchemy import create_engine, func, and_ , or_
from sqlalchemy.orm import sessionmaker
from setup import Base, Individual, Vehicle, KeyCheck, Location, Event, DefaultImages
from setup import Note, ImageIndividual, ImageVehicle, IndividualToEvent, ImageEvent
from setup import IndividualToLocation, VehicleToEvent, VehicleToIndividual
from setup import LocationToEvent, LocationToVehicle, IndividualToIndividual
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import PIL
from PIL import Image, ImageDraw, ImageOps
import io
import geocoder
#import plotly as ply
#import plotly.graph_objs as go
import requests
import pdb
import folium
import numpy as np
import webbrowser
import face_recognition

encryptionKey = ""
session = None

########################################################################
# GUI Classes
class editWindow(wx.Frame):
    def __init__(self,info,search):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Edit", size=(500,500))
        self.panel = wx.ScrolledWindow(self)
        self.panel.SetScrollbars(1, 1, 1, 1)
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        if info[0] =="Individual":
            self.SetTitle('Edit Individual')

        if info[0] =="Vehicle":
            self.SetTitle('Edit Vehicle')

        if info[0] =="Event":
            self.SetTitle('Edit Event')

        input = editPanel(self.panel, info, search)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(input, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.close)
        self.Layout()
        self.Show()

    def close(self,e):
        self.Destroy()

class editPanel(wx.Panel):
    def __init__(self, parent,info,search):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        col = wx.BoxSizer(wx.VERTICAL)

        self.currentDirectory = os.getcwd()
        self.paths=[]

        if info[0] == "Individual":

            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="First Name")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, info[1].firstname)
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Last Name")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, info[1].lastname)
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="Workplace")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, info[1].workplace)
            txtFour=wx.StaticText(self, id=wx.ID_ANY, label="Email")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFour = wx.TextCtrl(self, wx.ID_ANY, info[1].email)
            txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Phone")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFive = wx.TextCtrl(self, wx.ID_ANY, info[1].phone)
            txtSix=wx.StaticText(self, id=wx.ID_ANY, label="Facebook")
            txtSix.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSix = wx.TextCtrl(self, wx.ID_ANY, info[1].facebookurl)
            txtSeven=wx.StaticText(self, id=wx.ID_ANY, label="Twitter")
            txtSeven.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSeven = wx.TextCtrl(self, wx.ID_ANY, info[1].twitterurl)
            txtEight=wx.StaticText(self, id=wx.ID_ANY, label="Linkedin")
            txtEight.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEight = wx.TextCtrl(self, wx.ID_ANY, info[1].linkedinurl)
            txtNine=wx.StaticText(self, id=wx.ID_ANY, label="Primary Affiliation")
            txtNine.SetForegroundColour(wx.Colour(255,255,255))
            self.inputNine = wx.TextCtrl(self, wx.ID_ANY, info[1].organization)
            txtTen=wx.StaticText(self, id=wx.ID_ANY, label="Notes")
            txtTen.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTen =wx.TextCtrl(self,id=wx.ID_ANY,size=(200, 100), style=wx.TE_MULTILINE, value=info[1].notes)
            txtEleven=wx.StaticText(self, id=wx.ID_ANY, label="Known Violent Incidents (Int)")
            txtEleven.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEleven = wx.TextCtrl(self, wx.ID_ANY, str(info[1].violentincidents))
            txtTwelve = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
            txtTwelve.SetForegroundColour(wx.Colour(255,255,255))
            txtThirteen = wx.StaticText(self, id=wx.ID_ANY, label="Upload New Image")
            txtThirteen.SetForegroundColour(wx.Colour(255,255,255))

            addButton = wx.Button(self, wx.ID_ANY, label="Update")
            addButton.info = ["Individual", info[1]]
            addImage = wx.Button(self, wx.ID_ANY, label="Picture")
            self.Bind(wx.EVT_BUTTON, self.onOpenFile, addImage)
            self.Bind(wx.EVT_BUTTON, self.update, addButton)

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(txtThirteen, 0,wx.ALL, 5)
            col.Add(addImage, 0,wx.ALL, 5)
            col.Add(txtTwelve, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0, wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)
            col.Add(txtFour, 0, wx.ALL, 5)
            col.Add(self.inputFour, 0,wx.ALL, 5)
            col.Add(txtFive, 0, wx.ALL, 5)
            col.Add(self.inputFive, 0,wx.ALL, 5)
            col.Add(txtSix, 0,wx.ALL, 5)
            col.Add(self.inputSix, 0,wx.ALL, 5)
            col.Add(txtSeven, 0,wx.ALL, 5)
            col.Add(self.inputSeven, 0,wx.ALL, 5)
            col.Add(txtEight, 0,wx.ALL, 5)
            col.Add(self.inputEight, 0,wx.ALL, 5)
            col.Add(txtNine, 0, wx.ALL, 5)
            col.Add(self.inputNine, 0,wx.ALL, 5)
            col.Add(txtEleven, 0, wx.ALL, 5)
            col.Add(self.inputEleven, 0,wx.ALL, 5)
            col.Add(txtTen, 0, wx.ALL, 5)
            col.Add(self.inputTen, 0,wx.ALL, 5)

            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

            self.SetSizer(col)

        if info[0] == "Vehicle":
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Plate")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, info[1].plate)
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Color")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, info[1].color)
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="Make And Model")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, info[1].make_model)
            txtFour = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            txtFive = wx.StaticText(self, id=wx.ID_ANY, label="Upload New Image")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            addButton = wx.Button(self, wx.ID_ANY, label="Update")
            addButton.info = ["Vehicle", info[1]]
            addImage = wx.Button(self, wx.ID_ANY, label="Picture")
            self.Bind(wx.EVT_BUTTON, self.onOpenFile, addImage)
            self.Bind(wx.EVT_BUTTON, self.update, addButton)

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(txtFive, 0,wx.ALL, 5)
            col.Add(addImage, 0,wx.ALL, 5)
            col.Add(txtFour, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0, wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)

            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

        if info[0] == "Event":

            locid = session.query(LocationToEvent).filter_by(event_id=info[1].id).all()
            location = session.query(Location).filter_by(id=locid[-1].location_id).one()

            lat=wx.StaticText(self, id=wx.ID_ANY, label="Latitude")
            lat.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLat = wx.TextCtrl(self, wx.ID_ANY, location.latitude)
            long=wx.StaticText(self, id=wx.ID_ANY, label="Longitude")
            long.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLong = wx.TextCtrl(self, wx.ID_ANY, location.longitude)
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Address")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, location.streetaddress)
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Neighborhood")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, location.neighborhood)
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="City")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, location.city)
            txtFour=wx.StaticText(self, id=wx.ID_ANY, label="State")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFour = wx.TextCtrl(self, wx.ID_ANY, location.state)
            txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Zip")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFive = wx.TextCtrl(self, wx.ID_ANY, location.zip)
            txtSix=wx.StaticText(self, id=wx.ID_ANY, label="Event Date")
            txtSix.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSix = wx.TextCtrl(self, wx.ID_ANY, info[1].date)
            txtSeven=wx.StaticText(self, id=wx.ID_ANY, label="Event Title")
            txtSeven.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSeven = wx.TextCtrl(self, wx.ID_ANY, info[1].title)
            txtEight=wx.StaticText(self, id=wx.ID_ANY, label="Description")
            txtEight.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEight = wx.TextCtrl(self, wx.ID_ANY,size=(200, 100), style=wx.TE_MULTILINE, value=info[1].description)
            txtNine = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
            txtNine.SetForegroundColour(wx.Colour(255,255,255))
            addButton = wx.Button(self, wx.ID_ANY, label="Update")
            addButton.info = ["Event", info[1], locid[-1]]
            self.Bind(wx.EVT_BUTTON, self.update, addButton)

            col.Add(txtNine, 0,wx.ALL, 5)
            col.Add(lat, 0,wx.ALL, 5)
            col.Add(self.inputLat, 0,wx.ALL, 5)
            col.Add(long, 0, wx.ALL, 5)
            col.Add(self.inputLong, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0, wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)
            col.Add(txtFour, 0,wx.ALL, 5)
            col.Add(self.inputFour, 0,wx.ALL, 5)
            col.Add(txtFive, 0,wx.ALL, 5)
            col.Add(self.inputFive, 0,wx.ALL, 5)
            col.Add(txtSix, 0,wx.ALL, 5)
            col.Add(self.inputSix, 0,wx.ALL, 5)
            col.Add(txtSeven, 0,wx.ALL, 5)
            col.Add(self.inputSeven, 0,wx.ALL, 5)
            col.Add(txtEight, 0,wx.ALL, 5)
            col.Add(self.inputEight, 0,wx.ALL, 5)

            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

        self.SetSizer(col)

    def onOpenFile(self, event):
        wildcard = "JPEG (*.jpg)|*.jpg"
        dlg = wx.FileDialog(
            self, message="Choose Image To Upload",
            defaultDir=self.currentDirectory,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.paths = paths
        dlg.Destroy()

    def update(self, event):
        widget = event.GetEventObject()
        info = widget.info

        if info[0] == "Individual":
            info[1].firstname = self.inputOne.GetValue()
            info[1].lastname = self.inputTwo.GetValue()
            info[1].workplace = self.inputThree.GetValue()
            info[1].email = self.inputFour.GetValue()
            info[1].phone = self.inputFive.GetValue()
            info[1].facebookurl=self.inputSix.GetValue()
            info[1].twitterurl=self.inputSeven.GetValue()
            info[1].linkedinurl=self.inputEight.GetValue()
            info[1].organization=self.inputNine.GetValue()
            info[1].notes=self.inputTen.GetValue()
            info[1].violentincidents=int(self.inputEleven.GetValue())
            session.add(info[1])
            session.commit()
            if self.paths != []:
                for path in self.paths:
                    with open(path, "rb") as imageFile:
                        byte = imageFile.read()
                        enc = encrypt(byte, encryptionKey)
                        newImage = ImageIndividual(image=enc, individual_id=info[1].id)
                        session.add(newImage)
                        session.commit()

        if info[0] == "Vehicle":
            info[1].plate = self.inputOne.GetValue()
            info[1].color = self.inputTwo.GetValue()
            info[1].make_model = self.inputThree.GetValue()
            session.add(info[1])
            session.commit()
            if self.paths != []:
                for path in self.paths:
                    with open(path, "rb") as imageFile:
                        byte = imageFile.read()
                        enc = encrypt(byte, encryptionKey)
                        newImage = ImageVehicle(image=enc, vehicle_id=info[1].id)
                        session.add(newImage)
                        session.commit()

        if info[0] == "Event":
            info[1].date = self.inputSix.GetValue()
            info[1].title = self.inputSeven.GetValue()
            info[1].description = self.inputEight.GetValue()
            session.add(info[1])
            session.commit()
            newLocation = session.query(Location).filter_by(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
            city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(), latitude=self.inputLat.GetValue(), longitude = self.inputLong.GetValue()).all()
            if newLocation == []:
                newLocation = Location(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
                city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(),latitude=self.inputLat.GetValue(), longitude = self.inputLong.GetValue())
                session.add(newLocation)
                session.commit()
            else:
                newLocation = newLocation[0]
            association =  LocationToEvent(location_id = newLocation.id, event_id = info[1].id)
            session.add(association)
            session.commit()
            session.delete(info[2])
            session.commit()

        wx.MessageBox('Entry Updated')
        frame = wx.GetTopLevelParent(self)
        frame.Destroy()

class additionalInfoWindow(wx.Frame):
    def __init__(self,info):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Link Results", size=(1000,500))
        self.panel = wx.ScrolledWindow(self)
        self.panel.SetScrollbars(1, 1, 1, 1)
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        if info[0] == "ShowLocationIndividuals":
            self.SetTitle("Associated Individuals")

        if info[0] == "ShowVehicleIndividuals":
            self.SetTitle("Known Owner(s)")

        if info[0] == "ShowIndividualVehicles":
            self.SetTitle("Known Vehicles")

        display = additionalInfoPanel(self.panel,info)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(display, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.close)
        self.Layout()
        self.Show()

    def close(self,e):
        self.Destroy()

class additionalInfoPanel(wx.Panel):
    def __init__(self, parent, info):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        col = wx.BoxSizer(wx.VERTICAL)

        self.info = info

        if info[0] == "ShowLocationVehicles":
            title = wx.StaticText(self, id=wx.ID_ANY, label="VEHICLES ASSOCIATED WITH THIS LOCATION")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(LocationToVehicle).filter_by(location_id=info[1].id).all()
            for r in results:
                vehicle = session.query(Vehicle).filter_by(id=r.vehicle_id).one()
                image = session.query(ImageVehicle).filter_by(vehicle_id=vehicle.id).all()
                de = decrypt(image[-1].image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)

                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + vehicle.plate)
                plate.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(plate,0,wx.ALL,10)
                color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + vehicle.color)
                color.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(color,0,wx.ALL,10)
                make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + vehicle.make_model)
                make_model.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(make_model,0,wx.ALL,10)
                card.Add(inforow1)

                inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow6.Add(unlink,0,wx.ALL,10)
                card.Add(inforow6)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)
                self.SetSizer(col)

        if info[0] == "ShowLocationIndividuals":
            title = wx.StaticText(self, id=wx.ID_ANY, label="INDIVIDUALS ASSOCIATED WITH THIS LOCATION")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(IndividualToLocation).filter_by(location_id=info[1].id).all()
            for r in results:
                location = session.query(Location).filter_by(id=r.location_id).one()
                individual = session.query(Individual).filter_by(id=r.individual_id).one()
                image = session.query(ImageIndividual).filter_by(individual_id=individual.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + individual.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + individual.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + individual.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + individual.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + individual.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + individual.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if individual.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= individual.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if individual.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= individual.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if individual.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= individual.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                add.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(add,0,wx.ALL,10)
                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                city.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(city,0,wx.ALL,10)
                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                state.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(state,0,wx.ALL,10)
                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                zip.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(zip,0,wx.ALL,10)
                card.Add(inforow4)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                #in = wx.StaticText(self, id=wx.ID_ANY, label="INCIDENTS: " + str(r.violentincidents))
                #inforow4.Add(in,0,wx.ALL,5)
                notes = wx.StaticText(self, id=wx.ID_ANY, label="NOTES: " + individual.notes)
                notes.SetForegroundColour(wx.Colour(255,255,255))
                inforow5.Add(notes,0,wx.ALL,10)
                card.Add(inforow5)

                inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow6.Add(unlink,0,wx.ALL,10)
                card.Add(inforow6)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if info[0] == "ShowVehicleIndividuals":
            #pdb.set_trace()
            title = wx.StaticText(self, id=wx.ID_ANY, label="INDIVIDUALS ASSOCIATED WITH THIS VEHICLE")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(VehicleToIndividual).filter_by(vehicle_id=info[1].id).all()
            for r in results:
                locId= session.query(IndividualToLocation).filter_by(individual_id=r.individual_id).all()
                location = session.query(Location).filter_by(id=locId[0].location_id).one()
                individual = session.query(Individual).filter_by(id=r.individual_id).one()
                image = session.query(ImageIndividual).filter_by(individual_id=individual.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + individual.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + individual.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + individual.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + individual.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + individual.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + individual.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if individual.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= individual.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if individual.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= individual.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if individual.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= individual.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                add.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(add,0,wx.ALL,10)
                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                city.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(city,0,wx.ALL,10)
                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                state.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(state,0,wx.ALL,10)
                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                zip.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(zip,0,wx.ALL,10)
                card.Add(inforow4)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                #in = wx.StaticText(self, id=wx.ID_ANY, label="INCIDENTS: " + str(r.violentincidents))
                #inforow4.Add(in,0,wx.ALL,5)
                notes = wx.StaticText(self, id=wx.ID_ANY, label="NOTES: " + individual.notes)
                notes.SetForegroundColour(wx.Colour(255,255,255))
                inforow5.Add(notes,0,wx.ALL,10)
                card.Add(inforow5)

                inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow6.Add(unlink,0,wx.ALL,10)
                card.Add(inforow6)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if info[0] == "ShowLocationEvents":
            title = wx.StaticText(self, id=wx.ID_ANY, label="EVENTS AT THIS LOCATION")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(LocationToEvent).filter_by(location_id=info[1].id).all()
            for r in results:
                event = session.query(Event).filter_by(id=r.event_id).one()
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="DATE: " + event.date)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="TITLE: " + event.title)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="DESCRIPTION: " + event.description)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                card.Add(inforow2)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow5.Add(unlink,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)
                col.Add(card)

        if info[0] == "ShowIndividualEvents":
            #pdb.set_trace()
            results = session.query(IndividualToEvent).filter_by(individual_id=info[1].id).all()
            for r in results:
                event = session.query(Event).filter_by(id=r.event_id).one()
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="DATE: " + event.date)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="TITLE: " + event.title)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="DESCRIPTION: " + event.description)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                card.Add(inforow2)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow5.Add(unlink,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)
                col.Add(card)

        if info[0] == "ShowEventIndividuals":
            title = wx.StaticText(self, id=wx.ID_ANY, label="INDIVIDUALS ASSOCIATED WITH THIS EVENT")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(IndividualToEvent).filter_by(event_id=info[1].id).all()
            for r in results:
                locId= session.query(IndividualToLocation).filter_by(individual_id=r.individual_id).one()
                location = session.query(Location).filter_by(id=locId.location_id).one()
                individual = session.query(Individual).filter_by(id=r.individual_id).one()
                image = session.query(ImageIndividual).filter_by(individual_id=individual.id).all()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display---------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + individual.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + individual.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + individual.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + individual.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + individual.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + individual.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fb = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: " + individual.facebookurl)
                fb.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fb,0,wx.ALL,10)
                link = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: " + individual.linkedinurl)
                link.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(link,0,wx.ALL,10)
                twit = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: " + individual.twitterurl)
                twit.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                add.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(add,0,wx.ALL,10)
                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                city.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(city,0,wx.ALL,10)
                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                state.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(state,0,wx.ALL,10)
                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                zip.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(zip,0,wx.ALL,10)
                card.Add(inforow4)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                #in = wx.StaticText(self, id=wx.ID_ANY, label="INCIDENTS: " + str(r.violentincidents))
                #inforow4.Add(in,0,wx.ALL,5)
                notes = wx.StaticText(self, id=wx.ID_ANY, label="NOTES: " + individual.notes)
                notes.SetForegroundColour(wx.Colour(255,255,255))
                inforow5.Add(notes,0,wx.ALL,10)
                card.Add(inforow5)

                inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow6.Add(unlink,0,wx.ALL,10)
                card.Add(inforow6)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if info[0] == "ShowEventVehicles":
            title = wx.StaticText(self, id=wx.ID_ANY, label="VEHICLES ASSOCIATED WITH THIS EVENT")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(VehicleToEvent).filter_by(event_id=info[1].id).all()
            for r in results:
                vehicle = session.query(Vehicle).filter_by(id=r.vehicle_id).one()
                image = session.query(ImageVehicle).filter_by(vehicle_id=vehicle.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)

                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + vehicle.plate)
                plate.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(plate,0,wx.ALL,10)
                color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + vehicle.color)
                color.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(color,0,wx.ALL,10)
                make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + vehicle.make_model)
                make_model.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(make_model,0,wx.ALL,10)
                card.Add(inforow1)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow5.Add(unlink,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if info[0] == "ShowIndividualVehicles":
            title = wx.StaticText(self, id=wx.ID_ANY, label="VEHICLES ASSOCIATED WITH THIS INDIVIDUAL")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(VehicleToIndividual).filter_by(individual_id=info[1].id).all()
            for r in results:
                vehicle = session.query(Vehicle).filter_by(id=r.vehicle_id).one()
                image = session.query(ImageVehicle).filter_by(vehicle_id=vehicle.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)

                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + vehicle.plate)
                plate.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(plate,0,wx.ALL,10)
                color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + vehicle.color)
                color.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(color,0,wx.ALL,10)
                make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + vehicle.make_model)
                make_model.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(make_model,0,wx.ALL,10)
                card.Add(inforow1)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow5.Add(unlink,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)
                self.SetSizer(col)

        if info[0] == "ShowIndividualAssociates":
            title = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN ASSOCIATES")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            results = session.query(IndividualToIndividual).filter_by(individual1_id=info[1].id).all()
            for r in results:
                ind = session.query(Individual).filter_by(id=r.individual2_id).one()
                id = session.query(IndividualToLocation).filter_by(individual_id=ind.id).one()
                location = session.query(Location).filter_by(id=id.location_id).one()
                image = session.query(ImageIndividual).filter_by(individual_id=ind.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + ind.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + ind.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + ind.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + ind.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + ind.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + ind.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if ind.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= ind.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if ind.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= ind.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if ind.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= ind.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                add.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(add,0,wx.ALL,10)
                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                city.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(city,0,wx.ALL,10)
                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                state.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(state,0,wx.ALL,10)
                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                zip.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(zip,0,wx.ALL,10)
                card.Add(inforow4)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                unlink = wx.Button(self, wx.ID_ANY, label="Unlink")
                unlink.info = [r]
                self.Bind(wx.EVT_BUTTON, self.deleteLink, unlink)
                inforow5.Add(unlink,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if info[0] == "ShowVehicleLocations":
            title = wx.StaticText(self, id=wx.ID_ANY, label="SIGHTINGS OF THIS VEHICLE")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)

            self.locations = []

            add = wx.Button(self, wx.ID_ANY, label="Map Locations")
            self.Bind(wx.EVT_BUTTON, self.Map, add)
            col.Add(add,0,wx.ALL,10)
            results = session.query(LocationToVehicle).filter_by(vehicle_id=info[1].id).all()
            for r in results:
                location = session.query(Location).filter_by(id=r.location_id).one()

                locationQuery = []

                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                if location.latitude != "" and location.longitude != "":
                    locationQuery.append("coordinate")
                    street = wx.StaticText(self, id=wx.ID_ANY, label= "LATITUDE: " + location.latitude)
                    street.SetForegroundColour(wx.Colour(255,255,255))
                    inforow1.Add(street,0,wx.ALL,10)
                    locationQuery.append(location.latitude + ", ")
                    street = wx.StaticText(self, id=wx.ID_ANY, label= "LONGITUDE: " + location.longitude)
                    street.SetForegroundColour(wx.Colour(255,255,255))
                    inforow1.Add(street,0,wx.ALL,10)
                    locationQuery.append(location.longitude)
                else:
                    locationQuery.append("address")
                    if location.streetaddress != "":
                        street = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                        street.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(street,0,wx.ALL,10)
                        locationQuery.append(" " + location.streetaddress)
                    if location.neighborhood != "":
                        neigh = wx.StaticText(self, id=wx.ID_ANY, label="NEIGHBORHOOD: " + location.neighborhood)
                        neigh.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(neigh,0,wx.ALL,10)
                        locationQuery.append(" " + location.neighborhood)
                    if location.city != "":
                        city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                        city.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(city,0,wx.ALL,10)
                        locationQuery.append(" " + location.city)
                    if location.state != "":
                        state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                        state.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(state,0,wx.ALL,10)
                        locationQuery.append(" " + location.state)
                    if location.zip != "":
                        zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                        zip.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(zip,0,wx.ALL,10)
                        locationQuery.append(" " + location.zip)

                    if locationQuery != []:
                        self.locations.append(locationQuery)
                        add = wx.Button(self, wx.ID_ANY, label="Remove Sighting")
                        add.info = [r]
                        self.Bind(wx.EVT_BUTTON, self.deleteLink, add)
                        col.Add(add,0,wx.ALL,10)

        if info[0] == "ShowIndividualLocations":
            title = wx.StaticText(self, id=wx.ID_ANY, label="SIGHTINGS OF THIS INDIVIDUAL")
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)

            self.locations = []

            add = wx.Button(self, wx.ID_ANY, label="Map Locations")
            self.Bind(wx.EVT_BUTTON, self.Map, add)
            col.Add(add,0,wx.ALL,10)
            results = session.query(IndividualToLocation).filter_by(individual_id=info[1].id).all()
            for r in results:
                location = session.query(Location).filter_by(id=r.location_id).one()

                locationQuery = []

                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                if location.latitude != "" and location.longitude != "":
                    locationQuery.append("coordinate")
                    street = wx.StaticText(self, id=wx.ID_ANY, label= "LATITUDE: " + location.latitude)
                    street.SetForegroundColour(wx.Colour(255,255,255))
                    inforow1.Add(street,0,wx.ALL,10)
                    locationQuery.append(location.latitude + ", ")
                    street = wx.StaticText(self, id=wx.ID_ANY, label= "LONGITUDE: " + location.longitude)
                    street.SetForegroundColour(wx.Colour(255,255,255))
                    inforow1.Add(street,0,wx.ALL,10)
                    locationQuery.append(location.longitude)
                else:
                    locationQuery.append("address")
                    if location.streetaddress != "":
                        street = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                        street.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(street,0,wx.ALL,10)
                        locationQuery.append(" " + location.streetaddress)
                    if location.neighborhood != "":
                        neigh = wx.StaticText(self, id=wx.ID_ANY, label="NEIGHBORHOOD: " + location.neighborhood)
                        neigh.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(neigh,0,wx.ALL,10)
                        locationQuery.append(" " + location.neighborhood)
                    if location.city != "":
                        city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                        city.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(city,0,wx.ALL,10)
                        locationQuery.append(" " + location.city)
                    if location.state != "":
                        state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                        state.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(state,0,wx.ALL,10)
                        locationQuery.append(" " + location.state)
                    if location.zip != "":
                        zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                        zip.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(zip,0,wx.ALL,10)
                        locationQuery.append(" " + location.zip)
                col.Add(inforow1)

                if locationQuery != []:
                    self.locations.append(locationQuery)
                    add = wx.Button(self, wx.ID_ANY, label="Remove Sighting")
                    add.info = [r]
                    self.Bind(wx.EVT_BUTTON, self.deleteLink, add)
                    col.Add(add,0,wx.ALL,10)

        if info[0] == "ShowVehicleImages":
            images = session.query(ImageVehicle).filter_by(vehicle_id=info[1].id).all()
            for i in images:
                de = decrypt(i.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                col.Add(image,0,wx.ALL,10)

        if info[0] == "ShowEventImages":
            images = session.query(ImageEvent).filter_by(event_id=info[1].id).all()
            for i in images:
                de = decrypt(i.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                col.Add(image,0,wx.ALL,10)

        if info[0] == "ShowIndividualImages":
            images = session.query(ImageIndividual).filter_by(individual_id=info[1].id).all()
            for i in images:
                de = decrypt(i.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                col.Add(image,0,wx.ALL,10)

        if info[0] == "ShowAnalyzedImage":
            image = info[1]
            width, height = image.size
            bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
            image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
            col.Add(image,0,wx.ALL,10)

        self.SetSizer(col)

    def Map(self,event):
        points = []
        coordinates = []
        try:
            for point in self.locations:
                if point[0] == "address":
                    point.remove("address")
                    search = ''.join(point)
                    #print(search)
                    g = geocoder.osm(search)
                    data = g.json
                    if data:
                        c = []
                        c.append(data["lat"])
                        c.append(data["lng"])
                        coordinates.append(c)
                if point[0] == "coordinate":
                    c = []
                    c.append(point[1])
                    c.append(point[2])
                    coordinates.append(c)
            markers = folium.FeatureGroup(name="Locations")

            for marker in coordinates:
                markers.add_child(folium.Marker(location=marker))

            map = folium.Map(location=coordinates[0], zoom_start=6, tiles='openstreetmap')
            map.add_child(markers)
            map.add_child(folium.LayerControl())
            map.save("Graphics/tempmap.html")
            browser = webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s")
            path =  os.path.abspath("Graphics/tempmap.html")
            browser.open_new(path)
            os.remove("Graphics/tempmap.html")
            frame = wx.GetTopLevelParent(self)
            frame.Destroy()
        except:
            dial = wx.MessageDialog(None, 'Unable To Connect To The Internet', 'Mapping Failed', wx.OK)
            dial.ShowModal()

    def deleteLink(self,event):
        widget = event.GetEventObject()
        info = widget.info
        confirm = wx.MessageDialog(None, "Are You Sure You Want To Unlink?")
        if confirm.ShowModal() == wx.ID_OK:
            session.delete(info[0])
            session.commit()
            frame = wx.GetTopLevelParent(self)
            frame.Destroy()

        elif confirm.ShowModal() == wx.ID_CANCEL:
            sys.exit()

    def refresh(self,event):
        new = additionalInfoWindow(self.info)
        pos = list(self.GetScreenPosition())
        new.MoveXY(pos[0]-15,pos[1]-33)
        frame = wx.GetTopLevelParent(self)
        frame.Destroy()

class linkingWindow(wx.Frame):
    def __init__(self,directions):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Link Results", size=(1000,500))
        self.panel = wx.ScrolledWindow(self)
        self.panel.SetScrollbars(1, 1, 1, 1)
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        self.directions = directions

        display = linkingPanel(self.panel,directions)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(display, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.close)
        self.Layout()
        self.Show()

    def close(self,e):
        self.Destroy()

class linkingPanel(wx.Panel):
    def __init__(self, parent, direction):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        col = wx.BoxSizer(wx.VERTICAL)

        if direction[0] == "VehicleToIndividual":
            id = session.query(VehicleToIndividual).filter_by(individual_id=direction[1].id).all()
            if id != []:
                for i in id:
                    vehicle = session.query(Vehicle).filter(Vehicle.id != i.vehicle_id).all()
                if vehicle == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                vehicle = session.query(Vehicle).all()
                if vehicle == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            for v in vehicle:
                image = session.query(ImageVehicle).filter_by(vehicle_id=v.id).all()
                de = decrypt(image[-1].image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)

                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + v.plate)
                plate.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(plate,0,wx.ALL,10)
                color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + v.color)
                color.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(color,0,wx.ALL,10)
                make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + v.make_model)
                make_model.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(make_model,0,wx.ALL,10)
                card.Add(inforow1)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add")
                add.info = ["VehicleToIndividual",v.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if direction[0] == "IndividualToVehicle":
            pdb.set_trace()
            id = session.query(VehicleToIndividual).filter_by(vehicle_id=direction[1].id).all()
            if id != []:
                for i in id:
                    individual = session.query(Individual).filter(Individual.id != i.individual_id).all()
                if individual == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                individual = session.query(Individual).all()
            for ind in individual:
                id = session.query(IndividualToLocation).filter_by(individual_id=ind.id).all()
                location = session.query(Location).filter_by(id=id[0].location_id).one()
                image = session.query(ImageIndividual).filter_by(individual_id=ind.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + ind.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + ind.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + ind.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + ind.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + ind.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + ind.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if ind.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= ind.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if ind.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= ind.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if ind.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= ind.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                add.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(add,0,wx.ALL,10)
                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                city.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(city,0,wx.ALL,10)
                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                state.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(state,0,wx.ALL,10)
                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                zip.SetForegroundColour(wx.Colour(255,255,255))
                inforow4.Add(zip,0,wx.ALL,10)
                card.Add(inforow4)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add")
                add.info = ["IndividualToVehicle",ind.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if direction[0] == "IndividualToEvent":
            id = session.query(IndividualToEvent).filter_by(event_id=direction[1].id).all()
            if id != []:
                for i in id:
                    individual = session.query(Individual).filter(Individual.id != i.individual_id).all()
                if individual == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                individual = session.query(Individual).all()
            for ind in individual:
                image = session.query(ImageIndividual).filter_by(individual_id=ind.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + ind.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + ind.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + ind.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + ind.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + ind.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + ind.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if ind.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= ind.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if ind.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= ind.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if ind.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= ind.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add")
                add.info = ["IndividualToEvent",ind.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if direction[0] == "EventToIndividual":
            #pdb.set_trace()
            id = session.query(IndividualToEvent).filter_by(individual_id=direction[1].id).all()
            if id != []:
                for i in id:
                    event = session.query(Event).filter(Event.id != i.event_id).all()
                if event == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                event= session.query(Event).all()
                if event == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            for e in event:
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="DATE: " + e.date)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="TITLE: " + e.title)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="DESCRIPTION: " + e.description)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                card.Add(inforow2)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add")
                add.info = ["EventToIndividual",e.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                col.Add(card)

        if direction[0] == "VehicleToEvent":
            id = session.query(VehicleToEvent).filter_by(event_id=direction[1].id).all()
            if id != []:
                for i in id:
                    vehicle = session.query(Vehicle).filter(Vehicle.id != i.vehicle_id).all()
                if vehicle == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                vehicle = session.query(Vehicle).all()
                if vehicle == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            for v in vehicle:
                image = session.query(ImageVehicle).filter_by(vehicle_id=v.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)

                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + v.plate)
                plate.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(plate,0,wx.ALL,10)
                color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + v.color)
                color.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(color,0,wx.ALL,10)
                make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + v.make_model)
                make_model.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(make_model,0,wx.ALL,10)
                card.Add(inforow1)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add")
                add.info = ["VehicleToEvent",v.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if direction[0] == "VehicleToLocation":
            id = session.query(LocationToVehicle).filter_by(location_id=direction[1].id).all()
            if id != []:
                for i in id:
                    vehicle = session.query(Vehicle).filter(Vehicle.id != i.vehicle_id).all()
                if vehicle == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                vehicle = session.query(Vehicle).all()
                if vehicle == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            for v in vehicle:
                image = session.query(ImageVehicle).filter_by(vehicle_id=v.id).all()
                de = decrypt(image[-1].image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)

                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + v.plate)
                plate.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(plate,0,wx.ALL,10)
                color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + v.color)
                color.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(color,0,wx.ALL,10)
                make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + v.make_model)
                make_model.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(make_model,0,wx.ALL,10)
                card.Add(inforow1)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add")
                add.info = ["VehicleToLocation",v.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if direction[0] == "LocationToVehicle":

            lat=wx.StaticText(self, id=wx.ID_ANY, label="Latitude")
            lat.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLat = wx.TextCtrl(self, wx.ID_ANY, "")
            long=wx.StaticText(self, id=wx.ID_ANY, label="Longitude")
            long.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLong = wx.TextCtrl(self, wx.ID_ANY, "")
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Address")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Neighborhood")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="City")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFour=wx.StaticText(self, id=wx.ID_ANY, label="State")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFour = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Zip")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFive = wx.TextCtrl(self, wx.ID_ANY, "")

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(lat, 0, wx.ALL, 5)
            col.Add(self.inputLat, 0, wx.ALL, 5)
            col.Add(long, 0,wx.ALL, 5)
            col.Add(self.inputLong, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0,wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)
            col.Add(txtFour, 0,wx.ALL, 5)
            col.Add(self.inputFour, 0,wx.ALL, 5)
            col.Add(txtFive, 0,wx.ALL, 5)
            col.Add(self.inputFive, 0,wx.ALL, 5)

            inforow5 = wx.BoxSizer(wx.HORIZONTAL)
            add = wx.Button(self, wx.ID_ANY, label="Add")
            add.info = ["LocationToVehicle", direction[1].id]
            self.Bind(wx.EVT_BUTTON, self.add, add)
            inforow5.Add(add,0,wx.ALL,10)
            col.Add(inforow5)

        if direction[0] == "IndividualToIndividual":
            #pdb.set_trace()
            id = session.query(IndividualToIndividual).filter_by(individual1_id=direction[1].id).all()
            if id != []:
                for i in id:
                    individual = session.query(Individual).filter(and_(Individual.id != i.individual2_id,Individual.id != direction[1].id)).all()
                if individual == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                individual = session.query(Individual).filter(Individual.id != direction[1].id).all()
                if individual == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            for ind in individual:
                locid = session.query(IndividualToLocation).filter_by(individual_id=ind.id).all()
                if locid != []:
                    location = session.query(Location).filter_by(id=locid[0].location_id).one()
                image = session.query(ImageIndividual).filter_by(individual_id=ind.id).all()
                de = decrypt(image[-1].image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + ind.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + ind.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + ind.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + ind.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + ind.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + ind.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if ind.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= ind.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if ind.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= ind.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if ind.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= ind.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                if locid != []:
                    inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                    add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                    add.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(add,0,wx.ALL,10)
                    city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                    city.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(city,0,wx.ALL,10)
                    state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                    state.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(state,0,wx.ALL,10)
                    zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                    zip.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(zip,0,wx.ALL,10)
                    card.Add(inforow4)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add Associate")
                add.info = ["IndividualToIndividual",ind.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(1000, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if direction[0] == "IndividualToLocation":
            id = session.query(IndividualToLocation).filter_by(location_id=direction[1].id).all()
            if id != []:
                for i in id:
                    individual = session.query(Individual).filter(Individual.id != i.individual_id).all()
                if individual == []:
                    notice = wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    notice.SetForegroundColour(wx.Colour(255,255,255))
                    col.Add(notice,0,wx.ALL,10)
            else:
                individual = session.query(Individual).all()
            for ind in individual:
                image = session.query(ImageIndividual).filter_by(individual_id=ind.id).one()
                de = decrypt(image.image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                display.Add(image,0,wx.ALL,10)
                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + ind.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + ind.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + ind.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + ind.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + ind.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + ind.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if ind.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= ind.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if ind.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= ind.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if ind.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= ind.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                add = wx.Button(self, wx.ID_ANY, label="Add")
                add.info = ["IndividualToLocation",ind.id, direction[1].id]
                self.Bind(wx.EVT_BUTTON, self.add, add)
                inforow5.Add(add,0,wx.ALL,10)
                card.Add(inforow5)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        if direction[0] == "LocationToIndividual":
            lat=wx.StaticText(self, id=wx.ID_ANY, label="Latitude")
            lat.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLat = wx.TextCtrl(self, wx.ID_ANY, "")
            long=wx.StaticText(self, id=wx.ID_ANY, label="Longitude")
            long.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLong = wx.TextCtrl(self, wx.ID_ANY, "")
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Address")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Neighborhood")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="City")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFour=wx.StaticText(self, id=wx.ID_ANY, label="State")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFour = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Zip")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFive = wx.TextCtrl(self, wx.ID_ANY, "")

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(lat, 0, wx.ALL, 5)
            col.Add(self.inputLat, 0, wx.ALL, 5)
            col.Add(long, 0,wx.ALL, 5)
            col.Add(self.inputLong, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0,wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)
            col.Add(txtFour, 0,wx.ALL, 5)
            col.Add(self.inputFour, 0,wx.ALL, 5)
            col.Add(txtFive, 0,wx.ALL, 5)
            col.Add(self.inputFive, 0,wx.ALL, 5)

            inforow5 = wx.BoxSizer(wx.HORIZONTAL)
            add = wx.Button(self, wx.ID_ANY, label="Add")
            add.info = ["LocationToIndividual", direction[1].id]
            self.Bind(wx.EVT_BUTTON, self.add, add)
            inforow5.Add(add,0,wx.ALL,10)
            col.Add(inforow5)

        self.SetSizer(col)

    def add(self, event):
        widget = event.GetEventObject()
        info = widget.info

        if info[0] == "IndividualToVehicle":
            association =  VehicleToIndividual(individual_id = info[1], vehicle_id = info[2])
            session.add(association)
            session.commit()

        if info[0] == "VehicleToIndividual":
            association =  VehicleToIndividual(individual_id = info[2], vehicle_id = info[1])
            session.add(association)
            session.commit()

        if info[0] == "IndividualToEvent":
            sightingloc =  session.query(LocationToEvent).filter_by(event_id = info[1]).all()
            if sightingloc != []:
                sighting = IndividualToLocation(individual_id = info[1],location_id=sightingloc[0].id)
                session.add(sighting)
                session.commit()
            association =  IndividualToEvent(individual_id = info[2], event_id = info[1])
            session.add(association)
            session.commit()

        if info[0] == "EventToIndividual":
            #pdb.set_trace()
            sightingloc =  session.query(LocationToEvent).filter_by(event_id = info[1]).all()
            if sightingloc != []:
                sighting = IndividualToLocation(individual_id = info[2],location_id=sightingloc[0].id)
                session.add(sighting)
                session.commit()
            association =  IndividualToEvent(individual_id = info[2], event_id = info[1])
            session.add(association)
            session.commit()

        if info[0] == "VehicleToEvent":
            sightingloc =  session.query(LocationToEvent).filter_by(event_id = info[2]).all()
            if sightingloc != []:
                sighting = LocationToVehicle(vehicle_id = info[1],location_id=sightingloc[0].id)
                session.add(sighting)
                session.commit()
            association =  VehicleToEvent(vehicle_id = info[1], event_id = info[2])
            session.add(association)
            session.commit()

        if info[0] == "LocationToVehicle":
            location = session.query(Location).filter_by(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
            city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue()).all()
            if location == []:
                location = Location(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
                city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(), latitude = self.inputLat.GetValue(), longitude = self.inputLong.GetValue())
                session.add(location)
                session.commit()
            else:
                location = location[0]
            association = LocationToVehicle(vehicle_id = info[1],location_id=location.id)
            session.add(association)
            session.commit()

        if info[0] == "VehicleToLocation":
            association =  LocationToVehicle(vehicle_id = info[1], location_id = info[2])
            session.add(association)
            session.commit()

        if info[0] == "IndividualToIndividual":
            association =  IndividualToIndividual(individual2_id = info[1], individual1_id = info[2])
            session.add(association)
            session.commit()

        if info[0] == "IndividualToLocation":
            association =  IndividualToLocation(individual_id = info[1], location_id = info[2])
            session.add(association)
            session.commit()

        if info[0] == "LocationToIndividual":
            location = session.query(Location).filter_by(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
            city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue()).all()
            if location == []:
                location = Location(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
                city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(), latitude = self.inputLat.GetValue(), longitude = self.inputLong.GetValue())
                session.add(location)
                session.commit()
            else:
                location = location[0]
            association = IndividualToLocation(individual_id = info[1],location_id=location.id)
            session.add(association)
            session.commit()

        frame = wx.GetTopLevelParent(self)
        frame.Destroy()

class enterWindow(wx.Frame):
    def __init__(self,type):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Search Results", size=(500,500))
        self.panel = wx.ScrolledWindow(self)
        self.panel.SetScrollbars(1, 1, 1, 1)
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        if type=="individualNew":
            self.SetTitle('New Individual')
        elif type=="vehicleNew":
            self.SetTitle('New Vehicle')
        elif type=="eventNew":
            self.SetTitle('New Event')

        input = inputPanel(self.panel,type)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(input, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.close)
        self.Layout()
        self.Show()

    def close(self,e):
        self.Destroy()

class inputPanel(wx.Panel):
    def __init__(self, parent,type):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.currentDirectory = os.getcwd()

        self.type=type
        self.paths=[]

        if self.type == "individualNew":
            lat=wx.StaticText(self, id=wx.ID_ANY, label="Latitude")
            lat.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLat = wx.TextCtrl(self, wx.ID_ANY, "")
            long=wx.StaticText(self, id=wx.ID_ANY, label="Longitude")
            long.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLong = wx.TextCtrl(self, wx.ID_ANY, "")
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="First Name")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Last Name")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="Workplace")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFour=wx.StaticText(self, id=wx.ID_ANY, label="Email")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFour = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Phone")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFive = wx.TextCtrl(self, wx.ID_ANY, "")
            txtSix=wx.StaticText(self, id=wx.ID_ANY, label="Facebook")
            txtSix.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSix = wx.TextCtrl(self, wx.ID_ANY, "")
            txtSeven=wx.StaticText(self, id=wx.ID_ANY, label="Twitter")
            txtSeven.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSeven = wx.TextCtrl(self, wx.ID_ANY, "")
            txtEight=wx.StaticText(self, id=wx.ID_ANY, label="Linkedin")
            txtEight.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEight = wx.TextCtrl(self, wx.ID_ANY, "")
            txtNine=wx.StaticText(self, id=wx.ID_ANY, label="Primary Affiliation")
            txtNine.SetForegroundColour(wx.Colour(255,255,255))
            self.inputNine = wx.TextCtrl(self, wx.ID_ANY, "")
            txtTen=wx.StaticText(self, id=wx.ID_ANY, label="Notes")
            txtTen.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTen =wx.TextCtrl(self,id=wx.ID_ANY,size=(200, 100), style=wx.TE_MULTILINE)
            txtEleven=wx.StaticText(self, id=wx.ID_ANY, label="Known Violent Incidents (Int)")
            txtEleven.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEleven = wx.TextCtrl(self, wx.ID_ANY, "0")
            txtTwelve = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
            txtTwelve.SetForegroundColour(wx.Colour(255,255,255))
            txtThirteen = wx.StaticText(self, id=wx.ID_ANY, label="Upload Images")
            txtThirteen.SetForegroundColour(wx.Colour(255,255,255))
            txtFourteen=wx.StaticText(self, id=wx.ID_ANY, label="Street Address")
            txtFourteen.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFourteen = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFifteen=wx.StaticText(self, id=wx.ID_ANY, label="Neighborhood")
            txtFifteen.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFifteen = wx.TextCtrl(self, wx.ID_ANY, "")
            txtSixteen=wx.StaticText(self, id=wx.ID_ANY, label="City")
            txtSixteen.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSixteen = wx.TextCtrl(self, wx.ID_ANY, "")
            txtSeventeen=wx.StaticText(self, id=wx.ID_ANY, label="State")
            txtSeventeen.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSeventeen = wx.TextCtrl(self, wx.ID_ANY, "")
            txtEighteen=wx.StaticText(self, id=wx.ID_ANY, label="Zip")
            txtEighteen.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEighteen = wx.TextCtrl(self, wx.ID_ANY, "")
            addButton = wx.Button(self, wx.ID_ANY, label="Add")
            addImage = wx.Button(self, wx.ID_ANY, label="Pictures")
            self.Bind(wx.EVT_BUTTON, self.onOpenFile, addImage)
            self.Bind(wx.EVT_BUTTON, self.addNew, addButton)

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(txtThirteen, 0,wx.ALL, 5)
            col.Add(addImage, 0,wx.ALL, 5)
            col.Add(txtTwelve, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0, wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)
            col.Add(txtFour, 0, wx.ALL, 5)
            col.Add(self.inputFour, 0,wx.ALL, 5)
            col.Add(txtFive, 0, wx.ALL, 5)
            col.Add(self.inputFive, 0,wx.ALL, 5)
            col.Add(txtSix, 0,wx.ALL, 5)
            col.Add(self.inputSix, 0,wx.ALL, 5)
            col.Add(txtSeven, 0,wx.ALL, 5)
            col.Add(self.inputSeven, 0,wx.ALL, 5)
            col.Add(txtEight, 0,wx.ALL, 5)
            col.Add(self.inputEight, 0,wx.ALL, 5)
            col.Add(txtNine, 0, wx.ALL, 5)
            col.Add(self.inputNine, 0,wx.ALL, 5)
            col.Add(txtEleven, 0, wx.ALL, 5)
            col.Add(self.inputEleven, 0,wx.ALL, 5)
            col.Add(lat, 0,wx.ALL, 5)
            col.Add(self.inputLat, 0,wx.ALL, 5)
            col.Add(long, 0, wx.ALL, 5)
            col.Add(self.inputLong, 0,wx.ALL, 5)
            col.Add(txtFourteen, 0,wx.ALL, 5)
            col.Add(self.inputFourteen, 0,wx.ALL, 5)
            col.Add(txtFifteen, 0, wx.ALL, 5)
            col.Add(self.inputFifteen, 0,wx.ALL, 5)
            col.Add(txtSixteen, 0, wx.ALL, 5)
            col.Add(self.inputSixteen, 0,wx.ALL, 5)
            col.Add(txtSeventeen, 0, wx.ALL, 5)
            col.Add(self.inputSeventeen, 0,wx.ALL, 5)
            col.Add(txtEighteen, 0, wx.ALL, 5)
            col.Add(self.inputEighteen, 0,wx.ALL, 5)
            col.Add(txtTen, 0, wx.ALL, 5)
            col.Add(self.inputTen, 0,wx.ALL, 5)

            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

            self.SetSizer(col)

        if self.type == "vehicleNew":
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Plate")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Color")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="Make And Model")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFour = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            txtFive = wx.StaticText(self, id=wx.ID_ANY, label="Upload Images")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            addButton = wx.Button(self, wx.ID_ANY, label="Add")
            addImage = wx.Button(self, wx.ID_ANY, label="Pictures")
            self.Bind(wx.EVT_BUTTON, self.onOpenFile, addImage)
            self.Bind(wx.EVT_BUTTON, self.addNew, addButton)

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(txtFive, 0,wx.ALL, 5)
            col.Add(addImage, 0,wx.ALL, 5)
            col.Add(txtFour, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0, wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)

            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

        if self.type == "eventNew":
            lat=wx.StaticText(self, id=wx.ID_ANY, label="Latitude")
            lat.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLat = wx.TextCtrl(self, wx.ID_ANY, "")
            long=wx.StaticText(self, id=wx.ID_ANY, label="Longitude")
            long.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLong = wx.TextCtrl(self, wx.ID_ANY, "")
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Address")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Neighborhood")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="City")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFour=wx.StaticText(self, id=wx.ID_ANY, label="State")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFour = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Zip")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFive = wx.TextCtrl(self, wx.ID_ANY, "")
            txtSix=wx.StaticText(self, id=wx.ID_ANY, label="Event Date")
            txtSix.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSix = wx.TextCtrl(self, wx.ID_ANY, "")
            txtSeven=wx.StaticText(self, id=wx.ID_ANY, label="Event Title")
            txtSeven.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSeven = wx.TextCtrl(self, wx.ID_ANY, "")
            txtEight=wx.StaticText(self, id=wx.ID_ANY, label="Description")
            txtEight.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEight = wx.TextCtrl(self, wx.ID_ANY,size=(200, 100), style=wx.TE_MULTILINE)
            txtNine = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
            txtNine.SetForegroundColour(wx.Colour(255,255,255))
            addButton = wx.Button(self, wx.ID_ANY, label="Add")
            self.Bind(wx.EVT_BUTTON, self.addNew, addButton)
            addImage = wx.Button(self, wx.ID_ANY, label="Add Images")
            self.Bind(wx.EVT_BUTTON, self.onOpenFile, addImage)

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(txtNine, 0,wx.ALL, 5)
            col.Add(lat, 0,wx.ALL, 5)
            col.Add(self.inputLat, 0,wx.ALL, 5)
            col.Add(long, 0, wx.ALL, 5)
            col.Add(self.inputLong, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0, wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)
            col.Add(txtFour, 0,wx.ALL, 5)
            col.Add(self.inputFour, 0,wx.ALL, 5)
            col.Add(txtFive, 0,wx.ALL, 5)
            col.Add(self.inputFive, 0,wx.ALL, 5)
            col.Add(txtSix, 0,wx.ALL, 5)
            col.Add(self.inputSix, 0,wx.ALL, 5)
            col.Add(txtSeven, 0,wx.ALL, 5)
            col.Add(self.inputSeven, 0,wx.ALL, 5)
            col.Add(txtEight, 0,wx.ALL, 5)
            col.Add(self.inputEight, 0,wx.ALL, 5)
            col.Add(addImage, 0,wx.ALL, 5)

            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

        if self.type == "tipNew":
            col = wx.BoxSizer(wx.VERTICAL)
            title=wx.StaticText(self, id=wx.ID_ANY, label="NEW TIP")
            col.Add(title, 0,wx.ALL, 5)
            title.SetForegroundColour(wx.Colour(255,255,255))
            txtSeven=wx.StaticText(self, id=wx.ID_ANY, label="Title")
            col.Add(txtSeven, 0,wx.ALL, 5)
            txtSeven.SetForegroundColour(wx.Colour(255,255,255))
            self.inputSeven = wx.TextCtrl(self, wx.ID_ANY, "")
            col.Add(self.inputSeven, 0,wx.ALL, 5)
            txtEight=wx.StaticText(self, id=wx.ID_ANY, label="Description")
            col.Add(txtEight, 0,wx.ALL, 5)
            txtEight.SetForegroundColour(wx.Colour(255,255,255))
            self.inputEight = wx.TextCtrl(self, wx.ID_ANY,size=(300, 400), style=wx.TE_MULTILINE)
            col.Add(self.inputEight, 0,wx.ALL, 5)
            addButton = wx.Button(self, wx.ID_ANY, label="Add")
            self.Bind(wx.EVT_BUTTON, self.addNew, addButton)





            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

        if self.type == "locationNew":
            lat=wx.StaticText(self, id=wx.ID_ANY, label="Latitude")
            lat.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLat = wx.TextCtrl(self, wx.ID_ANY, "")
            long=wx.StaticText(self, id=wx.ID_ANY, label="Longitude")
            long.SetForegroundColour(wx.Colour(255,255,255))
            self.inputLong = wx.TextCtrl(self, wx.ID_ANY, "")
            txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Address")
            txtOne.SetForegroundColour(wx.Colour(255,255,255))
            self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
            txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Neighborhood")
            txtTwo.SetForegroundColour(wx.Colour(255,255,255))
            self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
            txtThree=wx.StaticText(self, id=wx.ID_ANY, label="City")
            txtThree.SetForegroundColour(wx.Colour(255,255,255))
            self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFour=wx.StaticText(self, id=wx.ID_ANY, label="State")
            txtFour.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFour = wx.TextCtrl(self, wx.ID_ANY, "")
            txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Zip")
            txtFive.SetForegroundColour(wx.Colour(255,255,255))
            self.inputFive = wx.TextCtrl(self, wx.ID_ANY, "")
            txtNine = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
            txtNine.SetForegroundColour(wx.Colour(255,255,255))
            addButton = wx.Button(self, wx.ID_ANY, label="Add")
            self.Bind(wx.EVT_BUTTON, self.addNew, addButton)

            col = wx.BoxSizer(wx.VERTICAL)
            col.Add(txtNine, 0,wx.ALL, 5)
            col.Add(lat, 0,wx.ALL, 5)
            col.Add(self.inputLat, 0,wx.ALL, 5)
            col.Add(long, 0, wx.ALL, 5)
            col.Add(self.inputLong, 0,wx.ALL, 5)
            col.Add(txtOne, 0,wx.ALL, 5)
            col.Add(self.inputOne, 0,wx.ALL, 5)
            col.Add(txtTwo, 0, wx.ALL, 5)
            col.Add(self.inputTwo, 0,wx.ALL, 5)
            col.Add(txtThree, 0,wx.ALL, 5)
            col.Add(self.inputThree, 0,wx.ALL, 5)
            col.Add(txtFour, 0,wx.ALL, 5)
            col.Add(self.inputFour, 0,wx.ALL, 5)
            col.Add(txtFive, 0,wx.ALL, 5)
            col.Add(self.inputFive, 0,wx.ALL, 5)

            row1 = wx.BoxSizer(wx.HORIZONTAL)
            row1.Add(addButton, 0,wx.ALL, 5)
            col.Add(row1)

        self.SetSizer(col)

    def onOpenFile(self, event):
        wildcard = "JPEG (*.jpg)|*.jpg"
        dlg = wx.FileDialog(
            self, message="Choose Image To Upload",
            defaultDir=self.currentDirectory,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.paths = paths
        dlg.Destroy()

    def addNew(self, event):

        success = ""

        if self.type == "individualNew":
            try:
                newIndividual = Individual(firstname = self.inputOne.GetValue(),lastname = self.inputTwo.GetValue(), workplace = self.inputThree.GetValue(), email = self.inputFour.GetValue(),
                phone = self.inputFive.GetValue(), facebookurl=self.inputSix.GetValue(),twitterurl=self.inputSeven.GetValue(),linkedinurl=self.inputEight.GetValue(), organization=self.inputNine.GetValue(),
                notes=self.inputTen.GetValue(),violentincidents=int(self.inputEleven.GetValue()))
                session.add(newIndividual)
                session.commit()
                newLocation = session.query(Location).filter_by(streetaddress= self.inputFourteen.GetValue(), neighborhood= self.inputFifteen.GetValue(),
                city= self.inputSixteen.GetValue(), state= self.inputSeventeen.GetValue(),  zip= self.inputEighteen.GetValue(), latitude= self.inputLat.GetValue(), longitude= self.inputLong.GetValue()).all()
                if newLocation == []:
                    newLocation = Location(streetaddress = self.inputFourteen.GetValue(), neighborhood = self.inputFifteen.GetValue(),
                    city = self.inputSixteen.GetValue(), state = self.inputSeventeen.GetValue(),  zip = self.inputEighteen.GetValue(),latitude=self.inputLat.GetValue(), longitude = self.inputLong.GetValue())
                    session.add(newLocation)
                    session.commit()
                else:
                    newLocation = newLocation[0]
                association = IndividualToLocation(individual_id = newIndividual.id,location_id=newLocation.id)
                session.add(association)
                session.commit()
                if self.paths != []:
                    for path in self.paths:
                        with open(path, "rb") as imageFile:
                            byte = imageFile.read()
                            enc = encrypt(byte, encryptionKey)
                            newImage = ImageIndividual(image=enc, individual_id=newIndividual.id)
                            session.add(newImage)
                            session.commit()
                else:
                        image = session.query(DefaultImages).filter_by(id=1).one()
                        print(image.image)
                        newImage = ImageIndividual(image=image.image, individual_id=newIndividual.id)
                        session.add(newImage)
                        session.commit()
                success = "new"
            except:
                success = "error"

        if self.type == "vehicleNew":
            try:
                newVehicle = Vehicle(plate = self.inputOne.GetValue(), color = self.inputTwo.GetValue(),
                make_model = self.inputThree.GetValue())
                session.add(newVehicle)
                session.commit()
                if self.paths != []:
                    for path in self.paths:
                        with open(path, "rb") as imageFile:
                            byte = imageFile.read()
                            enc = encrypt(byte, encryptionKey)
                            newImage = ImageVehicle(image=enc, vehicle_id=newVehicle.id)
                            session.add(newImage)
                            session.commit()
                else:
                        image = session.query(DefaultImages).filter_by(id=2).one()
                        newImage = ImageVehicle(image=image.image, vehicle_id=newVehicle.id)
                        session.add(newImage)
                        session.commit()
                success = "new"
            except:
                success = "error"

        if self.type == "eventNew":
            try:
                newEvent = Event(date = self.inputSix.GetValue(),title = self.inputSeven.GetValue(), description = self.inputEight.GetValue())
                session.add(newEvent)
                session.commit()
                newLocation = session.query(Location).filter_by(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
                city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(), latitude=self.inputLat.GetValue(), longitude = self.inputLong.GetValue()).all()
                if newLocation == []:
                    newLocation = Location(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
                    city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(),latitude=self.inputLat.GetValue(), longitude = self.inputLong.GetValue())
                    session.add(newLocation)
                    session.commit()
                else:
                    newLocation = newLocation[0]
                association =  LocationToEvent(location_id = newLocation.id, event_id = newEvent.id)
                session.add(association)
                session.commit()
                if self.paths != []:
                    for path in self.paths:
                        with open(path, "rb") as imageFile:
                            byte = imageFile.read()
                            enc = encrypt(byte, encryptionKey)
                            newImage = ImageEvent(image=enc, event_id=newEvent.id)
                            session.add(newImage)
                            session.commit()
                success = "new"
            except:
                success = "error"

        if self.type == "tipNew":
            try:
                newtip = Note(title = self.inputSeven.GetValue(), description = self.inputEight.GetValue())
                session.add(newtip)
                session.commit()
                success = "new"
            except:
                success = "error"

        if self.type == "locationNew":
            try:
                newLocation = session.query(Location).filter_by(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(), latitude=self.inputLat.GetValue(), longitude = self.inputLong.GetValue()).all()
                if newLocation == []:
                    newLocation = Location(streetaddress = self.inputOne.GetValue(), neighborhood = self.inputTwo.GetValue(),
                    city = self.inputThree.GetValue(), state = self.inputFour.GetValue(),  zip = self.inputFive.GetValue(), latitude=self.inputLat.GetValue(), longitude = self.inputLong.GetValue())
                    session.add(newLocation)
                    session.commit()
                else:
                    success = "existing"
                success = "new"
            except:
                success = "error"

        if success == "new":
            wx.MessageBox('Entry Added')
        if success == "error":
            wx.MessageBox("Error")
        if success == "existing":
            wx.MessageBox("Entry Already Exists")
        frame = wx.GetTopLevelParent(self)
        frame.Destroy()

class resultsWindow(wx.Frame):
    def __init__(self,search):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Search Results", size=(1000,500))
        self.panel = wx.ScrolledWindow(self)
        self.panel.SetScrollbars(1, 1, 1, 1)
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        resultsDisplay = resultsPanel(self.panel,search)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(resultsDisplay, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.close)
        self.Layout()
        self.Show()

    def close(self,e):
        self.Destroy()

class resultsPanel(wx.Panel):
    def __init__(self, parent, search):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        col = wx.BoxSizer(wx.VERTICAL)
        self.SetBackgroundColour((0,0,0))

        self.search = search

        self.linkTerm = []

        if search[0] == "Name":
                if search[1] == "" and search[2]=="" and search[3]=="" and search[4]=="" and search[5]=="":
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    if search[4] != "":
                        results = session.query(Individual).filter_by(phone=search[4]).all()
                    if search[5] != "":
                        results = session.query(Individual).filter_by(email=search[5]).all()
                    if search[1] != "":
                        results = session.query(Individual).filter_by(firstname=search[1]).all()
                    if search[2] != "":
                        results = session.query(Individual).filter_by(lastname=search[2]).all()
                    if search[3] != "":
                        results = session.query(Individual).filter_by(organization=search[3]).all()
                    if results == []:
                        t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                        t.SetForegroundColour(wx.Colour(255,255,255))
                    else:
                        refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                        self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                        col.Add(refresh,0,wx.ALL,10)
                        pdb.set_trace()
                        for r in results:
                            #--------Get Primary Image--------
                            locid = session.query(IndividualToLocation).filter_by(individual_id=r.id).all()
                            if locid != []:
                                location = session.query(Location).filter_by(id=locid[0].location_id).one()
                            image = session.query(ImageIndividual).filter_by(individual_id=r.id).all()
                            print(image)
                            de = decrypt(image[-1].image, encryptionKey)
                            image_data = de
                            image = Image.open(io.BytesIO(image_data))
                            width, height = image.size
                            if height > width:
                                new_height = 250
                                new_width  = new_height * width / height
                            else:
                                new_width  = 250
                                new_height = new_width * height / width
                            image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                            width, height = image.size
                            bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                            #--------Set Up Display----------
                            display = wx.BoxSizer(wx.HORIZONTAL)
                            img = wx.BoxSizer(wx.VERTICAL)
                            image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                            img.Add(image,0,wx.ALL,10)
                            images = session.query(ImageIndividual).filter_by(individual_id=r.id).count()
                            if images > 1:
                                moreImg = wx.Button(self, wx.ID_ANY, label="See " + str(images) + " Images")
                                moreImg.info = ["ShowIndividualImages", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, moreImg)
                                img.Add(moreImg,0,wx.ALL,10)
                            display.Add(img,0,wx.ALL,10)


                            card = wx.BoxSizer(wx.VERTICAL)
                            inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                            firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + r.firstname)
                            firstname.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(firstname,0,wx.ALL,10)
                            lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + r.lastname)
                            lastname.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(lastname,0,wx.ALL,10)
                            affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + r.organization)
                            affiliation.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(affiliation,0,wx.ALL,10)
                            card.Add(inforow1)

                            inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                            workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + r.workplace)
                            workplace.SetForegroundColour(wx.Colour(255,255,255))
                            inforow2.Add(workplace,0,wx.ALL,10)
                            email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " +  r.email)
                            email.SetForegroundColour(wx.Colour(255,255,255))
                            inforow2.Add(email,0,wx.ALL,10)
                            phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + r.phone)
                            phone.SetForegroundColour(wx.Colour(255,255,255))
                            inforow2.Add(phone,0,wx.ALL,10)
                            card.Add(inforow2)

                            inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                            fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                            fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                            inforow3.Add(fbtitle,0,wx.ALL,10)
                            if r.facebookurl != "":
                                fb = wx.adv.HyperlinkCtrl(self, url= r.facebookurl)
                                fb.SetNormalColour(wx.Colour(255,255,255))
                                inforow3.Add(fb,0,wx.ALL,10)
                            linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                            linktitle.SetForegroundColour(wx.Colour(255,255,255))
                            inforow3.Add(linktitle,0,wx.ALL,10)
                            if r.linkedinurl != "":
                                link = wx.adv.HyperlinkCtrl(self, url= r.linkedinurl)
                                link.SetNormalColour(wx.Colour(255,255,255))
                                inforow3.Add(link,0,wx.ALL,10)
                            twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                            twittitle.SetForegroundColour(wx.Colour(255,255,255))
                            inforow3.Add(twittitle,0,wx.ALL,10)
                            if r.twitterurl != "":
                                twit = wx.adv.HyperlinkCtrl(self, url= r.twitterurl)
                                twit.SetNormalColour(wx.Colour(255,255,255))
                                inforow3.Add(twit,0,wx.ALL,10)
                            card.Add(inforow3)

                            if locid != []:
                                inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                                add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                                add.SetForegroundColour(wx.Colour(255,255,255))
                                inforow4.Add(add,0,wx.ALL,10)
                                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                                city.SetForegroundColour(wx.Colour(255,255,255))
                                inforow4.Add(city,0,wx.ALL,10)
                                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                                state.SetForegroundColour(wx.Colour(255,255,255))
                                inforow4.Add(state,0,wx.ALL,10)
                                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                                zip.SetForegroundColour(wx.Colour(255,255,255))
                                inforow4.Add(zip,0,wx.ALL,10)
                                card.Add(inforow4)

                            inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                            #in = wx.StaticText(self, id=wx.ID_ANY, label="INCIDENTS: " + str(r.violentincidents))
                            #inforow4.Add(in,0,wx.ALL,5)
                            notes = wx.StaticText(self, id=wx.ID_ANY, label="NOTES: " + r.notes)
                            notes.SetForegroundColour(wx.Colour(255,255,255))
                            inforow5.Add(notes,0,wx.ALL,10)
                            card.Add(inforow5)

                            inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                            asscvehicles = session.query(VehicleToIndividual).filter_by(individual_id=r.id).count()
                            if asscvehicles > 0:
                                showVehicles = wx.Button(self, wx.ID_ANY, label=str(asscvehicles) + " Vehicles(s) Found")
                                showVehicles.info = ["ShowIndividualVehicles", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showVehicles)
                                inforow6.Add(showVehicles,0,wx.ALL,10)

                            asscloc = session.query(IndividualToLocation).filter_by(individual_id=r.id).count()
                            if asscloc > 0:
                                showLocations = wx.Button(self, wx.ID_ANY, label=str(asscloc) + " Location(s) Found")
                                showLocations.info = ["ShowIndividualLocations", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showLocations)
                                inforow6.Add(showLocations,0,wx.ALL,10)

                            asscevent = session.query(IndividualToEvent).filter_by(individual_id=r.id).count()
                            if asscevent > 0:
                                showEvents = wx.Button(self, wx.ID_ANY, label=str(asscevent) + " Event(s) Found")
                                showEvents.info = ["ShowIndividualEvents", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showEvents)
                                inforow6.Add(showEvents,0,wx.ALL,10)

                            asscevent = session.query(IndividualToIndividual).filter_by(individual1_id=r.id).count()
                            if asscevent > 0:
                                showEvents = wx.Button(self, wx.ID_ANY, label=str(asscevent) + " Associates(s) Found")
                                showEvents.info = ["ShowIndividualAssociates", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showEvents)
                                inforow6.Add(showEvents,0,wx.ALL,10)

                            card.Add(inforow6)

                            inforow7 = wx.BoxSizer(wx.HORIZONTAL)

                            add = wx.Button(self, wx.ID_ANY, label="Add Associate")
                            add.info = ["IndividualToIndividual", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow7.Add(add,0,wx.ALL,10)

                            add = wx.Button(self, wx.ID_ANY, label="Add Vehicle")
                            add.info = ["VehicleToIndividual", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow7.Add(add,0,wx.ALL,10)

                            add = wx.Button(self, wx.ID_ANY, label="Add Location")
                            add.info = ["LocationToIndividual", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow7.Add(add,0,wx.ALL,10)

                            add = wx.Button(self, wx.ID_ANY, label="Add Event")
                            add.info = ["EventToIndividual", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow7.Add(add,0,wx.ALL,10)

                            card.Add(inforow7)

                            inforow8 = wx.BoxSizer(wx.HORIZONTAL)
                            edit = wx.Button(self, wx.ID_ANY, label="Edit")
                            edit.info = ["Individual", r]
                            self.Bind(wx.EVT_BUTTON, self.editEntry, edit)
                            delete = wx.Button(self, wx.ID_ANY, label="Delete")
                            delete.info = ["Individual", r]
                            self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                            inforow8.Add(edit,0,wx.ALL,10)
                            inforow8.Add(delete,0,wx.ALL,10)
                            card.Add(inforow8)

                            sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                            sep.SetForegroundColour(wx.Colour(255,255,255))
                            col.Add(sep,0,wx.ALL,5)

                            display.Add(card)
                            col.Add(display)

        if search[0] == "Vehicle":
                if search[1] == "" and search[2]=="" and search[3]=="":
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    if search[1] != "":
                        results = session.query(Vehicle).filter_by(plate=search[1]).all()
                    if search[2] != "":
                        results = session.query(Vehicle).filter_by(color=search[2]).all()
                    if search[3] != "":
                        results = session.query(Vehicle).filter_by(make_model=search[3]).all()
                    if results == []:
                        t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                        t.SetForegroundColour(wx.Colour(255,255,255))
                    else:
                        refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                        self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                        col.Add(refresh,0,wx.ALL,10)
                        for index, r in enumerate(results):
                            #--------Get Primary Image--------
                            image = session.query(ImageVehicle).filter_by(vehicle_id=r.id).all()
                            de = decrypt(image[-1].image, encryptionKey)
                            image_data = de
                            image = Image.open(io.BytesIO(image_data))
                            width, height = image.size
                            if height > width:
                                new_height = 250
                                new_width  = new_height * width / height
                            else:
                                new_width  = 250
                                new_height = new_width * height / width
                            image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                            width, height = image.size
                            bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                            #--------Set Up Display----------
                            display = wx.BoxSizer(wx.HORIZONTAL)
                            img = wx.BoxSizer(wx.VERTICAL)
                            image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                            img.Add(image,0,wx.ALL,10)
                            images = session.query(ImageVehicle).filter_by(vehicle_id=r.id).count()
                            print(images)
                            if images > 1:
                                moreImg = wx.Button(self, wx.ID_ANY, label="See " + str(images) + " Images")
                                moreImg.info = ["ShowVehicleImages", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, moreImg)
                                img.Add(moreImg,0,wx.ALL,10)
                            display.Add(img,0,wx.ALL,10)

                            card = wx.BoxSizer(wx.VERTICAL)
                            inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                            plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + r.plate)
                            plate.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(plate,0,wx.ALL,10)
                            color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + r.color)
                            color.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(color,0,wx.ALL,10)
                            make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + r.make_model)
                            make_model.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(make_model,0,wx.ALL,10)
                            card.Add(inforow1)

                            inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                            asscind = session.query(VehicleToIndividual).filter_by(vehicle_id=r.id).count()
                            if asscind > 0:
                                showIndividuals = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Individual(s) Found")
                                showIndividuals.info = ["ShowVehicleIndividuals", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showIndividuals)
                                inforow2.Add(showIndividuals,0,wx.ALL,10)

                            asscloc = session.query(LocationToVehicle).filter_by(vehicle_id=r.id).count()
                            if asscloc > 0:
                                showSightings = wx.Button(self, wx.ID_ANY, label=str(asscloc) + " Sighting(s) Found")
                                showSightings.info = ["ShowVehicleLocations", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showSightings)
                                inforow2.Add(showSightings,0,wx.ALL,10)
                            card.Add(inforow2)

                            asscloc = session.query(VehicleToEvent).filter_by(vehicle_id=r.id).count()
                            if asscloc > 0:
                                showSightings = wx.Button(self, wx.ID_ANY, label=str(asscloc) + " Events(s) Found")
                                showSightings.info = ["ShowVehicleEvents", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showSightings)
                                inforow2.Add(showSightings,0,wx.ALL,10)
                            card.Add(inforow2)

                            inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                            add = wx.Button(self, wx.ID_ANY, label="Add Individual")
                            add.info = ["IndividualToVehicle", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow3.Add(add,0,wx.ALL,10)

                            add = wx.Button(self, wx.ID_ANY, label="Add Sighting")
                            add.info = ["LocationToVehicle", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow3.Add(add,0,wx.ALL,10)

                            add = wx.Button(self, wx.ID_ANY, label="Add Event")
                            add.info = ["EventToVehicle", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow3.Add(add,0,wx.ALL,10)
                            card.Add(inforow3)

                            inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                            edit = wx.Button(self, wx.ID_ANY, label="Edit")
                            edit.info = ["Vehicle", r]
                            self.Bind(wx.EVT_BUTTON, self.editEntry, edit)
                            delete = wx.Button(self, wx.ID_ANY, label="Delete")
                            delete.info = ["Vehicle", r]
                            self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                            inforow4.Add(edit,0,wx.ALL,10)
                            inforow4.Add(delete,0,wx.ALL,10)
                            card.Add(inforow4)

                            sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                            sep.SetForegroundColour(wx.Colour(255,255,255))
                            col.Add(sep,0,wx.ALL,5)

                            display.Add(card)
                            col.Add(display)

        if search[0] == "Location":
                #pdb.set_trace()
                if search[1] == "" and search[2]=="" and search[3]=="" and search[4]=="" and search[5]=="":
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    if search[1] != "":
                        results = session.query(Location).filter_by(streetaddress=search[1]).all()
                    if search[2] != "":
                        results = session.query(Location).filter_by(neighborhood=search[2]).all()
                    if search[3] != "":
                        results = session.query(Location).filter_by(city=search[3]).all()
                    if search[4] != "":
                        results = session.query(Location).filter_by(state=search[4]).all()
                    if search[5] != "":
                        results = session.query(Location).filter_by(zip=search[5]).all()

                    if results == []:
                        t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                        t.SetForegroundColour(wx.Colour(255,255,255))
                    else:
                        refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                        self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                        col.Add(refresh,0,wx.ALL,10)

                        self.locations = []

                        for r in results:

                            locationQuery = []

                            inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                            if r.latitude != "" and r.longitude != "":
                                locationQuery.append("coordinate")
                                street = wx.StaticText(self, id=wx.ID_ANY, label= "LATITUDE: " + r.latitude)
                                street.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(street,0,wx.ALL,10)
                                locationQuery.append(r.latitude + ", ")
                                street = wx.StaticText(self, id=wx.ID_ANY, label= "LONGITUDE: " + r.longitude)
                                street.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(street,0,wx.ALL,10)
                                locationQuery.append(r.longitude)
                            else:
                                locationQuery.append("address")
                                if r.streetaddress != "":
                                    street = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + r.streetaddress)
                                    street.SetForegroundColour(wx.Colour(255,255,255))
                                    inforow1.Add(street,0,wx.ALL,10)
                                    locationQuery.append(" " + r.streetaddress)
                                if r.neighborhood != "":
                                    neigh = wx.StaticText(self, id=wx.ID_ANY, label="NEIGHBORHOOD: " + r.neighborhood)
                                    neigh.SetForegroundColour(wx.Colour(255,255,255))
                                    inforow1.Add(neigh,0,wx.ALL,10)
                                    locationQuery.append(" " + r.neighborhood)
                                if r.city != "":
                                    city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + r.city)
                                    city.SetForegroundColour(wx.Colour(255,255,255))
                                    inforow1.Add(city,0,wx.ALL,10)
                                    locationQuery.append(" " + r.city)
                                if r.state != "":
                                    state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + r.state)
                                    state.SetForegroundColour(wx.Colour(255,255,255))
                                    inforow1.Add(state,0,wx.ALL,10)
                                    locationQuery.append(" " + r.state)
                                if r.zip != "":
                                    zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + r.zip)
                                    zip.SetForegroundColour(wx.Colour(255,255,255))
                                    inforow1.Add(zip,0,wx.ALL,10)
                                    locationQuery.append(" " + r.zip)

                                if locationQuery != []:
                                    self.locations.append(locationQuery)
                            col.Add(inforow1)

                            inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                            asscind = session.query(IndividualToLocation).filter_by(location_id=r.id).count()
                            if asscind > 0:
                                showIndividuals = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Individual(s) Found")
                                showIndividuals.info = ["ShowLocationIndividuals", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showIndividuals)
                                inforow2.Add(showIndividuals,0,wx.ALL,10)

                            asscevent = session.query(LocationToEvent).filter_by(location_id=r.id).count()
                            if asscevent > 0:
                                showEvents = wx.Button(self, wx.ID_ANY, label=str(asscevent) + " Event(s) Found")
                                showEvents.info = ["ShowLocationEvents", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showEvents)
                                inforow2.Add(showEvents,0,wx.ALL,10)

                            asscind = session.query(LocationToVehicle).filter_by(location_id=r.id).count()
                            if asscind > 0:
                                showVehicles = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Vehicle(s) Found")
                                showVehicles.info = ["ShowLocationVehicles", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showVehicles)
                                inforow2.Add(showVehicles,0,wx.ALL,10)

                            col.Add(inforow2)

                            inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                            map = wx.Button(self, wx.ID_ANY, label="Map")
                            map.query = locationQuery
                            self.Bind(wx.EVT_BUTTON, self.Map, map)
                            inforow3.Add(map,0,wx.ALL,10)
                            add = wx.Button(self, wx.ID_ANY, label="Add Vehicle")
                            add.info = ["VehicleToLocation", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow3.Add(add,0,wx.ALL,10)
                            add = wx.Button(self, wx.ID_ANY, label="Add Individual")
                            add.info = ["IndividualToLocation", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow3.Add(add,0,wx.ALL,10)
                            delete = wx.Button(self, wx.ID_ANY, label="Delete")
                            delete.info = ["Location", r]
                            self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                            inforow3.Add(delete,0,wx.ALL,10)
                            col.Add(inforow3)

                            sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                            sep.SetForegroundColour(wx.Colour(255,255,255))
                            col.Add(sep,0,wx.ALL,5)

        if search[0] == "Event":
                if search[1] == "" and search[2]=="":
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    if search[1] != "":
                        results = session.query(Event).filter_by(date=search[1]).all()
                    if search[2] != "":
                        results = session.query(Event).filter_by(title=search[2]).all()
                    if results == []:
                        t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                        t.SetForegroundColour(wx.Colour(255,255,255))
                    else:
                        refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                        self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                        col.Add(refresh,0,wx.ALL,10)
                        for r in results:
                            card = wx.BoxSizer(wx.VERTICAL)
                            locid = session.query(LocationToEvent).filter_by(event_id=r.id).all()

                            if locid != []:
                                location = session.query(Location).filter_by(id=locid[-1].location_id).all()

                                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                                add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                                add.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(add,0,wx.ALL,10)
                                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                                city.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(city,0,wx.ALL,10)
                                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                                state.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(state,0,wx.ALL,10)
                                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                                zip.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(zip,0,wx.ALL,10)
                                card.Add(inforow1)

                            inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                            date = wx.StaticText(self, id=wx.ID_ANY, label="DATE: " + r.date)
                            date.SetForegroundColour(wx.Colour(255,255,255))
                            inforow2.Add(date,0,wx.ALL,10)
                            title = wx.StaticText(self, id=wx.ID_ANY, label="TITLE: " + r.title)
                            title.SetForegroundColour(wx.Colour(255,255,255))
                            inforow2.Add(title,0,wx.ALL,10)
                            card.Add(inforow2)

                            inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                            desc = wx.StaticText(self, id=wx.ID_ANY, label="DESCRIPTION: " + r.description)
                            desc.SetForegroundColour(wx.Colour(255,255,255))
                            inforow3.Add(desc,0,wx.ALL,10)
                            card.Add(inforow3)

                            inforow4 = wx.BoxSizer(wx.HORIZONTAL)

                            asscind = session.query(ImageEvent).filter_by(event_id=r.id).count()
                            if asscind > 0:
                                showImages = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Image(s) Found")
                                showImages.info = ["ShowEventImages", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showImages)
                                inforow4.Add(showImages,0,wx.ALL,10)
                            card.Add(inforow4)

                            asscind = session.query(IndividualToEvent).filter_by(event_id=r.id).count()
                            if asscind > 0:
                                showIndividuals = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Individual(s) Found")
                                showIndividuals.info = ["ShowEventIndividuals", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showIndividuals)
                                inforow4.Add(showIndividuals,0,wx.ALL,10)

                            asscind = session.query(VehicleToEvent).filter_by(event_id=r.id).count()
                            if asscind > 0:
                                showVehicles = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Vehicles(s) Found")
                                showVehicles.info = ["ShowEventVehicles", r]
                                self.Bind(wx.EVT_BUTTON, self.additionalInfo, showVehicles)
                                inforow4.Add(showVehicles,0,wx.ALL,10)
                            card.Add(inforow4)

                            inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                            add = wx.Button(self, wx.ID_ANY, label="Add Individual")
                            add.info = ["IndividualToEvent", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow5.Add(add,0,wx.ALL,10)

                            add = wx.Button(self, wx.ID_ANY, label="Add Vehicle")
                            add.info = ["VehicleToEvent", r]
                            self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                            inforow5.Add(add,0,wx.ALL,10)
                            card.Add(inforow5)

                            inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                            edit = wx.Button(self, wx.ID_ANY, label="Edit")
                            edit.info = ["Event", r]
                            self.Bind(wx.EVT_BUTTON, self.editEntry, edit)
                            delete = wx.Button(self, wx.ID_ANY, label="Delete")
                            delete.info = ["Event", r]
                            self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                            inforow6.Add(edit,0,wx.ALL,10)
                            inforow6.Add(delete,0,wx.ALL,10)
                            card.Add(inforow6)

                            sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                            sep.SetForegroundColour(wx.Colour(255,255,255))
                            col.Add(sep,0,wx.ALL,5)
                            col.Add(card)

        if search[0] == "NameAll":
                results = session.query(Individual).all()
                if results == []:
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                    self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                    col.Add(refresh,0,wx.ALL,10)
                    for r in results:
                        locid = session.query(IndividualToLocation).filter_by(individual_id=r.id).all()
                        if locid != []:
                            location = session.query(Location).filter_by(id=locid[0].location_id).one()
                        image = session.query(ImageIndividual).filter_by(individual_id=r.id).all()
                        de = decrypt(image[-1].image, encryptionKey)
                        image_data = de
                        image = Image.open(io.BytesIO(image_data))
                        width, height = image.size
                        if height > width:
                            new_height = 250
                            new_width  = new_height * width / height
                        else:
                            new_width  = 250
                            new_height = new_width * height / width
                        image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                        width, height = image.size
                        bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                        #--------Set Up Display----------
                        display = wx.BoxSizer(wx.HORIZONTAL)
                        img = wx.BoxSizer(wx.VERTICAL)
                        image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                        img.Add(image,0,wx.ALL,10)
                        images = session.query(ImageIndividual).filter_by(individual_id=r.id).count()
                        if images > 1:
                            moreImg = wx.Button(self, wx.ID_ANY, label="See " + str(images) + " Images")
                            moreImg.info = ["ShowIndividualImages", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, moreImg)
                            img.Add(moreImg,0,wx.ALL,10)
                        display.Add(img,0,wx.ALL,10)

                        card = wx.BoxSizer(wx.VERTICAL)
                        inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                        firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + r.firstname)
                        firstname.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(firstname,0,wx.ALL,10)
                        lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + r.lastname)
                        lastname.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(lastname,0,wx.ALL,10)
                        affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + r.organization)
                        affiliation.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(affiliation,0,wx.ALL,10)
                        card.Add(inforow1)

                        inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                        workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + r.workplace)
                        workplace.SetForegroundColour(wx.Colour(255,255,255))
                        inforow2.Add(workplace,0,wx.ALL,10)
                        email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " + r.email)
                        email.SetForegroundColour(wx.Colour(255,255,255))
                        inforow2.Add(email,0,wx.ALL,10)
                        phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + r.phone)
                        phone.SetForegroundColour(wx.Colour(255,255,255))
                        inforow2.Add(phone,0,wx.ALL,10)
                        card.Add(inforow2)

                        inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                        fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                        fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                        inforow3.Add(fbtitle,0,wx.ALL,10)
                        if r.facebookurl != "":
                            fb = wx.adv.HyperlinkCtrl(self, url= r.facebookurl)
                            fb.SetNormalColour(wx.Colour(255,255,255))
                            inforow3.Add(fb,0,wx.ALL,10)
                        linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                        linktitle.SetForegroundColour(wx.Colour(255,255,255))
                        inforow3.Add(linktitle,0,wx.ALL,10)
                        if r.linkedinurl != "":
                            link = wx.adv.HyperlinkCtrl(self, url= r.linkedinurl)
                            link.SetNormalColour(wx.Colour(255,255,255))
                            inforow3.Add(link,0,wx.ALL,10)
                        twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                        twittitle.SetForegroundColour(wx.Colour(255,255,255))
                        inforow3.Add(twittitle,0,wx.ALL,10)
                        if r.twitterurl != "":
                            twit = wx.adv.HyperlinkCtrl(self, url= r.twitterurl)
                            twit.SetNormalColour(wx.Colour(255,255,255))
                            inforow3.Add(twit,0,wx.ALL,10)
                        card.Add(inforow3)

                        if locid != []:
                            inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                            add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                            add.SetForegroundColour(wx.Colour(255,255,255))
                            inforow4.Add(add,0,wx.ALL,10)
                            city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                            city.SetForegroundColour(wx.Colour(255,255,255))
                            inforow4.Add(city,0,wx.ALL,10)
                            state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                            state.SetForegroundColour(wx.Colour(255,255,255))
                            inforow4.Add(state,0,wx.ALL,10)
                            zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                            zip.SetForegroundColour(wx.Colour(255,255,255))
                            inforow4.Add(zip,0,wx.ALL,10)
                            card.Add(inforow4)

                        inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                        #in = wx.StaticText(self, id=wx.ID_ANY, label="INCIDENTS: " + str(r.violentincidents))
                        #inforow4.Add(in,0,wx.ALL,5)
                        notes = wx.StaticText(self, id=wx.ID_ANY, label="NOTES: " + r.notes)
                        notes.SetForegroundColour(wx.Colour(255,255,255))
                        inforow5.Add(notes,0,wx.ALL,10)
                        card.Add(inforow5)

                        inforow6= wx.BoxSizer(wx.HORIZONTAL)
                        asscvehicles = session.query(VehicleToIndividual).filter_by(individual_id=r.id).count()
                        if asscvehicles > 0:
                            showVehicles = wx.Button(self, wx.ID_ANY, label=str(asscvehicles) + " Vehicles(s) Found")
                            showVehicles.info = ["ShowIndividualVehicles", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showVehicles)
                            inforow6.Add(showVehicles,0,wx.ALL,10)
                            card.Add(inforow6)

                        asscloc = session.query(IndividualToLocation).filter_by(individual_id=r.id).count()
                        if asscloc > 0:
                            showLocations = wx.Button(self, wx.ID_ANY, label=str(asscloc) + " Location(s) Found")
                            showLocations.info = ["ShowIndividualLocations", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showLocations)
                            inforow6.Add(showLocations,0,wx.ALL,10)
                            card.Add(inforow6)

                        asscevent = session.query(IndividualToEvent).filter_by(event_id=r.id).count()
                        if asscevent > 0:
                            showEvents = wx.Button(self, wx.ID_ANY, label=str(asscevent) + " Event(s) Found")
                            showEvents.info = ["ShowIndividualEvents", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showEvents)
                            inforow6.Add(showEvents,0,wx.ALL,10)
                            card.Add(inforow6)

                        inforow7 = wx.BoxSizer(wx.HORIZONTAL)

                        add = wx.Button(self, wx.ID_ANY, label="Add Associate")
                        add.info = ["IndividualToIndividual", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow7.Add(add,0,wx.ALL,10)

                        add = wx.Button(self, wx.ID_ANY, label="Add Vehicle")
                        add.info = ["VehicleToIndividual", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow7.Add(add,0,wx.ALL,10)

                        add = wx.Button(self, wx.ID_ANY, label="Add Location")
                        add.info = ["LocationToIndividual", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow7.Add(add,0,wx.ALL,10)

                        add = wx.Button(self, wx.ID_ANY, label="Add Event")
                        add.info = ["EventToIndividual", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow7.Add(add,0,wx.ALL,10)

                        card.Add(inforow7)

                        inforow8 = wx.BoxSizer(wx.HORIZONTAL)
                        edit = wx.Button(self, wx.ID_ANY, label="Edit")
                        edit.info = ["Individual", r]
                        self.Bind(wx.EVT_BUTTON, self.editEntry, edit)
                        delete = wx.Button(self, wx.ID_ANY, label="Delete")
                        delete.info = ["Individual", r]
                        self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                        inforow8.Add(edit,0,wx.ALL,10)
                        inforow8.Add(delete,0,wx.ALL,10)
                        card.Add(inforow8)

                        sep = wx.StaticLine(self, id=wx.ID_ANY,size=(800, -1), style=wx.LI_HORIZONTAL)
                        sep.SetForegroundColour(wx.Colour(255,255,255))
                        col.Add(sep,0,wx.ALL,5)

                        display.Add(card)
                        col.Add(display)

        if search[0] == "VehicleAll":
                results = session.query(Vehicle).all()
                if results == []:
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                    self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                    col.Add(refresh,0,wx.ALL,10)
                    for index, r in enumerate(results):
                        #--------Get Primary Image--------
                        #pdb.set_trace()
                        image = session.query(ImageVehicle).filter_by(vehicle_id=r.id).all()
                        de = decrypt(image[-1].image, encryptionKey)
                        image_data = de
                        image = Image.open(io.BytesIO(image_data))
                        width, height = image.size
                        if height > width:
                            new_height = 250
                            new_width  = new_height * width / height
                        else:
                            new_width  = 250
                            new_height = new_width * height / width
                        image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                        width, height = image.size
                        bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                        #--------Set Up Display----------
                        display = wx.BoxSizer(wx.HORIZONTAL)
                        img = wx.BoxSizer(wx.VERTICAL)
                        image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                        img.Add(image,0,wx.ALL,10)
                        images = session.query(ImageVehicle).filter_by(vehicle_id=r.id).count()
                        if images > 1:
                            moreImg = wx.Button(self, wx.ID_ANY, label="See " + str(images) + " Images")
                            moreImg.info = ["ShowVehicleImages", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, moreImg)
                            img.Add(moreImg,0,wx.ALL,10)
                        display.Add(img,0,wx.ALL,10)

                        card = wx.BoxSizer(wx.VERTICAL)
                        inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                        plate = wx.StaticText(self, id=wx.ID_ANY, label="PLATE: " + r.plate)
                        plate.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(plate,0,wx.ALL,10)
                        color = wx.StaticText(self, id=wx.ID_ANY, label="COLOR: " + r.color)
                        color.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(color,0,wx.ALL,10)
                        make_model = wx.StaticText(self, id=wx.ID_ANY, label="MAKE_MODEL: " + r.make_model)
                        make_model.SetForegroundColour(wx.Colour(255,255,255))
                        inforow1.Add(make_model,0,wx.ALL,10)
                        card.Add(inforow1)

                        inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                        asscind = session.query(VehicleToIndividual).filter_by(vehicle_id=r.id).count()
                        if asscind > 0:
                            showIndividuals = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Individual(s) Found")
                            showIndividuals.info = ["ShowVehicleIndividuals", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showIndividuals)
                            inforow2.Add(showIndividuals,0,wx.ALL,10)

                        asscloc = session.query(LocationToVehicle).filter_by(vehicle_id=r.id).count()
                        if asscloc > 0:
                            showSightings = wx.Button(self, wx.ID_ANY, label=str(asscloc) + " Sighting(s) Found")
                            showSightings.info = ["ShowVehicleLocations", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showSightings)
                            inforow2.Add(showSightings,0,wx.ALL,10)

                        asscloc = session.query(VehicleToEvent).filter_by(vehicle_id=r.id).count()
                        if asscloc > 0:
                            showSightings = wx.Button(self, wx.ID_ANY, label=str(asscloc) + " Events(s) Found")
                            showSightings.info = ["ShowVehicleEvents", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showSightings)
                            inforow2.Add(showSightings,0,wx.ALL,10)

                        card.Add(inforow2)

                        inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                        add = wx.Button(self, wx.ID_ANY, label="Add Individual")
                        add.info = ["IndividualToVehicle", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow3.Add(add,0,wx.ALL,10)

                        add = wx.Button(self, wx.ID_ANY, label="Add Last Location")
                        add.info = ["LocationToVehicle", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow3.Add(add,0,wx.ALL,10)
                        card.Add(inforow3)

                        add = wx.Button(self, wx.ID_ANY, label="Add Event")
                        add.info = ["EventToVehicle", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow3.Add(add,0,wx.ALL,10)
                        card.Add(inforow3)

                        inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                        edit = wx.Button(self, wx.ID_ANY, label="Edit")
                        edit.info = ["Vehicle", r]
                        self.Bind(wx.EVT_BUTTON, self.editEntry, edit)
                        delete = wx.Button(self, wx.ID_ANY, label="Delete")
                        delete.info = ["Vehicle", r]
                        self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                        inforow4.Add(edit,0,wx.ALL,10)
                        inforow4.Add(delete,0,wx.ALL,10)
                        card.Add(inforow4)

                        sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                        col.Add(sep,0,wx.ALL,5)

                        display.Add(card)
                        col.Add(display)

        if search[0] == "LocationAll":
                results = session.query(Location).all()
                if results == []:
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                    self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                    col.Add(refresh,0,wx.ALL,10)

                    for r in results:

                        locationQuery = []

                        inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                        if r.latitude != "" and r.longitude != "":
                            locationQuery.append("coordinate")
                            street = wx.StaticText(self, id=wx.ID_ANY, label= "LATITUDE: " + r.latitude)
                            street.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(street,0,wx.ALL,10)
                            locationQuery.append(r.latitude + ", ")
                            street = wx.StaticText(self, id=wx.ID_ANY, label= "LONGITUDE: " + r.longitude)
                            street.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(street,0,wx.ALL,10)
                            locationQuery.append(r.longitude)
                        else:
                            locationQuery.append("address")
                            if r.streetaddress != "":
                                street = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + r.streetaddress)
                                street.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(street,0,wx.ALL,10)
                                locationQuery.append(" " + r.streetaddress)
                            if r.neighborhood != "":
                                neigh = wx.StaticText(self, id=wx.ID_ANY, label="NEIGHBORHOOD: " + r.neighborhood)
                                neigh.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(neigh,0,wx.ALL,10)
                                locationQuery.append(" " + r.neighborhood)
                            if r.city != "":
                                city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + r.city)
                                city.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(city,0,wx.ALL,10)
                                locationQuery.append(" " + r.city)
                            if r.state != "":
                                state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + r.state)
                                state.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(state,0,wx.ALL,10)
                                locationQuery.append(" " + r.state)
                            if r.zip != "":
                                zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + r.zip)
                                zip.SetForegroundColour(wx.Colour(255,255,255))
                                inforow1.Add(zip,0,wx.ALL,10)
                                locationQuery.append(" " + r.zip)

                        col.Add(inforow1)

                        inforow2 = wx.BoxSizer(wx.HORIZONTAL)

                        asscind = session.query(IndividualToLocation).filter_by(location_id=r.id).count()
                        if asscind > 0:
                            showIndividuals = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Individual(s) Found")
                            showIndividuals.info = ["ShowLocationIndividuals", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showIndividuals)
                            inforow2.Add(showIndividuals,0,wx.ALL,10)

                        asscevent = session.query(LocationToEvent).filter_by(location_id=r.id).count()
                        if asscevent > 0:
                            showEvents = wx.Button(self, wx.ID_ANY, label=str(asscevent) + " Event(s) Found")
                            showEvents.info = ["ShowLocationEvents", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showEvents)
                            inforow2.Add(showEvents,0,wx.ALL,10)


                        asscind = session.query(LocationToVehicle).filter_by(location_id=r.id).count()
                        if asscind > 0:
                            showVehicles = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Vehicle(s) Found")
                            showVehicles.info = ["ShowLocationVehicles", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showVehicles)
                            inforow2.Add(showVehicles,0,wx.ALL,10)

                        col.Add(inforow2)

                        inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                        map = wx.Button(self, wx.ID_ANY, label="Map")
                        map.query = locationQuery
                        self.Bind(wx.EVT_BUTTON, self.Map, map)
                        inforow3.Add(map,0,wx.ALL,10)
                        add = wx.Button(self, wx.ID_ANY, label="Add Vehicle")
                        add.info = ["VehicleToLocation", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow3.Add(add,0,wx.ALL,10)
                        add = wx.Button(self, wx.ID_ANY, label="Add Individual")
                        add.info = ["IndividualToLocation", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow3.Add(add,0,wx.ALL,10)
                        delete = wx.Button(self, wx.ID_ANY, label="Delete")
                        delete.info = ["Location", r]
                        self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                        inforow3.Add(delete,0,wx.ALL,10)
                        col.Add(inforow3)

                        sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                        col.Add(sep,0,wx.ALL,5)

        if search[0] == "EventAll":
                results = session.query(Event).all()
                if results == []:
                    t=wx.StaticText(self, id=wx.ID_ANY, label="NO RESULTS FOUND")
                    t.SetForegroundColour(wx.Colour(255,255,255))
                else:
                    refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
                    self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
                    col.Add(refresh,0,wx.ALL,10)
                    for r in results:
                        card = wx.BoxSizer(wx.VERTICAL)
                        locid = session.query(LocationToEvent).filter_by(event_id=r.id).all()

                        if locid != []:
                            location = session.query(Location).filter_by(id=locid[-1].location_id).all()

                            inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                            add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location[-1].streetaddress)
                            add.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(add,0,wx.ALL,10)
                            city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location[-1].city)
                            city.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(city,0,wx.ALL,10)
                            state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location[-1].state)
                            state.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(state,0,wx.ALL,10)
                            zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location[-1].zip)
                            zip.SetForegroundColour(wx.Colour(255,255,255))
                            inforow1.Add(zip,0,wx.ALL,10)
                            card.Add(inforow1)

                        inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                        date = wx.StaticText(self, id=wx.ID_ANY, label="DATE: " + r.date)
                        date.SetForegroundColour(wx.Colour(255,255,255))
                        inforow2.Add(date,0,wx.ALL,10)
                        title = wx.StaticText(self, id=wx.ID_ANY, label="TITLE: " + r.title)
                        title.SetForegroundColour(wx.Colour(255,255,255))
                        inforow2.Add(title,0,wx.ALL,10)
                        card.Add(inforow2)

                        inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                        desc = wx.StaticText(self, id=wx.ID_ANY, label="DESCRIPTION: " + r.description)
                        desc.SetForegroundColour(wx.Colour(255,255,255))
                        inforow3.Add(desc,0,wx.ALL,10)
                        card.Add(inforow3)

                        inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                        asscind = session.query(ImageEvent).filter_by(event_id=r.id).count()
                        if asscind > 0:
                            showImages = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Image(s) Found")
                            showImages.info = ["ShowEventImages", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showImages)
                            inforow4.Add(showImages,0,wx.ALL,10)
                        card.Add(inforow4)

                        asscind = session.query(IndividualToEvent).filter_by(event_id=r.id).count()
                        if asscind > 0:
                            showIndividuals = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Individual(s) Found")
                            showIndividuals.info = ["ShowEventIndividuals", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showIndividuals)
                            inforow4.Add(showIndividuals,0,wx.ALL,10)
                            card.Add(inforow4)

                        asscind = session.query(VehicleToEvent).filter_by(event_id=r.id).count()
                        if asscind > 0:
                            showVehicles = wx.Button(self, wx.ID_ANY, label=str(asscind) + " Vehicles(s) Found")
                            showVehicles.info = ["ShowEventVehicles", r]
                            self.Bind(wx.EVT_BUTTON, self.additionalInfo, showVehicles)
                            inforow4.Add(showVehicles,0,wx.ALL,10)
                            card.Add(inforow4)

                        inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                        add = wx.Button(self, wx.ID_ANY, label="Add Individual")
                        add.info = ["IndividualToEvent", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow5.Add(add,0,wx.ALL,10)
                        add = wx.Button(self, wx.ID_ANY, label="Add Vehicle")
                        add.info = ["VehicleToEvent", r]
                        self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                        inforow5.Add(add,0,wx.ALL,10)
                        card.Add(inforow5)

                        inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                        edit = wx.Button(self, wx.ID_ANY, label="Edit")
                        edit.info = ["Event", r]
                        self.Bind(wx.EVT_BUTTON, self.editEntry, edit)
                        delete = wx.Button(self, wx.ID_ANY, label="Delete")
                        delete.info = ["Event", r]
                        self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                        inforow6.Add(edit,0,wx.ALL,10)
                        inforow6.Add(delete,0,wx.ALL,10)
                        card.Add(inforow6)

                        sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                        col.Add(sep,0,wx.ALL,5)
                        col.Add(card)

        if search[0] == "ShowFacialRecResults":
            results = list(set(search[1]))
            for r in results:
                #--------Get Primary Image--------
                locid = session.query(IndividualToLocation).filter_by(individual_id=r.id).all()
                if locid != []:
                    location = session.query(Location).filter_by(id=locid[0].location_id).one()
                image = session.query(ImageIndividual).filter_by(individual_id=r.id).all()
                de = decrypt(image[-1].image, encryptionKey)
                image_data = de
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                if height > width:
                    new_height = 250
                    new_width  = new_height * width / height
                else:
                    new_width  = 250
                    new_height = new_width * height / width
                image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
                width, height = image.size
                bitmap = wx.BitmapFromBuffer(width, height, image.tobytes())
                #--------Set Up Display----------
                display = wx.BoxSizer(wx.HORIZONTAL)
                img = wx.BoxSizer(wx.VERTICAL)
                image = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=bitmap)
                img.Add(image,0,wx.ALL,10)
                images = session.query(ImageIndividual).filter_by(individual_id=r.id).count()
                if images > 1:
                    moreImg = wx.Button(self, wx.ID_ANY, label="See " + str(images) + " Images")
                    moreImg.info = ["ShowIndividualImages", r]
                    self.Bind(wx.EVT_BUTTON, self.additionalInfo, moreImg)
                    img.Add(moreImg,0,wx.ALL,10)
                display.Add(img,0,wx.ALL,10)


                card = wx.BoxSizer(wx.VERTICAL)
                inforow1 = wx.BoxSizer(wx.HORIZONTAL)
                firstname = wx.StaticText(self, id=wx.ID_ANY, label="FIRST NAME: " + r.firstname)
                firstname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(firstname,0,wx.ALL,10)
                lastname = wx.StaticText(self, id=wx.ID_ANY, label="LAST NAME: " + r.lastname)
                lastname.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(lastname,0,wx.ALL,10)
                affiliation = wx.StaticText(self, id=wx.ID_ANY, label="AFFILIATION: " + r.organization)
                affiliation.SetForegroundColour(wx.Colour(255,255,255))
                inforow1.Add(affiliation,0,wx.ALL,10)
                card.Add(inforow1)

                inforow2 = wx.BoxSizer(wx.HORIZONTAL)
                workplace = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN WORKPLACE: " + r.workplace)
                workplace.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(workplace,0,wx.ALL,10)
                email = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN EMAIL: " +  r.email)
                email.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(email,0,wx.ALL,10)
                phone = wx.StaticText(self, id=wx.ID_ANY, label="KNOWN PHONE: " + r.phone)
                phone.SetForegroundColour(wx.Colour(255,255,255))
                inforow2.Add(phone,0,wx.ALL,10)
                card.Add(inforow2)

                inforow3 = wx.BoxSizer(wx.HORIZONTAL)
                fbtitle = wx.StaticText(self, id=wx.ID_ANY, label="FACEBOOK PROFILE: ")
                fbtitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(fbtitle,0,wx.ALL,10)
                if r.facebookurl != "":
                    fb = wx.adv.HyperlinkCtrl(self, url= r.facebookurl)
                    fb.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(fb,0,wx.ALL,10)
                linktitle = wx.StaticText(self, id=wx.ID_ANY, label="LINKEDIN PROFILE: ")
                linktitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(linktitle,0,wx.ALL,10)
                if r.linkedinurl != "":
                    link = wx.adv.HyperlinkCtrl(self, url= r.linkedinurl)
                    link.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(link,0,wx.ALL,10)
                twittitle = wx.StaticText(self, id=wx.ID_ANY, label="TWITTER PROFILE: ")
                twittitle.SetForegroundColour(wx.Colour(255,255,255))
                inforow3.Add(twittitle,0,wx.ALL,10)
                if r.twitterurl != "":
                    twit = wx.adv.HyperlinkCtrl(self, url= r.twitterurl)
                    twit.SetNormalColour(wx.Colour(255,255,255))
                    inforow3.Add(twit,0,wx.ALL,10)
                card.Add(inforow3)

                if locid != []:
                    inforow4 = wx.BoxSizer(wx.HORIZONTAL)
                    add = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + location.streetaddress)
                    add.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(add,0,wx.ALL,10)
                    city = wx.StaticText(self, id=wx.ID_ANY, label="CITY: " + location.city)
                    city.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(city,0,wx.ALL,10)
                    state = wx.StaticText(self, id=wx.ID_ANY, label="STATE: " + location.state)
                    state.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(state,0,wx.ALL,10)
                    zip = wx.StaticText(self, id=wx.ID_ANY, label="ZIP: " + location.zip)
                    zip.SetForegroundColour(wx.Colour(255,255,255))
                    inforow4.Add(zip,0,wx.ALL,10)
                    card.Add(inforow4)

                inforow5 = wx.BoxSizer(wx.HORIZONTAL)
                #in = wx.StaticText(self, id=wx.ID_ANY, label="INCIDENTS: " + str(r.violentincidents))
                #inforow4.Add(in,0,wx.ALL,5)
                notes = wx.StaticText(self, id=wx.ID_ANY, label="NOTES: " + r.notes)
                notes.SetForegroundColour(wx.Colour(255,255,255))
                inforow5.Add(notes,0,wx.ALL,10)
                card.Add(inforow5)

                inforow6 = wx.BoxSizer(wx.HORIZONTAL)
                asscvehicles = session.query(VehicleToIndividual).filter_by(individual_id=r.id).count()
                if asscvehicles > 0:
                    showVehicles = wx.Button(self, wx.ID_ANY, label=str(asscvehicles) + " Vehicles(s) Found")
                    showVehicles.info = ["ShowIndividualVehicles", r]
                    self.Bind(wx.EVT_BUTTON, self.additionalInfo, showVehicles)
                    inforow6.Add(showVehicles,0,wx.ALL,10)

                asscloc = session.query(IndividualToLocation).filter_by(individual_id=r.id).count()
                if asscloc > 0:
                    showLocations = wx.Button(self, wx.ID_ANY, label=str(asscloc) + " Location(s) Found")
                    showLocations.info = ["ShowIndividualLocations", r]
                    self.Bind(wx.EVT_BUTTON, self.additionalInfo, showLocations)
                    inforow6.Add(showLocations,0,wx.ALL,10)

                asscevent = session.query(IndividualToEvent).filter_by(individual_id=r.id).count()
                if asscevent > 0:
                    showEvents = wx.Button(self, wx.ID_ANY, label=str(asscevent) + " Event(s) Found")
                    showEvents.info = ["ShowIndividualEvents", r]
                    self.Bind(wx.EVT_BUTTON, self.additionalInfo, showEvents)
                    inforow6.Add(showEvents,0,wx.ALL,10)

                asscevent = session.query(IndividualToIndividual).filter_by(individual1_id=r.id).count()
                if asscevent > 0:
                    showEvents = wx.Button(self, wx.ID_ANY, label=str(asscevent) + " Associates(s) Found")
                    showEvents.info = ["ShowIndividualAssociates", r]
                    self.Bind(wx.EVT_BUTTON, self.additionalInfo, showEvents)
                    inforow6.Add(showEvents,0,wx.ALL,10)

                card.Add(inforow6)

                inforow7 = wx.BoxSizer(wx.HORIZONTAL)

                add = wx.Button(self, wx.ID_ANY, label="Add Associate")
                add.info = ["IndividualToIndividual", r]
                self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                inforow7.Add(add,0,wx.ALL,10)

                add = wx.Button(self, wx.ID_ANY, label="Add Vehicle")
                add.info = ["VehicleToIndividual", r]
                self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                inforow7.Add(add,0,wx.ALL,10)

                add = wx.Button(self, wx.ID_ANY, label="Add Location")
                add.info = ["LocationToIndividual", r]
                self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                inforow7.Add(add,0,wx.ALL,10)

                add = wx.Button(self, wx.ID_ANY, label="Add Event")
                add.info = ["EventToIndividual", r]
                self.Bind(wx.EVT_BUTTON, self.linkInfo, add)
                inforow7.Add(add,0,wx.ALL,10)

                card.Add(inforow7)

                inforow8 = wx.BoxSizer(wx.HORIZONTAL)
                edit = wx.Button(self, wx.ID_ANY, label="Edit")
                edit.info = ["Individual", r]
                self.Bind(wx.EVT_BUTTON, self.editEntry, edit)
                delete = wx.Button(self, wx.ID_ANY, label="Delete")
                delete.info = ["Individual", r]
                self.Bind(wx.EVT_BUTTON, self.deleteEntry, delete)
                inforow8.Add(edit,0,wx.ALL,10)
                inforow8.Add(delete,0,wx.ALL,10)
                card.Add(inforow8)

                sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
                sep.SetForegroundColour(wx.Colour(255,255,255))
                col.Add(sep,0,wx.ALL,5)

                display.Add(card)
                col.Add(display)

        self.SetSizer(col)

    def linkInfo(self,event):
        widget = event.GetEventObject()
        info = widget.info
        linkingWindow(info)

    def additionalInfo(self,event):
        widget = event.GetEventObject()
        info = widget.info
        additionalInfoWindow(info)

    def deleteEntry(self, event):
        widget = event.GetEventObject()
        info = widget.info
        confirm = wx.MessageDialog(None, "Are You Sure You Want To Delete This Record?")
        if confirm.ShowModal() == wx.ID_OK:

            if info[0] == "Individual":
                record =  session.query(Individual).filter_by(id = info[1].id).one()
                session.delete(record)
                session.commit()
                record =  session.query(ImageIndividual).filter_by(individual_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(IndividualToEvent).filter_by(individual_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(VehicleToIndividual).filter_by(individual_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(IndividualToLocation).filter_by(individual_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(IndividualToIndividual).filter_by(individual1_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()

            if info[0] == "Event":
                record =  session.query(Event).filter_by(id = info[1].id).one()
                session.delete(record)
                session.commit()
                record =  session.query(IndividualToEvent).filter_by(event_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(LocationToEvent).filter_by(event_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(VehicleToEvent).filter_by(event_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()

            if info[0] == "Vehicle":
                record =  session.query(Vehicle).filter_by(id = info[1].id).one()
                session.delete(record)
                session.commit()
                record =  session.query(ImageVehicle).filter_by(vehicle_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(VehicleToEvent).filter_by(vehicle_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(VehicleToIndividual).filter_by(vehicle_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(LocationToVehicle).filter_by(vehicle_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()

            if info[0] == "Location":
                record =  session.query(Location).filter_by(id = info[1].id).one()
                session.delete(record)
                session.commit()
                record =  session.query(LocationToEvent).filter_by(location_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(IndividualToLocation).filter_by(location_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()
                record =  session.query(LocationToVehicle).filter_by(location_id = info[1].id).all()
                for r in record:
                    session.delete(r)
                    session.commit()

            refresh(self,event)

        elif confirm.ShowModal() == wx.ID_CANCEL:
            sys.exit()

    def editEntry(self,event):
        widget = event.GetEventObject()
        info = widget.info
        editWindow(info,self.search)

    def refresh(self,event):
        new = resultsWindow(self.search)
        pos = list(self.GetScreenPosition())
        new.MoveXY(pos[0]-15,pos[1]-33)
        frame = wx.GetTopLevelParent(self)
        frame.Destroy()

    def Map(self,event):
        widget = event.GetEventObject()
        point = widget.query
        coordinates = []
        try:
            if point[0] == "address":
                point.remove("address")
                search = ''.join(point)
                #print(search)
                g = geocoder.osm(search)
                data = g.json
                if data:
                    c = []
                    c.append(data["lat"])
                    c.append(data["lng"])
                    coordinates.append(c)
            if point[0] == "coordinate":
                c = []
                c.append(point[1])
                c.append(point[2])
                coordinates.append(c)
            markers = folium.FeatureGroup(name="Locations")

            for marker in coordinates:
                markers.add_child(folium.Marker(location=marker))
            map = folium.Map(location=coordinates[0], zoom_start=6, tiles='openstreetmap')
            map.add_child(markers)
            map.add_child(folium.LayerControl())
            map.save("Graphics/tempmap.html")
            browser = webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s")
            path =  os.path.abspath("Graphics/tempmap.html")
            browser.open_new(path)
            os.remove("Graphics/tempmap.html")
        except:
            dial = wx.MessageDialog(None, 'Unable To Connect To The Internet', 'Mapping Failed', wx.OK)
            dial.ShowModal()

class namePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        txtOne=wx.StaticText(self, id=wx.ID_ANY, label="First Name")
        txtOne.SetForegroundColour(wx.Colour(255,255,255))
        self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
        txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Last Name")
        txtTwo.SetForegroundColour(wx.Colour(255,255,255))
        self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
        txtThree=wx.StaticText(self, id=wx.ID_ANY, label="Affiliation")
        txtThree.SetForegroundColour(wx.Colour(255,255,255))
        self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
        txtFour=wx.StaticText(self, id=wx.ID_ANY, label="Phone Number")
        txtFour.SetForegroundColour(wx.Colour(255,255,255))
        self.inputFour = wx.TextCtrl(self, wx.ID_ANY, "")
        txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Email")
        txtFive.SetForegroundColour(wx.Colour(255,255,255))
        self.inputFive = wx.TextCtrl(self, wx.ID_ANY, "")
        txtSix = wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
        txtSix.SetForegroundColour(wx.Colour(255,255,255))
        searchButton = wx.Button(self, wx.ID_ANY, label="Search")
        self.Bind(wx.EVT_BUTTON, self.returnSearchParameters, searchButton)
        allButton = wx.Button(self, wx.ID_ANY, label="See All")
        self.Bind(wx.EVT_BUTTON, self.searchAll, allButton)
        newButton = wx.Button(self, wx.ID_ANY, label="Add New Individual")
        self.Bind(wx.EVT_BUTTON, self.openEnterWindow, newButton)

        col = wx.BoxSizer(wx.VERTICAL)
        col.Add(txtSix, 0,wx.ALL, 5)

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row1.Add(txtOne, 0,wx.ALL, 5)
        row1.Add(self.inputOne, 0,wx.ALL, 5)
        row1.Add(txtTwo, 0, wx.ALL, 5)
        row1.Add(self.inputTwo, 0,wx.ALL, 5)
        row1.Add(txtThree, 0, wx.ALL, 5)
        row1.Add(self.inputThree, 0,wx.ALL, 5)
        row1.Add(txtFour, 0, wx.ALL, 5)
        row1.Add(self.inputFour, 0,wx.ALL, 5)
        row1.Add(txtFive, 0, wx.ALL, 5)
        row1.Add(self.inputFive, 0,wx.ALL, 5)
        col.Add(row1)

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(searchButton, 0,wx.ALL, 5)
        row2.Add(allButton, 0,wx.ALL, 5)
        row2.Add(newButton, 0,wx.ALL, 5)
        col.Add(row2)

        self.SetSizer(col)

    def returnSearchParameters(self,e):
        first = self.inputOne.GetValue()
        last = self.inputTwo.GetValue()
        organization = self.inputThree.GetValue()
        phone = self.inputFour.GetValue()
        email = self.inputFive.GetValue()
        searchParameters = ["Name", first,last,organization,phone,email]
        resultsWindow(searchParameters)

    def searchAll(self,e):
        searchParameters = ["NameAll"]
        resultsWindow(searchParameters)

    def openEnterWindow(self,e):
        enterWindow('individualNew')

class locationPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Street Address")
        txtOne.SetForegroundColour(wx.Colour(255,255,255))
        self.inputOne = wx.TextCtrl(self, wx.ID_ANY, "")
        txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Neighborhood")
        txtTwo.SetForegroundColour(wx.Colour(255,255,255))
        self.inputTwo = wx.TextCtrl(self, wx.ID_ANY, "")
        txtThree=wx.StaticText(self, id=wx.ID_ANY, label="City")
        txtThree.SetForegroundColour(wx.Colour(255,255,255))
        self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
        txtFour=wx.StaticText(self, id=wx.ID_ANY, label="State")
        txtFour.SetForegroundColour(wx.Colour(255,255,255))
        self.inputFour = wx.TextCtrl(self, wx.ID_ANY, "")
        txtFive=wx.StaticText(self, id=wx.ID_ANY, label="Zip")
        txtFive.SetForegroundColour(wx.Colour(255,255,255))
        self.inputFive = wx.TextCtrl(self, wx.ID_ANY, "")
        txtSeven=wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
        txtSeven.SetForegroundColour(wx.Colour(255,255,255))
        searchButton = wx.Button(self, wx.ID_ANY, label="Search")
        self.Bind(wx.EVT_BUTTON, self.returnSearchParameters, searchButton)
        allButton = wx.Button(self, wx.ID_ANY, label="See All")
        self.Bind(wx.EVT_BUTTON, self.searchAll, allButton)
        newButton = wx.Button(self, wx.ID_ANY, label="New Location")
        self.Bind(wx.EVT_BUTTON, self.openEnterWindow, newButton)

        col = wx.BoxSizer(wx.VERTICAL)
        col.Add(txtSeven, 0,wx.ALL, 5)

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row1.Add(txtOne, 0,wx.ALL, 5)
        row1.Add(self.inputOne, 0,wx.ALL, 5)
        row1.Add(txtTwo, 0, wx.ALL, 5)
        row1.Add(self.inputTwo, 0,wx.ALL, 5)
        row1.Add(txtThree, 0,wx.ALL, 5)
        row1.Add(self.inputThree, 0, wx.ALL, 5)
        row1.Add(txtFour, 0, wx.ALL, 5)
        row1.Add(self.inputFour, 0, wx.ALL, 5)
        row1.Add(txtFive, 0, wx.ALL, 5)
        row1.Add(self.inputFive, 0, wx.ALL, 5)
        col.Add(row1)

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(searchButton, 0,wx.ALL, 5)
        row2.Add(allButton, 0,wx.ALL, 5)
        row2.Add(newButton, 0,wx.ALL, 5)
        col.Add(row2)

        self.SetSizer(col)

    def returnSearchParameters(self,e):
        address = self.inputOne.GetValue()
        neighborhood = self.inputTwo.GetValue()
        city = self.inputThree.GetValue()
        state = self.inputFour.GetValue()
        zip = self.inputFive.GetValue()
        searchParameters = ["Location", address,neighborhood,city,state,zip]
        resultsWindow(searchParameters)
        return searchParameters

    def searchAll(self,e):
        searchParameters = ["LocationAll"]
        resultsWindow(searchParameters)

    def openEnterWindow(self,e):
        enterWindow('locationNew')

class vehiclePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Plate")
        txtOne.SetForegroundColour(wx.Colour(255,255,255))
        txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Color")
        txtTwo.SetForegroundColour(wx.Colour(255,255,255))
        txtThree=wx.StaticText(self, id=wx.ID_ANY, label="Make & Model")
        txtThree.SetForegroundColour(wx.Colour(255,255,255))
        txtFour=wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
        txtFour.SetForegroundColour(wx.Colour(255,255,255))
        self.inputOne= wx.TextCtrl(self, wx.ID_ANY, "")
        self.inputTwo= wx.TextCtrl(self, wx.ID_ANY, "")
        self.inputThree = wx.TextCtrl(self, wx.ID_ANY, "")
        searchButton = wx.Button(self, wx.ID_ANY, label="Search")
        self.Bind(wx.EVT_BUTTON, self.returnSearchParameters, searchButton)
        allButton = wx.Button(self, wx.ID_ANY, label="See All")
        self.Bind(wx.EVT_BUTTON, self.searchAll, allButton)
        newButton = wx.Button(self, wx.ID_ANY, label="Add New Vehicle")
        self.Bind(wx.EVT_BUTTON, self.openEnterWindow, newButton)

        col = wx.BoxSizer(wx.VERTICAL)
        col.Add(txtFour, 0,wx.ALL, 5)

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row1.Add(txtOne, 0,wx.ALL, 5)
        row1.Add(self.inputOne, 0,wx.ALL, 5)
        row1.Add(txtTwo, 0, wx.ALL, 5)
        row1.Add(self.inputTwo, 0,wx.ALL, 5)
        row1.Add(txtThree, 0,wx.ALL, 5)
        row1.Add(self.inputThree, 0,wx.ALL, 5)
        col.Add(row1)

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(searchButton, 0,wx.ALL, 5)
        row2.Add(allButton, 0,wx.ALL, 5)
        row2.Add(newButton, 0,wx.ALL, 5)
        col.Add(row2)

        self.SetSizer(col)

    def returnSearchParameters(self,e):
        plate = self.inputOne.GetValue()
        color = self.inputTwo.GetValue()
        make = self.inputThree.GetValue()
        searchParameters = ["Vehicle", plate,color,make]
        resultsWindow(searchParameters)

    def searchAll(self,e):
        searchParameters = ["VehicleAll"]
        resultsWindow(searchParameters)

    def openEnterWindow(self,e):
        enterWindow('vehicleNew')

class eventPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        txtOne=wx.StaticText(self, id=wx.ID_ANY, label="Date")
        txtOne.SetForegroundColour(wx.Colour(255,255,255))
        txtTwo=wx.StaticText(self, id=wx.ID_ANY, label="Title")
        txtTwo.SetForegroundColour(wx.Colour(255,255,255))
        txtFour=wx.StaticText(self, id=wx.ID_ANY, label="Entries Are Case Sensitive")
        txtFour.SetForegroundColour(wx.Colour(255,255,255))
        self.inputOne= wx.TextCtrl(self, wx.ID_ANY, "")
        self.inputTwo= wx.TextCtrl(self, wx.ID_ANY, "")
        searchButton = wx.Button(self, wx.ID_ANY, label="Search")
        self.Bind(wx.EVT_BUTTON, self.returnSearchParameters, searchButton)
        allButton = wx.Button(self, wx.ID_ANY, label="See All")
        self.Bind(wx.EVT_BUTTON, self.searchAll, allButton)
        newButton = wx.Button(self, wx.ID_ANY, label="Add New Event")
        self.Bind(wx.EVT_BUTTON, self.openEnterWindow, newButton)


        col = wx.BoxSizer(wx.VERTICAL)
        col.Add(txtFour, 0,wx.ALL, 5)

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        row1.Add(txtOne, 0,wx.ALL, 5)
        row1.Add(self.inputOne, 0,wx.ALL, 5)
        row1.Add(txtTwo, 0, wx.ALL, 5)
        row1.Add(self.inputTwo, 0,wx.ALL, 5)
        col.Add(row1)

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        row2.Add(searchButton, 0,wx.ALL, 5)
        row2.Add(allButton, 0,wx.ALL, 5)
        row2.Add(newButton, 0,wx.ALL, 5)
        col.Add(row2)

        self.SetSizer(col)

    def returnSearchParameters(self,e):
        date = self.inputOne.GetValue()
        title = self.inputTwo.GetValue()
        searchParameters = ["Event", date,title]
        resultsWindow(searchParameters)
        return searchParameters

    def openEnterWindow(self,e):
        enterWindow('eventNew')

    def searchAll(self,e):
        searchParameters = ["EventAll"]
        resultsWindow(searchParameters)

class analyticsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.currentDirectory = os.getcwd()
        self.unknown = ""
        self.hits = []
        self.profiles = []
        self.knowns = []

        col = wx.BoxSizer(wx.VERTICAL)

        row1 = wx.BoxSizer(wx.HORIZONTAL)
        txt=wx.StaticText(self, id=wx.ID_ANY, label="Target Organization")
        row1.Add(txt, 0,wx.ALL, 5)
        txt.SetForegroundColour(wx.Colour(255,255,255))
        self.inputOrg= wx.TextCtrl(self, wx.ID_ANY, "")
        row1.Add(self.inputOrg, 0,wx.ALL, 5)
        col.Add(row1)

        row2 = wx.BoxSizer(wx.HORIZONTAL)
        network = wx.Button(self, wx.ID_ANY, label="Network Deconstruction Analysis")
        #self.Bind(wx.EVT_BUTTON, self.searchAll, network)
        row2.Add(network, 0,wx.ALL, 5)
        orgact = wx.Button(self, wx.ID_ANY, label="Organizational Activity Map")
        #self.Bind(wx.EVT_BUTTON, self.openEnterWindow, newButton)
        row2.Add(orgact, 0,wx.ALL, 5)
        col.Add(row2)

        sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
        sep.SetForegroundColour(wx.Colour(255,255,255))
        col.Add(sep,0,wx.ALL,5)

        row3 = wx.BoxSizer(wx.VERTICAL)
        db = wx.Button(self, wx.ID_ANY, label="Database Overview Report")
        #self.Bind(wx.EVT_BUTTON, self.openEnterWindow, newButton)
        row3.Add(db, 0,wx.ALL, 5)
        col.Add(row3)

        sep = wx.StaticLine(self, id=wx.ID_ANY,size=(950, -1), style=wx.LI_HORIZONTAL)
        sep.SetForegroundColour(wx.Colour(255,255,255))
        col.Add(sep,0,wx.ALL,5)

        txt=wx.StaticText(self, id=wx.ID_ANY, label="Facial Recognition")
        txt.SetForegroundColour(wx.Colour(255,255,255))
        col.Add(txt,0,wx.ALL,5)

        row4 = wx.BoxSizer(wx.HORIZONTAL)
        sf = wx.Button(self, wx.ID_ANY, label="Calibrate")
        self.Bind(wx.EVT_BUTTON, self.calibrateFacialRec, sf)
        row4.Add(sf, 0,wx.ALL, 5)
        col.Add(row4)

        row5 = wx.BoxSizer(wx.HORIZONTAL)
        up = wx.Button(self, wx.ID_ANY, label="Upload Image")
        self.Bind(wx.EVT_BUTTON, self.onOpenFile, up)
        row5.Add(up, 0,wx.ALL, 5)
        sa = wx.Button(self, wx.ID_ANY, label="Search Faces")
        self.Bind(wx.EVT_BUTTON, self.analyseGroupPicture, sa)
        row5.Add(sa, 0,wx.ALL, 5)
        col.Add(row5)

        self.SetSizer(col)

    def calibrateFacialRec(self,event):
        #pdb.set_trace()
        progress = 0
        results = session.query(Individual).all()
        if results == []:
            dlg = wx.MessageDialog(None, "No Targets In Database")
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
        else:
            max = len(results)
            bar = wx.ProgressDialog(title="Calibration", message="Calibrating " + str(progress) + " of " + str(max) + " images", maximum=max, parent=self, style=wx.PD_AUTO_HIDE)
        for r in results:
            if bar.WasCancelled == True:
                break
            image = session.query(ImageIndividual).filter_by(individual_id=r.id).all()
            for i in image:
                de = decrypt(i.image, encryptionKey)
                image_data = de
                im = Image.open(io.BytesIO(image_data))
                known_image = np.array(im)
                face_locations = face_recognition.face_locations(known_image, number_of_times_to_upsample=1, model="cnn")
                known_encodings = face_recognition.face_encodings(known_image, known_face_locations=face_locations)
                for encoding in known_encodings:
                    self.knowns.append(encoding)
                    self.profiles.append(r)
            progress += 1
            bar.Update(value=progress, newmsg = "Calibrating " + str(progress) + " of " + str(max) + " images")
        bar.Destroy()

    def analyseGroupPicture(self,event):
        #pdb.set_trace()
        progress = 0
        if self.knowns != [] and self.unknown != []:
            unknown_image = face_recognition.load_image_file(self.unknown[0])
            face_locations = face_recognition.face_locations(unknown_image, number_of_times_to_upsample=1, model="cnn")
            encodings = face_recognition.face_encodings(unknown_image, known_face_locations=face_locations)
            max = len(encodings)
            bar = wx.ProgressDialog(title="Calibration", message="Searching for " + str(progress) + " of " + str(max) + " faces", maximum=max, parent=self, style=wx.PD_AUTO_HIDE)
            pil_image = Image.fromarray(unknown_image)
            draw = ImageDraw.Draw(pil_image)
            for (top, right, bottom, left), face_encoding in zip(face_locations, encodings):
                if bar.WasCancelled == True:
                    break
                matches = face_recognition.compare_faces(self.knowns, face_encoding, tolerance=0.54)
                firstname = "Unknown"
                lastname = ""
                if True in matches:
                    first_match_index = matches.index(True)
                    hit = self.profiles[first_match_index]
                    firstname = hit.firstname
                    lastname = hit.lastname
                    self.hits.append(hit)
                name = firstname + " " + lastname
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
                text_width, text_height = draw.textsize(name)
                draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
                draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))
                progress += 1
                bar.Update(value=progress, newmsg = "Searching for " + str(progress) + " of " + str(max) + " faces" )
            bar.Destroy()
            del draw
            new = additionalInfoWindow(["ShowAnalyzedImage",pil_image])
            if self.hits != []:
                results = resultsWindow(["ShowFacialRecResults",self.hits])
            self.unknown = []
        else:
            confirm = wx.MessageDialog(None, "Facial Recognition Not Calibrated")
            if confirm.ShowModal() == wx.ID_OK:
                confirm.Destroy()

    def onOpenFile(self, event):
        wildcard = "JPEG (*.jpg)|*.jpg"
        dlg = wx.FileDialog(
            self, message="Choose Image To Upload",
            defaultDir=self.currentDirectory,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()
            self.unknown = path
        dlg.Destroy()

class modesPanel(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        self.SetBackgroundColour((0,0,0))

        tabOne = namePanel(self)
        self.AddPage(tabOne, "INDIVIDUALS")
        tabTwo = vehiclePanel(self)
        self.AddPage(tabTwo, "VEHICLES")
        tabThree = locationPanel(self)
        self.AddPage(tabThree, "LOCATIONS")
        tabThree = eventPanel(self)
        self.AddPage(tabThree, "EVENTS")
        tabFour = analyticsPanel(self)
        self.AddPage(tabFour, "ANALYTICS")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

class ipWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "IP Information", size=(300,250))
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        col = wx.BoxSizer(wx.VERTICAL)
        try:
            response = tor.get("http://ip-api.com/json")
            data = response.json()
            self.ip = data["query"]
            self.isp = data["isp"]
            self.city = data["city"]
            self.state = data["regionName"]
            self.country = data["country"]
            self.zip = data["zip"]
            self.lat = data["lat"]
            self.long = data["lon"]
            row = wx.StaticText(self, id=wx.ID_ANY, label="YOUR IP")
            row.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(row,0,wx.ALL,10)
            row = wx.StaticText(self, id=wx.ID_ANY, label="PUBLIC IP: " + self.isp + " " + self.ip)
            row.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(row,0,wx.ALL,10)
            row = wx.StaticText(self, id=wx.ID_ANY, label="ADDRESS: " + self.city + ", " + self.state + " " + self.country + " " + self.zip)
            row.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(row,0,wx.ALL,10)
            row = wx.StaticText(self, id=wx.ID_ANY, label="EXACT COORDINATES: " + str(self.lat) + ", " + str(self.long))
            row.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(row,0,wx.ALL,10)
            refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
            self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
            col.Add(refresh,0,wx.ALL,10)
            self.SetSizer(col)
            self.Layout()
            self.Show()
        except:
            dial = wx.MessageDialog(None, 'Unable To Connect To The Internet', 'IP Failed', wx.OK)
            dial.ShowModal()
            self.Destroy()

    def refresh(self,event):
        response = tor.get("http://ip-api.com/json")
        data = response.json()
        self.ip = data["query"]
        self.isp = data["isp"]
        self.city = data["city"]
        self.state = data["regionName"]
        self.country = data["country"]
        self.zip = data["zip"]
        self.lat = data["lat"]
        self.long = data["lon"]

class tipsWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "IP Information", size=(350,500))
        self.panel = wx.ScrolledWindow(self)
        self.panel.SetScrollbars(1, 1, 1, 1)
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        col = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, id=wx.ID_ANY, label="INVESTIGATIVE TIPS")
        title.SetForegroundColour(wx.Colour(255,255,255))
        col.Add(title,0,wx.ALL,10)
        refresh = wx.Button(self, wx.ID_ANY, label="Refresh")
        self.Bind(wx.EVT_BUTTON, self.refresh, refresh)
        col.Add(refresh,0,wx.ALL,10)
        add = wx.Button(self, wx.ID_ANY, label="Add Tip")
        self.Bind(wx.EVT_BUTTON, self.newtip, add)
        col.Add(add,0,wx.ALL,10)
        #pdb.set_trace()
        tips = session.query(Note).all()
        index=1
        for t in tips:
            title = wx.StaticText(self, id=wx.ID_ANY, label="Tip #" + str(index) + " " + t.title)
            title.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(title,0,wx.ALL,10)
            row = wx.StaticText(self, id=wx.ID_ANY, label= t.description)
            row.Wrap(280)
            row.SetForegroundColour(wx.Colour(255,255,255))
            col.Add(row,0,wx.ALL,10)
            buttons = wx.BoxSizer(wx.HORIZONTAL)
            edit = wx.Button(self, wx.ID_ANY, label="Edit")
            edit.info = ["editTip",t]
            self.Bind(wx.EVT_BUTTON, self.editTip, edit)
            buttons.Add(edit,0,wx.ALL,10)
            delete = wx.Button(self, wx.ID_ANY, label="Delete")
            delete.info = ["deleteTip",t]
            self.Bind(wx.EVT_BUTTON, self.deleteTip, delete)
            buttons.Add(delete,0,wx.ALL,10)
            col.Add(buttons)
        self.SetSizer(col)
        self.Layout()
        self.Show()


    def newtip(self,event):
        enterWindow("tipNew")

    def editTip(self,event):
        enterWindow("tipNew")

    def deleteTip(self,event):
        enterWindow("tipNew")

    def refresh(self,event):
        new = tipsWindow()
        pos = list(self.GetScreenPosition())
        new.MoveXY(pos[0]-15,pos[1]-33)
        frame = wx.GetTopLevelParent(self)
        frame.Destroy()

class mainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Database", size=(1000,500))
        panel = wx.Panel(self)
        self.SetBackgroundColour((25,25,25))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        notebook = modesPanel(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        menuBar = wx.MenuBar()
        fileButton = wx.Menu()
        connect = fileButton.Append(wx.ID_ANY,'Open IP Information')
        self.Bind(wx.EVT_MENU, self.openConnectionInfo, connect)
        tips = fileButton.Append(wx.ID_ANY,'Open Investigative Tips')
        self.Bind(wx.EVT_MENU, self.opentips, tips)
        self.Bind(wx.EVT_CLOSE, self.close)
        menuBar.Append(fileButton, "File")
        self.SetMenuBar(menuBar)

        self.Layout()
        self.Show()

    def close(self,e):
        self.Close()
        sys.exit()

    def openConnectionInfo(self,e):
        ipWindow()

    def opentips(self,e):
        tipsWindow()

class passwordWindow(wx.Frame):
    def __init__(self, parent):
        super(passwordWindow, self).__init__(parent)
        self.Bind(wx.EVT_CLOSE, self.close)

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

    def password(self, logins):
        passwordBox = wx.PasswordEntryDialog(None, "Enter Key: " + str(logins) + " Attempts Remaining", "Key")
        if passwordBox.ShowModal() == wx.ID_OK:
            password = passwordBox.GetValue()
            return password
        elif passwordBox.ShowModal() == wx.ID_CANCEL:
            sys.exit()

    def close(self,e):
        self.Close()
        sys.exit()

class passwordSetupWindow(wx.Frame):
    def __init__(self, parent):
        super(passwordSetupWindow, self).__init__(parent)
        self.Bind(wx.EVT_CLOSE, self.close)

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

    def setup(self):
        passwordBox = wx.PasswordEntryDialog(None, "Create a key. Use a mix of uppercase letters (A,C,N), lowercase letters (v,f,d), numbers (4,5,2), and special characters (#,*,$)", "Enter Key")
        if passwordBox.ShowModal() == wx.ID_OK:
            password = passwordBox.GetValue()
            return password
        elif passwordBox.ShowModal() == wx.ID_CANCEL:
            sys.exit()

    def close(self,e):
        self.Close()

class databaseOpenWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Choose Database", size=(300,300))
        self.SetBackgroundColour((0,0,0))

        try:
            ico = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
            self.SetIcon(ico)
        except:
            pass

        col = wx.BoxSizer(wx.VERTICAL)
        col.AddStretchSpacer()
        open = wx.Button(self, wx.ID_ANY, label="Open")
        self.Bind(wx.EVT_BUTTON, self.getDBPath, open)
        col.Add(open,0,wx.CENTER,10)
        new = wx.Button(self, wx.ID_ANY, label="New Database")
        self.Bind(wx.EVT_BUTTON, self.NewDB, new)
        col.Add(new,0,wx.CENTER,10)
        col.AddStretchSpacer()
        self.SetSizer(col)
        self.Layout()
        self.Show()

    def getDBPath(self, event):
        wildcard = "Database (*.db)|*.db"
        dlg = wx.FileDialog(
            self, message="Choose Database To Open",
            defaultDir= os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            global session
            engine = create_engine('sqlite:///' + paths[0])
            Base.metadata.create_all(engine)
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            session = DBSession()
            dlg.Destroy()
            self.Destroy()
            mainGUI()

        elif dlg.ShowModal() == wx.ID_CANCEL:
            dlg.Destroy()



    def NewDB(self, event):
        dlg = wx.TextEntryDialog(None,message="New Database Name")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            global session
            engine = create_engine('sqlite:///' + name + ".db")
            Base.metadata.create_all(engine)
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            session = DBSession()
            dlg.Destroy()
            self.Destroy()
            mainGUI()

        elif dlg.ShowModal() == wx.ID_CANCEL:
            dlg.Destroy()

#########################################################
# Utility Functions

# Pad Data For Encryption
def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

# Encrypt
def encrypt(message, key, key_size=256):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

# Decrypt
def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

# GUI Initialization And Key Check
def mainGUI():
    while True:
        check = session.query(KeyCheck).first()
        if check == None:
            gui = passwordSetupWindow(None)
            password = gui.setup()
            setupPassword(password)
        else:
            break
    gui = passwordWindow(None)
    logins = 3
    password = gui.password(logins)
    while logins > 0:
        key = deriveKeyCheck(password)
        check = checkKey(key)
        if check == True:
            global encryptionKey
            logins = 0
            encryptionKey = deriveKey(password)
            keycheck = KeyCheck()
            keycheck.setkey(encryptionKey)
            #pdb.set_trace()
            if os.path.exists("Images/default/indBlank.bmp"):
                with open("Images/default/indBlank.bmp", "rb") as imageFile:
                    byte = imageFile.read()
                    enc = encrypt(byte, encryptionKey)
                    newImage = DefaultImages(image=enc)
                    session.add(newImage)
                    session.commit()
                imageFile.close()
            if os.path.exists("Images/default/vehicleBlank.bmp"):
                with open("Images/default/vehicleBlank.bmp", "rb") as imageFile:
                    byte = imageFile.read()
                    enc = encrypt(byte, encryptionKey)
                    newImage = DefaultImages(image=enc)
                    session.add(newImage)
                    session.commit()
                imageFile.close()
            window = mainWindow()
            window.Show()
            break
        else:
            if logins > 0:
                logins -= 1
                password=gui.password(logins)
            elif logins<=0:
                sys.exit()


# Key Generation
def deriveKey(password):
    if len(password) > 64:
        return password
    else:
        return hashlib.sha256(password.encode("utf-8")).digest()

# Derive New Check
def deriveKeyCheck(password):
    password = bytes(password, "utf-8")
    salt = bytes("OjZfXlP1urblsfBE8V8Y6B9eHK4rJ7gqmKuVRTnPYV7KEfQcrpIDUOXhL0MVF40u3NAB0LXmSg4fXKWLmy7n9QysZmzFGK5eUF\
    32zLrZJlqhHxe3ddD3NKUpDTZ95d1MztTKzBDeDLoO5e5s7FJFtkLtieUUBMtbWwM1yvNkZH8adapFH83Hh85fNzastQhUlrm21TWZ5qfFqN0tsoEf5\
    ax1a5Cd7yqu0mS09ZPmLVlGQBnbsZ5eHClQeK", "utf-8")
    hash = str(hashlib.pbkdf2_hmac('sha256', password, salt, 400000))
    return hash

# Setup New Password
def setupPassword(password):
    check = deriveKeyCheck(password)
    newHash = KeyCheck(hash = check)
    session.add(newHash)
    session.commit()

# Checks Key Validity
def checkKey(key):
    check = session.query(KeyCheck).one()
    hash = check.hash
    if key == hash:
        return True
    else:
        return False
#########################################################
# Initialize Application
sys.setrecursionlimit(2000)

tor = requests.session()
#3tor.proxies = {}
#tor.proxies['http'] = 'socks5h://localhost:9050'
#tor.proxies['https'] = 'socks5h://localhost:9050'

#py.offline.init_notebook_mode(connected=True)
app = wx.App()
database = databaseOpenWindow()
app.MainLoop()
#########################################################
