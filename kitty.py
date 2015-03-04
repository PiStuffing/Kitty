#!/usr/bin/python
import io
import time
import picamera
import curses

try:
    stdscr = curses.initscr()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)
    scr_height, scr_width = stdscr.getmaxyx()
    stdscr.border(0)
    stdscr.refresh()

    width = 32
    height = 32

    win = curses.newwin(height + 2, width + 2, (scr_height - height - 1) / 2, (scr_width - width - 1) / 2)
    win.border(0)
    win.refresh()

    loops = 0
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.resolution = (width, height)
        camera.iso = 800
        camera.start_preview()

        while camera.analog_gain <= 1:
            time.sleep(0.1)
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g

        while loops < 100:
            loops += 1
            start_time = time.time()
            camera.capture(stream, 'yuv')

            y_string = ""
            average = 0
            peak = 0
            peak_x = 0
            peak_y = 0
            num_bytes = 0
            bytes = stream.getvalue()
            
            for ii in range(0, height * width):
                byte = ord(bytes[ii]) 
                average += byte
                num_bytes += 1
                
                if byte > peak:
                    peak = byte
                    peak_x = (ii + 1) % width
                    peak_y = ii / width 

            stdscr.addstr(0, 10, "X = %d, Y = %d, loops = %d, bytes = %d, time = %f" % (peak_x, peak_y, loops, num_bytes, time.time() - start_time))
            win.addch(peak_y + 1, peak_x + 1, 'O')
            stdscr.refresh()
            win.refresh()
            win.addch(peak_y + 1, peak_x + 1, ' ')

	    stream.flush()
            stream.seek(0)        

#                y_string += "%3.3d, " % byte
#                if (ii + 1) % width == 0:
#                   print y_string
#                   y_string = ""
#           average /= (width * height)
#           print "Processing: %f" % (time.time() - start_time)
#            
#           print "peak: %d" % peak
#           print "average: %f" % average
#           print "peak x: %d" % peak_x
#           print "peak y: %d" % peak_y
    stream.close()
        
finally:
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
	
 	
