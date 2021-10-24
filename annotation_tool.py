# imports
import os
import cv2
import sys
from argparse import ArgumentParser
import pickle
from msvcrt import getch


def main(p):
    for dirName, subDirList, fileList in os.walk(p.imageDir):
        process_dir(dirName, fileList)


def process_dir(dirName, fileList):
    '''
        -- fileList: list contain all the files in the directory
        -- dirName: directory name
    '''
    global imageList
    imageList = []

    for imageFile in fileList:
        if imageFile.endswith('.png') or imageFile.endswith('.jpeg') or imageFile.endswith('.jpg'):
            imageList.append(imageFile)

    start_process_dir(dirName, imageList) #function to start the main process


def start_process_dir(dirName, imageList):
    '''
        -- dirName :  directory name
        -- imageList :  list contain all the images names
    '''

    check_and_create_save_dir(p)#in case the dest folder not exist, we create it

    global image, num
    num = 0
    while num < len(imageList):

        if num == -len(imageList):  # fix the index to become circularity on the right side
            num = 0

        if num == len(imageList) - 1:  # fix the index to become circularity in the left side
            num = -1

        image = cv2.imread(os.path.join(dirName, imageList[num]))
        cv2.namedWindow(imageList[num])
        cv2.setMouseCallback(imageList[num], click_and_drag)  # Sets mouse handler for the specified window.
        wait_time = 1000

        while True:
            cv2.imshow(imageList[num], image)

            key = cv2.waitKeyEx(wait_time)

            if key == 2424832 or key == ord("l"):  # move to the left image - can also work with pressing 'l'
                cv2.destroyWindow(imageList[num])
                num -= 2
                break
            if key == 2555904 or key == ord("r"):  # move to the right image - can also work with pressing 'r'
                cv2.destroyWindow(imageList[num])
                break

            if key == ord("s"):  # pressing s for saving the coordinates
                save_coordinates(refPt) #save the coordinates on the face detection

            if key == ord("d"):  # delete the prev rectangles
                image = cv2.imread(os.path.join(dirName, imageList[num]))
                reset_coordinates(imageList[num])
                # cv2.setMouseCallback(imageList[num], click_and_drag)

            if key == ord("q"):
                save_coordinates(refPt)
                cv2.destroyAllWindows()  # close everything
                sys.exit()

        num += 1


def check_and_create_save_dir(p):

    saveCordinatesDir = p.saveDir #the directory to save the coordinates
    if not p.saveDir in os.listdir(os.getcwd()):
        os.makedirs(os.path.join(os.getcwd(), p.saveDir))

    if not saveCordinatesDir in os.listdir(os.getcwd()):
        os.makedirs(os.path.join(os.getcwd(), saveCordinatesDir))


# Listening for the mouse events
def click_and_drag(event, x, y, flags, param):
    '''
         --event: drawing param
         -- x,y: coordinates
         -- flags: binary
         -- param: additional argument
    '''
    global refPt, image
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]

    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:

        clone = image.copy()  # the use of clone here is to prevent spreading the rectangle all over
        cv2.rectangle(clone, refPt[0], (x, y), (0, 0, 255), 2)

        cv2.imshow(imageList[num], clone)

    elif event == cv2.EVENT_LBUTTONUP:

        refPt.append((x, y))
        cv2.rectangle(image, refPt[0], refPt[1], (255, 0, 0), 2)
        cv2.imshow(imageList[num], image)


def reset_coordinates(fileName):
    '''
         --fileName:file name
    '''
    pklName = fileName.split('.')[0] + '.pkl'  # pklName: pkl file name
    try:
        os.remove(os.path.join(p.saveDir, pklName))  # remove the coordinates file
    except FileNotFoundError:
        print("no rectangles specified")  # if there is no rectangles well print it


def save_coordinates(rect):
    '''
        -- rect :  coordinates we save to the pkl file
    '''
    saveDir = p.saveDir
    pklName ='results' + '.pkl'

    if os.path.exists(os.path.join(saveDir, pklName)):  # check if the file exists

        with open(os.path.join(saveDir, pklName), 'rb') as fp:
            coord = pickle.load(fp)
        coord += [rect]
        with open(os.path.join(saveDir, pklName), 'wb') as fp:
            pickle.dump(coord, fp)

    else:

        with open(os.path.join(saveDir, pklName), 'wb') as fp:  # start on new file
            pickle.dump([rect], fp)


if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument('--imageDir', type=str, required=True, help='Directory containing images')
    args.add_argument('--saveDir', type=str, required=True, help='Directory name to save images heads locations.')
    p = args.parse_args()
    main(p)
    cv2.destroyAllWindows()
