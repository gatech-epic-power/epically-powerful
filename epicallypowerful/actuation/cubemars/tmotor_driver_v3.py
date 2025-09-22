import can
CAN_ID = 0x68 # Example CAN ID, replace with actual motor ID
MIT_MODE_ID = 8

P_MIN = -12.56
P_MAX = 12.56
V_MIN = -28.0
V_MAX = 28.0
T_MIN = -54.0
T_MAX = 54.0
KP_MIN = 0
KP_MAX = 500.0
KD_MIN = 0
KD_MAX = 5.0

def float_to_uint(x, x_min, x_max, bits):
    span = float(x_max - x_min)
    return int( (x-x_min) * (((1 << bits)-1) / span))


arbitration_id = MIT_MODE_ID << 8 | CAN_ID
print(f'Arbitration ID for MIT Mode: {arbitration_id.to_bytes(4, "big").hex()}')


# Pack data
pos = 12.56
vel = 6.0
kp = 0.0
kd = 2.0
torque = 0.0


torque = max(T_MIN, min(T_MAX, torque))
pos = max(P_MIN, min(P_MAX, pos))
vel = max(V_MIN, min(V_MAX, vel))
kp = max(KP_MIN, min(KP_MAX, kp))
kd = max(KD_MIN, min(KD_MAX, kd))

pos_uint16 = float_to_uint(pos, P_MIN, P_MAX, 16)
torque_uint12 = float_to_uint(torque, T_MIN, T_MAX, 12)
vel_uint12 = float_to_uint(vel, V_MIN, V_MAX, 12)
kp_uint12 = float_to_uint(kp, KP_MIN, KP_MAX, 12)
kd_uint12 = float_to_uint(kd, KD_MIN, KD_MAX, 12)

print(f'P: {pos_uint16}, V: {vel_uint12}, KP: {kp_uint12}, KD: {kd_uint12}, Torque: {torque_uint12}')

buffer = [0]*8
buffer[0] = kp_uint12 >> 4 # KP High 4 bits
buffer[1] = ((kp_uint12 & 0xF) << 4) | (kd_uint12 >> 8)  # KP Low 4 bits, Kd High 4 bits
buffer[2] = kd_uint12 & 0xFF  # Kd low 8 bits
buffer[3] = pos_uint16 >> 8  # position high 8 bits
buffer[4] = pos_uint16 & 0xFF  # position low 8 bits
buffer[5] = vel_uint12 >> 4  # speed high 8 bits
buffer[6] = ((vel_uint12 & 0xF) << 4) | (torque_uint12 >> 8)  # speed low 4 bits torque high 4 bits
buffer[7] = torque_uint12 & 0xFF  # torque low 8 bits
print(f'Packed Buffer: {buffer}')

# Construct Message
msg = can.Message(
    arbitration_id=arbitration_id,
    data=buffer,  # Example data, replace with actual payload
    is_extended_id=True,
)

print(f'Constructed CAN Message: {msg}')