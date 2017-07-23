import os

from azure.storage.table import TableService, Entity

class AzureTable(object):
    def __init__(self, table_name, account_name, account_key):
        self._table_name = table_name
        self._table = TableService(account_name=account_name, account_key=account_key)
        self._table.create_table(table_name, fail_on_exist=False)

    def get_all_row_keys(self, partition_key):
        for entity in self._table.query_entities(self._table_name, filter="PartitionKey eq '%s'" % partition_key, select='RowKey'):
            yield entity.RowKey

    def get(self, partition_key, row_key):
        entity = self._table.get_entity(self._table_name, partition_key, row_key)
        if entity==None: return None
        return entity.data

    def set(self, partition_key, row_key, data):
        entity = Entity()
        entity.PartitionKey = partition_key
        entity.RowKey = row_key
        entity.data = data
        self._table.insert_or_replace_entity(self._table_name, entity)

    def delete(self, partition_key, row_key):
        self._table.delete_entity(self._table_name, partition_key, row_key)

if __name__=='__main__':
    table = AzureTable('Articles', os.environ['STORAGE_ACCOUNT_NAME'], os.environ['STORAGE_ACCOUNT_KEY'])
    table.set('test', 'test', 'I am Hari')
    print table.get('test', 'test')
    table.delete('test', 'test')

    