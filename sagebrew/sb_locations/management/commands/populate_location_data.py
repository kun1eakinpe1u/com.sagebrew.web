import os
import us
from json import loads, dumps

from neomodel import DoesNotExist, db, MultipleNodesReturned

from django.core.management.base import BaseCommand

from sb_locations.neo_models import Location
from sb_quests.neo_models import Position


class Command(BaseCommand):
    args = 'None.'

    def populate_location_data(self):
        try:
            usa = Location.nodes.get(name='United States of America')
        except (DoesNotExist, Location.DoesNotExist):
            usa = Location(name="United States of America").save()
        query = 'MATCH (a:Location {object_uuid: "%s"})-' \
                '[:POSITIONS_AVAILABLE]->' \
                '(p:Position) RETURN p.name' % usa.object_uuid
        res, _ = db.cypher_query(query)
        positions = [row[0] for row in res]
        if "President" not in positions:
            pres = Position(name="President").save()
            pres.location.connect(usa)
        for root, dirs, files in \
                os.walk('sb_locations/management/commands/states/'):
            if not dirs:
                _, state = root.split("states/")
                state_name = us.states.lookup(state).name
                with open(root + "/" + files[0]) as geo_data:
                    file_data = loads(geo_data.read())
                    try:
                        state = Location.nodes.get(name=state_name)
                    except (DoesNotExist, Location.DoesNotExist):
                        state = Location(name=state_name,
                                         geo_data=dumps(
                                             file_data['coordinates'])).save()
                    except MultipleNodesReturned:
                        continue
                    usa.encompasses.connect(state)
                    state.encompassed_by.connect(usa)
                    query = 'MATCH (a:Location {object_uuid: "%s"})-' \
                            '[:POSITIONS_AVAILABLE]->' \
                            '(p:Position) RETURN p.name' % state.object_uuid
                    res, _ = db.cypher_query(query)
                    positions = [row[0] for row in res]
                    if "Senator" not in positions:
                        senator = Position(name='Senator').save()
                        senator.location.connect(state)
        for root, dirs, files in \
                os.walk('sb_locations/management/commands/districts/'):
            try:
                if files[0] != '.DS_Store':
                    _, district_data = root.split('districts/')
                    state, district = district_data.split('-')
                    if not int(district):
                        district = 1
                    try:
                        state_node = Location.nodes.get(
                            name=us.states.lookup(state).name)
                    except MultipleNodesReturned:
                        continue
                    with open(root + "/shape.geojson") as geo_data:
                        file_data = loads(geo_data.read())
                        query = 'MATCH (l:Location {name:"%s"})-' \
                                '[:ENCOMPASSES]->(d:Location {name:"%s"}) ' \
                                'RETURN d' % \
                                (state_node.name, district)
                        res, _ = db.cypher_query(query)
                        if not res:
                            district = Location(
                                name=int(district),
                                geo_data=dumps(
                                    file_data['coordinates'])).save()
                            district.encompassed_by.connect(state_node)
                            usa.encompasses.connect(district)
                            state_node.encompasses.connect(district)
                            query = 'MATCH (a:Location {object_uuid: "%s"})-' \
                                    '[:POSITIONS_AVAILABLE]->' \
                                    '(p:Position) ' \
                                    'RETURN p.name' % district.object_uuid
                            res, _ = db.cypher_query(query)
                            positions = [row[0] for row in res]
                            if "House Representative" not in positions:
                                house_rep = Position(
                                    name="House Representative").save()
                                house_rep.location.connect(district)
            except IndexError:
                pass
        return True

    def handle(self, *args, **options):
        self.populate_location_data()
