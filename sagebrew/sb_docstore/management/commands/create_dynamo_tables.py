from json import loads
from django.core.management.base import BaseCommand
from django.conf import settings

from boto.dynamodb2.fields import (HashKey, RangeKey, AllIndex)
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import STRING
from boto.dynamodb2.exceptions import JSONResponseError

from sb_docstore.utils import connect_to_dynamo, get_table_name


class Command(BaseCommand):
    args = 'None.'
    help = 'Creates the required DynamoDB tables.'

    def create_dynamo_tables(self):
        with open('%s/sb_docstore/management/commands'
                  '/dynamo_table.json' % settings.PROJECT_DIR,
                  'r') as data_file:
            data = loads(data_file.read())
            conn = connect_to_dynamo()
            reads = 1
            writes = 1

            if isinstance(conn, Exception):
                print "Unable to connect to dynamo table, potential error"
            for item in data:
                table_name = get_table_name(item['table_name'])
                '''
                # Don't think we want to automatically delete the tables every
                # deployment anymore. We probably want to be able to hit an
                # endpoint that triggers a rebuilding of the tables that we can
                # more closely monitor.
                try:
                    table = Table(table_name=table_name,
                                  connection=conn)
                    table.delete()
                    while (table.describe()['Table']['TableStatus'] ==
                            "DELETING"):
                        time.sleep(1)
                except JSONResponseError:
                    print 'The table %s does not exist' % table_name
                '''
                try:
                    if 'range_key' and 'local_index' in item.keys():
                        Table.create(table_name, schema=[
                            HashKey(item['hash_key'], data_type=STRING),
                            RangeKey(item['range_key']),
                        ], indexes=[
                            AllIndex(item['local_index_name'], parts=[
                                HashKey(item['hash_key']),
                                RangeKey(item['local_index'],
                                         data_type=item['type']),
                            ])
                        ], throughput={
                            'read': reads,
                            'write': writes
                        }, connection=conn)
                    elif 'range_key' in item.keys():
                        Table.create(table_name, schema=[
                            HashKey(item['hash_key'], data_type=STRING),
                            RangeKey(item['range_key']),
                        ], throughput={
                            'read': reads,
                            'write': writes
                        }, connection=conn)
                    else:
                        Table.create(table_name, schema=[
                            HashKey(item['hash_key'], data_type=STRING),
                        ], throughput={
                            'read': reads,
                            'write': writes
                        }, connection=conn)
                except JSONResponseError:
                    print 'Table %s already exists' % item['table_name']
        '''
        users = Table.create('users-full', schema=[
            HashKey('email', data_type=STRING),
            RangeKey('last_name', data_type=STRING),
        ],  throughput={
            'read': 5,
            'write': 15,
        },
        connection=conn)
        '''

    def handle(self, *args, **options):
        self.create_dynamo_tables()
        self.stdout.write('Created Dynamo Tables')
