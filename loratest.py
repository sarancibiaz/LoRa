import serial
import time
import codecs
from PIL import Image
import threading

# Configuración del puerto serial
serial_port = "/dev/ttyUSB0"
baud_rate = 115200

# Configuración de radio
freq = 915
mod = "SF9"
band_width = 125
tx_pr = 8
rx_pr = 8
power = 22

# Cadena de configuración RF
rf_conf_str = "AT+TEST=RFCFG,{},{},{},{},{},{},OFF,OFF,OFF\n".format(freq, mod, band_width, tx_pr, rx_pr, power)

# Objeto serial
ser = serial.Serial(serial_port, baud_rate)
send = False

def init():
    global usr
    usr = "LoRa"
    initialize_radio()
    print("Radio Initialized")
    print("Your name is: {}".format(usr))
    print("Beginning LoRa Radio Chat...")

def initialize_radio():
    ser.write("AT+MODE=TEST\n".encode())
    time.sleep(0.5)
    ser.write(rf_conf_str.encode())
    print(ser.readline().decode())

def send_msg(message):
    ser.write("AT+TEST=TXLPRKT,\"{}\"\n".format(message).encode())
    print(ser.readline().decode())

def receive_msg():
    global send
    ser.write("AT+TEST=RXLPRKT\n".encode())
    while True:
        if not send and ser.in_waiting:
            rx_msg = ser.readline().decode()
            with open("image.txt", "ab") as f:
                if '+TEST: RX' in rx_msg:
                    msg_data = rx_msg.split('\"')[1]
                    print(hex_to_chr(msg_data))
                    f.write(hex_to_chr(msg_data).encode())
                    f.write(b",")

def chr_to_hex(string):
    return codecs.encode(string.encode(), 'hex').decode()

def hex_to_chr(string):
    return codecs.decode(string, 'hex').decode()

def image_to_packets(image_path, packet_size):
    # Leer la imagen
    image = Image.open(image_path)
    # Redimensionar la imagen
    image = image.resize((64, 64))
    # Convertir la imagen a escala de grises
    image = image.convert("L")
    # Obtener bytes de la imagen
    image_bytes = image.tobytes()
    # Dividir la imagen en paquetes
    packets = split_bytes_into_packets(image_bytes, packet_size)
    return packets

def itp_rgb(image_path, packet_size):
    # Leer la imagen
    image = Image.open(image_path)
    # Redimensionar imagen como arreglo 64x64
    image = image.resize((64, 64))
    # Separar por colores
    red, green, blue = image.split()
    # Dividir cada canal de colores en paquetes
    red_packets = split_bytes_into_packets(red.tobytes(), packet_size)
    green_packets = split_bytes_into_packets(green.tobytes(), packet_size)
    blue_packets = split_bytes_into_packets(blue.tobytes(), packet_size)
    return red_packets, green_packets, blue_packets

def split_bytes_into_packets(data_bytes, packet_size):
    packets = []
    total_bytes = len(data_bytes)
    num_packets = (total_bytes + packet_size - 1) // packet_size
    for packet_num in range(num_packets):
        start_index = packet_num * packet_size
        end_index = start_index + packet_size
        packet_data = data_bytes[start_index:end_index]
        packets.append(packet_data)
    return packets

def send_image_packets_to_lora(packets):
    for packet in packets:
        data = packet.decode('latin-1')
        print("Enviando el dato: ", data)
        send_msg(chr_to_hex(data))
        time.sleep(0.5)
    send_msg(chr_to_hex("|" * 5))

def send_color_packets_to_lora(red_packets, green_packets, blue_packets):
    for color_packets in [red_packets, green_packets, blue_packets]:
        for packet in color_packets:
            data = packet.decode('latin-1')
            print("Enviando el dato: ", data)
            send_msg(chr_to_hex(data))
            time.sleep(0.5)
        send_msg(chr_to_hex("|||"))
        time.sleep(0.5)

if __name__ == "__main__":
    init()
    listening_thread = threading.Thread(target=receive_msg, daemon=True)
    listening_thread.start()
    
    while True:
        msg = input(f"{usr}:")
        msg = f"{usr} -->{msg}"
        send = True
        send_msg(chr_to_hex(msg))
        ser.write("AT+TEST=RXLPRKT\n".encode())
        time.sleep(0.5)
        send = False

    packets = image_to_packets('test_camera.jpg', 10)
    send_image_packets_to_lora(packets)
    
    red_packets, green_packets, blue_packets = itp_rgb('test_camera.jpg', 20)
    send_color_packets_to_lora(red_packets, green_packets, blue_packets)
