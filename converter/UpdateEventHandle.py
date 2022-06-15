from converter import get_ua_type


class UpdateEventHandler:

    def set_lists(self, ualist, dalist):
        self.ualist=ualist
        self.dalist=dalist

    def OnDataChange(self, TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps):
        i = 0
        # print(TransactionID, NumItems, ClientHandles, ItemValues, Qualities, TimeStamps)
        while (i < NumItems):
            handle = ClientHandles[i]
            value = ItemValues[i]
            quality = Qualities[i]
            time = TimeStamps[i]

            self.ualist[self.dalist[handle]].set_value(value, get_ua_type(value))
            # print('is worked...')
            i = i + 1
