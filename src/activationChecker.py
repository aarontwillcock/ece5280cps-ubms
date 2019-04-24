#Update active loads
def updateActiveLoads(acceptedLoadDict, activeLoadDict, now):

    #For each token in the accepted load request dictionary
    for token in acceptedLoadDict:

        #If accepted load request release time is now or earlier and we haven't missed deadline
        if( acceptedLoadDict.get(token).releaseTime <= now
            and now < acceptedLoadDict.get(token).deadline):

            #Flag load as active
            activeLoadDict.update({token:1})
        
        else:

            #Update its key
            activeLoadDict.update({token:0})

    return acceptedLoadDict, activeLoadDict