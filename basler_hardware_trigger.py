# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 12:34:58 2022

@author: rıdvan özdemir
Hardware Trigger With Event Handler

this script grab new image on every trigger without blocking your program
"""

import time
import cv2
from pypylon import pylon

total_time = time.time()

tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
img = pylon.PylonImage()
camera = pylon.InstantCamera(tl_factory.CreateFirstDevice())


print('Start acquiring')
camera.Attach(tl_factory.CreateFirstDevice())
camera.Open()

#camera settings for triggering an input
camera.MaxNumBuffer = 1
camera.TriggerSource ='Line1'
camera.TriggerSelector ='FrameStart'
camera.TriggerMode ='On'
camera.TriggerActivation='FallingEdge'
camera.AcquisitionMode='Continuous'

print("Trigger mode: ", camera.TriggerMode.Value)

converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

class ImageEventPrinter(pylon.ImageEventHandler):
    def OnImagesSkipped(self, camera, countOfSkippedImages):
        print("OnImagesSkipped event for device ", camera.GetDeviceInfo().GetModelName())
        print(countOfSkippedImages, " images have been skipped.")

    def OnImageGrabbed(self, camera, grabResult):
        print("OnImageGrabbed event for device ", camera.GetDeviceInfo().GetModelName())
        print('Waiting for trigger')
        if grabResult.GrabSucceeded():
            print("SizeX: ", grabResult.GetWidth())
            print("SizeY: ", grabResult.GetHeight())
            image = converter.Convert(grabResult)
            image = image.GetArray()
            print("image taken")
            cv2.namedWindow("Detection Window", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Detection Window", 1024,1024)
            cv2.imshow('Detection Window', image)
            print(camera.TriggerMode.Value)
            k= cv2.waitKey(1)
            if k == 27:
                print("program terminated")
                grabResult.Release()
                camera.StopGrabbing()
                cv2.destroyAllWindows()
                camera.Close()

camera.RegisterImageEventHandler(ImageEventPrinter(), pylon.RegistrationMode_Append, pylon.Cleanup_Delete)
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByInstantCamera)
 
print("total time: ", (time.time() - total_time))