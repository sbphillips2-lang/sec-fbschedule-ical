import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import os
import glob

SEC_TEAMS = {
    "alabama": "333",
    "arkansas": "8",
    "auburn": "2",
    "florida": "57",
    "georgia": "61",
    "kentucky": "96",
    "lsu": "99",
    "mississippi-state": "344",
    "missouri": "142",
    "ole-miss": "145",
    "south-carolina": "2579",
    "tennessee": "2633",
    "texas-am": "245",
    "vanderbilt": "238",
}

BASE_URL = "https://www.espn.com/college-football/team/schedule/_/id/{}"

OUTPUT_DIR = "docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def scrape_team(team_name, team_id):
    url = BASE_URL.format(team_id)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    cal = Calendar()
    cal.add("prodid", f"-//{team_name} Football Schedule//EN")
    cal.add("version", "2.0")

    rows = soup.select("table tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        date_text = cols[0].get_text(" ", strip=True)
        opponent = cols[1].get_text(" ", strip=True)
        result_or_time = cols[2].get_text(" ", strip=True)

        if "TBD" in result_or_time or result_or_time == "":
            continue

        try:
            dt = datetime.strptime(date_text + " 2025", "%a, %b %d %Y")
        except:
            continue

        event = Event()
        event.add("summary", f"{team_name.title()} vs {opponent}")
        event.add("dtstart", pytz.timezone("US/Central").localize(dt))
        event.add("dtend", pytz.timezone("US/Central").localize(dt))
        event.add("dtstamp", datetime.now(pytz.UTC))
        event["uid"] = f"{team_name}-{dt.isoformat()}@sec"

        cal.add_component(event)

    outfile = os.path.join(OUTPUT_DIR, f"{team_name}.ics")
    with open(outfile, "wb") as f:
        f.write(cal.to_ical())

    print(f"✅ Wrote {outfile}")

def merge_calendars():
    master = Calendar()
    master.add("prodid", "-//SEC Master Calendar//EN")
    master.add("version", "2.0")

    seen = set()
    for file in glob.glob(f"{OUTPUT_DIR}/*.ics"):
        with open(file, "rb") as f:
            cal = Calendar.from_ical(f.read())
            for component in cal.walk():
                if component.name == "VEVENT":
                    uid = str(component.get("uid"))
                    if uid not in seen:
                        master.add_component(component)
                        seen.add(uid)

    outfile = os.path.join(OUTPUT_DIR, "sec_master.ics")
    with open(outfile, "wb") as f:
        f.write(master.to_ical())

    print(f"✅ Wrote {outfile}")

if __name__ == "__main__":
    for team, tid in SEC_TEAMS.items():
        scrape_team(team, tid)
    merge_calendars()
