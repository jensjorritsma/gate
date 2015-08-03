#!/usr/bin/env python

import time
import RPi.GPIO as GPIO

from flask import Flask, render_template, Response
from threading import Thread

from camera import VideoCamera


app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.output


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@async
def close_gate(delay=60):
    time.sleep(delay)
    GPIO.output(21, GPIO.LOW)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/open")
def open_gate():
    if GPIO.input(21):
        GPIO.output(21, GPIO.LOW)
    else:
        GPIO.output(21, GPIO.HIGH)
        close_gate(10)

    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True)

    except KeyboardInterrupt:
        print("Keyboard Interupt... cleaning up")

    finally:
        GPIO.cleanup()
