import uuid
from threading import Thread
import copy
import logging
import datetime
import time
import sys
import converter

from opcua.ua import NodeId, NodeIdType
from opcua import Client

sys.path.insert(0, "..")

try:
    from IPython import embed
except ImportError:
    import code


    def embed():
        myvars = globals()
        myvars.update(locals())
        shell = code.InteractiveConsole(myvars)
        shell.interact()

from opcua import ua, uamethod, Server


def has_duplicates(lst):
    if lst != False:
        mass_tag = []
        for i in range(len(lst)):
            mass_tag.append(lst[i]['tag'])
        x = set(mass_tag)
        for c in x:
            if (mass_tag.count(c) > 1):
                indices = [i for i, x in enumerate(mass_tag) if x == c]
                lst.pop(indices[0])
        return lst
    else:
        return False


# Разделение на число флоат и все остальное типа стринг
def float_or_str(value):
    try:
        return float(value)
    except:
        return value


#     Добавление значение в тэг
def adder_variable(index, values):
    try:
        timestamp = datetime.datetime.strptime(values['date'], '%d-%b-%Y %H:%M:%S')
        datavalue = ua.DataValue(variant=float_or_str(values['value']))
        datavalue.SourceTimestamp = timestamp
        if (values['Status'] == 'Bad'):
            datavalue.StatusCode = ua.StatusCode(ua.StatusCodes.Bad)
        index.set_value(datavalue)
    except KeyError:
        print('Пустой тег')


# Построение дерева тэгов
def create_tree(tags):
    Montags = []
    Montags.clear()
    for tags1 in tags:
        nodeID = NodeId(identifier=tags1['tag'], namespaceidx=idx, nodeidtype=NodeIdType.String)
        var = myobj.add_variable(nodeid=nodeID,
                                 bname=tags1['tag'],
                                 val=float_or_str(tags1['value']),
                                 varianttype=converter.get_ua_type(float_or_str(tags1['value']))
                                 )
        # print(var)
        Montags.append(var)
        adder_variable(var, tags1)
    return Montags


# def create_tree(tags):
#     Montags = []
#     Montags.clear()
#     for tags1 in tags:
#         if tags1['tag'].endswith('Comment'):
#             nodeID = NodeId(identifier=tags1['tag'], namespaceidx=idx, nodeidtype=NodeIdType.String)
#             var = myobj.add_variable(nodeid=nodeID,
#                                      bname=tags1['tag'],
#                                      val=tags1['value'],
#                                      varianttype=ua.VariantType.String)
#             Montags.append(var)
#             timestamp = datetime.datetime.strptime(tags1['date'], '%d-%b-%Y %H:%M:%S')
#             datavalue = ua.DataValue(variant=tags1['value'])
#             datavalue.SourceTimestamp = timestamp
#             if (tags1['Status'] == 'Bad'):
#                 datavalue.StatusCode = ua.StatusCode(ua.StatusCodes.Bad)
#             var.set_value(datavalue)
#         else:
#             nodeID = NodeId(identifier=tags1['tag'], namespaceidx=idx, nodeidtype=NodeIdType.String)
#             var = myobj.add_variable(nodeid=nodeID,
#                                      bname=tags1['tag'],
#                                      val=float(tags1['value']),
#                                      varianttype=ua.VariantType.Float)
#             Montags.append(var)
#             print('In the work..Float.')
#             timestamp = datetime.datetime.strptime(tags1['date'], '%d-%b-%Y %H:%M:%S')
#             datavalue = ua.DataValue(variant=float(tags1['value']))
#             datavalue.SourceTimestamp = timestamp
#             if (tags1['Status'] == 'Bad'):
#                 datavalue.StatusCode = ua.StatusCode(ua.StatusCodes.Bad)
#             var.set_value(datavalue)
#     return Montags

class VarUpdater(Thread):
    def __init__(self, var):
        Thread.__init__(self)
        self._stopev = False
        self.var = var

    def stop(self):
        self._stopev = True

    def run(self):
        flag = 0
        while not self._stopev:
            # Мигающий бит
            if flag != 1:
                flag = 1
                self.var.set_value(True)
            else:
                flag = 0
                self.var.set_value(False)
            # Чтение значений из файла и проверка на дубли, если находит дубли убирает
            tags = has_duplicates(converter.get_file(path))
            if tags != False:

                if 'myvar2' in locals():
                    if len(tags) != len_old_myvar2:
                        print("Произошло изменение в списке ")
                        server.delete_nodes(myvar2)

                        myvar2 = []
                        myvar2 = create_tree(tags)

                    else:
                        for i in range(len(tags)):
                            adder_variable(myvar2[i], tags[i])

                    len_old_myvar2 = len(tags)
                    print("Кол-во тегов: " + str(len_old_myvar2))
                else:
                    myvar2 = []
                    myvar2 = create_tree(tags)
                    len_old_myvar2 = len(tags)

            print('In the work...')
            time.sleep(15)


if __name__ == '__main__':
    config = converter.get_config()
    path = config['path']
    time_period = config['UPDATE_RATE']

    server = Server()

    server.set_endpoint(config['UA_HOST'])
    server.set_server_name(config['UA_SERVER_NAME'])
    # setup our own namespace, not really necessary but should as spec
    uri = config['UA_ROOT_NAMESPACE']
    idx = server.register_namespace(uri)
    myobj = server.nodes.objects.add_folder(idx, "DATA")

    date_time_str = '29-Sep-2021 12:27:43'
    timestamp = datetime.datetime.strptime(date_time_str, '%d-%b-%Y %H:%M:%S')
    datavalue = ua.DataValue(variant=True)
    datavalue.SourceTimestamp = timestamp
    nodeID = NodeId(identifier="Life_Server", namespaceidx=idx, nodeidtype=NodeIdType.String)

    # mysin = myobj.add_variable(idx,"Life_Server", False, ua.VariantType.Boolean)
    mysin = myobj.add_variable(nodeid=nodeID,
                               bname="Life_Server",
                               val=False,
                               varianttype=ua.VariantType.Boolean)
    # mysin = myobj.add_variable(idx, "Life_Server", 42)

    mysin.set_value(datavalue)

    # starting!
    server.start()
    vup = VarUpdater(mysin)  # just  a stupide class update a variable
    vup.start()
