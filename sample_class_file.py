class Node:
    def __init__(self, conn_id, conn_obj):
        self.conn_id = conn_id
        self.conn_obj = conn_obj

    def get_conn_id(self):
        return self.conn_id

node_obj = Node(5,5)
print(node_obj.conn_id)
