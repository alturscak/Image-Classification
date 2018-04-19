import numpy as np
from os import listdir
from glob import glob
from time import time
import cv2
import matplotlib.pyplot as plt
from os.path import isfile
from os import getlogin

def dataSetGenerator(path,resize=True,resize_to=224,percentage=100):
    """
    Generate a image dataSet from a picture dataSets

    the picture dataSets must be in the same structure to generate also labels

    example of pictureFolder: http://weegee.vision.ucmerced.edu/datasets/landuse.html

    picture dataSets
      |
      |----------class-1
      |        .   |-------image-1
      |        .   |         .
      |        .   |         .
      |        .   |         .
      |        .   |-------image-n
      |        .
      |-------class-n

    :param str path: the path for picture dataSets folder
    :param bool resize: choose resize the pictures or not
    :param int resize_to: the new size of pictures
    :param int or float percentage: how many pictures you want to get from this pictureFolder
    :return:give as tuple of images, labels , classes
    :rtype: tuple[object[numpy.ndarray],object[numpy.ndarray],object[numpy.ndarray]]
        """
    try:
        start_time = time()
        classes = listdir(path)
        image_list = []
        labels = []
        for classe in classes:
            for filename in glob(path+'/'+classe+'/*'):
                if resize: image_list.append(cv2.resize(cv2.imread(filename, cv2.COLOR_BGR2RGB),(resize_to, resize_to)))
                else:image_list.append(cv2.imread(filename, cv2.COLOR_BGR2RGB))
                #if resize: image_list.append(cv2.cvtColor(cv2.resize(cv2.imread(filename),(resize_to, resize_to)), cv2.COLOR_BGR2RGB))
                #else:image_list.append((cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)))
                label = np.zeros(len(classes))
                label[classes.index(classe)] = 1
                labels.append(label)
        indice = np.random.permutation(len(image_list))[:int(len(image_list)*percentage/100)]
        print("\n --- dataSet generated in  %s seconds --- \n" % (np.round(time()-start_time)))
        return np.array([image_list[x] for x in indice]),np.array([labels[x] for x in indice]),np.array(classes)

    except IOError as e:
            print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,path))

def dataSetToNPY(path,dataSet_name,resize=True,resize_to=224,percentage=80):
    """
    Generate a image dataSet from a picture dataSets and save it in pny files for fast reading in teast and train

    the picture dataSets must be in the same structure to generate also labels

    example of pictureFolder: http://weegee.vision.ucmerced.edu/datasets/landuse.html

    picture dataSets
      |
      |----------class-1
      |        .   |-------image-1
      |        .   |         .
      |        .   |         .
      |        .   |         .
      |        .   |-------image-n
      |        .
      |-------class-n

    :param str path: the path for picture dataSets folder
    :param str dataSet_name: dataSets name for output file.npy
    :param bool resize: choose resize the pictures or not
    :param int resize_to: the new size of pictures
    :param int or float percentage: how many pictures you want to get from this pictureFolder for training
    :return: return dataset in npy files for fast Test and Train
    """
    try:
        data,labels,classes = dataSetGenerator(path,resize,resize_to,100)
        indice = np.random.permutation(len(data))
        indice80 = indice[:int(len(data)*percentage/100)]
        indice20 = indice[int(len(data)*percentage/100):]
        np.save(dataSet_name+'_dataTrain.npy',[data[x] for x in indice80])
        np.save(dataSet_name+'_labelsTrain.npy',[labels[x] for x in indice80])
        np.save(dataSet_name+'_dataTest.npy',[data[x] for x in indice20])
        np.save(dataSet_name+'_labelsTest.npy',[labels[x] for x in indice20])
        np.save(dataSet_name+'_classes.npy',classes)
    except IOError as e:
            print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,path))

def picShow(data,labels,classes,just=None,predict=None,autoClose = False):
    """
    show a pictures and which class belong in one figure

    :param list[int or float] data: list of picture that you need to show
    :param list[int or float] labels: list of labels for this picture
    :param list[str] classes: list of classes for this picture
    :param int or None just: how much picture you want to show
    :param list[str] or None predict: the list of probability of picture for each class
    :param bool autoClose: auto close of plot window after seconds
    :return: a figure contain this picture
    """
    fig =plt.figure()
    if just is None: just = len(data)
    for i in range(1, just+1):
        true_out = classes[labels[i-1].argmax()] # the true class of picture i
        sub = fig.add_subplot(np.ceil(np.sqrt(just)), np.rint(np.sqrt(just)), i)
        title = "true: "+true_out
        color = 'black'
        if predict is not None:
            classIndex = predict[i-1].argmax()
            predict_out = classes[classIndex] #the predicted class of picture i
            title += " predicted: "+ str(round(predict[i-1][classIndex]*100,2)) + " " + predict_out
            color = 'green' if predict_out == true_out else 'red'
        #sub.set_title(title,color=color, fontsize=7, fontweight='bold', y=-0.2-sub.get_ylim()[0])
        sub.set_title(title,color=color, fontsize=7, fontweight='bold')
        sub.axis('off')
        sub.imshow(data[i-1], interpolation='nearest', aspect="auto")
    if autoClose:
        plt.show(0)
        plt.pause(10)
        plt.close()
    else:
        plt.show()



def plotFiles(*path, xlabel='# epochs', ylabel='Error and Accu',autoClose = False):
    """
    Read data files and show it all in one graph figure

    :rtype: object
    :param list[str] or str path: the path for all the file who contain data to plot
    :param str xlabel: x axes label name
    :param str ylabel: y axes label name
    :param bool autoClose: auto close of plot window after seconds
    :return: Show data graph of files
    """
    for _ in path:
        if isfile(_):
            with open(_) as f:
                plt.plot([float(i.strip('\x00')) for i in f.read().split('\n')[:-1] if float(i.strip('\x00'))], label=f.name.split("/")[-1])
        else:
            print("I/O error({}): {} \nlike : {}".format(IOError.errno, IOError.strerror,_))

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend(loc='center left')
    if autoClose:
        plt.show(0)
        plt.pause(10)
        plt.close()
    else:
        plt.show()

def saveArray(data,npy_path):
    """
    save array to file.npy

    :param list[int] data: data array to save
    :param str npy_path: the path of npy file for saving
    """
    try:
        y = np.load(npy_path) if isfile(npy_path) else []
        np.save(npy_path,np.append(y,data))
        print("file saved", npy_path)
        return npy_path
    except IOError as e:
        print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,npy_path))

def txtToNpy(txt_path,npy_path):
    """
    convert file.txt to file.npy

    :param str txt_path: the path of text file to convert into npy
    :param str npy_path: the path of npy file for saving
    """
    try:
        with open(txt_path) as f:
            saveArray([float(i) for i in f.read().split('\n')[:-1]],npy_path)
    except IOError as e:
        print("I/O error({}): {} \nlike : {}".format(e.errno, e.strerror,txt_path))

def saveClasses(path,save_to,mode = 'w'):
    """
    read picture dataSets folder and save classes name in texty file

    picture dataSets
      |
      |----------class-1
      |        .   |-------image-1
      |        .   |         .
      |        .   |         .
      |        .   |         .
      |        .   |-------image-n
      |        .
      |-------class-n

    :param str path: the path for picture dataSets folder
    :param str save_to: path for the text file where you want save classes name
    :param str mode: mode writing in text file so => a = append and w = write
    :return None :
    """
    if mode != 'a': open(save_to, 'w')
    for classe in listdir(path):
        with open(save_to, 'a') as f:
                    f.write(classe+'\n')


def loadClasses(path):
    """
    load classes name from text file
    :param str path:the path for text file contain the classes name
    :return list[str]: retrun list of classes name
    """
    with open(path) as f:
        return f.read().split('\n')[:-1]

def getLabel(classe,classes):
    """
    Generate a label From lot of resources

     - path for text file contain the classes name
     - path for picture dataSets folder
     - list contain classes name
     - numpy array contain classes name

    :param str classe :the name of classe
    :param list[int] or list[str] or str or object[numpy.ndarray] classes: the path of text file or dataSet folder or list of integer or String
    :return list[int]: label in probability form [0,0,1,0] of shape (1,n)

    """
    if type(classes) is str:
        classes = loadClasses(classes) if isfile(classes) else listdir(classes)
    elif isinstance(classes,np.ndarray):
        classes =classes.tolist()
    label = np.zeros(len(classes))
    label[classes.index(classe)] = 1
    return [label]

def imread(path,resize=224):
    """
    read a picture

    :param str path :path for pictures or folder to read
    :param int resize: the new size of picture
    :return list[float]: list of picture of shape (n,height,width,channel)

    """
    if isfile(path):
        return [cv2.resize(cv2.imread(_, cv2.COLOR_BGR2RGB),(resize, resize)) for _ in [path]]
    else:
        return [cv2.resize(cv2.imread(path+"/"+_, cv2.COLOR_BGR2RGB),(resize, resize)) for _ in listdir(path)]

def append(data,to):
    """
    save list() to text File

    :param data: list() of Data to save
    :param to: text file Were you wnat to save Data
    """

    for _ in data:
        with open(to, 'a') as f:
            f.write(_)
