#Update active loads
def updateActiveLoads(acceptedLoadDict, activeLoadDict, now):

    #For each token in the accepted load request dictionary
    for token in acceptedLoadDict:

        #If accepted load request release time is now or later
        if( acceptedLoadDict.get(token).releaseTime >= now
            and acceptedLoadDict.get(token).deadline < now):

            #Flag load as active
            activeLoadDict.update({token:1})
        
        else:

            #Update its key
            activeLoadDict.update({token:0})