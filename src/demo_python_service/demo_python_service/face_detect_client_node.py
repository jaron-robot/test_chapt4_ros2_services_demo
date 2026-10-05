import rclpy
from rclpy.node import Node
from chapt4_interfaces.srv import FaceDetector
import face_recognition
import cv2
from ament_index_python.packages import get_package_share_directory #获取功能包share目录的绝对路径
import os
from cv_bridge import CvBridge
import time
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter,ParameterValue,ParameterType



class FaceDetectorClientNode(Node):
    def __init__(self):
        super().__init__('face_detect_client_node')
        self.bridge = CvBridge()
        self.default_image_path = os.path.join(get_package_share_directory
        ('demo_python_service'),'resource/test1.png')
        self.get_logger().info(f"人脸检测客户端已启动")
        self.client = self.create_client(FaceDetector,'face_detect')
        self.image = cv2.imread(self.default_image_path)

    def call_set_parameters(self,parameters):
        """
        调用服务，修改参数值
        """
        # 1.创建客户端，等待服务上线
        update_param_client = self.create_client(SetParameters,'/face_detect_node/set_parameters')
        while update_param_client.wait_for_service(timeout_sec=1.0) is False:
            self.get_logger().info(f'等待参数更新服务端上线')

        # 2.创建request
        request = SetParameters.Request()
        request.parameters = parameters

        # 3.调用服务端更新参数
        future = update_param_client.call_async(request)
        rclpy.spin_until_future_complete(self,future)
        response = future.result()
        return response

    def update_detect_model(self,model = 'hog'):
        """
        根据传入的model,构造parameters,然后调用call_set_parameters更新服务端的参数
        """

        # 1.创建参数对象
        param = Parameter()
        param.name = 'model'
        # 2.创建param_value,这一步很迷糊，为什么这样初始化，尤其是param_value = param_value
        param_value = ParameterValue()
        param_value.string_value = model
        param_value.type = ParameterType.PARAMETER_STRING
        param.value = param_value
        # 3.请求更新参数
        response = self.call_set_parameters([param])
        for result in response.results:
            self.get_logger().info(f'设置参数结果:{result.successful}{result.reason}')

    """
    改进：方法二，采用回调函数
    def result_callback(self,result_future):
        response = result_future.result()  #获取响应
        self.get_logger().info(f'接受到响应，共检测到{response.number}张人脸，耗时{response.use_time}s')
        self.show_response(response)
    """

    def send_request(self):
        #1.判断服务端是否在线
        while self.client.wait_for_service(timeout_sec=1.0) is False:
            self.get_logger().info(f"等待服务端上线")

        #构造request
        request = FaceDetector.Request()
        request.image = self.bridge.cv2_to_imgmsg(self.image)

        #发送请求并等待处理完成
        future = self.client.call_async(request)  #并没有包含响应结果，需要等待服务端处理完成才会把结果放在future中
        future.add_done_callback(self.result_callback)
    """
    方法一：但是可能会阻塞
    """    
    def result_callback(self,result_future):
        response = result_future.result()  #获取响应
        self.get_logger().info(f'接受到响应，共检测到{response.number}张人脸，耗时{response.use_time}s')
        #self.show_response(response)
        

    def show_response(self,response):
        for i in range(response.number):
            #为什么代码顺序要这样写，可以是先写left-bottom-top-right·这种顺序吗
            top = response.top[i]
            right = response.right[i]
            bottom = response.bottom[i]
            left = response.left[i]
            cv2.rectangle(self.image,(left,top),(right,bottom),(0,0,255),4)
        cv2.imshow('Face Detect Result',self.image)
        cv2.waitKey(0)  #也是阻塞的，会导致spin无法正常运行，那应该怎么改进呢


def main():
    rclpy.init()
    node = FaceDetectorClientNode()
    node.update_detect_model('hog')
    node.send_request()
    node.update_detect_model('cnn')
    node.send_request()
    rclpy.spin(node)
    rclpy.shutdown()