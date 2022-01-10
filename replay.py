import time
import sys
from threading import Thread

from pynput import keyboard, mouse

COMBINATION = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('f')}

current = set()
cmds = []
clock = 0
kill = False


def tick():
    global clock
    global kill
    while True:
        if kill:
            return
        time.sleep(0.01)
        clock = clock + 0.01


def on_press(key):
    current.add(key)
    if all(k in current for k in COMBINATION):
        kc = keyboard.Controller()
        global kill
        kill = True
        for kd in current:
            kc.release(kd)
        replay()
        return False
    cmds.append({'type': 'keypress', 'data': key, 'time': clock})


def on_release(key):
    global kill
    if kill:
        return False
    if key in current:
        current.remove(key)
    cmds.append({'type': 'keyrelease', 'data': key, 'time': clock})


def on_move(x, y):
    global kill
    if kill:
        return False
    cmds.append({'type': 'move', 'data': (x, y), 'time': clock})


def on_click(x, y, button, pressed):
    global kill
    if kill:
        return False
    if pressed:
        cmds.append({'type': 'mousepress', 'data': button, 'time': clock})
    else:
        cmds.append({'type': 'mouserelease', 'data': button, 'time': clock})


def on_scroll(x, y, dx, dy):
    global kill
    if kill:
        return False
    cmds.append({'type': 'scroll', 'data': (dx, dy), 'time': clock})


def replay():
    kc = keyboard.Controller()
    mc = mouse.Controller()
    curr_time = 0
    for cmd in cmds:
        type = cmd['type']
        cmd_time = cmd['time']
        data = cmd['data']

        diff = cmd_time - curr_time
        if diff > 0:
            time.sleep(diff)
        curr_time = cmd_time

        if type == 'keypress':
            kc.press(data)
        elif type == 'keyrelease':
            kc.release(data)
        elif type == 'move':
            mc.position = data
        elif type == 'mousepress':
            mc.press(data)
        elif type == 'mouserelease':
            mc.release(data)
        elif type == 'scroll':
            mc.scroll(data[0], data[1])
    sys.exit()


if __name__ == '__main__':
    keyboard_listener = keyboard.Listener(
        on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    mouse_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    mouse_listener.start()

    timer_thread = Thread(target=tick)
    timer_thread.start()

    keyboard_listener.join()
    mouse_listener.join()
    timer_thread.join()
