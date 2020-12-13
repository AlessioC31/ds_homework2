import grpc

from definitions import def_pb2
from definitions import def_pb2_grpc

def image_iterator(num_frames=10):
    for i in range(num_frames):
        yield def_pb2.Image(
            width=1920,
            height=1080,
            #image_data=...here the image should be read,
            frame_id=i
        )

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = def_pb2_grpc.TemperatureSensorStub(channel)

        response_info = stub.SensorInfo(
            def_pb2.Sensor(uid = 5)
        )
        
        print('Data received from SensorInfo with Sensor(uid=5):', response_info)

        
        response_sensordata = stub.SensorData(def_pb2.Sensor(uid = 5))
        print('Data received from SensorData with Sensor(uid=5):')
        
        for data in response_sensordata:
            print(data)
            

        stub2 = def_pb2_grpc.ObjectDetectionStub(channel)

        response_summary = stub2.SummaryDetection(image_iterator())
        print('Data received from SummaryDetection:', response_summary)
        
        response_detect = stub2.Detect(image_iterator())

        for detections in response_detect:
            print('Number of detection:', len(detections.list))

            for detection in detections.list:
                print(detection)

if __name__ == '__main__':
    run()