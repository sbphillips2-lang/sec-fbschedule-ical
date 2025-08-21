import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

SEC_TEAMS = {
    "alabama": 333,
    "arkansas": 8,
    "auburn": 2,
    "florida": 57,
    "georgia": 61,
    "kentucky": 96,
    "lsu": 99,
    "mississippi-state": 344,
    "missouri": 142,
    "ole-miss": 145,
    "oklahoma": 201,
    "south-carolina": 2579,
    "tennessee": 2633,
    "texas": 251,
    "texas-am": 245,
    "vanderbilt": 238
}

BASE_URL = "https://www.espn.com/college-football/team/schedule/_/id/{id}"


def fetch_schedule(team_name, espn_id):
    url = BASE_URL.format(id=espn_id)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    games = []
    rows = soup.select("table tbody tr")
    for row in rows:
        cols = row.find_all("td")
        if not cols or "date" in cols[0].get("class", []):
            continue

        date_text = cols[0].get_text(" ", strip=True)
        opponent_text = cols[1].get_text(" ", strip=True)
        result_or_time = cols[2].get_text(" ", strip=True)
        tv = cols[3].get_text(" ", strip=True) if len(cols) > 3 else "TBA"

        try:
            dt = datetime.strptime(date_text, "%a, %b %d")
            dt = dt.replace(year=datetime.now().year)
        except:
            continue

        if ":" in result_or_time:
            try:
                dt_local = datetime.strptime(date_text + " " + result_or_time, "%a, %b %d %I:%M %p")
                dt_local = dt_local.replace(year=datetime.now().year)
                dt_utc = dt_local + timedelta(hours=5)  # CT -> UTC approx
                dtend = dt_utc + timedelta(hours=3)
                dtstart_str = dt_utc.strftime("%Y%m%dT%H%M%SZ")
                dtend_str = dtend.strftime("%Y%m%dT%H%M%SZ")
            except:
                dtstart_str = dt.strftime("%Y%m%d")
                dtend_str = (dt + timedelta(days=1)).strftime("%Y%m%d")
        else:
            dtstart_str = dt.strftime("%Y%m%d")
            dtend_str = (dt + timedelta(days=1)).strftime("%Y%m%d")

        games.append({
            "team": team_name,
            "opponent": opponent_text,
            "start": dtstart_str,
            "end": dtend_str,
            "tv": tv
        })
    return games


def make_ics(team_name, games):
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//SEC//{team_name}//EN"]
    seen = set()
    
    for g in games:
        # Deduplicate by date+opponent+team
        key = (g["start"], g["end"], tuple(sorted([team_name, g["opponent"]])))
        if key in seen:
            continue
        seen.add(key)

        uid = f"{team_name}-{g['start']}@sec.com"
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        ics.append("BEGIN:VEVENT")
        ics.append(f"UID:{uid}")
        ics.append(f"DTSTAMP:{dtstamp}")
        ics.append(f"DTSTART:{g['start']}")
        ics.append(f"DTEND:{g['end']}")
        ics.append(f"SUMMARY:{team_name.title()} vs {g['opponent']}")
        ics.append(f"DESCRIPTION:TV: {g['tv']}")
        ics.append("END:VEVENT")
    
    ics.append("END:VCALENDAR")
    return "\n".join(ics)


def main():
    os.makedirs("docs", exist_ok=True)
    all_games = []

    for team, eid in SEC_TEAMS.items():
        games = fetch_schedule(team, eid)
        all_games.extend(games)
        ics = make_ics(team, games)
        with open(f"docs/{team}.ics", "w") as f:
            f.write(ics)

if __name__ == "__main__":
    main()


import glob
from icalendar import Calendar

def merge_calendars(input_files, output_file):
    master = Calendar()
    master.add("prodid", "-//SEC Master Calendar//EN")
    master.add("version", "2.0")

    seen = set()
    for file in input_files:
        with open(file, "rb") as f:
            cal = Calendar.from_ical(f.read())
            for component in cal.walk():
                if component.name == "VEVENT":
                    uid = str(component.get("uid"))
                    if uid not in seen:
                        master.add_component(component)
                        seen.add(uid)

    with open(output_file, "wb") as f:
        f.write(master.to_ical())

# Merge all team calendars into sec_master.ics
ics_files = glob.glob("docs/*.ics")
merge_calendars(ics_files, "docs/sec_master.ics")
