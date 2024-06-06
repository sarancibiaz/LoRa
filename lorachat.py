import serial
import time
import codecs
from PIL import Image
import numpy as np
import threading

serial_port = "/dev/ttyUSBO0"
baud_rate  = 115200

#Radio set up
freq = 915
mod  = "SF9"
band_width = 125
tx_pr = 8
rx_pr = 8
power = 22

#RF configuration string 
rf_conf_str = "AT+TEST=RFCFG,{},{},{},{},{},{},OFF,OFF,OFF\n".format(freq, mod, band_width, tx_pr, rx_pr, power)

#serial object
ser = serial.Serial(serial_port, baud_rate)
send = False
def init():
  global usr, ser
  ser = serial.Serial(serial_port, baud_rate)
  usr = "LoRa"
  initialize_radio()
  print("Radio Initialized")
  print("Your name is: {}".format(usr))
  print("Beginging LoRa Radio Chat...")

def initialize_radio():
  ser.write("AT+MODE=TEST\n".encode())
  time.sleep(0.5)
  ser.write(rf_conf_str.encode())
  print(ser.readline().decode())

def send_msg(message):
  ser.write("AT+TEST=TXLPRKT,\"{}\"n".format(message).encode())
  print(ser.readline().decode())

def receive_meg():
  ser.write("AT+TEST=RXLPRKT".encode())
  while True:
    while not send:
      if ser.inWaiting():
        rx_msg = ser.redaline().decode()
        with open("image.txt", "ab") as f:
          if '+TEST: RX' in rx_msg:
            msg_data = rx_msg.split('\"')[1]
            print(hex_to_chr(msg_data))
            f.write(hex_to_chr(msg_data).encode())
            f.write(b",")

def chr_to_hex(string):
  return codecs.encode(string.encode(),'hex').decode()

def hex_to_chr(string):
  return codecs.decode(string,'hex').decode()

def image_to_packets(image_path, packet_size):
  #Leer la imagen
  image = Image.open(image_path)
  #redimensionar la imagen
  new_width = 64
  new_height = 64
  image = image_resize((new_width, new_height))
  #Convertir la imagen a escala de grises
  image = image.convert("L")
  #Obtener bytes de la imagen
  image_bytes = image.tobytes()
  #Dividir la imagen en packets
  packets = []
  total_bytes = len(image_bytes)
  num_packets = total_bytes//packet_size + 1
  for packet_num in range(num_packets):
    star_index = packet_num * packet_size
    end_index = start_index + packet_size
    packet_data = image_bytes[start_index:end_index]
    packets.append(packet_data)
  return packets

def itp_rgb(image_path, packet_size):
  #leer imagen
  image = Image.open(image_path)
  #redimensionar imagen como arreglo 64x64
  new_width = 64
  new_height = 64
  image = image_resize((new_width, new_height))
  #separar por colores
  red, green, blue = image.split()
  red_bytes = red.tobytes()
  green_bytes = green.tobytes()
  blue_bytes = blue.tobytes()
  #dividir cada canal de colores en paquetes
  red_packets = split_bytes_into_packets(red_bytes, packet_size)
  green_packets = split_bytes_into_packets(green_bytes, packet_size)
  blue_packets = split_bytes_into_packets(blue_bytes, packet_size)
  return red_packets, green_packets, blue_packets

####la cague borre la funcion que esta en el material de u-cursos

def split_bytes_into_packets(data_bytes, packet_size):
  packets = []
  total_bytes = len(data_bytes)
  num_packets = total_bytes//packet_size + 1
  for packet_num in range(num_packets):
    start_index = packet_num * packet_size
    end_index = start_index + packet_size
    packet_data = data_bytes[start_index:end_index]
    packets.append(packet_data)
  return packets

def send_image_packets_to_lora(packets):
  for packet in packets:
    print(packet)
    data = str(packet)
    print("Enviando el dato: ", data)
    send_msg(chr_to_hex(data))
    time.sleep(0.5)
  send_msg(chr_to_hex("|"*5))
  for red in red_packets:
    print(red)
    data = str(red)
    print("Enviando el dato: ", data)
    send_msg(chr_to_hex(data))
    time.sleep(0.5)
  send_msg(chr_to_hex("|||"))
  time.sleep(0.5)
  for green in green_packets:
    print(green)
    data = str(green)
    print("Enviando el dato: ", data)
    send_msg(chr_to_hex(data))
    time.sleep(0.5)
  send_msg(chr_to_hex("|||"))
  time.sleep(0.5)
  for blue in blue_packets:
    print(blue)
    data = str(blue)
    print("Enviando el dato:", data)
    send_msg(chr_to_hex(data))
    time.sleep(0.5)

initialize_radio()
time.sleep(1)

listening = threading.Thread(target = receive_msg, daemon=True)

if __name__ == "__main__":
  init()
  listenig.start()
  while True:
    msg = input(f"{LoRa}:")
    msg = f"{LoRa} -->{msg}"
    send = True
    send_msg(chr_to_hex(msg))
    ser.write("AT+TEST=RXLRPKT".encode())
    time.sleep(0.5)
    send = False

packets = image_to_packets('test_camera.jpg', 10)
main()
send_image_packets_to_lora(packets)
red_packtes, green_packets, blue_packets = image_to_packets('test_camera.jpg', 20)
send_image_to_packets_to_lora(red_packtes, green_packets, blue_packets)
