from pydantic import BaseModel
import gspread
import pandas as pd
from datetime import datetime

CREDENTIAL_PATH="./google_sheet_creds.json"
SHEET_ID='1JHUOVxvL_UDA3tqxTiwWO095eOxppAWJi7PtDnxnGt8'


class ScoutingRecord(BaseModel):
    tstamp: str = datetime.now().isoformat()
    team_number: int = 0
    match_number: str = ''
    scouter_name: str = ''
    team_present: bool = False
    notes_speaker_auto: int = 0
    notes_amp_auto: int = 0
    speaker_subwoofer_completed_auto: int = 0
    speaker_subwoofer_attempted_auto: int = 0
    speaker_podium_completed_auto: int = 0
    speaker_podium_attempted_auto: int = 0
    speaker_medium_completed_auto: int = 0
    speaker_medium_attempted_auto: int = 0
    speaker_midfield_completed_auto: int = 0
    speaker_midfield_attempted_auto: int = 0
    alliance_coop: bool = False
    robot_disabled_time: int = 0
    robot_speed: float = 0.0
    notes_speaker_teleop: int = 0
    notes_amp_teleop: int = 0
    speaker_subwoofer_completed_teleop: int = 0
    speaker_subwoofer_attempted_teleop: int = 0
    speaker_podium_completed_teleop: int = 0
    speaker_podium_attempted_teleop: int = 0
    speaker_medium_completed_teleop: int = 0
    speaker_medium_attempted_teleop: int = 0
    speaker_midfield_completed_teleop: int = 0
    speaker_midfield_attempted_teleop: int = 0
    park: bool = False
    climb: bool = False
    high_note: bool = False
    trap: bool = False
    penalties: int = 0
    rps: int = 0
    mobility: bool = False
    fouls: int = 0
    defense_rating: int = 0
    defense_forced_penalties: int = 0
    notes: str = ''


    def calc_fields(self):
        self.notes_speaker_teleop = self.speaker_subwoofer_completed_teleop +\
                                    self.speaker_podium_completed_teleop +\
                                    self.speaker_medium_completed_teleop + self.speaker_midfield_completed_teleop
    def as_tuple(self):
        return list(self.model_dump().values())


    @staticmethod
    def header_columns():
        #this generates the fields in dot format
        return [ f.replace('_','.') for f in ScoutingRecord.__fields__.keys() ]


def connect_sheet():
    gs = gspread.service_account(CREDENTIAL_PATH)
    CHARLESTON_TAB = 0
    s = gs.open_by_key(SHEET_ID).get_worksheet(CHARLESTON_TAB)
    return s

def get_match_data():
    gs = connect_sheet()
    d = gs.get()

    columns_with_underscores = [ c.replace('.','_') for c in d[0]]
    print("Cols=",columns_with_underscores)
    rows = d[1:]
    list_of_record=[]
    for r in d[1:]:
        dr = dict(zip(columns_with_underscores,r))
        sr = ScoutingRecord(**dr)
        list_of_record.append(sr)

    #this incantation from SO https://stackoverflow.com/questions/61814887/how-to-convert-a-list-of-pydantic-basemodels-to-pandas-dataframe
    df = pd.DataFrame([r.model_dump() for r in list_of_record])
    df['tstamp'] = pd.to_datetime(df['tstamp'])
    return df


def write_header_if_needed(sheet):
    a1 = sheet.cell(1,1)

    if a1.value is None:
        print("Writing Header!",ScoutingRecord.header_columns())
        s = connect_sheet()
        s.append_row( ScoutingRecord.header_columns())

def write_scouting_row(rec:ScoutingRecord):
    rec.calc_fields()
    s = connect_sheet()
    write_header_if_needed(s)
    t = rec.as_tuple()
    print("Writing Record:",t)
    s.append_row(t)


