#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import serial
from sensor_msgs.msg import Imu
from sensor_msgs.msg import FluidPressure
from std_msgs.msg import Float32MultiArray

class SerialImuPressureNode(Node):
    def __init__(self):
        super().__init__("serial_IMU_pressure")
        self.timer = self.create_timer(0.1, self.send_data_cmd)
        self.IMU_pub_ = self.create_publisher(Imu, '/imu/data_raw', 10)    
        self.pressure_pub_ = self.create_publisher(Float32MultiArray, '/sensor/pressure', 10)
        self.get_logger().info("Starting: serial_IMU_pressure")


    def serial_line(self): 
        try:
            self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200)
            self.line = self.ser.readline().decode('utf-8').strip().split(',')
            #self.get_logger().info(f"Raw serial data: {self.line}")
            self.line = [float(n) for n in self.line]
        except Exception as e:
            self.get_logger().error(f"Serial read error: {e}")
            self.line = [0.0] * 9  # Default values if read fails

    def send_data_cmd(self):
        self.serial_line()
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link' 
        msg.linear_acceleration.x = self.line[0]
        msg.linear_acceleration.y = self.line[1]
        msg.linear_acceleration.z = self.line[2]

        msg.angular_velocity.x = self.line[3]
        msg.angular_velocity.y = self.line[4]
        msg.angular_velocity.z = self.line[5]
        self.IMU_pub_.publish(msg)
        print("linear acceleration:",self.line[4:7]," m/s2")
        print("angular velocity  :",self.line[7:10]," rad/s")
        print("Tempreture         :",self.line[10]," C")
        ##########################################
       # pressure
        pressure_msg = Float32MultiArray()
        pressure_msg.data = [self.line[0], self.line[2], self.line[3]]  # [Pressure, Depth, Altitude]
        self.pressure_pub_.publish(pressure_msg)

        print("Pressure Sensor Data: Pressure =", self.line[0], " Pa, Depth =", self.line[2], " m, Altitude =", self.line[3], " m")



def main(args=None):
    rclpy.init(args=args)
    node = SerialImuPressureNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
