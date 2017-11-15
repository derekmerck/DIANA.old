"""
guid-mint

Hashes an alphanumeric guid from a given string value
Given a guid, gender (M/F/U), and name lists, returns a reproducible pseudonym
Given a dob (%Y-%m-%d), returns a reproducible pseudodob within 6 months of the original dob

If age is input, the dob is assumed to be (now - age*3655.25 days)
"""

import logging
from hashlib import sha256
from base64 import b32encode
import re
import random
from datetime import datetime, timedelta

__version__ = "0.9.0"

MAX_DATE_OFFSET = int(365/2)   # generated pseudodob is within 6 months
DEFAULT_NAMEBANK = "US_CENSUS"
PREFIX_LENGTH = 8  # 8 = 64bits, -1 = entire value

class NameBank (object):
    # NameBanks should contain gender specific surnames
    # and a single list of family names

    def __init__(self, source=DEFAULT_NAMEBANK):
        super(NameBank, self).__init__()
        self.mnames = []
        self.fnames = []
        self.lnames = []

        if source == "US_CENSUS":
            self.set_from_census()

    def set_from_census(self):

        # Should weight these as well to match census distribution...

        with open("names/dist.male.first.txt") as f:
            lines = f.readlines()
            for line in lines:
                words = line.split(" ")
                self.mnames.append(words[0])

        with open("names/dist.female.first.txt") as f:
            lines = f.readlines()
            for line in lines:
                words = line.split(" ")
                self.fnames.append(words[0])

        with open("names/dist.all.last.txt") as f:
            lines = f.readlines()
            for line in lines:
                words = line.split(" ")
                self.lnames.append(words[0])

class GUIDMint(object):

    def __init__(self, name_source="US_CENSUS", name_format="DICOM"):
        super(GUIDMint, self).__init__()
        self.name_bank = NameBank(name_source)
        self.name_format = name_format
        self.__version__ = __version__

    def mint_guid(self, value):

        candidate = b32encode(sha256(value.encode('utf-8')).digest())
        while not re.match(b"^[A-Z]{3}", candidate):
            candidate = b32encode(sha256(candidate).digest())

        candidate = candidate[:PREFIX_LENGTH].decode().strip("=")
        return candidate

    def pseudonym(self, guid, gender):

        if self.name_format == "DICOM":
            i_fam = 0
            i_sur = 1
            i_mid = 2
        else:
            i_sur = 0
            i_mid = 1
            i_fam = 2

        fam_names = [x for x in self.name_bank.lnames if x.startswith(guid[i_fam])]

        if gender == "M":
            sur_names = self.name_bank.mnames
        elif gender== "F":
            sur_names = self.name_bank.fnames
        else:
            sur_names = self.name_bank.mnames+self.name_bank.fnames

        sur_names = [x for x in sur_names if x.startswith(guid[i_sur])]

        random.seed(guid)
        fam_name = random.choice(fam_names)
        sur_name = random.choice(sur_names)

        middle = guid[i_mid]

        if self.name_format == "DICOM":
            name = "^".join([fam_name, sur_name, middle])
        else:
            name = " ".join([sur_name, middle, fam_name])

        return name

    def pseudo_dob(self, guid, dob):

        d = datetime.strptime(dob, "%Y-%m-%d")
        random.seed(guid)
        r = random.randint(-MAX_DATE_OFFSET,MAX_DATE_OFFSET)
        rd = timedelta(days=r)

        return str((d+rd).date())


    def pseudo_identity(self, name, gender="U", dob=None, age=None):

        if not dob and age:
            ddob = datetime.now()-timedelta(days=age*365.25)
            dob = str(ddob.date())

        value = "|".join([name, dob, gender])

        g = self.mint_guid(value)
        n = self.pseudonym(g, gender)
        d = self.pseudo_dob(g, dob)

        logging.debug("guid:      {0}".format(g))
        logging.debug("pseudonym: {0}".format(n))
        logging.debug("pseudodob: {0}".format(d))

        return g, n, d


if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)

    mint = GUIDMint()

    name = "MERCK^DEREK^L"
    gender = "M"
    dob = "1971-06-06"

    mint.pseudo_identity(name, gender, dob=dob)

    name = "MERCK^LISA^H"
    gender = "F"
    dob = "1973-01-01"

    mint.pseudo_identity(name, gender, dob=dob)

    name = "BOOSTSU001"
    age = 65

    mint.pseudo_identity(name, age=age)
