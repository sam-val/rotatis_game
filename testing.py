import pygame as pg
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from libs import Display
import pprint
import pickle
from pathlib import Path

def main():
    root = tk.Tk()
    root.withdraw()
    rs =  mb.askyesnocancel("hello,?", message="a kiss?")
    print(rs)
    root.destroy()




if __name__ == '__main__':
    pg.init()

    # main()
    pg.quit()