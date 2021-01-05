import os 
import sys
import numpy as np
import pyautogui
import cv2
import time
import imutils

class TFTBot:
    scale = None
    imagePath = None

    ## Used to get scale of client
    def __init__(self, imagePath):
        if(imagePath[-1] != '/'):
            self.imagePath = imagePath + '/'
        else:
            self.imagePath = imagePath

        img_init = self.imagePath + 'find_match.png'

        ## This screenshot of one monitor only
        screenshot = pyautogui.screenshot()
        ssGrey = cv2.cvtColor(np.array(screenshot),cv2.COLOR_BGR2GRAY)

        template = cv2.imread(img_init,0)

        best_scale = None
        best_max_val = -1

        for scale in np.linspace(0.3, 1.0, 50)[::-1]:
            resized = imutils.resize(template, width = int(template.shape[1] * scale))
            res = cv2.matchTemplate(ssGrey,resized,cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            print(f"Matching value to image is: {max_val}")
            if(max_val > best_max_val):
                best_max_val = max_val
                best_scale = scale

        if(best_max_val >= 0.85):
            print(f"Best Scale value: {best_scale} with best image accuracy of: {best_max_val}")
            self.scale = best_scale
        else:
            raise Exception("Could NOT find image scaling for client, unable to continue.") 

    def runner(self, iterations = 1):
        imageArray = ['find_match.png', 'accept.png', 'settings.png', 'surrender_p1.png', 'surrender_p2.png', 'ok.png', 'play_again.png']
        gameStartImage = self.imagePath + 'start.png'
        playAgainImage = self.imagePath + 'play_again.png'

        for i in range(iterations):
            print(f"Iteration: {i+1} / {iterations}")
            
            for image in imageArray:
                imageFile = self.imagePath + image
                time.sleep(0.500)
                if(image == 'accept.png'):
                    acceptLocation = self.findImageLoop(imageFile,sleepTime=8,accuracy=0.85)
                    self.clickImage(acceptLocation[0],acceptLocation[1])
                    print("Waiting for the game to start")

                    location = self.findImage(gameStartImage)
                    while(location[0] == -1):
                        acceptLocation = self.findImage(imageFile)
                        self.clickImage(acceptLocation[0],acceptLocation[1],duration=0)
                        time.sleep(8)
                        location = self.findImage(gameStartImage)
                elif(image == 'settings.png'):
                    print("The game has started, sleeping for 10 minutes...")
                    for j in range(10):
                        print(f"Sleeping for {j+1} out of 10 minutes...", end='\r')
                        time.sleep(60)
                    print("")
                    time.sleep(5) # Extra 5 seconds just in case
                    location = self.findImageLoop(imageFile,sleepTime=3,accuracy=0.85)
                elif(image == 'ok.png'):
                    playAgainLocation = self.findImage(playAgainImage)
                    while(playAgainLocation[0] == -1):
                        location = self.findImage(imageFile)
                        self.clickImage(location[0],location[1])
                        time.sleep(5)
                        playAgainLocation = self.findImage(playAgainImage)
                else:  
                    location = self.findImageLoop(imageFile,sleepTime=15,accuracy=0.85)

                exit()
                self.clickImage(location[0],location[1])

    def clickImage(self, x, y, duration = 0.5):
        if(x != -1 and y != -1):
            # print(f"Moving mouse to x: {x}, y: {y}")
            pyautogui.moveTo(x,y,duration)
            # pyautogui.click(button='left') # This doesn't click in league, it maybe too fast
            pyautogui.mouseDown()
            pyautogui.mouseUp()

    def findImage(self, imagePath, accuracy = 0.85):
        # start = time.time()

        ## This screenshot of one monitor only
        screenshot = pyautogui.screenshot()
        ssGrey = cv2.cvtColor(np.array(screenshot),cv2.COLOR_BGR2GRAY)

        template = cv2.imread(imagePath,0)
        resized = imutils.resize(template, width = int(template.shape[1] * self.scale))
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(ssGrey,resized,cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print(f"Matching value to image is: {max_val}")

        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        middle = (top_left[0] + (w // 2), top_left[1] + (h // 2))

        # print(top_left)
        # print(bottom_right)
        # print(middle)
        cv2.rectangle(ssGrey,top_left, bottom_right, 255, 1)
        cv2.rectangle(ssGrey,middle, middle, 255, 6)

        # cv2.imwrite('output.png',ssGrey)

        # end = time.time()
        # print(end - start)
        if(max_val < accuracy):
            return (-1,-1)
        return middle

    def findImageLoop(self, image, sleepTime = 15, accuracy = 0.85):
        location = self.findImage(image,accuracy)
        while(location[0] == -1):
            print(f"Image: {image} was not found... sleeping for {sleepTime} seconds")
            time.sleep(sleepTime)
            location = self.findImage(image,accuracy)
        return location

    def findImageIterations(self, image, iterations = 5, sleepTime = 5, accuracy = 0.85):
        for i in range(iterations):
            location = self.findImage(image,accuracy)
            if(location[0] != -1):
                break
            print(f"Image: {image} was not found... sleeping for {sleepTime} seconds")
            time.sleep(sleepTime)
        return location

if __name__ == '__main__':
    imagePath = 'images/'
    tft = TFTBot(imagePath)
    if(len(sys.argv) == 2):
        tft.runner(int(sys.argv[1]))
    else:
        tft.runner()