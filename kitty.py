#!/usr/bin/python
import io
import time
import picamera
import curses

####################################################################################################
#
# Kitty.py - laser pointer tracker.  This code will abort if your console screen is less than 68 x 36
#            pixels.
#
####################################################################################################

try:
    #-----------------------------------------------------------------------------------------------
    # Set up the curses screen to fill the console screen and set up a border around the edge of the
    # screen.
    #-----------------------------------------------------------------------------------------------
    stdscr = curses.initscr()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)
    scr_height, scr_width = stdscr.getmaxyx()
    stdscr.border(0)
    stdscr.refresh()

    #-----------------------------------------------------------------------------------------------
    # Picture is 32 x 32 pixels - the minimum size supported, but more than enough for brightest point
    # analysis.
    #-----------------------------------------------------------------------------------------------
    img_width = 32
    img_height = 32

    win_width = img_width * 2 + 2
    win_height = img_height + 2

    #-----------------------------------------------------------------------------------------------
    # Create a bordered window to surround the 32 x 32 pixel picture in the middle of the screen.
    #-----------------------------------------------------------------------------------------------
    win = curses.newwin(win_height, win_width, (scr_height - win_height - 1) / 2, (scr_width - win_width - 1) / 2)
    win.border(0)
    win.refresh()

    #-----------------------------------------------------------------------------------------------
    # Setup a memory based data stream for the PiCamera images
    #-----------------------------------------------------------------------------------------------
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.resolution = (img_width, img_height)
        camera.iso = 800

        while camera.analog_gain <= 1:
            time.sleep(0.1)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g

        #-------------------------------------------------------------------------------------------
        # Take 100 photos as fast as allowed, and process each seperately
        #-------------------------------------------------------------------------------------------
        loops = 0
        while loops < 100:
            loops += 1
            y_string = ""
            average = 0
            peak = 0
            peak_x = 0
            peak_y = 0
            num_bytes = 0

            #---------------------------------------------------------------------------------------
            # Take a picture and record the time taken so we can see how long it takes for taking
            # and processing
            #---------------------------------------------------------------------------------------
            start_time = time.time()
            camera.capture(stream, 'yuv')

            #---------------------------------------------------------------------------------------
            # YUV format presents brightness for the whole picture first as one byte per pixel,
            # followed by UV taking a single each.  We're only interested in Y / B&W / contrast /
            # luminance / brightness so we only process the first 32 x 32 bytes on the stream (1024)
            # and ignore the rest.
            #---------------------------------------------------------------------------------------
            bytes = stream.getvalue()

            #---------------------------------------------------------------------------------------
            # For each of the 1024 bytes we care about, check whether it's brighter than the previous
            # brightest and record brightness and position for posterity if so.
            #---------------------------------------------------------------------------------------
            for ii in range(0, img_height * img_width ):
                byte = ord(bytes[ii])
                average += byte
                num_bytes += 1

                if byte > peak:
                    peak = byte
                    peak_x = ii % img_width
                    peak_y = ii / img_width


            #---------------------------------------------------------------------------------------
            # Output the results of this shot to screen and refresh.  Overwrite the last peak point
            # immediately with a space but do not refresh; this ensure that if the peak point moves
            # the previous one gets 'deleted'
            #---------------------------------------------------------------------------------------
            average /= num_bytes
            stdscr.addstr(0, 10, "X = %d, Y = %d, peaks = %d, average = %d, time = %f" % (peak_x, peak_y, peak, average, time.time() - start_time))
            win.addch(peak_y + 1, peak_x * 2 + 1, '[')
            win.addch(peak_y + 1, peak_x * 2 + 2, ']')
            stdscr.refresh()
            win.refresh()
            win.addch(peak_y + 1, peak_x * 2 + 1, ' ')
            win.addch(peak_y + 1, peak_x *2 ++ 2, ' ')

            #---------------------------------------------------------------------------------------
            # Flush the data stream (probably unnecessary) and move the starting point back to the
            # beginning ready for the next shot
            #---------------------------------------------------------------------------------------
	    stream.flush()
            stream.seek(0)

    stream.close()

#---------------------------------------------------------------------------------------------------
# Critically tidy up regardless of the cause of any exception to ensure terminal is returned to
# normal working order.
#---------------------------------------------------------------------------------------------------
finally:
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
	
 	
