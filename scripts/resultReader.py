'''
Created on Dec 3, 2013

@author: nitinkp
'''
import pickle
import original
import algorithm

'''
4.  "no prediction" cases (assumed to be 0 in your experiments?).
you can choose to explicitly discuss it, and your result can show a big improvement in the prediction rate
(percentage of predicted movies).
acknowledging the existence of "no prediction" cases
reporting the MAE for predicted cases and the improvement of prediction rate.
still keep the overall MAE for the purpose of comparing with other papers.
'''
if __name__ == '__main__':
    cid='one'
    dumpname = "../rating_details/" + cid +"/orgdetails_" + cid
    #dumpname = "../rating_details/" + cid +"/algodetails"
    
    
    orgdetails = pickle.load(open(dumpname, "rb"))
    oitemsim = pickle.load(open( '../pickle/oitemsim.pickle','rb'))
    itemsim = pickle.load(open( '../pickle/one/oitemsim_0.pickle','rb'))
                           
    unable = 0
    predict = 0
    for user in orgdetails:
        userdict = orgdetails[user]
        #print userdict
        for item in userdict:
            if (userdict[item] == 0.0):
                unable += 1
            else:
                predict +=1
    
    print 'Unable %d'%(unable)
    print 'Predict %d'%(predict)
#     print oitemsim['1']
#     print itemsim['1']
#     
#     original_prefs = original.load()
#     new = algorithm.calculateSimilarItems(original_prefs, n=150)
#     print new['1']