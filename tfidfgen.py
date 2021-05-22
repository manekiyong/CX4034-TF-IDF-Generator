import pandas as pd
import numpy as np

def tfCalc(col, idf, tfnotation):
    # col is not processed if tfnotation == 'n'
    if tfnotation == 'l': # Log
        col = col.apply(lambda x: 1+np.log10(float(x)) if x!=0 else 1)
#        col = col.apply(lambda x: np.log10(1+float(x)))
    elif tfnotation =='a': # Augmented 
        temp = col.apply(lambda x:(0.5+(0.5*x)/max(col)))
        col=temp
    col = col.multiply(idf)
    return col

def idfCalc(df):
    N = len(df.columns)-1
    tempdf = pd.DataFrame(columns=['idf'])
    docfreq = (df != 0).astype(int).sum(axis=1)-1
    count=0
    for i in docfreq:
        tempdf.at[count]=np.log10(N/i)
        count+=1
    return tempdf


def cosNormCalc(tfcol):
    tempsum = 0
    for i in tfcol:
        tempsum = tempsum+i*i
    return 1/np.sqrt(tempsum)

def EucDistCalc(col1, col2):
    if(len(col1)!=len(col2)): 
        print("ERROR")
        return
    sumval = 0
    for i in range(len(col1)):
        sumval=sumval+np.square(col1[i]-col2[i])
    return np.sqrt(sumval)

def cosSimCalc(col1, col2):
    if(len(col1)!=len(col2)): 
        print("ERROR")
        return
    sumval = 0
    for i in range(len(col1)):
        sumval=sumval+(col1[i]*col2[i])
    return sumval

if __name__ == "__main__":
    validchar1 = ['n','l','a']
    validchar2 = ['n','t']
    validchar3 = ['n','c']

    SMART=input("Input SMART notation in the format of ddd.qqq (lower case): ")
    while not SMART[0] in validchar1 or not SMART[4] in validchar1 or not SMART[1] in validchar2 or not SMART[5] in validchar2 or not SMART[2] in validchar3 or not SMART[6] in validchar3:
        SMART=input("INVALID! Input SMART notation in the format of ddd.qqq (lower case): ")
    query=input("Input Query Phrase: ")

    df = pd.read_excel('tfidf-input.xlsx')
    qlist = query.split(" ")

    #Calculate idf
    idfd=pd.DataFrame()
    idfq=pd.DataFrame()
    defaultVal = np.zeros(len(df))
    # Create default idf of all values 1 (Natural)
    idfd['idf']=defaultVal+1
    idfq['idf']=defaultVal+1
    if SMART[1]=='t':
        idfd=idfCalc(df)
    if SMART[-2]=='t':
        idfq=idfCalc(df)

    #Calculate Term's score
    res=pd.DataFrame()
    for col in df:
        if col=='term' or col=='query':
            continue
        res[(col+SMART[0:2])]=tfCalc(df[col],idfd['idf'],SMART[0])
        if SMART[2]=='c':
            res[("norm"+col)]=cosNormCalc(res[(col+SMART[0:2])])
        else:
            res[("norm"+col)]=1
        res[(col+SMART[0:3])]= res[(col+SMART[0:2])].multiply(res[("norm"+col)])


    #Calculating Query Score
    qdf = pd.DataFrame()
    qdf['term']= df['term']
    qdf['tf']=0
    for i in qlist:
        if i not in df['term'].values:
            print("WARNING:", i, "is not found in dictionary")
    print("")
    for i in qlist:
        for index, j in qdf.iterrows():
            if i==j['term']:
                qdf['tf'].at[index]+=1
    qres=pd.DataFrame()
    qres[('query'+SMART[4:6])]=tfCalc(qdf['tf'],idfq['idf'],SMART[5])
    if SMART[6]=='c':
        qres[("querynorm")]=cosNormCalc(qres[('query'+SMART[4:6])])
    else:
        qres[("querynorm")]=1
    qres[("query"+SMART[4:])]=qres[('query'+SMART[4:6])].multiply(qres[("querynorm")])
            
    #Output Cosine Similarity & Euclidean Distance
    for colX in res.columns:
        if(colX[-3:]==SMART[0:3]):
            print("Euclidean Distance of", colX, "& query"+SMART[4:],":", EucDistCalc(res[colX], qres[qres.columns[2]]))
            #If vector isn't length normalised, we need to do normalisation first. Otherwise, it can be a simple dot product. 
            tempdf1 = res[colX]
            tempdf2 = qres[qres.columns[2]]
            if(SMART[2]!='c'):
                tempdf1 = tempdf1.multiply(cosNormCalc(tempdf1))
            if(SMART[6]!='c'):
                tempdf2 = tempdf2.multiply(cosNormCalc(tempdf2))
            print("Cosine Similarity of", colX, "& query"+SMART[4:],":", cosSimCalc(tempdf1, tempdf2))
            print("")
    fres = pd.concat([res, qres],  axis=1)
    fres['term']=df['term']
    fres.to_excel('tfidf-results.xlsx')
    print("Intermediate values stored in tfidf-results.xlsx")