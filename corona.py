import json
import urllib.request as ur
from datetime import datetime


class LocationData:
    def __init__(self, world=False, *args, **kwargs):
        if world:
            self.countries = {}
            self.last_update_raw = 0
            self.last_update = ""
            self.confirmed_cases = 0
            self.deaths = 0
            self.recovered = 0
            self.coords = [0, 0]
            self.google_location_link = ""
        else:
            self.last_update_raw = kwargs["Last_Update"]
            self.last_update = datetime.utcfromtimestamp(self.last_update_raw / 1000)
            self.confirmed_cases = kwargs["Confirmed"]
            self.deaths = kwargs["Deaths"]
            self.recovered = kwargs["Recovered"]
            self.coords = [kwargs["Lat"], kwargs["Long_"]]
            self.google_location_link = "https://www.google.com/maps/place/{},{}".format(self.coords[0], self.coords[1])

    def __repr__(self):
        return "#################################################\n" \
               "-------- Region info --------\n" + \
               self.format_location_info() + \
               "-------- Raw numbers --------\n" + \
               self.format_numbers() + \
               "----------- Stats -----------\n" + \
               self.format_resolved() + \
               "#################################################"

    def format_location_info(self):
        raise NotImplementedError

    def format_numbers(self):
        return "Confirmed cases: {}\n" \
               "Deaths: {} \t\t-> [{}%]\n" \
               "Recovered: {} \t-> [{}%]\n" \
               "Unresolved: {} \t-> [{}%]\n".format(self.confirmed_cases, self.deaths, self.get_death_ratio(),
                                                  self.recovered, self.get_recover_ratio(), self.get_unresolved(),
                                                  self.get_unresolved_ratio())

    def format_resolved(self):
        return "Death percentage (resolved cases): {}%\n" \
               "Recovery rate (resolved cases): {}%\n".format(self.get_death_ratio_resolved(),
                                                            self.get_recovery_rate_resolved())

    def get_death_ratio(self):
        return round(self.deaths / self.confirmed_cases * 100, 2)

    def get_recover_ratio(self):
        return round(self.recovered / self.confirmed_cases * 100, 2)

    def get_unresolved(self):
        return self.confirmed_cases - (self.deaths + self.recovered)

    def get_unresolved_ratio(self):
        return round(self.get_unresolved() / self.confirmed_cases * 100, 2)

    def get_death_ratio_resolved(self):
        if self.deaths + self.recovered != 0:
            return round(self.deaths / (self.deaths + self.recovered) * 100, 2)
        else:
            return "NaN"

    def get_recovery_rate_resolved(self):
        if self.deaths + self.recovered != 0:
            return round(self.recovered / (self.deaths + self.recovered) * 100, 2)
        else:
            return "NaN"


class Province(LocationData):
    def __init__(self, *args, **kwargs):
        super(Province, self).__init__(*args, **kwargs)
        self.name = kwargs["Province_State"]

    def format_location_info(self):
        return "Province"


class Country(LocationData):
    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        super(Country, self).__init__(*args, **kwargs)
        self.provinces = {}
        self.name = kwargs["Country_Region"]
        if kwargs["Province_State"] is not None:
            self.provinces[kwargs["Province_State"]] = Province(**kwargs)

    def add_province(self, *args, **kwargs):
        self.provinces[kwargs["Province_State"]] = Province(**kwargs)
        if self.last_update_raw < kwargs["Last_Update"]:
            self.last_update_raw = kwargs["Last_Update"]
            self.last_update = datetime.utcfromtimestamp(self.last_update_raw / 1000)
        if self.confirmed_cases < kwargs["Confirmed"]:
            self.coords = [kwargs["Lat"], kwargs["Long_"]]
            self.google_location_link = "https://www.google.com/maps/place/{},{}".format(self.coords[0],
                                                                                         self.coords[1])
        self.confirmed_cases += kwargs["Confirmed"]
        self.deaths += kwargs["Deaths"]
        self.recovered += kwargs["Recovered"]

    def format_location_info(self):
        """

        :return:
        """
        return "Info for region: {}\nIncludes: {}\n" \
               "Estimated largest centre: {}\nLast update: {}\n".format(self.name, self.provinces.keys(), self.google_location_link, self.last_update)


class World(LocationData):
    def __init__(self, *args, **kwargs):
        super(World, self).__init__(*args, *kwargs)

        for country in args:
            location_details = country["attributes"]
            if location_details["Country_Region"].lower() in self.countries:
                self.countries[location_details["Country_Region"].lower()].add_province(**location_details)
            else:
                self.countries[location_details["Country_Region"].lower()] = Country(**location_details)

            if self.last_update_raw < location_details["Last_Update"]:
                self.last_update_raw = location_details["Last_Update"]
                self.last_update = datetime.utcfromtimestamp(self.last_update_raw / 1000)
            if self.confirmed_cases < location_details["Confirmed"]:
                self.coords = [location_details["Lat"], location_details["Long_"]]
                self.google_location_link = "https://www.google.com/maps/place/{},{}".format(self.coords[0],
                                                                                             self.coords[1])
            self.confirmed_cases += location_details["Confirmed"]
            self.deaths += location_details["Deaths"]
            self.recovered += location_details["Recovered"]

    def print_country(self, country):
        print(self.countries[country])

    def format_location_info(self):
        return "Info for region: {}\nIncludes: {}\n" \
               "Estimated largest centre: {}\nLast update: {}\n".format("World", self.countries.keys(),
                                                                self.google_location_link, self.last_update)


def main():

    user_agent = "Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv: 73.0) Gecko / 20100101 Firefox / 73.0"
    headers = {"User-Agent": user_agent}
    url = "https://coronavirus-6728.gserveri.workers.dev/"

    req = ur.Request(url=url, headers=headers)
    html = ur.urlopen(req)

    data = json.loads(html.read().decode())
    world = World(world=True, *data)
    world.print_country("croatia")
    print(world)


if __name__ == "__main__":
    main()