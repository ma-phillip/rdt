from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    lastAcked = 0
    lastSent = 0
    sentData = []
    receivedData = []
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        self.lastAcked = 0
        self.lastSent = 0
        self.sentData = []
        self.receivedData = []
        # Add items as needed

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self,data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...

        received_data_str = ""
        for segment in self.receivedData:
            received_data_str += segment.payload  # Access the payload attribute directly

        print('Received Data: ', received_data_str)

        # ############################################################################################################ #
        return received_data_str

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        segmentSend = Segment()

        unacked_received_packets = self.receivedData[self.lastAcked + 1:]
        print("Length of unacknowledged received packets list: ", len(unacked_received_packets))

        # ############################################################################################################ #
        while self.lastSent - self.lastAcked < self.FLOW_CONTROL_WIN_SIZE and self.lastSent < len(
                self.dataToSend) / self.DATA_LENGTH:
            start = self.lastSent * self.DATA_LENGTH
            end = start + self.DATA_LENGTH
            data = self.dataToSend[start:end]
            seqnum = str(self.lastSent)
            segmentSend = Segment()
            segmentSend.setData(seqnum, data)
            print("Sending segment: ", segmentSend.to_string())
            self.sendChannel.send(segmentSend)
            self.lastSent += 1
            self.sentData.append(segmentSend)
            # If there's no more data to send, don't try to create a new segment.
        unacked_sent_packets = self.sentData[self.lastAcked + 1:]
        print("Length of unacknowledged sent packets list: ", len(unacked_sent_packets))

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        segmentAck = Segment()                  # Segment acknowledging packet(s) received
        listIncomingSegments = self.receiveChannel.receive()
        for segment in listIncomingSegments:
            if segment.acknum != -1 and int(segment.acknum) > self.lastAcked:
                self.lastAcked = int(segment.acknum)
            elif segment.acknum == -1 and int(segment.seqnum) == len(self.receivedData):
                self.receivedData.append(segment)
                acknum = str(len(self.receivedData))
                segmentAck = Segment()
                segmentAck.setAck(acknum)
                print("Sending ack: ", segmentAck.to_string())
                self.sendChannel.send(segmentAck)



        # ############################################################################################################ #
        # How do you respond to what you have received?
        # How can you tell data segments apart from ack segemnts?
        print('processReceive(): Complete this...')


